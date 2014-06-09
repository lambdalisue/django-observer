from django.db.models import ForeignKey, OneToOneField, ManyToManyField
from django.contrib.contenttypes.generic import (GenericForeignKey,
                                                 GenericRelation)
from base import WatcherBase
from value import ValueWatcher
from related import RelatedWatcher, ManyRelatedWatcher, GenericRelatedWatcher


RELATIONAL_FIELDS = (ForeignKey, OneToOneField,)
MANY_RELATIONAL_FIELDS = (ManyToManyField,)
GENERIC_RELATIONAL_FIELDS = (GenericForeignKey, GenericRelation)


class AutoWatcher(WatcherBase):
    """
    A base watcher field for relational field such as ForeignKey, ManyToMany
    """
    def __init__(self, model, attr, callback, **kwargs):
        """
        Construct watcher field

        Args:
            model (model): A target model class
            attr (str): A name of attribute
            callback (fn): A callback function
            **kwargs: Passed to sub watchers
        """
        super(AutoWatcher, self).__init__(model, attr, callback)
        self._kwargs = kwargs

    def watch(self, **kwargs):
        if hasattr(self, '_internal_watcher'):
            self.unwatch()
        Watcher = self.get_suitable_watcher_class()
        self._internal_watcher = Watcher(self.model,
                                         self.attr,
                                         self.callback,
                                         **self._kwargs)
        self._internal_watcher.watch(**kwargs)

    def unwatch(self):
        self._internal_watcher.unwatch()

    def get_suitable_watcher_class(self, field=None):
        field = field or self.get_field()
        if field in RELATIONAL_FIELDS:
            return RelatedWatcher
        if field in MANY_RELATIONAL_FIELDS:
            return ManyRelatedWatcher
        if field in GENERIC_RELATIONAL_FIELDS:
            return GenericRelatedWatcher
        return ValueWatcher
