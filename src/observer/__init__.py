from app_version import get_versions
__version__, VERSION = get_versions('django-observer')

# backward compatibility
from observer.watchers import Watcher
from observer.shortcuts import watch, unwatch_all
