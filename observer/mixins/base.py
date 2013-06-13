#!/usr/bin/env python
"""
A set of base classes for mixins


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
import inspect
from callbacks import ObserverCallback
from django.db.models.base import ModelBase

class ObserverModelBase(ModelBase):
    """
    Metaclass for models with observers.
    """
    def __new__(cls, name, bases, attrs):
        attr_observers = attrs.pop('Observers', None)
        new_class = super(ObserverModelBase, cls).__new__(cls, name, bases, attrs)
        if attr_observers:
            observers = inspect.getmembers(attr_observers, predicate=lambda a: isinstance(a, ObserverCallback))
            new_class.add_to_class('_observers', observers)
        return new_class