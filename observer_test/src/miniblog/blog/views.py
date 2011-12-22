#!/usr/bin/env python
# vim: set fileencoding=utf8:
"""
Mini blog views


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
from django.views.generic import ListView
from django.views.generic import DetailView
from django.views.generic import CreateView
from django.views.generic import UpdateView
from django.views.generic import DeleteView
from django.core.urlresolvers import reverse

from models import Entry
from forms import EntryForm

class EntryListView(ListView):
    model = Entry
class EntryDetailView(DetailView):
    model = Entry
    slug_field = 'title'

class EntryCreateView(CreateView):
    form_class = EntryForm
    model = Entry
class EntryUpdateView(UpdateView):
    form_class = EntryForm
    model = Entry
class EntryDeleteView(DeleteView):
    model = Entry
    def get_success_url(self):
        return reverse('blog-entry-list')


