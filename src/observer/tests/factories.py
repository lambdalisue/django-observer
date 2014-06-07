import factory
from observer.tests.models import Article
from observer.tests.models import User, Supplement
from observer.tests.models import Revision, Project, Hyperlink, Tag


class SupplementFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Supplement
    label = factory.Sequence(lambda n: 'label%s' % n)


class UserFactory(factory.DjangoModelFactory):
    FACTORY_FOR = User
    label = factory.Sequence(lambda n: 'john%s' % n)


class RevisionFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Revision
    label = factory.Sequence(lambda n: 'label%s' % n)


class ProjectFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Project
    label = factory.Sequence(lambda n: 'label%s' % n)


class HyperlinkFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Hyperlink
    label = factory.Sequence(lambda n: 'label%s' % n)


class TagFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Tag
    label = factory.Sequence(lambda n: 'label%s' % n)


class ArticleFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Article

    title = factory.Sequence(lambda n: 'title%s' % n)
    content = 'This is an article content'
    supplement = factory.SubFactory(SupplementFactory)
    author = factory.SubFactory(UserFactory)
    revision = factory.RelatedFactory(RevisionFactory, 'article')

    @factory.post_generation
    def collaborators(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for collaborator in extracted:
                self.collaborators.add(collaborator)

    @factory.post_generation
    def projects(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for project in extracted:
                self.projects.add(project)

    @factory.post_generation
    def hyperlinks(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for hyperlink in extracted:
                self.hyperlinks.add(hyperlink)

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for tag in extracted:
                self.tags.add(tag)
