from observer.tests.compat import TestCase
from observer.tests.compat import MagicMock
from observer.tests.models import Article
from observer.tests.factories import ArticleFactory
from observer.watchers.value import ValueWatcher


class ObserverWatchersValueWatcherTestCase(TestCase):
    def setUp(self):
        self.model = Article
        self.attr = 'title'
        self.callback = MagicMock()
        self.Watcher = MagicMock(wraps=ValueWatcher)
        self.watcher = self.Watcher(self.model,
                                    self.attr,
                                    self.callback)
        self.addCleanup(self.watcher.unwatch)

    def test_callback_not_called_on_create_without_watch(self):
        ArticleFactory()
        # have not watched, thus callback should not be called
        self.assertFalse(self.callback.called)

    def test_callback_called_on_create_with_watch(self):
        self.watcher.watch()
        new_instance = ArticleFactory()
        # callback should be called with newly created instance
        self.callback.assert_called_once_with(
            obj=new_instance, attr=self.attr, sender=self.watcher)

    def test_callback_not_called_on_create_without_call_on_created(self):
        self.watcher.watch(call_on_created=False)
        ArticleFactory()
        # have not watched, thus callback should not be called
        self.assertFalse(self.callback.called)

    def test_callback_not_called_on_modification_without_watch(self):
        new_instance = ArticleFactory()
        new_instance.title = 'modified'
        new_instance.save()
        # have not watched, thus callback should not be called
        self.assertFalse(self.callback.called)

    def test_callback_called_on_modification_with_watch(self):
        new_instance = ArticleFactory()
        self.watcher.watch()
        new_instance.title = 'modified'
        new_instance.save()
        # callback should be called with instance modification
        self.callback.assert_called_once_with(
            obj=new_instance, attr=self.attr, sender=self.watcher)

    def test_callback_not_called_on_modification_with_non_interest_attr(self):
        new_instance = ArticleFactory()
        new_instance.content = 'modified'
        new_instance.save()
        # content is not watched thus callback should not be called
        self.assertFalse(self.callback.called)
