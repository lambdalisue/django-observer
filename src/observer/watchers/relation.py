from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import pre_save
from django.db.models.signals import post_save
from django.db.models.signals import post_delete
from django.db.models.signals import m2m_changed
from observer.watchers.base import Watcher
from observer.utils.models import find_related_attr_name, get_latest_obj


class ManyRelatedManagerWatcher(Watcher):
    """Watcher class for wathching many to many relation attribute"""
    def watch(self):
        through = self.get_through()
        m2m_changed.connect(self._m2m_changed_reciver, sender=through)

    def unwatch(self):
        through = self.get_through()
        m2m_changed.disconnect(self._m2m_changed_reciver, sender=through)

    def _m2m_changed_reciver(self, sender, instance, action,
                             reverse, model, pk_set, **kwargs):
        if action not in ('post_add', 'post_remove', 'post_clear'):
            return
        obj = self.get_object()
        model = self.get_model()
        if instance == obj or pk_set is None:
            self.call()
        else:
            for pk in pk_set:
                if model._default_manager.get(pk=pk) == obj:
                    self.call()
                    return

    def get_model(self):
        return self.get_attr_value().model

    def get_object(self):
        return self.get_attr_value().instance

    def get_through(self):
        return self.get_attr_value().through


class RelatedManagerWatcher(Watcher):
    """Watcher class for wathching many to one relation attribute"""
    def watch(self):
        # Add recivers
        model = self.get_model()
        self._related_updated = {}
        self._related_attr_name = self._find_related_attr_name()
        pre_save.connect(self._pre_save_reciver,
                         sender=model, weak=False)
        post_save.connect(self._post_save_reciver,
                          sender=model, weak=False)
        post_delete.connect(self._post_delete_reciver,
                            sender=model, weak=False)

    def unwatch(self):
        """stop watching the field"""
        model = self.get_model()
        pre_save.disconnect(self._pre_save_reciver, sender=model)
        post_save.disconnect(self._post_save_reciver, sender=model)
        post_delete.disconnect(self._post_delete_reciver, sender=model)

    def _find_related_attr_name(self):
        return find_related_attr_name(self.get_model(), self._attr)

    def _get_related_attr_value(self, instance):
        return getattr(instance, self._related_attr_name, KeyError)

    def _pre_save_reciver(self, sender, instance, **kwargs):
        if not self._validate_signal_instance(instance):
            return
        # find unsaved_obj and unsaved_related_attr_value
        if instance.pk is None:
            unsaved_obj = None
        else:
            try:
                unsaved_obj = get_latest_obj(instance)
                unsaved_rav = self._get_related_attr_value(unsaved_obj)
            except ObjectDoesNotExist:
                unsaved_obj = None
        # compare values
        related_attr_value = self._get_related_attr_value(instance)
        if related_attr_value.pk == self._obj.pk:
            if (not unsaved_obj or
                    getattr(unsaved_rav, 'pk', None) != self._obj.pk):
                # New relation has created
                self._related_updated[id(instance)] = True
                return
        elif unsaved_obj and unsaved_rav.pk == self._obj.pk:
            if related_attr_value.pk != self._obj.pk:
                # Old relation has removed
                self._related_updated[id(instance)] = True
                return
        self._related_updated[id(instance)] = False

    def _post_save_reciver(self, sender, instance, **kwargs):
        if not self._validate_signal_instance(instance):
            return
        if self._related_updated.pop(id(instance), None):
            self.call()

    def _post_delete_reciver(self, sender, instance, **kwargs):
        if not self._validate_signal_instance(instance):
            return
        related_attr_value = self._get_related_attr_value(instance)
        if related_attr_value.pk == self._obj.pk:
            self.call()

    def _validate_signal_instance(self, instance):
        related_attr_value = self._get_related_attr_value(instance)
        if related_attr_value is KeyError:
            # related attr value could not get thus just ignore
            return False
        return True

    def get_model(self):
        return self.get_attr_value().model


class GenericRelatedObjectManagerWatcher(RelatedManagerWatcher):
    """Watcher class for wathching generic relation attribute"""
    def watch(self):
        super(GenericRelatedObjectManagerWatcher, self).watch()
        # remove unused attrs
        del self._related_attr_name
        # add required instance
        rel = self.get_attr_value()
        self._object_id_field_name = rel.object_id_field_name
        self._content_type_field_name = rel.content_type_field_name

    def _find_related_attr_name(self):
        # GenericRelatedObjectManagerWatcher does not require this
        return None

    def _get_related_attr_value(self, instance):
        content_type = getattr(instance, self._content_type_field_name)
        object_id = getattr(instance, self._object_id_field_name)
        return content_type.get_object_for_this_type(pk=object_id)
