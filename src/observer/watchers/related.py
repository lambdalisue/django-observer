from django.db.models.signals import pre_save
from django.db.models.signals import post_save
from django.db.models.signals import m2m_changed
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes.generic import GenericForeignKey
from observer.conf import settings
from observer.compat import lru_cache
from observer.investigator import Investigator
from observer.utils.signals import register_reciever, unregister_reciever
from base import WatcherBase
from value import ValueWatcher


class RelatedWatcherBase(WatcherBase):
    """
    A base watcher field for relational field such as ForeignKey, ManyToMany
    """
    def __init__(self, model, attr, callback,
                 call_on_created=True,
                 include=None, exclude=None):
        """
        Construct watcher field

        Args:
            model (model): A target model class
            attr (str): A name of attribute
            callback (fn): A callback function
            call_on_created (bool): Call callback when the new instance is
                created
            include (None, list, tuple): A related object field name list
                which will be investigated to determine the modification
            exclude (None, list, tuple): A related object field name list
                which won't be investigated to determine the modification
        """
        super(RelatedWatcherBase, self).__init__(model, attr, callback)
        self.include = include
        self.exclude = exclude
        self._call_on_created = call_on_created

    @property
    @lru_cache(settings.OBSERVER_LRU_CACHE_SIZE)
    def is_reversed(self):
        return self.get_field().model != self._model

    @property
    @lru_cache(settings.OBSERVER_LRU_CACHE_SIZE)
    def related_model(self):
        field = self.get_field()
        if self.is_reversed:
            return field.model
        return field.related.parent_model

    @property
    @lru_cache(settings.OBSERVER_LRU_CACHE_SIZE)
    def related_attr(self):
        field = self.get_field()
        if self.is_reversed:
            return field.name
        return field.related.get_accessor_name()

    def watch(self, call_on_created=None, include=None, exclude=None):
        self._call_on_created = (self._call_on_created
                                 if call_on_created is None
                                 else call_on_created)
        include = include or self.include
        exclude = exclude or self.exclude
        self._investigator = Investigator(self.related_model,
                                          include=include,
                                          exclude=exclude)
        # register the receivers
        register_reciever(self.model, pre_save,
                          self._pre_save_receiver,
                          sender=self.related_model)
        register_reciever(self.model, post_save,
                          self._post_save_receiver,
                          sender=self.related_model)
        register_reciever(self.model, post_save,
                          self._post_save_receiver_for_creation)

    def unwatch(self):
        # unregister the receivers
        unregister_reciever(self.model, pre_save,
                            self._pre_save_receiver)
        unregister_reciever(self.model, post_save,
                            self._post_save_receiver)
        unregister_reciever(self.model, post_save,
                            self._post_save_receiver_for_creation)

    def get_value(self, instance):
        try:
            return getattr(instance, self.related_attr, None)
        except ObjectDoesNotExist:
            return None

    def get_values(self, instance):
        value = self.get_value(instance)
        if value is None:
            return set()
        if hasattr(value, 'iterator'):
            value = value.iterator()
        elif not hasattr(value, '__iter__'):
            value = tuple([value])
        return set(value)

    def _pre_save_receiver(self, sender, instance, **kwargs):
        if kwargs.get('row', False):
            # should not call any callback while it is called via fixtures or
            # so on
            return
        self._investigator.prepare(instance)

    def _post_save_receiver(self, sender, instance, **kwargs):
        if kwargs.get('row', False):
            # should not call any callback while it is called via fixtures or
            # so on
            return
        # get a reverse related objects from the instance
        instance_cached = self._investigator.get_cached(instance.pk)
        values_cached = self.get_values(instance_cached)
        values_latest = self.get_values(instance)
        object_set = values_cached | values_latest
        if any(self._investigator.investigate(instance)):
            for obj in object_set:
                self.call(obj)

    def _post_save_receiver_for_creation(self, sender, instance,
                                         created, **kwargs):
        if kwargs.get('row', False):
            # should not call any callback while it is called via fixtures or
            # so on
            return
        if self._call_on_created and created:
            self.call(instance)


