try:
    # Python 3 have mock in unittest
    from unittest.mock import MagicMock, patch, DEFAULT, call
except ImportError:
    from mock import MagicMock, patch, DEFAULT, call

try:
    from django.test.utils import override_settings
except ImportError:
    from override_settings import override_settings

try:
    from unittest import skip
except ImportError:
    from unittest2 import skip

from django.test import TestCase

# does the TestCase is based on new unittest?
if not hasattr(TestCase, 'addCleanup'):
    # convert old TestCase to new TestCase via unittest2
    import unittest2
    class TestCase(TestCase, unittest2.case.TestCase):
        pass
