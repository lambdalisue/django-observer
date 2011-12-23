#!/usr/bin/env python
# vim: set fileencoding=utf8:
"""
initialization django-object-permission

Add this backend to your ``AUTHENTICATION_BACKENDS`` like below::

    AUTHENTICATION_BACKENDS = (
        'django.contrib.auth.backends.ModelBackend',
        'object_permission.backends.ObjectPermBackend',
    )

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
from django.conf import settings

from watcher import Watcher
from watcher import ComplexWatcher

__all__ = ['watch']

settings.OBSERVER_DEFAULT_WATCHER = \
        getattr(settings, 'OBSERVER_DEFAULT_WATCHER', ComplexWatcher)

def watch(obj, attr, callback):
    """Shortcut method for creating Watcher instance
    
    If you want to use different watcher class as default, set
    'OBSERVER_DEFAULT_WATCHER' in your settings.py
    """
    watcher = settings.OBSERVER_DEFAULT_WATCHER(obj, attr, callback)
    return watcher

def unwatch_all():
    """Shortcut method for unwatch all watcher"""
    Watcher.unwatch_all()

