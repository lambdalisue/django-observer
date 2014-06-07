from django.core.exceptions import ObjectDoesNotExist
from observer.tests.compat import TestCase
from observer.tests.compat import MagicMock, skip
from observer.tests.models import Article, Tag
from observer.tests.factories import (ArticleFactory,
                                      SupplementFactory,
                                      RevisionFactory,
                                      UserFactory,
                                      ProjectFactory,
                                      HyperlinkFactory,
                                      TagFactory)
from observer.watchers.related import (RelatedWatcherBase,
                                       RelatedWatcher,
                                       ManyRelatedWatcher,
                                       GenericRelatedWatcher)


# ============================================================================
# RelatedWatcherBase
# ============================================================================
class ObserverWatchersRelatedWatcherBaseTestCaseOneToOneRel(TestCase):
    def setUp(self):
        self.model = Article
        self.attr = 'supplement'
        self.callback = MagicMock()
        self.watcher = RelatedWatcherBase(self.model,
                                          self.attr,
                                          self.callback)
        self.addCleanup(self.watcher.unwatch)

    def test_callback_not_called_on_modification_without_watch(self):
        new_instance = ArticleFactory()
        supplement = new_instance.supplement
        supplement.label = 'modified'
        supplement.save()
        # have not watched, thus callback should not be called
        self.assertFalse(self.callback.called)

    def test_callback_called_on_modification_with_watch(self):
        new_instance = ArticleFactory()
        self.watcher.watch()
        supplement = new_instance.supplement
        supplement.label = 'modified'
        supplement.save()
        # callback should be called with instance modification
        self.callback.assert_called_once_with(
            obj=new_instance, attr=self.attr, sender=self.watcher)


class ObserverWatchersRelatedWatcherBaseTestCaseRevOneToOneRel(
        TestCase):
    def setUp(self):
        self.model = Article
        self.attr = 'revision'
        self.callback = MagicMock()
        self.watcher = RelatedWatcherBase(self.model,
                                          self.attr,
                                          self.callback)
        self.addCleanup(self.watcher.unwatch)

    def test_callback_not_called_on_modification_without_watch(self):
        new_instance = ArticleFactory()
        revision = new_instance.revision
        revision.label = 'modified'
        revision.save()
        # have not watched, thus callback should not be called
        self.assertFalse(self.callback.called)

    def test_callback_called_on_modification_with_watch(self):
        new_instance = ArticleFactory()
        self.watcher.watch()
        revision = new_instance.revision
        revision.label = 'modified'
        revision.save()
        # callback should be called with instance modification
        self.callback.assert_called_once_with(
            obj=new_instance, attr=self.attr, sender=self.watcher)


class ObserverWatchersRelatedWatcherBaseTestCaseOneToManyRel(TestCase):
    def setUp(self):
        self.model = Article
        self.attr = 'author'
        self.callback = MagicMock()
        self.watcher = RelatedWatcherBase(self.model,
                                          self.attr,
                                          self.callback)
        self.addCleanup(self.watcher.unwatch)

    def test_callback_not_called_on_modification_without_watch(self):
        new_instance = ArticleFactory()
        user = new_instance.author
        user.label = 'modified'
        user.save()
        # have not watched, thus callback should not be called
        self.assertFalse(self.callback.called)

    def test_callback_called_on_modification_with_watch(self):
        new_instance = ArticleFactory()
        self.watcher.watch()
        user = new_instance.author
        user.label = 'modified'
        user.save()
        # callback should be called with instance modification
        self.callback.assert_called_once_with(
            obj=new_instance, attr=self.attr, sender=self.watcher)


class ObserverWatchersRelatedWatcherBaseTestCaseRevManyToOneRel(TestCase):
    def setUp(self):
        self.projects = (
            ProjectFactory(),
            ProjectFactory(),
            ProjectFactory(),
            ProjectFactory(),
            ProjectFactory(),
        )
        self.model = Article
        self.attr = 'projects'
        self.callback = MagicMock()
        self.watcher = RelatedWatcherBase(self.model,
                                          self.attr,
                                          self.callback)
        self.addCleanup(self.watcher.unwatch)

    def test_callback_not_called_on_modification_without_watch(self):
        new_instance = ArticleFactory(projects=self.projects)
        project = new_instance.projects.get(pk=1)
        project.label = 'modified'
        project.save()
        # have not watched, thus callback should not be called
        self.assertFalse(self.callback.called)

    def test_callback_called_on_modification_with_watch(self):
        new_instance = ArticleFactory(projects=self.projects)
        self.watcher.watch()
        project = new_instance.projects.get(pk=1)
        project.label = 'modified'
        project.save()
        # callback should be called with instance modification
        self.callback.assert_called_once_with(
            obj=new_instance, attr=self.attr, sender=self.watcher)


