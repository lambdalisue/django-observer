from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import pre_save
from django.db.models.signals import post_save
from django.db.models.signals import post_delete
from observer.watchers.base import Watcher


class ModelWatcher(Watcher):
    """Watcher class for wathching model"""

    def __init__(self, obj, attr, callback, start_watch=True):
        # ModelWatcher does not require attr
        if attr is not None:
            raise AttributeError("'attr' must be None for ModelWatcher")
        super(ModelWatcher, self).__init__(obj, attr, callback, start_watch)

    def watch(self):
        model = self.get_model()
        # Add recivers
        pre_save.connect(self._pre_save_reciver,
                         sender=model, weak=False)
        post_save.connect(self._post_save_reciver,
                          sender=model, weak=False)
        post_delete.connect(self._post_delete_reciver,
                            sender=model, weak=False)
        # Initialize variable
        self._field_names = [field.name for field in model._meta.fields]
        self._previous_values = None

    def unwatch(self):
        model = self.get_model()
        pre_save.disconnect(self._pre_save_reciver, sender=model)
        post_save.disconnect(self._post_save_reciver, sender=model)
        post_delete.disconnect(self._post_delete_reciver, sender=model)

    def _pre_save_reciver(self, sender, instance, **kwargs):
        # validate instance via pk
        if not self._validate_signal_instance(instance):
            return
        # get previous values from unsaved object
        try:
            unsaved_obj = self.get_object(use_cached=False)
            if self._previous_values is None:
                self._previous_values = {}
            for field_name in self._field_names:
                self._previous_values[field_name] = getattr(unsaved_obj,
                                                            field_name)
        except ObjectDoesNotExist:
            self._previous_values = None

    def _post_save_reciver(self, sender, instance, **kwargs):
        # validate instance via pk
        if not self._validate_signal_instance(instance):
            return
        # could pre reciver found the object in the database?
        if self._previous_values is None:
            return
        # compare the values with previous values
        for field_name in self._field_names:
            previous_value = self._previous_values[field_name]
            current_value = getattr(instance, field_name)
            if previous_value != current_value:
                # modification is found thus update cached_obj and call the
                # callback and exit
                self._obj = instance
                self.call()
                return

    def _post_delete_reciver(self, sender, instance, **kwargs):
        self._obj = instance
        self.call()
