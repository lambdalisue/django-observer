#!/usr/bin/env python
# vim: set fileencoding=utf8:
"""
Unittest module of django-observer


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
from django.contrib.auth.models import User

from observer import watch
from observer.watchers.model import ModelWatcher
from observer.watchers.value import ValueWatcher
from observer.watchers.relation import RelatedManagerWatcher
from observer.watchers.relation import ManyRelatedManagerWatcher
from observer.watchers.relation import GenericRelatedObjectManagerWatcher
from observer.watchers.complex import ComplexWatcher

from ..models import Entry
from ..models import TaggedItem

#
# Note:
#
#   'obj' of callback is latest instance thus I have to use 'sender._obj' for
#   testing
#
class ModelWatcherTestCase(TestCase):
    def test_watch_after_create(self):
        """observer.ModelWatcher: watch after create works correctly"""
        def callback(sender, obj, attr):
            assert isinstance(sender, ModelWatcher)
            self.assertEqual(obj, entry)
            self.assertEqual(attr, None)
            sender._obj.watch_callback_called = True
        # watch -> initial save
        entry = Entry(title='foo', body='bar')
        entry.watch_callback_called = False
        entry.save()
        watcher = ModelWatcher(entry, None, callback)
        self.assertEqual(entry.watch_callback_called, False)

        entry.title = 'foofoo'
        entry.save()
        self.assertEqual(entry.watch_callback_called, True)
        entry.watch_callback_called = False

        entry.body = 'barbar'
        entry.save()
        self.assertEqual(entry.watch_callback_called, True)
        entry.watch_callback_called = False

        # teardown
        watcher.unwatch()

    def test_watch_before_create(self):
        """observer.ModelWatcher: watch before create fails correctly"""
        # watch -> initial save
        entry = Entry(title='foo', body='bar')
        self.assertRaises(AttributeError, ModelWatcher, entry, None, None)

class ValueWatcherTestCase(TestCase):
    def test_watch_after_create(self):
        """observer.ValueWatcher: watch after create works correctly"""
        def callback(sender, obj, attr):
            assert isinstance(sender, ValueWatcher)
            self.assertEqual(obj, entry)
            self.assertEqual(attr, 'title')
            sender._obj.watch_callback_called = True
        # initial save -> watch
        entry = Entry(title='foo', body='bar')
        entry.watch_callback_called = False
        entry.save()
        watcher = ValueWatcher(entry, 'title', callback)
        self.assertEqual(entry.watch_callback_called, False)

        entry.body = 'barbar'
        entry.save()
        self.assertEqual(entry.watch_callback_called, False)

        entry.title = 'foofoo'
        entry.save()
        self.assertEqual(entry.watch_callback_called, True)

        # teardown
        watcher.unwatch()

    def test_watch_before_create(self):
        """observer.ValueWatcher: watch before create fails correctly"""
        # watch -> initial save
        entry = Entry(title='foo', body='bar')
        self.assertRaises(AttributeError, ValueWatcher, entry, None, None)

class RelatedManagerWatcherTestCase(TestCase):
    def test_watch_after_create(self):
        """observer.RelatedManagerWatcher: watch after create works correctly"""
        def callback(sender, obj, attr):
            assert isinstance(sender, RelatedManagerWatcher)
            self.assertEqual(obj, foo)
            self.assertEqual(attr, 'entrys_create')
            sender._obj.watch_callback_called = True
        # initial save -> watch
        foo = User.objects.get(username='foo')
        bar = User.objects.get(username='bar')
        foo.watch_callback_called = False
        watcher = RelatedManagerWatcher(foo, 'entrys_create', callback)
        self.assertEqual(foo.watch_callback_called, False)

        foo.email = 'foofoo@test.com'
        foo.save()
        self.assertEqual(foo.watch_callback_called, False)

        entry = Entry.objects.create(title='Hello', author=foo)
        entry.save()
        self.assertEqual(foo.watch_callback_called, True)
        foo.watch_callback_called = False

        entry.author = bar
        entry.save()
        self.assertEqual(foo.watch_callback_called, True)
        foo.watch_callback_called = False

        # teardown
        watcher.unwatch()

    def test_watch_before_create(self):
        """observer.RelatedManagerWatcher: watch before create fails correctly"""
        # initial save -> watch
        entry = Entry(title='foo', body='bar')
        self.assertRaises(AttributeError, RelatedManagerWatcher, entry, None, None)

class ManyRelatedManagerWatcherTestCase(TestCase):
    def test_watch_after_create(self):
        """observer.ManyRelatedManagerWatcher: watch after create works correctly"""
        def callback(sender, obj, attr):
            assert isinstance(sender, ManyRelatedManagerWatcher)
            self.assertEqual(obj, entry)
            self.assertEqual(attr, 'collaborators')
            sender._obj.watch_callback_called = True
        # initial save -> watch
        entry = Entry(title='foo', body='bar')
        entry.watch_callback_called = False
        entry.save()
        watcher = ManyRelatedManagerWatcher(entry, 'collaborators', callback)
        self.assertEqual(entry.watch_callback_called, False)

        entry.title = 'foofoo'
        entry.save()
        self.assertEqual(entry.watch_callback_called, False)

        foo = User.objects.get(username='foo')
        bar = User.objects.get(username='bar')
        entry.collaborators.add(foo)
        self.assertEqual(entry.watch_callback_called, True)
        entry.watch_callback_called = False

        entry.collaborators.remove(foo)
        self.assertEqual(entry.watch_callback_called, True)
        entry.watch_callback_called = False

        entry.collaborators.add(foo, bar)
        self.assertEqual(entry.watch_callback_called, True)
        entry.watch_callback_called = False

        entry.collaborators.clear()
        self.assertEqual(entry.watch_callback_called, True)
        entry.watch_callback_called = False

        # teardown
        watcher.unwatch()

    def test_watch_before_create(self):
        """observer.ManyRelatedManagerWatcher: watch before create fails correctly"""
        # initial save -> watch
        entry = Entry(title='foo', body='bar')
        self.assertRaises(AttributeError, ManyRelatedManagerWatcher, entry, None, None)


class GenericRelatedObjectManagerWatcherTestCase(TestCase):
    def test_watch_after_create(self):
        """observer.GenericRelatedObjectManagerWatcher: watch after create works correctly"""
        def callback(sender, obj, attr):
            assert isinstance(sender, GenericRelatedObjectManagerWatcher)
            self.assertEqual(obj, entry)
            self.assertEqual(attr, 'tags')
            sender._obj.watch_callback_called = True
        # initial save -> watch
        entry = Entry(title='foo', body='foo')
        entry.watch_callback_called = False
        entry.save()
        watcher = GenericRelatedObjectManagerWatcher(entry, 'tags', callback)
        self.assertEqual(entry.watch_callback_called, False)

        entry.title = 'foofoo'
        entry.save()
        self.assertEqual(entry.watch_callback_called, False)

        tag1 = TaggedItem(content_object=entry, tag='foo')
        tag1.save()
        self.assertEqual(entry.watch_callback_called, True)
        entry.watch_callback_called = False

        tag1.delete()
        self.assertEqual(entry.watch_callback_called, True)
        entry.watch_callback_called = False

        # teardown
        watcher.unwatch()

    def test_watch_before_create(self):
        """observer.GenericRelatedObjectManagerWatcher: watch before create fails correctly"""
        # initial save -> watch
        entry = Entry(title='foo', body='bar')
        self.assertRaises(AttributeError, GenericRelatedObjectManagerWatcher, entry, None, None)


class ComplexWatcherTestCase(TestCase):
    def test_watch_one_to_many(self):
        """observer.OneToMany: watch one to many field works correctly
        
        Watch `author` and all field of `author` model instance
        """
        def callback(sender, obj, attr):
            sender._obj.watch_callback_called = True

        foo = User.objects.get(username='foo')
        bar = User.objects.get(username='bar')

        entry = Entry(title='foo', body='bar', author=None)
        entry.watch_callback_called = False
        entry.save()
        watcher = ComplexWatcher(entry, 'author', callback)

        self.assertEqual(entry.watch_callback_called, False)
        self.assert_(getattr(watcher, '_value_watcher'))
        self.assert_(getattr(watcher, '_model_watcher'))

        # Set author
        entry.author = foo
        entry.save()
        self.assertEqual(entry.watch_callback_called, True)
        entry.watch_callback_called = False
        
        # Change email of author
        foo.email = 'foofoo@test.com'
        foo.save()
        self.assertEqual(entry.watch_callback_called, True)
        entry.watch_callback_called = False

        # Change author
        entry.author = bar
        entry.save()
        self.assertEqual(entry.watch_callback_called, True)
        entry.watch_callback_called = False

        # Change email of author
        bar.email = 'barbar@test.com'
        bar.save()
        self.assertEqual(entry.watch_callback_called, True)
        entry.watch_callback_called = False

        # teardown
        watcher.unwatch()

    def test_watch_many_to_one(self):
        """observer.ManyToOne: watch many to one field works correctly
        
        Watch `entrys_create` and all field of each `entrys_create` model instance
        """
        def callback(sender, obj, attr):
            sender._obj.watch_callback_called = True

        foo = User.objects.get(username='foo')
        foo.watch_callback_called = False
        watcher = ComplexWatcher(foo, 'entrys_create', callback)

        entry1 = Entry.objects.create(title='1')
        entry2 = Entry.objects.create(title='2')

        # Add entry
        entry1.author = foo
        entry1.save()
        self.assertEqual(foo.watch_callback_called, True)
        foo.watch_callback_called = False

        # Modify entry
        entry1.title = 'hello1'
        entry1.save()
        self.assertEqual(foo.watch_callback_called, True)
        foo.watch_callback_called = False

        # Non related object modification doesn't interfere
        entry2.title = 'hello2'
        entry2.save()
        self.assertEqual(foo.watch_callback_called, False)

        # Delete related entry
        entry1.delete()
        self.assertEqual(foo.watch_callback_called, True)
        foo.watch_callback_called = False

        # teardown
        watcher.unwatch()

    def test_watch_many_to_many(self):
        """observer.ManyToMany: watch many to many field works correctly
        
        Watch `collaborators` and all field of each `collaborators` model instance
        """
        def callback(sender, obj, attr):
            sender._obj.watch_callback_called = True

        foo = User.objects.get(username='foo')
        bar = User.objects.get(username='bar')
        entry = Entry.objects.create(title='1')
        entry.watch_callback_called = False
        watcher = ComplexWatcher(entry, 'collaborators', callback)

        # Add collaborators
        entry.collaborators.add(foo, bar)
        self.assertEqual(entry.watch_callback_called, True)
        entry.watch_callback_called = False

        # Remove collaborator
        entry.collaborators.remove(foo)
        self.assertEqual(entry.watch_callback_called, True)
        entry.watch_callback_called = False

        # Clear collaborator
        entry.collaborators.clear()
        self.assertEqual(entry.watch_callback_called, True)
        entry.watch_callback_called = False

        # Modify collaborator instance
        entry.collaborators.add(foo)
        entry.watch_callback_called = False
        foo.email = 'foofoo@test.com'
        foo.save()
        self.assertEqual(entry.watch_callback_called, True)
        entry.watch_callback_called = False

        # Non related object doesn't inference
        bar.email = 'barbar@test.com'
        bar.save()
        self.assertEqual(entry.watch_callback_called, False)
        
        # Delete related collaborator instance
        foo.delete()
        self.assertEqual(entry.watch_callback_called, True)
        entry.watch_callback_called = False

        # teardown
        watcher.unwatch()

    def test_watch_generic_foreign_key(self):
        """observer.GenericForeignKey: watch generic foreign key field works correctly

        Watch `content_object` and all field of content_object related model instance
        """
        def callback(sender, obj, attr):
            sender._obj.watch_callback_called = True

        foo = Entry.objects.create(title='foo', body='foo')
        bar = Entry.objects.create(title='bar', body='bar')

        item = TaggedItem(content_object=foo, tag='foo')
        item.watch_callback_called = False
        item.save()
        watcher = ComplexWatcher(item, 'content_object', callback)

        bar.title = 'barbar'
        bar.save()
        self.assertEqual(item.watch_callback_called, False)

        foo.title = 'foofoo'
        foo.save()
        self.assertEqual(item.watch_callback_called, True)
        item.watch_callback_called = False

        item.content_object = bar
        item.save()
        self.assertEqual(item.watch_callback_called, True)
        item.watch_callback_called = False

        bar.title = 'bar'
        bar.save()
        self.assertEqual(item.watch_callback_called, True)
        item.watch_callback_called = False

        # teardown
        watcher.unwatch()

    def test_watch_generic_relation(self):
        """observer.GenericRelation: watch generic relation field works correctly
        
        Watch `tags` and all field of each `tags` model instance
        """
        def callback(sender, obj, attr):
            sender._obj.watch_callback_called = True

        entry = Entry.objects.create(title='foo')
        entry.watch_callback_called = False
        watcher = ComplexWatcher(entry, 'tags', callback)

        foo = TaggedItem(content_object=User.objects.get(pk=1), tag='foo') 
        foo.save()
        self.assertEqual(entry.watch_callback_called, False)

        bar = TaggedItem(content_object=entry, tag='bar') 
        bar.save()
        self.assertEqual(entry.watch_callback_called, True)
        entry.watch_callback_called = False

        hoge = TaggedItem(content_object=entry, tag='hoge') 
        hoge.save()
        self.assertEqual(entry.watch_callback_called, True)
        entry.watch_callback_called = False

        bar.tag = 'barbar'
        bar.save()
        self.assertEqual(entry.watch_callback_called, True)
        entry.watch_callback_called = False

        hoge.delete()
        self.assertEqual(entry.watch_callback_called, True)
        entry.watch_callback_called = False

        # teardown
        watcher.unwatch()