class ObserverWatchersRelatedWatcherBaseTestCaseManyToManyRel(TestCase):
    def setUp(self):
        self.users = (
            UserFactory(),
            UserFactory(),
            UserFactory(),
            UserFactory(),
            UserFactory(),
        )
        self.model = Article
        self.attr = 'collaborators'
        self.callback = MagicMock()
        self.watcher = RelatedWatcherBase(self.model,
                                          self.attr,
                                          self.callback)
        self.addCleanup(self.watcher.unwatch)

    def test_callback_not_called_on_modification_without_watch(self):
        new_instance = ArticleFactory(collaborators=self.users)
        user = new_instance.collaborators.get(pk=1)
        user.label = 'modified'
        user.save()
        # have not watched, thus callback should not be called
        self.assertFalse(self.callback.called)

    def test_callback_called_on_modification_with_watch(self):
        new_instance = ArticleFactory(collaborators=self.users)
        self.watcher.watch()
        user = new_instance.collaborators.get(pk=1)
        user.label = 'modified'
        user.save()
        # callback should be called with instance modification
        self.callback.assert_called_once_with(
            obj=new_instance, attr=self.attr, sender=self.watcher)


class ObserverWatchersRelatedWatcherBaseTestCaseRevManyToManyRel(TestCase):
    def setUp(self):
        self.hyperlinks = (
            HyperlinkFactory(),
            HyperlinkFactory(),
            HyperlinkFactory(),
            HyperlinkFactory(),
            HyperlinkFactory(),
        )
        self.model = Article
        self.attr = 'hyperlinks'
        self.callback = MagicMock()
        self.watcher = RelatedWatcherBase(self.model,
                                          self.attr,
                                          self.callback)
        self.addCleanup(self.watcher.unwatch)

    def test_callback_not_called_on_modification_without_watch(self):
        new_instance = ArticleFactory(hyperlinks=self.hyperlinks)
        hyperlink = new_instance.hyperlinks.get(pk=1)
        hyperlink.label = 'modified'
        hyperlink.save()
        # have not watched, thus callback should not be called
        self.assertFalse(self.callback.called)

    def test_callback_called_on_modification_with_watch(self):
        new_instance = ArticleFactory(hyperlinks=self.hyperlinks)
        self.watcher.watch()
        hyperlink = new_instance.hyperlinks.get(pk=1)
        hyperlink.label = 'modified'
        hyperlink.save()
        # callback should be called with instance modification
        self.callback.assert_called_once_with(
            obj=new_instance, attr=self.attr, sender=self.watcher)


# ============================================================================
# RelatedWatcher
# ============================================================================
class ObserverWatchersRelatedWatcherTestCaseOneToOneRel(TestCase):
    def setUp(self):
        self.model = Article
        self.attr = 'supplement'
        self.callback = MagicMock()
        self.watcher = RelatedWatcher(self.model,
                                      self.attr,
                                      self.callback)
        self.addCleanup(self.watcher.unwatch)

    def test_callback_not_called_on_create_without_watch(self):
        ArticleFactory()
        # have not watched, thus callback should not be called
        self.assertFalse(self.callback.called)

    def test_callback_called_on_create_with_watch(self):
        self.watcher.watch()
        new_instance = ArticleFactory()
        # callback should be called with newly created instance
        self.callback.assert_called_once_with(
            obj=new_instance, attr=self.attr, sender=self.watcher)

    def test_callback_not_called_on_create_without_call_on_created(self):
        self.watcher.watch(call_on_created=False)
        ArticleFactory()
        # have not watched, thus callback should not be called
        self.assertFalse(self.callback.called)

    def test_callback_not_called_on_modification_without_watch(self):
        new_instance = ArticleFactory()
        new_instance.supplement = SupplementFactory()
        new_instance.save()
        # have not watched, thus callback should not be called
        self.assertFalse(self.callback.called)

    def test_callback_called_on_modification_with_watch(self):
        new_instance = ArticleFactory()
        self.watcher.watch()
        new_instance.supplement = SupplementFactory()
        new_instance.save()
        # callback should be called with instance modification
        self.callback.assert_called_once_with(
            obj=new_instance, attr=self.attr, sender=self.watcher)

    def test_callback_not_called_on_modification_with_non_interest_attr(self):
        new_instance = ArticleFactory()
        new_instance.content = 'modified'
        new_instance.save()
        # content is not watched thus callback should not be called
        self.assertFalse(self.callback.called)

    def test_callback_not_called_on_related_modification_without_watch(self):
        new_instance = ArticleFactory()
        supplement = new_instance.supplement
        supplement.label = 'modified'
        supplement.save()
        # have not watched, thus callback should not be called
        self.assertFalse(self.callback.called)

    def test_callback_called_on_related_modification_with_watch(self):
        new_instance = ArticleFactory()
        self.watcher.watch()
        supplement = new_instance.supplement
        supplement.label = 'modified'
        supplement.save()
        # callback should be called with instance modification
        self.callback.assert_called_once_with(
            obj=new_instance, attr=self.attr, sender=self.watcher)


