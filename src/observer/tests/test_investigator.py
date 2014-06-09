from django.core.exceptions import ObjectDoesNotExist
from observer.tests.models import Article
from observer.tests.factories import ArticleFactory
from observer.tests.compat import TestCase
from observer.tests.compat import MagicMock
from observer.investigator import Investigator


class ObserverInvestigatorTestCase(TestCase):
    def setUp(self):
        self.model = Article
        self.attr = 'foobar'
        self.callback = MagicMock()
        self.Investigator = MagicMock(wraps=Investigator)
        self.investigator = self.Investigator(self.model)
        self.investigator._object_cached[1] = ArticleFactory()
        self.investigator._object_cached[2] = ArticleFactory()
        self.investigator._object_cached[3] = ArticleFactory()

    def test_get_cached_return_cached_objects(self):
        """get_cached should return cached obj"""
        for i in range(3):
            pk = i + 1
            cached_obj = self.investigator._object_cached[pk]
            r = self.investigator.get_cached(pk)
            self.assertEqual(r, cached_obj)

    def test_get_cached_return_none(self):
        """get_cached should return None if no object is found"""
        r = self.investigator.get_cached(0)
        self.assertEqual(r, None)

    def test_get_cached_raise_exception(self):
        """get_cached should raise ObjectDoesNotExist with !ignore_exception"""
        self.assertRaises(ObjectDoesNotExist,
                          self.investigator.get_cached,
                          0, ignore_exception=False)

    def test_get_object_return_obj_from_database(self):
        """get_object should return obj from database"""
        unsaved_obj = ArticleFactory()
        unsaved_obj.title = 'unsaved value'
        r = self.investigator.get_object(unsaved_obj.pk)
        # title should not be different because unsaved_obj has not saved yet
        self.assertNotEqual(r.title, unsaved_obj.title)
        # save
        unsaved_obj.save()
        r = self.investigator.get_object(unsaved_obj.pk)
        self.assertEqual(r.title, unsaved_obj.title)

    def test_get_object_return_none(self):
        """get_object should return None if no object is found"""
        r = self.investigator.get_object(-1)
        self.assertIsNone(r)

    def test_get_object_raise_exception(self):
        """get_object should raise ObjectDoesNotExist if !ignore_exception"""
        self.assertRaises(ObjectDoesNotExist,
                          self.investigator.get_object,
                          -1, ignore_exception=False)

    def test_prepare_update_cache(self):
        """prepare should update cache"""
        pk = 1
        new_instance = MagicMock(pk=pk)
        raw_instance = MagicMock(pk=pk)
        old_instance = MagicMock(pk=pk)
        # prepare cache manually / patch method
        self.investigator._object_cached[pk] = old_instance
        self.investigator.get_object = MagicMock(return_value=raw_instance)
        # make sure that get_cached(pk) return correct value
        self.assertEqual(self.investigator.get_cached(pk), old_instance)
        # call prepare with new instance
        self.investigator.prepare(new_instance)
        self.assertNotEqual(self.investigator.get_cached(pk), old_instance)
        self.assertNotEqual(self.investigator.get_cached(pk), new_instance)
        self.assertEqual(self.investigator.get_cached(pk), raw_instance)

    def test_prepare_not_update_cache(self):
        """prepare should not update cache if instance does not have pk"""
        pk = None
        new_instance = MagicMock(pk=pk)
        raw_instance = MagicMock(pk=pk)
        old_instance = MagicMock(pk=pk)
        # prepare cache manually / patch method
        self.investigator._object_cached[pk] = old_instance
        self.investigator.get_object = MagicMock(return_value=raw_instance)
        # make sure that get_cached(pk) return correct value
        self.assertEqual(self.investigator.get_cached(pk), old_instance)
        # call prepare with new instance
        self.investigator.prepare(new_instance)
        self.assertEqual(self.investigator.get_cached(pk), old_instance)
        self.assertNotEqual(self.investigator.get_cached(pk), new_instance)
        self.assertNotEqual(self.investigator.get_cached(pk), raw_instance)

    def test_investigate_yield_modified_attributes(self):
        """investigate should yields modified attribute names"""
        article = ArticleFactory()
        article.title = 'modified'
        article.content = 'modified'
        # call prepare before save
        self.investigator.prepare(article)
        # save the change
        article.save()
        # investigate
        iterator = self.investigator.investigate(article)
        self.assertEqual(set(list(iterator)), set([
            'title', 'content',
        ]))

    def test_investigate_not_yield_created(self):
        """investigate should not yields anythong on creation"""
        article = ArticleFactory.build()
        article.title = 'modified'
        article.content = 'modified'
        # call prepare before save
        self.investigator.prepare(article)
        # save the change
        article.save()
        # investigate
        iterator = self.investigator.investigate(article)
        self.assertEqual(set(list(iterator)), set())

    def test_investigate_yield_included_modified_attributes(self):
        """investigate should yields only included modified attribute names"""
        self.investigator.include = ['content']
        article = ArticleFactory()
        article.title = 'modified'
        article.content = 'modified'
        # call prepare before save
        self.investigator.prepare(article)
        # save the change
        article.save()
        # investigate
        iterator = self.investigator.investigate(article)
        self.assertEqual(set(list(iterator)), set([
            'content',
        ]))

    def test_investigate_not_yield_excluded_modified_attributes(self):
        """investigate should not yields excluded modified attribute names"""
        self.investigator.exclude = ['content']
        article = ArticleFactory()
        article.title = 'modified'
        article.content = 'modified'
        # call prepare before save
        self.investigator.prepare(article)
        # save the change
        article.save()
        # investigate
        iterator = self.investigator.investigate(article)
        self.assertEqual(set(list(iterator)), set([
            'title',
        ]))
