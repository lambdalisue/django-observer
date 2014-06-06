from django.test import TestCase
from django.core.exceptions import ObjectDoesNotExist
from observer.watchers.base import Watcher
from observer.tests.compat import MagicMock, patch, DEFAULT


@patch.multiple('observer.watchers.base', registry=DEFAULT)
class ObserverWatcherTestCase(TestCase):
    def setUp(self):
        self.obj = MagicMock()
        self.obj.pk = 1
        self.obj.foo = 'bar'
        self.attr = 'foo'
        self.callback = MagicMock()
        with patch.object(Watcher, 'watch'):
            self.watcher = Watcher(self.obj, self.attr, self.callback)

    def test_watcher_interface(self, registry):
        """Watcher should have correct interface"""
        # properties
        properties = (
            'obj', 'attr', 'callback'
        )
        for prop in properties:
            self.assertTrue(hasattr(Watcher, prop))

        # methods
        methods = (
            'get_attr_value',
            'watch',
            'unwatch',
            'call',
            'get_model',
            'get_object'
        )
        for method in methods:
            self.assertTrue(hasattr(Watcher, method))
            self.assertTrue(callable(getattr(Watcher, method)))

    def test_watcher_construction_property_assign(self, registry):
        with patch.object(Watcher, 'watch'):
            r = Watcher(self.obj, self.attr, self.callback)
            self.assertEqual(r.obj, self.obj)
            self.assertEqual(r.attr, self.attr)
            self.assertEqual(r.callback, self.callback)

    def test_watcher_construction_call_registry_register(self, registry):
        with patch.object(Watcher, 'watch'):
            r = Watcher(self.obj, self.attr, self.callback)
            registry.register.assert_called_with(r)

    def test_watcher_construction_call_watch_method(self, registry):
        with patch.object(Watcher, 'watch'):
            Watcher(self.obj, self.attr, self.callback)
            Watcher.watch.assert_called()

    def test_watcher_construction_does_not_call_watch_method(self, registry):
        with patch.object(Watcher, 'watch'):
            Watcher(self.obj, self.attr, self.callback, start_watch=False)
            self.assertFalse(Watcher.watch.called)

    def test_watcher_construction_raise_exception(self, registry):
        with patch.object(Watcher, 'watch'):
            self.obj.pk = None
            self.assertRaises(AttributeError,
                              Watcher,
                              self.obj, self.attr, self.callback)

    def test_watcher_get_attr_value(self, registry):
        r = self.watcher.get_attr_value()
        self.assertEqual(r, self.obj.foo)

    def test_watcher_watch_raise_exception(self, registry):
        self.assertRaises(NotImplementedError,
                          self.watcher.watch)

    def test_watcher_unwatch_raise_exception(self, registry):
        self.assertRaises(NotImplementedError,
                          self.watcher.unwatch)

    def test_watcher_call_call_get_object_method(self, registry):
        # 'with' with comma separated contexts is introduced from python 2.7.
        # 'contextlib.nested' is removed from python 3.
        # Thus the ugly way below is the simplest way to do...
        with patch.object(Watcher, 'get_object'):
            with patch.object(Watcher, 'callback'):
                self.watcher.call()
                self.watcher.get_object.assert_called()

    def test_watcher_call_call_callback(self, registry):
        # 'with' with comma separated contexts is introduced from python 2.7.
        # 'contextlib.nested' is removed from python 3.
        # Thus the ugly way below is the simplest way to do...
        with patch.object(Watcher, 'get_object'):
            with patch.object(Watcher, 'callback'):
                self.watcher.call()
                self.watcher.callback.assert_called()

    def test_watcher_get_model_return_class(self, registry):
        # comma separated with is introduced from Python 2.7
        r = self.watcher.get_model()
        self.assertEqual(r, self.obj.__class__)

    def test_watcher_get_object_return_new_obj(self, registry):
        new_obj = MagicMock()
        model = MagicMock()
        model._default_manager.get = MagicMock(return_value=new_obj)
        with patch.object(Watcher, 'get_model',
                          new=MagicMock(return_value=model)):
            obj = self.watcher.get_object()
            self.watcher.get_model()._default_manager.get.assert_called_with(
                pk=self.obj.pk)
            self.assertNotEqual(obj, self.obj)
            self.assertEqual(obj, new_obj)

    def test_watcher_get_object_return_cached_obj_when_no_obj_found(self,
                                                                    registry):
        new_obj = MagicMock()
        model = MagicMock()
        model._default_manager.get = MagicMock(
            return_value=new_obj,
            side_effect=ObjectDoesNotExist)
        with patch.object(Watcher, 'get_model',
                          new=MagicMock(return_value=model)):
            obj = self.watcher.get_object()
            self.watcher.get_model()._default_manager.get.assert_called_with(
                pk=self.obj.pk)
            self.assertEqual(obj, self.obj)
            self.assertNotEqual(obj, new_obj)

    def test_watcher_get_object_raise_exception_when_no_obj_found(self,
                                                                  registry):
        new_obj = MagicMock()
        model = MagicMock()
        model._default_manager.get = MagicMock(
            return_value=new_obj,
            side_effect=ObjectDoesNotExist)
        with patch.object(Watcher, 'get_model',
                          new=MagicMock(return_value=model)):
            self.assertRaises(ObjectDoesNotExist,
                              self.watcher.get_object,
                              use_cached=False)
