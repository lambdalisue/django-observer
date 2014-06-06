# coding=utf-8
"""
A model class of django-observer unittest
"""
__author__ = 'Alisue <lambdalisue@hashnote.net>'
from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from observer.tests.compat import auth_user_model


class ObserverTestLabel(models.Model):
    label = models.CharField('label', max_length=120)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey()

    class Meta:
        app_label = 'observer'

    def __unicode__(self):
        return "<Tag %s>" % self.label


class ObserverTestArticle(models.Model):
    title = models.CharField('title', max_length=50)
    content = models.TextField('content')

    author = models.ForeignKey(auth_user_model, blank=True, null=True,
                               related_name='observer_test_article')
    collaborators = models.ManyToManyField(auth_user_model,
                                           related_name='observer_test_'
                                                        'collaborate_aritcles')
    labels = generic.GenericRelation(ObserverTestLabel)

    class Meta:
        app_label = 'observer'

    def __unicode__(self):
        return "<Article %s>" % self.title
