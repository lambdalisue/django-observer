from observer.utils.singleton import Singleton


class Registry(list, Singleton):
    def register(self, watcher):
        self.append(watcher)

    def unregister(self, watcher):
        self.remove(watcher)

registry = Registry()
