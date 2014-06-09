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
