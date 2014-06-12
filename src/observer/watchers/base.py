from observer.conf import settings
from observer.compat import lru_cache
from observer.utils.models import get_field
from observer.utils.models import resolve_relation_lazy


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
            def resolve_related_class(model, self):
                self._model = model
            resolve_relation_lazy(model, resolve_related_class, self=self)

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
        def recall_lazy_watch(sender, self, **kwargs):
            self.lazy_watch(**kwargs)
        # check if the model is ready
        if not is_relation_ready(self.model):
            resolve_relation_lazy(self.model, recall_lazy_watch,
                                  self=self, **kwargs)
            return

        # check if the related models is ready
        field = self.get_field()
        if field.rel and not is_relation_ready(field.rel.to):
            resolve_relation_lazy(field.rel.to, recall_lazy_watch,
                                  self=self, **kwargs)
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