class ObserverWatchersRelatedWatcherTestCaseRevOneToOneRel(TestCase):
    def setUp(self):
        self.model = Article
        self.attr = 'revision'
        self.callback = MagicMock()
        self.watcher = RelatedWatcher(self.model,
                                      self.attr,
                                      self.callback)
        self.addCleanup(self.watcher.unwatch)

    def test_callback_not_called_on_create_without_watch(self):
        ArticleFactory()
        # have not watched, thus callback should not be called
        self.assertFalse(self.callback.called)

    def test_callback_called_on_create_with_watch(self):
        self.watcher.watch()
        new_instance = ArticleFactory()
        # callback should be called with newly created instance
        self.callback.assert_called_once_with(
            obj=new_instance, attr=self.attr, sender=self.watcher)

    def test_callback_not_called_on_create_without_call_on_created(self):
        self.watcher.watch(call_on_created=False)
        ArticleFactory()
        # have not watched, thus callback should not be called
        self.assertFalse(self.callback.called)

    def test_callback_not_called_on_modification_without_watch(self):
        new_instance = ArticleFactory()
        new_instance.revision = RevisionFactory()
        new_instance.save()
        # have not watched, thus callback should not be called
        self.assertFalse(self.callback.called)

    def test_callback_called_on_modification_with_watch(self):
        new_instance = ArticleFactory(revision=None)
        new_revision = RevisionFactory()
        self.watcher.watch()
        # reverse assignment does not work (it is django's definition)
        new_instance.revision = new_revision
        new_instance.save()
        self.assertRaises(
            ObjectDoesNotExist,
            lambda: Article.objects.get(pk=new_instance.pk).revision)
        # thus assign directly to new_revision
        new_revision.article = new_instance
        new_revision.save()
        # callback should be called with instance modification
        self.callback.assert_called_once_with(
            obj=new_instance, attr=self.attr, sender=self.watcher)

    def test_callback_not_called_on_modification_with_non_interest_attr(self):
        new_instance = ArticleFactory()
        new_instance.content = 'modified'
        new_instance.save()
        # content is not watched thus callback should not be called
        self.assertFalse(self.callback.called)

    def test_callback_not_called_on_related_modification_without_watch(self):
        new_instance = ArticleFactory()
        revision = new_instance.revision
        revision.label = 'modified'
        revision.save()
        # have not watched, thus callback should not be called
        self.assertFalse(self.callback.called)

    def test_callback_called_on_related_modification_with_watch(self):
        new_instance = ArticleFactory()
        self.watcher.watch()
        revision = new_instance.revision
        revision.label = 'modified'
        revision.save()
        # callback should be called with instance modification
        self.callback.assert_called_once_with(
            obj=new_instance, attr=self.attr, sender=self.watcher)


