django-observer
==========================
.. image:: https://secure.travis-ci.org/lambdalisue/django-observer.png?branch=master
    :target: http://travis-ci.org/lambdalisue/django-observer
    :alt: Build status

.. image:: https://coveralls.io/repos/lambdalisue/django-observer/badge.png?branch=master
    :target: https://coveralls.io/r/lambdalisue/django-observer/
    :alt: Coverage

.. image:: https://img.shields.io/pypi/dm/django-observer.svg
    :target: https://pypi.python.org/pypi/django-observer/
    :alt: Downloads

.. image:: https://img.shields.io/pypi/v/django-observer.svg
    :target: https://pypi.python.org/pypi/django-observer/
    :alt: Latest version

.. image:: https://img.shields.io/pypi/wheel/django-observer.svg
    :target: https://pypi.python.org/pypi/django-observer/
    :alt: Wheel Status

.. image:: https://pypip.in/egg/django-observer/badge.png
    :target: https://pypi.python.org/pypi/django-observer/
    :alt: Egg Status

.. image:: https://img.shields.io/pypi/l/django-observer.svg
    :target: https://pypi.python.org/pypi/django-observer/
    :alt: License

Author
    Alisue <lambdalisue@hashnote.net>
Supported python versions
    Python 2.6, 2.7, 3.2, 3.3
Supported django versions
    Django 1.2 - 1.6

Observe django model attribute modifications and call the specified callback.
django-observer can recognize the modifications of

-   Any value type of fields (CharField, IntegerField, etc.)
-   Any relational fields (ForeignKey, OneToOneField, ManyToManyField)
-   Any reverse relational fields (fields given by `related_name`)
-   Any generic relational fields (GenericForeignKey, GenericRelation)


Documentation
-------------
http://django-observer.readthedocs.org/en/latest/

Installation
------------
Use pip_ like::

    $ pip install django-observer

.. _pip:  https://pypi.python.org/pypi/pip

Usage
-----

Configuration
~~~~~~~~~~~~~
1.  Add ``observer`` to the ``INSTALLED_APPS`` in your settings
    module

    .. code:: python

        INSTALLED_APPS = (
            # ...
            'observer',
        )

Example
~~~~~~~~~~~

.. code:: python

    from django.db import models
    from django.contrib.auth.models import User

    def status_changed(sender, obj, attr):
        if obj.status == 'draft':
            obj.title = "Draft %s" % obj.title
        else:
            obj.title = obj.title.replace("Draft ")
        obj.save()
    
    # watch status attribute via decorator
    from observer.decorators import watch
    @watch('status', status_changed, call_on_created=True)
    class Entry(models.Model):
        title = models.CharField(max_length=30)
        status = models.CharFiled(max_length=10)

        body = models.TextField('title', max_length=100)
        author = models.ForeignKey(User, null=True, blank=True)


    def author_changed(sender, obj, attr):
        if obj.author is None:
            obj.status = "draft"
            obj.save()

    # watch author attribute via function
    from observer.shortcuts import watch
    watch(Entry, 'author', author_changed)
