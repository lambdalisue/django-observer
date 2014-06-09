from django.db.models.loading import get_model
from django.db.models.signals import class_prepared
from observer.conf import settings
from observer.compat import lru_cache
from observer.utils.models import get_field


# ============================================================================
# COPIED AND MODIFIED FROM DJANGO 1.2.2

pending_lookups = {}


def add_lazy_relation(field, relation, operation):
    # Look for an "app.Model" relation
    try:
        app_label, model_name = relation.split(".")
    except AttributeError:
        # If it doesn't have a split it's actually a model class
        app_label = relation._meta.app_label
        model_name = relation._meta.object_name

    # Try to look up the related model, and if it's already loaded resolve the
    # string right away. If get_model returns None, it means that the related
    # model isn't loaded yet, so we need to pend the relation until the class
    # is prepared.
    model = get_model(app_label, model_name, False)
    if model:
        operation(field, model)
    else:
        key = (app_label, model_name)
        value = (field, operation)
        pending_lookups.setdefault(key, []).append(value)


def do_pending_lookups(sender, **kwargs):
    key = (sender._meta.app_label, sender.__name__)
    for field, operation in pending_lookups.pop(key, []):
        operation(field, sender)

class_prepared.connect(do_pending_lookups)
# ============================================================================


def is_relation_ready(relation):
    """
    Return if the relation is ready to use
    """
    if isinstance(relation, basestring) or relation._meta.pk is None:
        return False
    return True


class WatcherBase(object):
    """
    A base watcher field class. Subclass must override `watch` and `unwatch`
    methods.
    """
    def __init__(self, model, attr, callback):
        """
        Construct watcher field

        Args:
            model (model or string): A target model class or app_label.Model
            attr (str): A name of attribute
            callback (fn): A callback function
        """
        self._model = model
        self._attr = attr
        self._callback = callback

        # resolve string model specification
        if not is_relation_ready(model):
            def resolve_related_class(self, model):
                self._model = model
            add_lazy_relation(self, model, resolve_related_class)

    @property
    def model(self):
        return self._model

    @property
    def attr(self):
        return self._attr

    @property
    def callback(self):
        return self._callback

    def lazy_watch(self, **kwargs):
        """
        Call watch safely. It wait until everything get ready.
        """
        def recall_lazy_watch(field, sender):
            field.lazy_watch(**kwargs)
        # check if the model is ready
        if not is_relation_ready(self.model):
            add_lazy_relation(self, self.model, recall_lazy_watch)
            return

        # check if the related models is ready
        rel = self.get_field().rel
        if rel and not is_relation_ready(rel.to):
            add_lazy_relation(self, rel.to, recall_lazy_watch)
            return

        # ready to watch
        self.watch(**kwargs)

    def watch(self):
        """
        Start watching the attribute of the model
        """
        raise NotImplementedError

    def unwatch(self):
        """
        Stop watching the attribute of the model
        """
        raise NotImplementedError

    def call(self, obj):
        """
        Call the registered callback function with latest object

        Args:
            obj (obj): An object instance
        """
        self.callback(sender=self, obj=obj, attr=self.attr)

    @lru_cache(settings.OBSERVER_LRU_CACHE_SIZE)
    def get_field(self, attr=None):
        """
        Get field instance of the attr in the target object
        """
        attr = attr or self.attr
        return get_field(self.model, attr)
