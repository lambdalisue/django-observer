from django.core.exceptions import ObjectDoesNotExist
import logging

logger = logging.getLogger(__name__)

# Note: Why staticmethod is used insted of classmethod
#
#   Watcher is used as watcher instance holder and if I use classmethod
#   for _register/_unregister then the instance list belongs to
#   each subclass and that is not what I need (if I use 'cls' insted of Watcher)
#
class Watcher(object):
    def __init__(self, obj, attr, callback):
        if obj.pk is None:
            raise AttributeError(
                    """'%s' instance needs to have primary key before """
                    """observer can watch the instance""" % obj.__class__.__name__)
        self._obj = obj
        self._attr = attr
        self._callback = callback

        # Register the instance
        Watcher._register(self)

    @staticmethod
    def _register(instance):
        if not hasattr(Watcher, '_instances'):
            Watcher._instances = []
        Watcher._instances.append(instance)
    @staticmethod
    def _unregister(instance):
        if not hasattr(Watcher, '_instances'):
            return
        Watcher._instances.remove(instance)
    @staticmethod
    def unwatch_all():
        for watcher in getattr(Watcher, '_instances', []):
            logger.debug('%s is unwatched' % watcher)
            watcher.unwatch()
        Watcher._instances = []

    def get_attr_value(self):
        """get attribute value"""
        return getattr(self._obj, self._attr)

    def unwatch(self):
        """remove all receivers used in this watcher"""
        raise NotImplementedError

    def call(self):
        """call callback registered in this watcher"""
        # hand latest instance (self._obj is not latest)
        try:
            instance = self._obj.__class__._default_manager.get(pk=self._obj.pk)
        except ObjectDoesNotExist:
            instance = self._obj
        self._callback(sender=self, obj=instance, attr=self._attr)