class ObserverWatchersRelatedWatcherTestCaseOneToManyRel(TestCase):
    def setUp(self):
        self.model = Article
        self.attr = 'author'
        self.callback = MagicMock()
        self.watcher = RelatedWatcher(self.model,
                                      self.attr,
                                      self.callback)
        self.addCleanup(self.watcher.unwatch)

    def test_callback_not_called_on_create_without_watch(self):
        ArticleFactory()
        # have not watched, thus callback should not be called
        self.assertFalse(self.callback.called)

    def test_callback_called_on_create_with_watch(self):
        self.watcher.watch()
        new_instance = ArticleFactory()
        # callback should be called with newly created instance
        self.callback.assert_called_once_with(
            obj=new_instance, attr=self.attr, sender=self.watcher)

    def test_callback_not_called_on_create_without_call_on_created(self):
        self.watcher.watch(call_on_created=False)
        ArticleFactory()
        # have not watched, thus callback should not be called
        self.assertFalse(self.callback.called)

    def test_callback_not_called_on_modification_without_watch(self):
        new_instance = ArticleFactory()
        new_instance.author = UserFactory()
        new_instance.save()
        # have not watched, thus callback should not be called
        self.assertFalse(self.callback.called)

    def test_callback_called_on_modification_with_watch(self):
        new_instance = ArticleFactory()
        self.watcher.watch()
        new_instance.author = UserFactory()
        new_instance.save()
        # callback should be called with instance modification
        self.callback.assert_called_once_with(
            obj=new_instance, attr=self.attr, sender=self.watcher)

    def test_callback_not_called_on_modification_with_non_interest_attr(self):
        new_instance = ArticleFactory()
        new_instance.content = 'modified'
        new_instance.save()
        # content is not watched thus callback should not be called
        self.assertFalse(self.callback.called)

    def test_callback_not_called_on_related_modification_without_watch(self):
        new_instance = ArticleFactory()
        user = new_instance.author
        user.label = 'modified'
        user.save()
        # have not watched, thus callback should not be called
        self.assertFalse(self.callback.called)

    def test_callback_called_on_related_modification_with_watch(self):
        new_instance = ArticleFactory()
        self.watcher.watch()
        user = new_instance.author
        user.label = 'modified'
        user.save()
        # callback should be called with instance modification
        self.callback.assert_called_once_with(
            obj=new_instance, attr=self.attr, sender=self.watcher)


class ObserverWatchersManyRelatedWatcherTestCaseRevManyToOneRel(TestCase):
    def setUp(self):
        self.projects = (
            ProjectFactory(),
            ProjectFactory(),
            ProjectFactory(),
            ProjectFactory(),
            ProjectFactory(),
        )
        self.model = Article
        self.attr = 'projects'
        self.callback = MagicMock()
        self.watcher = ManyRelatedWatcher(self.model,
                                          self.attr,
                                          self.callback)
        self.addCleanup(self.watcher.unwatch)

    def test_callback_not_called_on_add_without_watch(self):
        new_instance = ArticleFactory(projects=self.projects)
        new_instance.projects.add(ProjectFactory())
        # have not watched, thus callback should not be called
        self.assertFalse(self.callback.called)

    def test_callback_called_on_add_with_watch(self):
        new_instance = ArticleFactory(projects=self.projects)
        self.watcher.watch()
        new_instance.projects.add(ProjectFactory())
        # callback should be called with instance modification
        self.callback.assert_called_once_with(
            obj=new_instance, attr=self.attr, sender=self.watcher)

    def test_callback_not_called_on_remove_without_watch(self):
        new_instance = ArticleFactory(projects=self.projects)
        new_instance.projects.remove(self.projects[0])
        # have not watched, thus callback should not be called
        self.assertFalse(self.callback.called)

    def test_callback_called_on_remove_with_watch(self):
        new_instance = ArticleFactory(projects=self.projects)
        self.watcher.watch()
        new_instance.projects.remove(self.projects[0])
        # callback should be called with instance modification
        self.callback.assert_called_once_with(
            obj=new_instance, attr=self.attr, sender=self.watcher)

    def test_callback_not_called_on_reverse_add_without_watch(self):
        new_instance = ProjectFactory()
        add_instance = ArticleFactory()
        new_instance.article = add_instance
        new_instance.save()
        # have not watched, thus callback should not be called
        self.assertFalse(self.callback.called)

    def test_callback_called_on_reverse_add_with_watch(self):
        new_instance = ProjectFactory()
        add_instance = ArticleFactory()
        self.watcher.watch()
        new_instance.article = add_instance
        new_instance.save()
        # callback should be called with instance modification
        self.callback.assert_called_once_with(
            obj=add_instance, attr=self.attr, sender=self.watcher)

    def test_callback_not_called_on_reverse_remove_without_watch(self):
        ArticleFactory(projects=self.projects)
        self.projects[0].article = None
        self.projects[0].save()
        # have not watched, thus callback should not be called
        self.assertFalse(self.callback.called)

    def test_callback_called_on_reverse_remove_with_watch(self):
        new_instance = ArticleFactory(projects=self.projects)
        self.watcher.watch()
        self.projects[0].article = None
        self.projects[0].save()
        # callback should be called with instance modification
        self.callback.assert_called_once_with(
            obj=new_instance, attr=self.attr, sender=self.watcher)

    def test_callback_not_called_on_create_without_watch(self):
        ArticleFactory()
        # have not watched, thus callback should not be called
        self.assertFalse(self.callback.called)

    def test_callback_called_on_create_with_watch(self):
        self.watcher.watch()
        new_instance = ArticleFactory()
        # callback should be called with newly created instance
        self.callback.assert_called_once_with(
            obj=new_instance, attr=self.attr, sender=self.watcher)

    def test_callback_not_called_on_create_without_call_on_created(self):
        self.watcher.watch(call_on_created=False)
        ArticleFactory()
        # have not watched, thus callback should not be called
        self.assertFalse(self.callback.called)

    def test_callback_not_called_on_modification_with_non_interest_attr(self):
        new_instance = ArticleFactory()
        new_instance.content = 'modified'
        new_instance.save()
        # content is not watched thus callback should not be called
        self.assertFalse(self.callback.called)

    def test_callback_not_called_on_modification_without_watch(self):
        new_instance = ArticleFactory(projects=self.projects)
        project = new_instance.projects.get(pk=1)
        project.label = 'modified'
        project.save()
        # have not watched, thus callback should not be called
        self.assertFalse(self.callback.called)

    def test_callback_called_on_modification_with_watch(self):
        new_instance = ArticleFactory(projects=self.projects)
        self.watcher.watch()
        project = new_instance.projects.get(pk=1)
        project.label = 'modified'
        project.save()
        # callback should be called with instance modification
        self.callback.assert_called_once_with(
            obj=new_instance, attr=self.attr, sender=self.watcher)


