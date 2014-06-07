from django.core.exceptions import ObjectDoesNotExist


class Investigator(object):
    """
    A model modification investigator

    Create an instance of investigator with a model class and call 'prepare'
    method just before save the model. After the model is saved, call
    'investigate' method and the method will yields the field names modified.
    """
    def __init__(self, model, include=None, exclude=None):
        """
        Construct investigator

        Args:
            model (model): A model class of the object interest
            include (None, list, tuple): A field name list which will be
                investigated
            exclude (None, list, tuple): A field name list which wont't be
                investigated
        """
        self.model = model
        self.include = set(include) if include is not None else None
        self.exclude = set(exclude) if exclude is not None else None
        self._object_cached = {}

    def prepare(self, instance):
        """
        Call this function before save the model instance
        """
        if instance.pk is None:
            return
        # find raw instance from the database
        raw_instance = self.get_object(instance.pk)
        # update object cache
        self._object_cached[instance.pk] = raw_instance

    def investigate(self, instance):
        """
        Call this function after the model instance is saved.
        It yield a name of modified attributes
        """
        cached_obj = self.get_cached(instance.pk)
        if cached_obj is None:
            return
        field_names = set(x.name for x in self.model._meta.fields)
        if self.include:
            field_names.intersection_update(self.include)
        if self.exclude:
            field_names.difference_update(self.exclude)
        # compare field difference
        for field_name in field_names:
            old = getattr(cached_obj, field_name, None)
            new = getattr(instance, field_name, None)
            if old != new:
                yield field_name

    def get_cached(self, pk, ignore_exception=True):
        """
        Get cached object

        Args:
            pk (any): A primary key of the object
            ignore_exception (bool): Return None if the object is not found,
                if this is False, ObjectDoesNotExist raised

        Raises:
            ObjectDoesNotExist: When a specified object does not exists in the
                cache and `ignore_exception` is False.

        Returns:
            object or None
        """
        if pk not in self._object_cached and not ignore_exception:
            raise ObjectDoesNotExist
        return self._object_cached.get(pk, None)

    def get_object(self, pk, ignore_exception=True):
        """
        Get latest object

        It try to get the latest (unsaved) object from the database.
        If `ignore_exception` is True, return None, otherwise it raise
        ObjectDoesNotExist exception when no object is found.

        Args:
            pk (any): A primary key of the object
            ignore_exception (bool): Return None if the object is not found.
                if this is False, ObjectDoesNotExist raised.

        Raises:
            ObjectDoesNotExist: When a specified object does not exists
                `ignore_exception` is False.

        Returns:
            object or None
        """

        default_manager = self.model._default_manager
        # try to find the latest (unsaved) object from the database
        try:
            latest_obj = default_manager.get(pk=pk)
            return latest_obj
        except ObjectDoesNotExist:
            if ignore_exception:
                return None
            raise
