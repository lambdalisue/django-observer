from django.db.models.loading import get_model
from django.db.models.fields import FieldDoesNotExist


def get_field(model, attr, ignore_exception=True):
    """
    Get a Field instance of 'attr' in the model

    This function is required while django builtin `meta.get_field(name)` does
    not refer reverse relations, many to many relations, and vritual
    fields.

    Notice that this function iterate all fields to find the corresponding
    field instance. This may cause a performance issue thus you should use
    your own cache system to store the found instance.
    If you are using Python 3.2 or above, you might interested in
    a `functools.lru_cache` or `pylru.lrudecorator` to memoizing the result

    Args:
        model (model): A model or model instance
        attr (name): A name of the attribute interest
        ignore_exception (bool): return None when no corresponding field is
            found if this is True, otherwise raise FieldDoesNotExist

    Raises:
        FieldDoesNotExist: raised when no corresponding field is found and
        `ignore_exception` is False.

    Returns:
        None or an instance of Field.
    """
    meta = model._meta
    # try to find with get_field
    try:
        return meta.get_field(attr)
    except FieldDoesNotExist:
        # reverse relations and virtual fields could not be found
        # with `get_field` thus just ignore it.
        pass
    # from reverse relations of ForeignKey/OneToOneField
    for robj in meta.get_all_related_objects():
        if attr == robj.get_accessor_name():
            # notice that the field belongs to related object
            return robj.field
    # from reverse relations of ManyToMany
    for robj in meta.get_all_related_many_to_many_objects():
        if attr == robj.get_accessor_name():
            # notice that the field belongs to related object
            return robj.field
    # from virtual fields
    for field in meta.virtual_fields:
        if field.name == attr:
            return field
    # could not be found
    if ignore_exception:
        return None
    raise FieldDoesNotExist


def get_relation(relation):
    """
    Resolve relation

    This function resolve a relation indicated as a string (e.g.
    'app_name.Model'). The 'relation' can be a model class for convinience.
    It return ``None`` when the relation could not be resolved. It is happend
    when the related class is not loaded yet.

    Args:
        relation (str or class): A model indicated as a string or class

    Returns:
        (None or a class, app_label, model_name)
    """
    # Try to split the relation
    try:
        app_label, model_name = relation.split('.', 1)
    except AttributeError:
        app_label = relation._meta.app_label
        model_name = relation._meta.model_name
    model = get_model(app_label, model_name, False)
    return model, app_label, model_name


_pending_lookups = {}


def resolve_relation_lazy(relation, operation, **kwargs):
    """
    Resolve relation and call the operation with the specified kwargs.

    The operation will be called when the relation is ready to resolved.
    The original idea was copied from Django 1.2.2 source code thus the
    license belongs to the Django's license (BSD License)

    Args:
        relation (str or class): A relation which you want to resolve
        operation (fn): A callback function which will called with resolved
            relation (class) and the specified kwargs.
    """
    model, app_label, model_name = get_relation(relation)
    if model:
        operation(model, **kwargs)
    else:
        key = (app_label, model_name)
        value = (operation, kwargs)
        _pending_lookups.setdefault(key, []).append(value)


def _do_pending_lookups(sender, **kwargs):
    key = (sender._meta.app_label, sender.__name__)
    for operation, kwargs in _pending_lookups.pop(key, []):
        operation(sender, **kwargs)


from django.db.models.signals import class_prepared
class_prepared.connect(_do_pending_lookups)
