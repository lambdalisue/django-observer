#!/usr/bin/env python
# vim: set fileencoding=utf8:
"""
Watcher module for watching any relational field

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
from django.db.models import ForeignKey
from django.db.models.signals import pre_save
from django.db.models.signals import post_save
from django.db.models.signals import post_delete
from django.db.models.signals import m2m_changed

from base import Watcher

__all__ = ['ManyRelatedManagerWatcher', 'RelatedManagerWatcher', 'GenericRelatedObjectManagerWatcher']

class ManyRelatedManagerWatcher(Watcher):
    """Watcher class for wathching many to many relation attribute"""
    def __init__(self, obj, attr, callback):
        super(ManyRelatedManagerWatcher, self).__init__(obj, attr, callback)
        through = self.get_attr_value().through
        m2m_changed.connect(self._m2m_changed_reciver, sender=through)

    def unwatch(self):
        """stop watching the field"""
        through = self.get_attr_value().through
        m2m_changed.disconnect(self._m2m_changed_reciver, sender=through)

    def _m2m_changed_reciver(self, sender, instance, action, reverse, model, pk_set, **kwargs):
        if action not in ('post_add', 'post_remove', 'post_clear'):
            return
        if instance == self.get_attr_value().instance or pk_set is None:
            self.call()
        else:
            model = self.get_attr_value().model
            manager = model._default_manager
            for pk in pk_set:
                if manager.get(pk=pk) == self.get_attr_value().instance:
                    self.call()
                    return

class RelatedManagerWatcher(Watcher):
    """Watcher class for wathching many to one relation attribute"""
    def __init__(self, obj, attr, callback):
        super(RelatedManagerWatcher, self).__init__(obj, attr, callback)
        self._model = self.get_attr_value().model
        self._related_attr_name = self._find_related_attr_name()
        self._related_updated = {}
        # Add recivers
        pre_save.connect(self._pre_save_reciver, sender=self._model, weak=False)
        post_save.connect(self._post_save_reciver, sender=self._model, weak=False)
        post_delete.connect(self._post_delete_reciver, sender=self._model, weak=False)

    def unwatch(self):
        """stop watching the field"""
        pre_save.disconnect(self._pre_save_reciver, sender=self._model)
        post_save.disconnect(self._post_save_reciver, sender=self._model)
        post_delete.disconnect(self._post_delete_reciver, sender=self._model)
    
    def _find_related_attr_name(self):
        for field in self._model._meta.fields:
            if not isinstance(field, ForeignKey):
                continue
            accessor_name = field.related.get_accessor_name()
            if accessor_name == self._attr:
                return field.name
        return None

    def _get_related_attr_value(self, instance):
        return getattr(instance, self._related_attr_name, None)

    def _pre_save_reciver(self, sender, instance, **kwargs):
        if instance.pk is None:
            unsaved_obj = None
        else:
            try:
                unsaved_obj = instance.__class__._default_manager.get(pk=instance.pk)
                unsaved_related_attr_value = self._get_related_attr_value(unsaved_obj)
            except ObjectDoesNotExist:
                unsaved_obj = None
        related_attr_value = self._get_related_attr_value(instance)
        if not related_attr_value:
            return
        if related_attr_value.pk == self._obj.pk:
            if not unsaved_obj or getattr(unsaved_related_attr_value, 'pk', None) != self._obj.pk:
                # New relation has created
                self._related_updated[id(instance)] = True
                return
        elif unsaved_obj and unsaved_related_attr_value.pk == self._obj.pk:
            if related_attr_value.pk != self._obj.pk:
                # Old relation has removed
                self._related_updated[id(instance)] = True
                return
        self._related_updated[id(instance)] = False
    def _post_save_reciver(self, sender, instance, **kwargs):
        related_attr_value = self._get_related_attr_value(instance)
        if not related_attr_value:
            return
        if self._related_updated.pop(id(instance), None):
            self.call()

    def _post_delete_reciver(self, sender, instance, **kwargs):
        related_attr_value = self._get_related_attr_value(instance)
        if not related_attr_value:
            return
        if related_attr_value.pk == self._obj.pk:
            self.call()

class GenericRelatedObjectManagerWatcher(RelatedManagerWatcher):
    """Watcher class for wathching generic relation attribute"""
    def __init__(self, obj, attr, callback):
        super(GenericRelatedObjectManagerWatcher, self).__init__(obj, attr, callback)
        # remove unused attrs
        self._related_attr_name = None
        # add required instance
        rel = self.get_attr_value()
        self._object_id_field_name = rel.object_id_field_name
        self._content_type_field_name = rel.content_type_field_name
    def _get_related_attr_value(self, instance):
        content_type = getattr(instance, self._content_type_field_name)
        object_id = getattr(instance, self._object_id_field_name)
        return content_type.get_object_for_this_type(pk=object_id)
