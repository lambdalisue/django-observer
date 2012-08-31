#!/usr/bin/env python
"""
A mixins module to improve watchers declarations


AUTHOR:
    Marek Malek (marek.malek@ymail.com)
    
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
__AUTHOR__ = "Marek Malek (marek.malek@ymail.com)"
import logging

from base import ObserverModelBase
from callbacks import CallFunction, CallMethod
from observer import watch
from django.utils.importlib import import_module

log = logging.getLogger(__name__)

class ObserverMixin(object):
    """
    Mixin to install observer on model attributes.
    """
    __metaclass__ = ObserverModelBase
    _registered_watchers = None

    def save(self, *args, **kwargs):
        # register watchers
        self._register_watchers()
        try:
            super(ObserverMixin, self).save(*args, **kwargs)
        finally:
            self._unregister_watchers()
    
    def _not_registered_observers(self):
        watched_attrs = map(lambda watcher: watcher._attr, self._registered_watchers)
        return filter(lambda (attr, observer): attr not in watched_attrs, self._observers)

    def _register_watchers(self):
        if self._registered_watchers is None:
            self._registered_watchers = []
        # install observers
        for attr_name, observer in self._not_registered_observers():
            try:
                if isinstance(observer, CallMethod):
                    callback = getattr(self, observer.callback)
                elif isinstance(observer, CallFunction):
                    callback = observer.callback
                    if isinstance(callback, basestring):
                        # resolve callable from string
                        parts = callback.rsplit('.', 1)
                        if len(parts) > 1:
                            module = import_module(parts[0])
                            callback = getattr(module, parts[1])
                        else:
                            module = import_module(self.__module__)
                            callback = getattr(module, parts[0])
                else:
                    callback = None
            except Exception, e:
                log.exception(e)
                callback = None

            if callback:
                self._registered_watchers.append(watch(self, attr_name, callback))
            else:
                log.warning('Unable to resolve callback for: %s in %s', attr_name, self.__class__)
                
    def _unregister_watchers(self):
        try:
            while True:
                watcher = self._registered_watchers.pop()
                watcher.unwatch()
        except IndexError:
            pass
