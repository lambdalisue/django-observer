from django.test import TestCase
from observer.watchers.model import ModelWatcher
from observer.tests.test_watchers.mixin import ObserverWatcherTestCaseMixin
from observer.tests.compat import skip


class ObserverModelWatcherTestCase(TestCase, ObserverWatcherTestCaseMixin):
    WATCHER = ModelWatcher
    ATTR_NAME = None

    def setUp(self):
        self.create_requirements()

    def test_watcher_callback_called_with_modification(self):
        """Watcher callback should be called if the watched attr is modified"""
        self.create_watcher()

        # modifing the field does not call
        self.obj.title = "modified"
        self.assertFalse(self.callback.called,
                         'The callback should not be called')

        # saving trigger the call
        self.obj.save()
        self.assertTrue(self.callback.called,
                        'The callback should be called')

    @skip("ModelWatcher watch any change of the model thus skip this.")
    def test_watcher_callback_not_called_with_unwatched_modification(self):
        pass