class RelatedWatcher(RelatedWatcherBase):
    def __init__(self, model, attr, callback,
                 call_on_created=True, include=None, exclude=None):
        """
        Construct watcher field

        Args:
            model (model): A target model class
            attr (str): A name of attribute
            callback (fn): A callback function
            call_on_created (bool): Call callback when the new instance is
                created
            include (None, list, tuple): A related object field name list
                which will be investigated to determine the modification
            exclude (None, list, tuple): A related object field name list
                which won't be investigated to determine the modification
        """
        # add internal valuefiled
        super(RelatedWatcher, self).__init__(model, attr, callback,
                                             include, exclude)
        self._call_on_created = call_on_created
        inner_callback = lambda sender, obj, attr: self.call(obj)
        self._inner_watcher = ValueWatcher(self.model,
                                           self.attr,
                                           inner_callback)

    def watch(self, call_on_created=None,
              include=None, exclude=None):
        super(RelatedWatcher, self).watch(call_on_created,
                                          include, exclude)
        # register value watcher if this is not reverse relation
        if not self.is_reversed:
            # make sure that the inner watcher has correct model instance
            # it is required when lazy_watch is used
            self._inner_watcher._model = self._model
            self._inner_watcher.watch(call_on_created=False)

    def unwatch(self):
        super(RelatedWatcher, self).unwatch()
        self._inner_watcher.unwatch()


class ManyRelatedWatcher(RelatedWatcherBase):
    @property
    @lru_cache(settings.OBSERVER_LRU_CACHE_SIZE)
    def through_model(self):
        return getattr(self.get_field().rel, 'through', None)

    def watch(self, call_on_created=None):
        if call_on_created is not None:
            self._call_on_created = call_on_created
        super(ManyRelatedWatcher, self).watch(call_on_created)
        if self.through_model:
            # m2m relation
            register_reciever(self.model, m2m_changed,
                              self._m2m_changed_receiver,
                              sender=self.through_model)

    def unwatch(self):
        super(ManyRelatedWatcher, self).unwatch()
        if self.through_model:
            unregister_reciever(self.model, m2m_changed,
                                self._m2m_changed_receiver)

    def _m2m_changed_receiver(self, sender, instance, action,
                              reverse, model, pk_set, **kwargs):
        if kwargs.get('row', False):
            # should not call any callback while it is called via fixtures or
            # so on
            return
        if action not in ('post_add', 'post_remove', 'post_clear'):
            return
        if instance.__class__ == self.model:
            self.call(instance)
        else:
            # TODO: pk_set is None for post_clear thus cache the pk_set
            #       with 'pre_clear' and use the cache to tell.
            manager = self.model._default_manager
            for obj in manager.filter(pk__in=pk_set):
                self.call(obj)


class GenericRelatedWatcher(RelatedWatcher):
    @property
    @lru_cache(settings.OBSERVER_LRU_CACHE_SIZE)
    def is_reversed(self):
        return isinstance(self.get_field(), GenericForeignKey)

    @property
    @lru_cache(settings.OBSERVER_LRU_CACHE_SIZE)
    def related_model(self):
        field = self.get_field()
        if self.is_reversed:
            return field.model
        return field.rel.to

    @property
    @lru_cache(settings.OBSERVER_LRU_CACHE_SIZE)
    def related_attr(self):
        field = self.get_field()
        if self.is_reversed:
            return field.name
        # find GenericForeignKey field
        for related_field in self.related_model._meta.virtual_fields:
            if isinstance(related_field, GenericForeignKey):
                return related_field.name
        raise KeyError

    def get_value(self, instance):
        try:
            if self.is_reversed:
                field = self.get_field()
                return super(GenericRelatedWatcher, self).get_value(instance)
            else:
                if instance is None:
                    return None
                field = self.get_field()
                ct = getattr(instance, field.content_type_field_name)
                pk = getattr(instance, field.object_id_field_name)
                if ct is None:
                    return None
                return ct.get_object_for_this_type(pk=pk)
        except ObjectDoesNotExist:
            return None
