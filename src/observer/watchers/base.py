from django.core.exceptions import ObjectDoesNotExist
from observer.utils.registry import registry


class Watcher(object):
    """
    A base class of watcher.
    """
    @staticmethod
    def unwatch_all():
        """
        Unwatch all watchers in this Python session
        """
        for watcher in registry:
            watcher.unwatch()
        registry.clear()

    def __init__(self, obj, attr, callback, start_watch=True):
        """
        Constructor

        It construct watcher and start watch.

        Args:
            obj (obj): A target obj
            attr (str): A name of attribute
            callback (fn): A callback function
            start_watch (bool): If it is True, automatically start watch.
                Default value is True

        Raises:
            AttributeError: When the obj does not have primary key
        """
        if obj.pk is None:
            raise AttributeError(
                "'%s' instance needs to have primary key before "
                "observer can watch the instance" % obj.__class__.__name__)
        self._obj = obj
        self._attr = attr
        self._callback = callback
        # Register the instance
        registry.register(self)
        # Start watch
        if start_watch:
            self.watch()

    @property
    def obj(self):
        return self._obj

    @property
    def attr(self):
        return self._attr

    @property
    def callback(self):
        return self._callback

    def get_attr_value(self, obj=None):
        """
        Get specified attribute value of obj

        Args:
            obj (instance or None): A target object. If it is not specified,
                cached obj is used.

        Return:
            any
        """
        return getattr(obj or self._obj, self._attr)

    def watch(self):
        """
        Start watching the object
        """
        raise NotImplementedError

    def unwatch(self):
        """
        Stop watching the object
        """
        raise NotImplementedError

    def call(self):
        """
        Call the registered callback with watched object
        """
        obj = self.get_object()
        self.callback(sender=self, obj=obj, attr=self._attr)

    def get_model(self):
        """
        Get model of this watcher watched.

        Returns:
            class (model of the cached_obj)
        """
        return self._obj.__class__

    def get_object(self, use_cached=True):
        """
        Get object which this watcher watched.
        This method try to load the latest object instance from the database.

        Args:
            use_cached (bool): If True, use cached obj when no object is found

        Raises:
            ObjectDoesNotExist: If use_cached is False and the object is not
                found in the database

        Returns:
            obj
        """
        default_manager = self.get_model()._default_manager
        # while self._obj is not the latest instance, try to get the latest
        # instance from a database
        try:
            obj = default_manager.get(pk=self._obj.pk)
        except ObjectDoesNotExist:
            if not use_cached:
                raise
            obj = self._obj
        return obj

    def _validate_signal_instance(self, instance):
        if instance.pk != self.get_object().pk:
            return False
        return True
