#!/usr/bin/env python
# vim: set fileencoding=utf8:
"""
Watch module for watching model field attribute


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

from base import Watcher

__all__ = ['ValueWatcher']

class ValueWatcher(Watcher):
    """Watcher class for wathching value attribute"""
    def __init__(self, obj, attr, callback):
        super(ValueWatcher, self).__init__(obj, attr, callback)
        model = self._obj.__class__
        # Add recivers
        pre_save.connect(self._pre_save_reciver, sender=model, weak=False)
        post_save.connect(self._post_save_reciver, sender=model, weak=False)
        # Initialize variable
        self._previous_value = None

    def unwatch(self):
        """stop watching the field"""
        model = self._obj.__class__
        pre_save.disconnect(self._pre_save_reciver, sender=model)
        post_save.disconnect(self._post_save_reciver, sender=model)

    def _pre_save_reciver(self, sender, instance, **kwargs):
        if instance.pk is None or instance.pk != self._obj.pk:
            return
        # get previous value from unsaved object
        try:
            unsaved_obj = instance.__class__._default_manager.get(pk=instance.pk)
            self._previous_value = getattr(unsaved_obj, self._attr)
        except ObjectDoesNotExist:
            self._previous_value = ObjectDoesNotExist
    def _post_save_reciver(self, sender, instance, **kwargs):
        if self._previous_value is ObjectDoesNotExist or instance.pk != self._obj.pk:
            return
        # compare the value with previous value
        if self._previous_value != getattr(instance, self._attr):
            self.call()