# ============================================================================
# ManyRelatedWatcher
# ============================================================================
class ObserverWatchersManyRelatedWatcherTestCaseManyToManyRel(TestCase):
    def setUp(self):
        self.users = (
            UserFactory(),
            UserFactory(),
            UserFactory(),
            UserFactory(),
            UserFactory(),
        )
        self.model = Article
        self.attr = 'collaborators'
        self.callback = MagicMock()
        self.watcher = ManyRelatedWatcher(self.model,
                                          self.attr,
                                          self.callback)
        self.addCleanup(self.watcher.unwatch)

    def test_callback_not_called_on_add_without_watch(self):
        new_instance = ArticleFactory(collaborators=self.users)
        new_instance.collaborators.add(UserFactory())
        # have not watched, thus callback should not be called
        self.assertFalse(self.callback.called)

    def test_callback_called_on_add_with_watch(self):
        new_instance = ArticleFactory(collaborators=self.users)
        self.watcher.watch()
        new_instance.collaborators.add(UserFactory())
        # callback should be called with instance modification
        self.callback.assert_called_once_with(
            obj=new_instance, attr=self.attr, sender=self.watcher)

    def test_callback_not_called_on_remove_without_watch(self):
        new_instance = ArticleFactory(collaborators=self.users)
        new_instance.collaborators.get(pk=1).delete()
        # have not watched, thus callback should not be called
        self.assertFalse(self.callback.called)

    def test_callback_called_on_remove_with_watch(self):
        new_instance = ArticleFactory(collaborators=self.users)
        self.watcher.watch()
        new_instance.collaborators.remove(self.users[0])
        # callback should be called with instance modification
        self.callback.assert_called_once_with(
            obj=new_instance, attr=self.attr, sender=self.watcher)

    def test_callback_not_called_on_reverse_add_without_watch(self):
        new_instance = UserFactory()
        add_instance = ArticleFactory()
        new_instance.articles.add(add_instance)
        # have not watched, thus callback should not be called
        self.assertFalse(self.callback.called)

    def test_callback_called_on_reverse_add_with_watch(self):
        new_instance = UserFactory()
        add_instance = ArticleFactory()
        self.watcher.watch()
        new_instance.articles.add(add_instance)
        # callback should be called with instance modification
        self.callback.assert_called_once_with(
            obj=add_instance, attr=self.attr, sender=self.watcher)

    def test_callback_not_called_on_reverse_remove_without_watch(self):
        add_instance = ArticleFactory(collaborators=self.users)
        self.users[0].articles.remove(add_instance)
        # have not watched, thus callback should not be called
        self.assertFalse(self.callback.called)

    def test_callback_called_on_reverse_remove_with_watch(self):
        add_instance = ArticleFactory(collaborators=self.users)
        self.watcher.watch()
        self.users[0].articles.remove(add_instance)
        # callback should be called with instance modification
        self.callback.assert_called_once_with(
            obj=add_instance, attr=self.attr, sender=self.watcher)

    def test_callback_not_called_on_create_without_watch(self):
        ArticleFactory()
        # have not watched, thus callback should not be called
        self.assertFalse(self.callback.called)

    def test_callback_called_on_create_with_watch(self):
        self.watcher.watch()
        new_instance = ArticleFactory()
        # callback should be called with newly created instance
        self.callback.assert_called_once_with(
            obj=new_instance, attr=self.attr, sender=self.watcher)

    def test_callback_not_called_on_create_without_call_on_created(self):
        self.watcher.watch(call_on_created=False)
        ArticleFactory()
        # have not watched, thus callback should not be called
        self.assertFalse(self.callback.called)

    def test_callback_not_called_on_modification_with_non_interest_attr(self):
        new_instance = ArticleFactory()
        new_instance.content = 'modified'
        new_instance.save()
        # content is not watched thus callback should not be called
        self.assertFalse(self.callback.called)

    def test_callback_not_called_on_modification_without_watch(self):
        new_instance = ArticleFactory(collaborators=self.users)
        user = new_instance.collaborators.get(pk=1)
        user.label = 'modified'
        user.save()
        # have not watched, thus callback should not be called
        self.assertFalse(self.callback.called)

    def test_callback_called_on_modification_with_watch(self):
        new_instance = ArticleFactory(collaborators=self.users)
        self.watcher.watch()
        user = new_instance.collaborators.get(pk=1)
        user.label = 'modified'
        user.save()
        # callback should be called with instance modification
        self.callback.assert_called_once_with(
            obj=new_instance, attr=self.attr, sender=self.watcher)


