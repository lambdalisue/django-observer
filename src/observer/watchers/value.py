from django.db.models.signals import pre_save
from django.db.models.signals import post_save
from observer.investigator import Investigator
from observer.utils.signals import (register_reciever,
                                    unregister_reciever)
from base import WatcherBase


class ValueWatcher(WatcherBase):
    """
    Watcher field for watching non relational field such as CharField.
    """
    def __init__(self, model, attr, callback, call_on_created=True):
        super(ValueWatcher, self).__init__(model, attr, callback)
        self._call_on_created = call_on_created

    def watch(self, call_on_created=None):
        self._call_on_created = (self._call_on_created
                                 if call_on_created is None
                                 else call_on_created)
        # initialize investigator
        self._investigator = Investigator(self.model, include=[self.attr])
        # register the receivers
        register_reciever(self.model, pre_save,
                          self._pre_save_receiver)
        register_reciever(self.model, post_save,
                          self._post_save_receiver)

    def unwatch(self):
        unregister_reciever(self.model, pre_save,
                            self._pre_save_receiver)
        unregister_reciever(self.model, post_save,
                            self._post_save_receiver)

    def _pre_save_receiver(self, sender, instance, **kwargs):
        if kwargs.get('row', False):
            # should not call any callback while it is called via fixtures or
            # so on
            return
        self._investigator.prepare(instance)

    def _post_save_receiver(self, sender, instance, created, **kwargs):
        if kwargs.get('row', False):
            # should not call any callback while it is called via fixtures or
            # so on
            return
        if self._call_on_created and created:
            self.call(instance)
        # if investigator yield any field_name, call the callback
        if any(self._investigator.investigate(instance)):
            self.call(instance)
