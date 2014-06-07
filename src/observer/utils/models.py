# coding=utf-8
"""
"""
__author__ = 'Alisue <lambdalisue@hashnote.net>'
from django.db.models import ForeignKey
from django.db.models.fields import FieldDoesNotExist
from django.core.exceptions import ObjectDoesNotExist


def get_latest_obj(obj, ignore_exception=True):
    """
    Get latest object from database

    It return None when no object is found or raise ObjectDoesNotExist
    when ignore_exception is False
    """
    default_manager = obj.__class__._default_manager
    try:
        return default_manager.get(pk=obj.pk)
    except ObjectDoesNotExist:
        if ignore_exception:
            return None
        raise


def iterate_related_attr_names(model):
    """
    Iterate over the foreign key attribute of model to find the related
    attribute names.

    This function yield a tuple of accessor name (attribute name of the model)
    and related attribute name

    Args:
        model (class): A django model class

    Yields:
        tuple: (accessor_name, related_attr_name)
    """
    for field in model._meta.fields:
        if not isinstance(field, ForeignKey):
            continue
        accessor_name = field.related.get_accessor_name()
        yield accessor_name, field.name


def find_related_attr_name(model, attr):
    """
    Find corresponding related attribute name of specified attribute.

    This function return a corresponding related attribute name of specified
    attribute of the model.
    It will raise KeyError when no attribute is found.

    Args:
        model (class): A django model class
        attr (str): An attribute name (accessor name)

    Returns:
        str: A corresponding related attribute name

    Raises:
        KeyError: When the specified attribute is not found as ForeignKey
            in model
    """
    for accessor_name, related_attr_name in iterate_related_attr_names(model):
        if accessor_name == attr:
            return related_attr_name
    raise KeyError("%s does not have '%s' attribute" % (model, attr))


def get_field(obj, attr, ignore_exception=True):
    """
    Get attribute field object of the obj
    It return None if the field is not exists or raise FieldDoesNotExist when
    ignore_exception is False
    """
    meta = obj._meta
    try:
        return meta.get_field_by_name(attr)[0]
    except FieldDoesNotExist:
        if ignore_exception:
            return None
        raise
