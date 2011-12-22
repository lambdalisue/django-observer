#!/usr/bin/env python
# vim: set fileencoding=utf8:
"""
Unittest module of models


AUTHOR:
    lambdalisue[Ali su ae] (lambdalisue@hashnote.net)
    
Copyright:
    Copyright 2011 Alisue allright reserved.

License:
    Licensed under the Apache License, Version 2.0 (the "License"); 
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unliss required by applicable law or agreed to in writing, software
    distributed under the License is distrubuted on an "AS IS" BASICS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""
__AUTHOR__ = "lambdalisue (lambdalisue@hashnote.net)"
from django.test import TestCase

from ..models import Entry

class EntryModelTestCase(TestCase):
    def test_creation(self):
        """blog.Entry: creation works correctly"""
        entry = Entry(title='foo', body='bar')
        entry.full_clean()
        self.assertEqual(entry.title, 'foo')
        self.assertEqual(entry.body, 'bar')

        entry.save()
        entry = Entry.objects.get(pk=entry.pk)
        self.assertEqual(entry.title, 'foo')
        self.assertEqual(entry.body, 'bar')

    def test_modification(self):
        """blog.Entry: modification works correctly"""
        entry = Entry(title='foo', body='bar')
        entry.full_clean()
        entry.save()

        entry.title = 'foofoo'
        entry.body = 'barbar'
        entry.full_clean()
        entry.save()
        entry = Entry.objects.get(pk=entry.pk)
        self.assertEqual(entry.title, 'foofoo')
        self.assertEqual(entry.body, 'barbar')

    def test_validation(self):
        """blog.Entry: validation works correctly"""
        from django.core.exceptions import ValidationError
        entry = Entry(title='foo', body='bar')
        entry.full_clean()
        entry.save()

        entry.title = ''
        self.assertRaises(ValidationError, entry.full_clean)

        entry.body = ''
        self.assertRaises(ValidationError, entry.full_clean)

        entry.title = '*' * 100
        self.assertRaises(ValidationError, entry.full_clean)

        entry.title = '!#$%&()'
        self.assertRaises(ValidationError, entry.full_clean)

    def test_deletion(self):
        """blog.Entry: deletion works correctly"""
        entry = Entry(title='foo', body='bar')
        entry.full_clean()
        entry.save()

        num = Entry.objects.all().count()
        entry.delete()
        self.assertEqual(Entry.objects.all().count(), num - 1)

    def test_with_author(self):
        """blog.Entry: with_author works correctly"""
        entry = Entry(title='foo', body='bar')
        entry.full_clean()
        entry.save()

        # None for AnonymousUser (AuthorDefaultBackend)
        self.assertEqual(entry.author, None)
        self.assertEqual(entry.updated_by, None)
