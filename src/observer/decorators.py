

def watch(attr, callback, **kwargs):
    """
    A decorator function for watching model attribute
    """
    def decorator(model):
        from observer.watchers.auto import AutoWatcher
        watcher = AutoWatcher(model, attr, callback, **kwargs)
        watcher.lazy_watch()
        if not hasattr(model, '_watchers'):
            model._watchers = []
        model._watchers.append(watcher)
        return model
    return decorator
