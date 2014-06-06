from django.test import TestCase
from observer.watchers.relation import RelatedManagerWatcher
from observer.watchers.relation import ManyRelatedManagerWatcher
from observer.watchers.relation import GenericRelatedObjectManagerWatcher
from observer.tests.test_watchers.mixin import ObserverWatcherTestCaseMixin
from observer.tests.factories import ArticleFactory, LabelFactory


class ObserverRelatedManagerWatcherTestCase(TestCase,
                                            ObserverWatcherTestCaseMixin):
    WATCHER = RelatedManagerWatcher
    ATTR_NAME = 'observer_test_article'

    def setUp(self):
        self.create_requirements()
        # it only works oppsitoly
        self.article = self.obj
        self.obj = self.obj.author

    def test_watcher_callback_called_with_modification(self):
        """Watcher callback should be called if the watched attr is modified"""
        self.create_watcher()

        # the registered model modification does not call the callback
        self.obj.username = 'modified'
        self.obj.save()
        self.assertFalse(self.callback.called,
                         'The callback should not be called')

        # user.observer_test_article link changed from the original
        # thus the callback is called
        article = ArticleFactory(author=self.obj)
        self.assertTrue(self.callback.called,
                        'The callback should be called')

        self.callback.called = False
        self.assertFalse(self.callback.called,
                         'The callback should not be called')

        # user.observer_test_article link changed from the original
        # thus the callback is called
        article.author = self.users[0]
        article.save()
        self.assertTrue(self.callback.called,
                        'The callback should be called')


class ObserverManyRelatedManagerWatcherTestCase(TestCase,
                                                ObserverWatcherTestCaseMixin):
    WATCHER = ManyRelatedManagerWatcher
    ATTR_NAME = 'collaborators'

    def setUp(self):
        self.create_requirements()

    def test_watcher_callback_called_with_modification(self):
        """Watcher callback should be called if the watched attr is modified"""
        self.create_watcher()

        # add collaborator
        self.obj.collaborators.add(self.users[0])
        self.assertTrue(self.callback.called,
                        'The callback should be called')
        self.callback.called = False

        # remove collaborator
        self.obj.collaborators.remove(self.users[0])
        self.assertTrue(self.callback.called,
                        'The callback should be called')
        self.callback.called = False

        # add collaborators
        self.obj.collaborators.add(self.users[1], self.users[2])
        self.assertTrue(self.callback.called,
                        'The callback should be called')
        self.callback.called = False

        # clear collaborators
        self.obj.collaborators.clear()
        self.assertTrue(self.callback.called,
                        'The callback should be called')
        self.callback.called = False


class ObserverGenericRelatedObjectManagerWatcherTestCase(
        TestCase, ObserverWatcherTestCaseMixin):
    WATCHER = GenericRelatedObjectManagerWatcher
    ATTR_NAME = 'labels'

    def setUp(self):
        self.create_requirements()

    def test_watcher_callback_called_with_modification(self):
        """Watcher callback should be called if the watched attr is modified"""
        self.create_watcher()

        # add label
        label = LabelFactory(content_object=self.obj)
        self.obj.collaborators.add(self.users[0])
        self.assertTrue(self.callback.called,
                        'The callback should be called')
        self.callback.called = False

        # remove label
        label.delete()
        self.assertTrue(self.callback.called,
                        'The callback should be called')
        self.callback.called = False
