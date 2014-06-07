from django.db import models
from django.db.models import FieldDoesNotExist
from django.contrib.contenttypes.generic import (GenericRelation,
                                                 GenericForeignKey)
from observer.tests.compat import TestCase
from observer.utils.models import get_field
from observer.tests.models import Article, Tag


class ObserverUtilsModelsGetFieldTestCase(TestCase):
    def setUp(self):
        self.model = Article

    def test_get_field_return_none(self):
        r = get_field(Article, 'non_existing_field')
        self.assertIsNone(r)

    def test_get_field_raise_exception(self):
        self.assertRaises(FieldDoesNotExist,
                          get_field,
                          Article, 'non_existing_field',
                          ignore_exception=False)

    def test_get_field_with_concreat_fields(self):
        concreate_fields = (
            ('title', models.CharField),
            ('content', models.TextField),
            ('supplement', models.OneToOneField),
            ('author', models.ForeignKey),
            ('collaborators', models.ManyToManyField),
        )
        for attr, expect in concreate_fields:
            field = get_field(Article, attr)
            self.assertTrue(isinstance(field, expect))
            # field's model is Article
            self.assertEqual(field.model, Article)

    def test_get_field_with_relational_fields(self):
        relational_fields = (
            ('revision', models.OneToOneField),
            ('projects', models.ForeignKey),
            ('hyperlinks', models.ManyToManyField),
        )
        for attr, expect in relational_fields:
            field = get_field(Article, attr)
            self.assertTrue(isinstance(field, expect))
            # field's model is not Article
            self.assertNotEqual(field.model, Article)

    def test_get_field_with_virtual_fields(self):
        virtual_fields = (
            ('tags', GenericRelation, Article),
            ('content_object', GenericForeignKey, Tag),
        )
        for attr, expect, model in virtual_fields:
            field = get_field(model, attr)
            self.assertTrue(isinstance(field, expect))
            # field's model is equal
            self.assertEqual(field.model, model)
