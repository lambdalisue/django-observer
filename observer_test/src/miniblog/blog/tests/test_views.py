#!/usr/bin/env python
# vim: set fileencoding=utf8:
"""
Unittest module of ...


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


class EntryViewTestCase(TestCase):
    fixtures = ['test.yaml']

    def test_list(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_detail(self):
        response = self.client.get('/foo/')
        self.assertEqual(response.status_code, 200)

    def test_create(self):
        response = self.client.get('/create/')
        self.assertEqual(response.status_code, 200)

    def test_update(self):
        response = self.client.get('/update/1/')
        self.assertEqual(response.status_code, 200)

    def test_delete(self):
        response = self.client.get('/delete/1/')
        self.assertEqual(response.status_code, 200)

    def test_with_author(self):
        from django.contrib.auth.models import User
        from ..models import Entry
        response = self.client.post('/create/', {
                'title': 'foo',
                'body': 'foo'
            })
        self.assertEqual(response.status_code, 200)

        entry = Entry.objects.get(title='foo')
        self.assertEqual(entry.author, None)
        self.assertEqual(entry.updated_by, None)

        assert self.client.login(username='admin', password='password')
        response = self.client.post('/create/', {
                'title': 'barbar',
                'body': 'barbar'
            })
        # if post success, redirect occur
        self.assertEqual(response.status_code, 302)

        admin = User.objects.get(username='admin')
        entry = Entry.objects.get(title='barbar')
        self.assertEqual(entry.author, admin)
        self.assertEqual(entry.updated_by, admin)

        self.client.logout()
        assert self.client.login(username='foo', password='password')
        response = self.client.post('/update/%d/' % entry.pk, {
                'title': 'barbarbar',
                'body': 'barbarbar'
            })
        # if post success, redirect occur
        self.assertEqual(response.status_code, 302)

        foo = User.objects.get(username='foo')
        entry = Entry.objects.get(pk=entry.pk)
        self.assertEqual(entry.author, admin)
        self.assertEqual(entry.updated_by, foo)
