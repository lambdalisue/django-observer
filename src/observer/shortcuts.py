

def get_watcher(watcher_class=None):
    """
    Get watcher instance

    If no `watcher_class` is specified, the watcher class is determined from
    the value of `settings.OBSERVER_DEFAULT_WATCHER`.
    `watcher_class` can be a class object or dots separated python import path

    Returns:
        watcher instance
    """
    from observer.conf import settings
    from observer.compat import import_module
    cache_name = '_watcher_instance'
    if not hasattr(get_watcher, cache_name):
        watcher_class = watcher_class or settings.OBSERVER_DEFAULT_WATCHER
        if isinstance(watcher_class, basestring):
            module_path, class_name = watcher_class.rsplit(".", 1)
            module = import_module(module_path)
            watcher_class = getattr(module, class_name)
        setattr(get_watcher, cache_name, watcher_class)
    return getattr(get_watcher, cache_name)


def watch(obj, attr, callback):
    """
    Shortcut method for creating Watcher instance

    If you want to use different watcher class as default, set
    'OBSERVER_DEFAULT_WATCHER' in your settings.py
    """
    Watcher = get_watcher()
    watcher = Watcher(obj, attr, callback)
    return watcher


def unwatch_all():
    """Shortcut method for unwatch all watcher"""
    Watcher = get_watcher()
    Watcher.unwatch_all()
