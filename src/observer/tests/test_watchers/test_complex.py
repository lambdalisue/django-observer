from django.test import TestCase
from observer.watchers.complex import ComplexWatcher
from observer.tests.test_watchers.mixin import ObserverWatcherTestCaseMixin
from observer.tests.factories import ArticleFactory, LabelFactory


class ObserverComplexWatcherTestCase(TestCase, ObserverWatcherTestCaseMixin):
    WATCHER = ComplexWatcher
    ATTR_NAME = 'title'

    def setUp(self):
        self.create_requirements()

    def test_watcher_callback_with_one_to_many_called(self):
        """Watcher callback should be called if the watched attr is modified"""
        self.create_watcher(attr_name='author')

        # replacement call the callback
        self.obj.author = self.users[0]
        self.obj.save()
        self.assertTrue(self.callback.called,
                        'The callback should be called')
        self.callback.called = False

        # linked object modification call the callback
        self.obj.author.last_name = 'modified'
        self.obj.author.save()
        self.assertTrue(self.callback.called,
                        'The callback should be called')

    def test_watcher_callback_with_many_to_one_called(self):
        """Watcher callback should be called if the watched attr is modified"""
        obj = self.users[0]
        article = ArticleFactory()
        article2 = ArticleFactory()

        self.create_watcher(obj=obj,
                            attr_name='observer_test_article')

        # assign author call the callback
        article.author = obj
        article.save()
        self.assertTrue(self.callback.called,
                        'The callback should be called')
        self.callback.called = False

        # modification call the callback
        article.title = 'modified'
        article.save()
        self.assertTrue(self.callback.called,
                        'The callback should be called')
        self.callback.called = False

        # unwatched object modification does not call the callback
        article2.title = 'modified'
        article2.save()
        self.assertFalse(self.callback.called,
                         'The callback should not be called')

        # remove object modification call the callback
        article.delete()
        self.assertTrue(self.callback.called,
                        'The callback should be called')

    def test_watcher_callback_with_many_to_many_called(self):
        """Watcher callback should be called if the watched attr is modified"""
        self.create_watcher(attr_name='collaborators')

        # add collaborator call the callback
        self.obj.collaborators.add(self.users[0], self.users[1])
        self.assertTrue(self.callback.called,
                        'The callback should be called')
        self.callback.called = False

        # remove collaborator call the callback
        self.obj.collaborators.remove(self.users[0])
        self.assertTrue(self.callback.called,
                        'The callback should be called')
        self.callback.called = False

        # clear collaborators call the callback
        self.obj.collaborators.clear()
        self.assertTrue(self.callback.called,
                        'The callback should be called')
        self.callback.called = False

        # add collaborators for next tests
        self.obj.collaborators.add(self.users[0], self.users[1])
        self.callback.called = False

        # modify collaborator call the callback
        self.users[0].last_name = 'modified'
        self.users[0].save()
        self.assertTrue(self.callback.called,
                        'The callback should be called')
        self.callback.called = False

        # modify non collaborators does not call the callback
        self.users[2].last_name = 'modified'
        self.users[2].save()
        self.assertFalse(self.callback.called,
                         'The callback should not be called')

        # modify collaborator call the callback
        self.users[0].delete()
        self.assertTrue(self.callback.called,
                        'The callback should be called')
        self.callback.called = False

    def test_watcher_callback_with_generic_foreign_key(self):
        """Watcher callback should be called if the watched attr is modified"""
        article1 = ArticleFactory()
        article2 = ArticleFactory()
        label1 = LabelFactory(content_object=article1)
        LabelFactory(content_object=article2)
        self.create_watcher(obj=label1, attr_name='content_object')

        # modify foreign key object call the callback
        article1.title = 'modified'
        article1.save()
        self.assertTrue(self.callback.called,
                        'The callback should be called')
        self.callback.called = False

        # modify non foreign key object does not call the callback
        article2.title = 'modified'
        article2.save()
        self.assertFalse(self.callback.called,
                         'The callback should not be called')

        # replace foreign key object call the callback
        label1.content_object = article2
        label1.save()
        self.assertTrue(self.callback.called,
                        'The callback should be called')
        self.callback.called = False

        # modify replaced foreign key object call the callback
        article2.title = 're-modified'
        article2.save()
        self.assertTrue(self.callback.called,
                        'The callback should be called')
        self.callback.called = False

    def test_watcher_callback_with_generic_relation(self):
        """Watcher callback should be called if the watched attr is modified"""
        self.create_watcher(attr_name='labels')

        # add generic related object to non watched obj does not  call the
        # callback
        LabelFactory(content_object=self.users[0])
        self.assertFalse(self.callback.called,
                         'The callback should not be called')

        # add generic related object call the callback
        label = LabelFactory(content_object=self.obj)
        self.assertTrue(self.callback.called,
                        'The callback should be called')
        self.callback.called = False

        # modify generic related object call the callback
        label.label = "modified"
        label.save()
        self.assertTrue(self.callback.called,
                        'The callback should be called')
        self.callback.called = False

        # remove generic related object call the callback
        label.delete()
        self.assertTrue(self.callback.called,
                        'The callback should be called')
        self.callback.called = False
