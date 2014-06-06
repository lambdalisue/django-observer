from django.test import TestCase
from observer.watchers.value import ValueWatcher
from observer.tests.test_watchers.mixin import ObserverWatcherTestCaseMixin


class ObserverValueWatcherTestCase(TestCase, ObserverWatcherTestCaseMixin):
    WATCHER = ValueWatcher
    ATTR_NAME = 'title'

    def setUp(self):
        self.create_requirements()

    def test_watcher_callback_called_with_modification(self):
        """Watcher callback should be called if the watched attr is modified"""
        self.create_watcher()

        # modifing the field does not call
        self.obj.title = 'modified'
        self.assertFalse(self.callback.called,
                         'The callback should not be called')

        # saving trigger the call
        self.obj.save()
        self.callback.assert_called()
        self.assertTrue(self.callback.called,
                        'The callback should be called')
