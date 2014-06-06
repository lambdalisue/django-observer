from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import pre_save
from django.db.models.signals import post_save
from observer.watchers.base import Watcher


class ValueWatcher(Watcher):
    """Watcher class for wathching value attribute"""
    def watch(self):
        model = self.get_model()
        # Add recivers
        pre_save.connect(self._pre_save_reciver, sender=model, weak=False)
        post_save.connect(self._post_save_reciver, sender=model, weak=False)
        # Initialize variable
        self._previous_value = None

    def unwatch(self):
        model = self.get_model()
        pre_save.disconnect(self._pre_save_reciver, sender=model)
        post_save.disconnect(self._post_save_reciver, sender=model)

    def _pre_save_reciver(self, sender, instance, **kwargs):
        # validate with the instance pk
        if not self._validate_signal_instance(instance):
            return
        # use a value of obj in database (unsaved) or specify
        # ObjectDoesNotExist to tell the post_reciver that the object could not
        # found.
        try:
            unsaved_obj = self.get_object(use_cached=False)
            self._previous_value = self.get_attr_value(unsaved_obj)
        except ObjectDoesNotExist:
            # `None` cannot be used in this caes because the attribute
            # possibly assigned as `None`. Probaly nobody would assign the
            # attribute as `ObjectDoesNotExist` thus I use it in this case.
            self._previous_value = ObjectDoesNotExist

    def _post_save_reciver(self, sender, instance, **kwargs):
        # validate with the instance pk
        if not self._validate_signal_instance(instance):
            return
        # if pre reciever could not found the object, ignore
        if self._previous_value is ObjectDoesNotExist:
            return
        # compare the value with previous value and call when the value is
        # changed
        if self._previous_value != self.get_attr_value(instance):
            self.call()
