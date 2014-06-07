from observer.watchers.base import Watcher
from observer.watchers.value import ValueWatcher
from observer.watchers.model import ModelWatcher
from observer.watchers.relation import RelatedManagerWatcher
from observer.watchers.relation import ManyRelatedManagerWatcher
from observer.watchers.relation import GenericRelatedObjectManagerWatcher
from observer.utils.models import get_field


class DummyWatcher(object):
    def watch(self):
        pass

    def unwatch(self):
        pass


class ComplexWatcher(Watcher):
    def watch(self):
        # initialize variables
        self._value_watcher = None
        self._model_watcher = None
        self._model_watchers = []
        self._related_manager_watcher = None
        self._many_related_manager_watcher = None
        self._generic_related_object_manager_watcher = None
        # detect sutable watchers and assign
        field = self.get_field()
        attr_value = self.get_attr_value()
        if self._is_generic_field(field, attr_value):
            # A generic relation attribute. This should be checked before
            # related field because GenericRelation is inherited from
            # RelatedObject class
            self._set_generic_related_object_manager_watcher()
            self._set_model_watchers()
        elif self._is_related_field(field, attr_value):
            # A related field (ManyToOne)
            self._set_related_manager_watcher()
            self._set_model_watchers()
        elif self._is_many_related_field(field, attr_value):
            # A many related field (ManyToMany)
            self._set_many_related_manager_watcher()
            self._set_model_watchers()
        elif self._is_model_field(field, attr_value):
            # A single model attribute (OneToMany)
            self._set_value_watcher()
            self._set_model_watcher()
        else:
            # Probaly normal value field
            self._set_value_watcher()

    def unwatch(self):
        # unwatch all possible watcher (fail silently)
        self._delete_watcher('_value_watcher')
        self._delete_watcher('_model_watcher')
        self._delete_watcher('_model_watchers')
        self._delete_watcher('_related_manager_watcher')
        self._delete_watcher('_many_related_manager_watcher')
        self._delete_watcher('_generic_related_object_manager_watcher')

    def get_field(self, obj=None, attr=None):
        """Get attribute field object of obj"""
        return get_field(obj or self._obj,
                         attr or self._attr)

    def _is_model_field(self, field, attr_value):
        """Return True if the field seem to be ForeignKey field"""
        from django.db.models import Model, ForeignKey
        conditions = (
            isinstance(field, ForeignKey),
            # required for generic foreign key distinguish
            isinstance(attr_value, Model),
        )
        return any(conditions)

    def _is_generic_field(self, field, attr_value):
        """Return True if the field seem to be GenericRelation field"""
        from django.contrib.contenttypes.generic import GenericRelation
        conditions = (
            # django 1.3-1.5
            isinstance(field, GenericRelation),
            # django 1.6 and above
            isinstance(getattr(field, 'field', None), GenericRelation),
        )
        return any(conditions)

    def _is_related_field(self, field, attr_value):
        """Return True if the field seem to be RelatedObject field"""
        from django.db.models import ForeignKey
        conditions = (
            isinstance(getattr(field, 'field', None), ForeignKey),
        )
        return any(conditions)

    def _is_many_related_field(self, field, attr_value):
        """Return True if the field seeem to be ManyToMany field"""
        from django.db.models import ManyToManyField
        conditions = (
            isinstance(field, ManyToManyField),
        )
        return any(conditions)

    def _delete_watcher(self, name):
        """delete named watcher"""
        if name == '_model_watchers':
            if self._model_watchers != []:
                for model_watcher in self._model_watchers:
                    model_watcher.unwatch()
            self._model_watchers = []
        else:
            watcher = getattr(self, name, None)
            if watcher:
                watcher.unwatch()
                setattr(self, name, None)

    def _set_value_watcher(self):
        self._delete_watcher('_value_watcher')
        self._value_watcher = ValueWatcher(self.obj,
                                           self.attr,
                                           self._value_watcher_callback)

    def _set_model_watcher(self):
        self._delete_watcher('_model_watcher')
        attr_value = self.get_attr_value()
        if attr_value:
            self._model_watcher = ModelWatcher(attr_value,
                                               None,
                                               self._model_watcher_callback)
        else:
            # for ForeignKey(null=True)
            self._model_watcher = DummyWatcher()

    def _set_model_watchers(self):
        self._delete_watcher('_model_watchers')
        for model in self.get_attr_value().iterator():
            self._model_watchers.append(
                ModelWatcher(model, None, self._model_watcher_callback))

    def _set_related_manager_watcher(self):
        self._delete_watcher('_related_manager_watcher')
        self._related_manager_watcher = \
            RelatedManagerWatcher(self.obj, self.attr,
                                  self._related_manager_watcher_callback)

    def _set_many_related_manager_watcher(self):
        self._delete_watcher('_many_related_manager_watcher')
        self._many_related_manager_watcher = \
            ManyRelatedManagerWatcher(
                self.obj, self.attr,
                self._many_related_manager_watcher_callback)

    def _set_generic_related_object_manager_watcher(self):
        self._delete_watcher('_generic_related_object_manager_watcher')
        self._generic_related_object_manager_watcher = \
            GenericRelatedObjectManagerWatcher(
                self.obj, self.attr,
                self._generic_related_object_manager_watcher_callback)

    def _value_watcher_callback(self, sender, obj, attr):
        self.call()
        if self._model_watcher:
            self._set_model_watcher()

    def _model_watcher_callback(self, sender, obj, attr):
        self.call()

    def _related_manager_watcher_callback(self, sender, obj, attr):
        self.call()
        self._set_model_watchers()

    def _many_related_manager_watcher_callback(self, sender, obj, attr):
        self.call()
        self._set_model_watchers()

    def _generic_related_object_manager_watcher_callback(self, sender,
                                                         obj, attr):
        self.call()
        self._set_model_watchers()