class ObserverWatchersManyRelatedWatcherTestCaseRevManyToManyRel(TestCase):
    def setUp(self):
        self.hyperlinks = (
            HyperlinkFactory(),
            HyperlinkFactory(),
            HyperlinkFactory(),
            HyperlinkFactory(),
            HyperlinkFactory(),
        )
        self.model = Article
        self.attr = 'hyperlinks'
        self.callback = MagicMock()
        self.watcher = ManyRelatedWatcher(self.model,
                                          self.attr,
                                          self.callback)
        self.addCleanup(self.watcher.unwatch)

    def test_callback_not_called_on_add_without_watch(self):
        new_instance = ArticleFactory(hyperlinks=self.hyperlinks)
        new_instance.hyperlinks.add(HyperlinkFactory())
        # have not watched, thus callback should not be called
        self.assertFalse(self.callback.called)

    def test_callback_called_on_add_with_watch(self):
        new_instance = ArticleFactory(hyperlinks=self.hyperlinks)
        self.watcher.watch()
        new_instance.hyperlinks.add(HyperlinkFactory())
        # callback should be called with instance modification
        self.callback.assert_called_once_with(
            obj=new_instance, attr=self.attr, sender=self.watcher)

    def test_callback_not_called_on_remove_without_watch(self):
        new_instance = ArticleFactory(hyperlinks=self.hyperlinks)
        new_instance.hyperlinks.get(pk=1).delete()
        # have not watched, thus callback should not be called
        self.assertFalse(self.callback.called)

    def test_callback_called_on_remove_with_watch(self):
        new_instance = ArticleFactory(hyperlinks=self.hyperlinks)
        self.watcher.watch()
        new_instance.hyperlinks.remove(self.hyperlinks[0])
        # callback should be called with instance modification
        self.callback.assert_called_once_with(
            obj=new_instance, attr=self.attr, sender=self.watcher)

    def test_callback_not_called_on_reverse_add_without_watch(self):
        new_instance = HyperlinkFactory()
        add_instance = ArticleFactory()
        new_instance.articles.add(add_instance)
        # have not watched, thus callback should not be called
        self.assertFalse(self.callback.called)

    def test_callback_called_on_reverse_add_with_watch(self):
        new_instance = HyperlinkFactory()
        add_instance = ArticleFactory()
        self.watcher.watch()
        new_instance.articles.add(add_instance)
        # callback should be called with instance modification
        self.callback.assert_called_once_with(
            obj=add_instance, attr=self.attr, sender=self.watcher)

    def test_callback_not_called_on_reverse_remove_without_watch(self):
        add_instance = ArticleFactory(hyperlinks=self.hyperlinks)
        self.hyperlinks[0].articles.remove(add_instance)
        # have not watched, thus callback should not be called
        self.assertFalse(self.callback.called)

    def test_callback_called_on_reverse_remove_with_watch(self):
        add_instance = ArticleFactory(hyperlinks=self.hyperlinks)
        self.watcher.watch()
        self.hyperlinks[0].articles.remove(add_instance)
        # callback should be called with instance modification
        self.callback.assert_called_once_with(
            obj=add_instance, attr=self.attr, sender=self.watcher)

    def test_callback_not_called_on_create_without_watch(self):
        ArticleFactory()
        # have not watched, thus callback should not be called
        self.assertFalse(self.callback.called)

    def test_callback_called_on_create_with_watch(self):
        self.watcher.watch()
        new_instance = ArticleFactory()
        # callback should be called with newly created instance
        self.callback.assert_called_once_with(
            obj=new_instance, attr=self.attr, sender=self.watcher)

    def test_callback_not_called_on_create_without_call_on_created(self):
        self.watcher.watch(call_on_created=False)
        ArticleFactory()
        # have not watched, thus callback should not be called
        self.assertFalse(self.callback.called)

    def test_callback_not_called_on_modification_with_non_interest_attr(self):
        new_instance = ArticleFactory()
        new_instance.content = 'modified'
        new_instance.save()
        # content is not watched thus callback should not be called
        self.assertFalse(self.callback.called)

    def test_callback_not_called_on_modification_without_watch(self):
        new_instance = ArticleFactory(hyperlinks=self.hyperlinks)
        hyperlink = new_instance.hyperlinks.get(pk=1)
        hyperlink.label = 'modified'
        hyperlink.save()
        # have not watched, thus callback should not be called
        self.assertFalse(self.callback.called)

    def test_callback_called_on_modification_with_watch(self):
        new_instance = ArticleFactory(hyperlinks=self.hyperlinks)
        self.watcher.watch()
        hyperlink = new_instance.hyperlinks.get(pk=1)
        hyperlink.label = 'modified'
        hyperlink.save()
        # callback should be called with instance modification
        self.callback.assert_called_once_with(
            obj=new_instance, attr=self.attr, sender=self.watcher)


