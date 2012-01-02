#!/usr/bin/env python
# vim: set fileencoding=utf8:
"""
Watcher module for watching Model

AUTHOR:
    lambdalisue[Ali su ae] (lambdalisue@hashnote.net)
    
Copyright:
    Copyright 2011 Alisue allright reserved.

License:
    Licensed under the Apache License, Version 2.0 (the "License"); 
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unliss required by applicable law or agreed to in writing, software
    distributed under the License is distrubuted on an "AS IS" BASICS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""
__AUTHOR__ = "lambdalisue (lambdalisue@hashnote.net)"
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import pre_save
from django.db.models.signals import post_save
from django.db.models.signals import post_delete

from base import Watcher

__all__ = ['ModelWatcher']

class ModelWatcher(Watcher):
    """Watcher class for wathching model"""

    def __init__(self, obj, attr, callback):
        if attr is not None:
            raise AttributeError("'attr' must be None for ModelWatcher")
        super(ModelWatcher, self).__init__(obj, attr, callback)
        model = self._obj.__class__
        # Add recivers
        pre_save.connect(self._pre_save_reciver, sender=model, weak=False)
        post_save.connect(self._post_save_reciver, sender=model, weak=False)
        post_delete.connect(self._post_delete_reciver, sender=model, weak=False)
        # Initialize variable
        self._field_names = [field.name for field in model._meta.fields]
        self._previous_values = None

    def unwatch(self):
        model = self._obj.__class__
        pre_save.disconnect(self._pre_save_reciver, sender=model)
        post_save.disconnect(self._post_save_reciver, sender=model)

    def _pre_save_reciver(self, sender, instance, **kwargs):
        if instance.pk is None or instance.pk != self._obj.pk:
            return
        # get previous values from unsaved object
        try:
            unsaved_obj = instance.__class__._default_manager.get(pk=instance.pk)
        except ObjectDoesNotExist:
            unsaved_obj = None
        if unsaved_obj:
            if self._previous_values is None:
                self._previous_values = {}
            for field_name in self._field_names:
                self._previous_values[field_name] = getattr(unsaved_obj, field_name)
        else:
            self._previous_values = None
    def _post_save_reciver(self, sender, instance, **kwargs):
        if self._previous_values is None or instance.pk != self._obj.pk:
            return
        # compare the values with previous values
        def check():
            for field_name in self._field_names:
                previous_value = self._previous_values[field_name]
                current_value = getattr(instance, field_name)
                if previous_value != current_value:
                    return False
            return True
        if not check():
            # update obj
            self._obj = instance
            self.call()

    def _post_delete_reciver(self, sender, instance, **kwargs):
        # update obj
        self._obj = instance
        self.call()
