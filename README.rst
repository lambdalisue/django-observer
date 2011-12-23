Watch modification of any type of field in Django's model and call registered callback function

This observer can watch

-   Any value type of field (CharField, IntegerField ...)
-   Any Model type of field (ForeignKey, OneToOneField, GenericForeignKey)
-   Any RelatedManager type of field (field automatically created via ``related_name`` of ForeignKey)
-   Any ManyRelatedManager type of field (ManyToManyField)
-   Any GenericRelatedObjectManager type of field (GenericRelation)
-   Any Model instance


Install
==============
This library is on PyPI so you can install it with::

    pip install django-observer

or from github::
    
    pip install git+https://github.com/lambdalisue/django-observer.git


Usage
==========

>>> from django.db import models
>>> from observer import watch
>>> 
>>> class Entry(models.Model):
...     status = models.CharFiled('status', max_length=10)
...     body = models.CharField('title', max_length=100)
... 
...     def save(self, *args, **kwargs):
...         super(Entry, self).save(*args, **kwargs)
... 
...         # Watch callback, this is automatically called if `status` is **changed**
...         def watch_callback(sender, obj, attr):
...             # sender is a watcher instance
...             # obj is a instance of target
...             # attr is a name of target field
...             if obj.status == 'draft':
...                 obj.title = "draft - %s" % obj.body
...             else:
...                 obj.title = "publish - %s" % obj.body
...         # Start watching
...         self._watcher = watch(self, 'status', watch_callback)

See `observer_test/src/miniblog/blog/tests/test_observer.py <https://github.com/lambdalisue/django-observer/blob/master/observer_test/src/miniblog/blog/tests/test_observer.py>`_ for more detail.

Settings
================

OBSERVER_DEFAULT_WATCHER
    A class of watcher. Default is 'observer.watcher.complex.ComplexWatcher'
