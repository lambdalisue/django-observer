from observer.tests.compat import MagicMock
from observer.tests.factories import ArticleFactory, UserFactory


class ObserverWatcherTestCaseMixin(object):
    def create_requirements(self):
        self.callback = MagicMock()
        self.obj = ArticleFactory()
        self.users = (
            UserFactory(),
            UserFactory(),
            UserFactory(),
            UserFactory(),
            UserFactory(),
        )

    def create_watcher(self, obj=None, attr_name=None, callback=None):
        obj = obj or self.obj
        attr_name = attr_name or self.ATTR_NAME
        callback = callback or self.callback
        watcher = self.WATCHER(obj, attr_name, callback)
        return watcher

    def test_watcher_assign_before_save(self):
        """Watcher cannot be assigned to non saved object"""
        article = ArticleFactory.build()    # build does not save
        self.assertRaises(AttributeError,
                          self.WATCHER,
                          article,
                          self.ATTR_NAME,
                          self.callback)

    def test_watcher_assign_after_save(self):
        """Watcher can be assigned to saved object"""
        self.create_watcher()

    def test_watcher_callback_not_called_without_modification(self):
        """Watcher callback should not be called without modification"""
        # create watcher
        self.create_watcher()

        # creation does not call the callback
        self.assertFalse(self.callback.called,
                         'The callback should not be called')

        # saving without modification does not call the callback
        self.obj.save()
        self.assertFalse(self.callback.called,
                         'The callback should not be called')

    def test_watcher_callback_not_called_with_unwatched_modification(self):
        """Watcher callback should not be called with unwatched modification"""
        # create watcher
        self.create_watcher()

        # No watcher watching this attribute
        #
        # Notice:
        #   Any watcher must not watch this attribute to keep the test clean
        #
        self.obj.content = "modified"

        # saving with unwatched modification does not call the callback
        self.obj.save()
        self.assertFalse(self.callback.called,
                         'The callback should not be called')
