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
from ..models import TaggedItem

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
        entry.title = 'foo'

        entry.body = ''
        self.assertRaises(ValidationError, entry.full_clean)
        entry.body = 'bar'

        entry.title = '*' * 100
        self.assertRaises(ValidationError, entry.full_clean)
        entry.title = 'foo'

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

class TaggedItemModelTestCase(TestCase):
    def setUp(self):
        self.foo = Entry.objects.create(title='foo', body='foo')
        self.bar = Entry.objects.create(title='bar', body='bar')
        self.hoge = Entry.objects.create(title='hoge', body='hoge')

    def test_creation(self):
        """blog.TaggedItem: creation works correctly"""
        item = TaggedItem(content_object=self.foo, tag='foo')
        item.full_clean()
        self.assertEqual(item.content_object, self.foo)
        self.assertEqual(item.tag, 'foo')

        item.save()
        item = TaggedItem.objects.get(pk=item.pk)
        self.assertEqual(item.content_object, self.foo)
        self.assertEqual(item.tag, 'foo')

    def test_modification(self):
        """blog.TaggedItem: modification works correctly"""
        item = TaggedItem(content_object=self.foo, tag='foo')
        item.full_clean()
        item.save()

        item.content_object = self.bar
        item.tag = 'bar'
        item.full_clean()
        item.save()
        item = TaggedItem.objects.get(pk=item.pk)
        self.assertEqual(item.content_object, self.bar)
        self.assertEqual(item.tag, 'bar')

    def test_validation(self):
        """blog.TaggedItem: validation works correctly"""
        from django.core.exceptions import ValidationError
        item = TaggedItem(content_object=self.foo, tag='foo')
        item.full_clean()
        item.save()

        item.tag = ''
        self.assertRaises(ValidationError, item.full_clean)
        item.tag = 'foo'

        item.tag = '*' * 300
        self.assertRaises(ValidationError, item.full_clean)
        item.tag = 'foo'

    def test_deletion(self):
        """blog.TaggedItem: deletion works correctly"""
        item = TaggedItem(content_object=self.foo, tag='foo')
        item.full_clean()
        item.save()

        num = TaggedItem.objects.all().count()
        item.delete()
        self.assertEqual(TaggedItem.objects.all().count(), num - 1)
