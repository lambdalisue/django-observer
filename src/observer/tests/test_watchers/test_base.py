from django.db import models
from observer.tests.compat import TestCase
from observer.tests.compat import MagicMock, patch, DEFAULT
from observer.watchers.base import WatcherBase
from observer.tests.models import ObserverTestArticle as Article


class ObserverWatchersWatcherBaseTestCase(TestCase):
    def setUp(self):
        self.model = Article
        self.attr = 'title'
        self.callback = MagicMock()
        self.watcher = WatcherBase(self.model,
                                   self.attr,
                                   self.callback)

    def test_watch_raise_exception(self):
        """watch should raise NotImplementedError"""
        self.assertRaises(NotImplementedError,
                          self.watcher.watch)

    def test_unwatch_raise_exception(self):
        """unwatch should raise NotImplementedError"""
        self.assertRaises(NotImplementedError,
                          self.watcher.watch)

    def test_call_call_callback(self):
        """call should call callback"""
        obj = MagicMock()
        self.watcher.call(obj)
        self.callback.assert_called_once_with(
            sender=self.watcher, obj=obj, attr=self.attr)

    def test_get_field_return_field(self):
        """get_field should return field instance"""
        self.assertTrue(isinstance(self.watcher.get_field(),
                                   models.CharField))

    def test_get_field_return_field_with_attr(self):
        """get_field should return field instance"""
        self.assertTrue(isinstance(self.watcher.get_field('author'),
                                   models.ForeignKey))

    def test_construct_with_string_relation(self):
        field = WatcherBase('observer.ObserverTestArticle',
                            self.attr, self.callback)
        self.assertEqual(field.model, Article)

    @patch.multiple('observer.watchers.base',
                    get_model=DEFAULT, class_prepared=DEFAULT)
    def test_construct_with_string_relation_lazy_relation(self, get_model,
                                                          class_prepared):
        from observer.watchers.base import do_pending_lookups
        # emulate the situlation that Article has not prepared yet
        get_model.return_value = None
        field = WatcherBase('observer.ObserverTestArticle',
                            self.attr, self.callback)
        # Article haven't ready yet (get_model return None)
        self.assertEqual(field.model, 'observer.ObserverTestArticle')
        # emulate class_prepared signal
        do_pending_lookups(Article)
        # Article had ready (class_prepared signal call do_pending_lookups)
        self.assertEqual(field.model, Article)

    def test_lazy_watch_call_watch(self):
        self.watcher.watch = MagicMock()
        kwargs = dict(
            foo=MagicMock(),
            bar=MagicMock(),
            hoge=MagicMock(),
        )
        self.watcher.lazy_watch(**kwargs)
        self.watcher.watch.assert_called_once_with(**kwargs)

    @patch.multiple('observer.watchers.base',
                    get_model=DEFAULT, class_prepared=DEFAULT)
    def test_lazy_watch_with_unprepared_model(self, get_model,
                                              class_prepared):
        from observer.watchers.base import do_pending_lookups
        # emulate the situlation that Article has not prepared yet
        get_model.return_value = None

        field = WatcherBase('observer.ObserverTestArticle',
                            self.attr, self.callback)
        field.watch = MagicMock()
        kwargs = dict(
            foo=MagicMock(),
            bar=MagicMock(),
            hoge=MagicMock(),
        )
        field.lazy_watch(**kwargs)
        # the model have not ready yet thus watch should not be called yet
        self.assertFalse(field.watch.called)
        # emulate class_prepared signal
        do_pending_lookups(Article)
        # Article has ready thus watch should be called automatically
        field.watch.assert_called_once_with(**kwargs)

    @patch.multiple('observer.watchers.base',
                    get_model=DEFAULT, class_prepared=DEFAULT)
    def test_lazy_watch_with_unprepared_relation(self, get_model,
                                                 class_prepared):
        from observer.watchers.base import do_pending_lookups
        from observer.tests.models import User
        # emulate the situlation that User has not prepared yet
        get_model.return_value = None
        self.watcher._attr = 'author'
        self.watcher.watch = MagicMock()
        self.watcher.get_field().rel.to = 'observer.ObserverTestUser'
        kwargs = dict(
            foo=MagicMock(),
            bar=MagicMock(),
            hoge=MagicMock(),
        )
        self.watcher.lazy_watch(**kwargs)
        # the rel.to have not ready yet thus watch should not be called yet
        self.assertFalse(self.watcher.watch.called)
        # emulate class_prepared signal
        #   Note:
        #   rel.to assignment is proceeded by other function thus it is
        #   required to do manually, not like model assignment
        self.watcher.get_field().rel.to = User
        do_pending_lookups(User)
        # User has ready thus watch should be called automatically
        self.watcher.watch.assert_called_once_with(**kwargs)