# ============================================================================
# GenericRelatedWatcher
# ============================================================================
class ObserverWatchersGenericRelatedWatcherTestCase(TestCase):
    def setUp(self):
        self.tags = (
            TagFactory(),
            TagFactory(),
            TagFactory(),
            TagFactory(),
            TagFactory(),
        )
        self.model = Article
        self.attr = 'tags'
        self.callback = MagicMock()
        self.watcher = GenericRelatedWatcher(self.model,
                                             self.attr,
                                             self.callback)
        self.addCleanup(self.watcher.unwatch)

    def test_callback_not_called_on_add_without_watch(self):
        new_instance = ArticleFactory(tags=self.tags)
        new_instance.tags.add(TagFactory())
        # have not watched, thus callback should not be called
        self.assertFalse(self.callback.called)

    def test_callback_called_on_add_with_watch(self):
        new_instance = ArticleFactory(tags=self.tags)
        self.watcher.watch()
        new_instance.tags.add(TagFactory())
        # callback should be called with instance modification
        self.callback.assert_called_once_with(
            obj=new_instance, attr=self.attr, sender=self.watcher)

    def test_callback_not_called_on_remove_without_watch(self):
        new_instance = ArticleFactory(tags=self.tags)
        new_instance.tags.remove(self.tags[0])
        # have not watched, thus callback should not be called
        self.assertFalse(self.callback.called)

    @skip("TODO: Fixme")
    def test_callback_called_on_remove_with_watch(self):
        new_instance = ArticleFactory(tags=self.tags)
        self.watcher.watch()
        new_instance.tags.remove(self.tags[0])
        self.assertFalse(self.tags in new_instance.tags.all())
        new_instance.save()
        # callback should be called with instance modification
        self.callback.assert_called_once_with(
            obj=new_instance, attr=self.attr, sender=self.watcher)

    def test_callback_not_called_on_reverse_add_without_watch(self):
        new_instance = TagFactory()
        add_instance = ArticleFactory()
        new_instance.content_object = add_instance
        new_instance.save()
        # have not watched, thus callback should not be called
        self.assertFalse(self.callback.called)

    def test_callback_called_on_reverse_add_with_watch(self):
        new_instance = TagFactory()
        add_instance = ArticleFactory()
        self.watcher.watch()
        new_instance.content_object = add_instance
        new_instance.save()
        # callback should be called with instance modification
        self.callback.assert_called_once_with(
            obj=add_instance, attr=self.attr, sender=self.watcher)

    def test_callback_not_called_on_reverse_remove_without_watch(self):
        ArticleFactory(tags=self.tags)
        self.tags[0].article = None
        self.tags[0].save()
        # have not watched, thus callback should not be called
        self.assertFalse(self.callback.called)

    @skip("TODO: Fixme")
    def test_callback_called_on_reverse_remove_with_watch(self):
        new_instance = ArticleFactory(tags=self.tags)
        self.watcher.watch()
        self.tags[0].article = None
        self.tags[0].save()
        # callback should be called with instance modification
        self.callback.assert_called_once_with(
            obj=new_instance, attr=self.attr, sender=self.watcher)

    def test_callback_not_called_on_create_without_watch(self):
        ArticleFactory()
        # have not watched, thus callback should not be called
        self.assertFalse(self.callback.called)

    def test_callback_called_on_create_with_watch(self):
        self.watcher.watch()
        new_instance = ArticleFactory()
        # callback should be called with newly created instance
        self.callback.assert_called_once_with(
            obj=new_instance, attr=self.attr, sender=self.watcher)

    def test_callback_not_called_on_create_without_call_on_created(self):
        self.watcher.watch(call_on_created=False)
        ArticleFactory()
        # have not watched, thus callback should not be called
        self.assertFalse(self.callback.called)

    def test_callback_not_called_on_modification_with_non_interest_attr(self):
        new_instance = ArticleFactory()
        new_instance.content = 'modified'
        new_instance.save()
        # content is not watched thus callback should not be called
        self.assertFalse(self.callback.called)

    def test_callback_not_called_on_modification_without_watch(self):
        new_instance = ArticleFactory(tags=self.tags)
        tag = new_instance.tags.get(pk=1)
        tag.label = 'modified'
        tag.save()
        # have not watched, thus callback should not be called
        self.assertFalse(self.callback.called)

    def test_callback_called_on_modification_with_watch(self):
        new_instance = ArticleFactory(tags=self.tags)
        self.watcher.watch()
        tag = new_instance.tags.get(pk=1)
        tag.label = 'modified'
        tag.save()
        # callback should be called with instance modification
        self.callback.assert_called_once_with(
            obj=new_instance, attr=self.attr, sender=self.watcher)


