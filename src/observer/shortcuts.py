

def watch(model, attr, callback, **kwargs):
    """
    A shortcut function for watching model attribute
    """
    from observer.watchers.auto import AutoWatcher
    watcher = AutoWatcher(model, attr, callback, **kwargs)
    watcher.lazy_watch()
    return watcher
