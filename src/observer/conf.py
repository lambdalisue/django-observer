# coding=utf-8
"""
Confiurations of django-observer
"""
__author__ = 'Alisue <lambdalisue@hashnote.net>'
from django.conf import settings
from appconf import AppConf


class ObserverAppConf(AppConf):
    DEFAULT_WATCHER = 'observer.watchers.ComplexWatcher'

    LRU_CACHE_SIZE = 128