class ObserverWatchersGenericRelatedWatcherTestCaseRev(TestCase):
    def setUp(self):
        self.model = Tag
        self.attr = 'content_object'
        self.callback = MagicMock()
        self.watcher = GenericRelatedWatcher(self.model,
                                             self.attr,
                                             self.callback)
        self.addCleanup(self.watcher.unwatch)

    def test_callback_not_called_on_create_without_watch(self):
        TagFactory()
        # have not watched, thus callback should not be called
        self.assertFalse(self.callback.called)

    def test_callback_called_on_create_with_watch(self):
        self.watcher.watch()
        new_instance = TagFactory()
        # callback should be called with newly created instance
        self.callback.assert_called_once_with(
            obj=new_instance, attr=self.attr, sender=self.watcher)

    def test_callback_not_called_on_create_without_call_on_created(self):
        self.watcher.watch(call_on_created=False)
        TagFactory()
        # have not watched, thus callback should not be called
        self.assertFalse(self.callback.called)

    def test_callback_not_called_on_modification_without_watch(self):
        new_instance = TagFactory()
        new_instance.content_object = ArticleFactory()
        new_instance.save()
        # have not watched, thus callback should not be called
        self.assertFalse(self.callback.called)

    @skip("TODO: Fix me")
    def test_callback_called_on_modification_with_watch(self):
        new_instance = TagFactory()
        self.watcher.watch()
        new_instance.content_object = ArticleFactory()
        new_instance.save()
        # callback should be called with instance modification
        self.callback.assert_called_once_with(
            obj=new_instance, attr=self.attr, sender=self.watcher)

    def test_callback_not_called_on_modification_with_non_interest_attr(self):
        new_instance = TagFactory()
        new_instance.label = 'modified'
        new_instance.save()
        # content is not watched thus callback should not be called
        self.assertFalse(self.callback.called)

    def test_callback_not_called_on_related_modification_without_watch(self):
        new_instance = TagFactory(content_object=UserFactory())
        user = new_instance.content_object
        user.label = 'modified'
        user.save()
        # have not watched, thus callback should not be called
        self.assertFalse(self.callback.called)

    @skip("TODO: Fix me")
    def test_callback_called_on_related_modification_with_watch(self):
        new_instance = TagFactory(content_object=UserFactory())
        user = new_instance.content_object
        user.label = 'modified'
        user.save()
        # callback should be called with instance modification
        self.callback.assert_called_once_with(
            obj=new_instance, attr=self.attr, sender=self.watcher)
