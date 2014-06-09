# coding=utf-8
"""
A model class of django-observer unittest
"""
__author__ = 'Alisue <lambdalisue@hashnote.net>'
from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType


def alias(name):
    """Define alias name of the class"""
    def decorator(cls):
        globals()[name] = cls
        return cls
    return decorator


@alias('Article')
class ObserverTestArticle(models.Model):
    # concrete fields ========================================================
    # ValueField
    title = models.CharField(max_length=50)
    content = models.TextField()

    # RelatedField (OneToOneRel)
    supplement = models.OneToOneField(
        'observer.ObserverTestSupplement', blank=True, null=True,
        related_name='article')

    # RelatedField (OneToManyRel)
    author = models.ForeignKey(
        'observer.ObserverTestUser', blank=True, null=True,
        related_name='article')

    # ManyRelatedField (ManyToManyRel)
    collaborators = models.ManyToManyField(
        'observer.ObserverTestUser',
        related_name='articles')

    # relational fields ======================================================

    # RelatedField (OneToOneRel)
    # revision: reverse OneToOneField

    # ManyRelatedField (ManyToOneRel)
    # projects: reverse ForeignKey

    # ManyRelatedField (ManyToManyRel)
    # hyperlinks: reverse ManyToManyField

    # virtual fields
    tags = generic.GenericRelation('observer.ObserverTestTag')

    class Meta:
        app_label = 'observer'

    def __unicode__(self):
        return "<Article %s>" % self.title


# connected from Article =====================================================
@alias('User')
class ObserverTestUser(models.Model):
    label = models.CharField(max_length=20)

    class Meta:
        app_label = 'observer'

    def __unicode__(self):
        return "<User %s>" % self.label


@alias('Supplement')
class ObserverTestSupplement(models.Model):
    label = models.CharField(max_length=50)

    class Meta:
        app_label = 'observer'

    def __unicode__(self):
        return "<Supplement %s>" % self.label


# connected to Article =======================================================
@alias('Revision')
class ObserverTestRevision(models.Model):
    label = models.CharField(max_length=50)
    article = models.OneToOneField(
        'observer.ObserverTestArticle', blank=True, null=True,
        related_name='revision')

    class Meta:
        app_label = 'observer'

    def __unicode__(self):
        return "<Revision %s>" % self.label


@alias('Project')
class ObserverTestProject(models.Model):
    label = models.CharField(max_length=50)
    article = models.ForeignKey(
        'observer.ObserverTestArticle', blank=True, null=True,
        related_name='projects')

    class Meta:
        app_label = 'observer'

    def __unicode__(self):
        return "<Project %s>" % self.label


@alias('Hyperlink')
class ObserverTestHyperlink(models.Model):
    label = models.CharField(max_length=50)
    articles = models.ManyToManyField(
        'observer.ObserverTestArticle',
        related_name='hyperlinks')

    class Meta:
        app_label = 'observer'

    def __unicode__(self):
        return "<Hyperlink %s>" % self.label


@alias('Tag')
class ObserverTestTag(models.Model):
    label = models.CharField(max_length=50)
    content_type = models.ForeignKey(ContentType, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = generic.GenericForeignKey()

    class Meta:
        app_label = 'observer'

    def __unicode__(self):
        return "<Tag %s>" % self.label
