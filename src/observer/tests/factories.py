import factory
from observer.tests.compat import make_password
from observer.tests.compat import auth_user_model
from observer.tests.models import ObserverTestArticle as Article
from observer.tests.models import ObserverTestLabel as Label


class UserFactory(factory.DjangoModelFactory):
    FACTORY_FOR = auth_user_model
    FACTORY_DJANGO_GET_OR_CREATE = ('username',)

    last_name = 'john'
    first_name = 'titer'
    username = factory.Sequence(lambda n: 'john%s' % n)
    password = make_password('password')
    email = factory.LazyAttribute(lambda o: '%s.%s@example.com' % (
        o.last_name, o.first_name))


class ArticleFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Article

    title = factory.Sequence(lambda n: 'title%s' % n)
    content = 'This is an article content'
    author = factory.SubFactory(UserFactory)

    @factory.post_generation
    def collaborators(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for collaborator in extracted:
                self.collaborators.add(collaborator)


class LabelFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Label

    label = factory.Sequence(lambda n: 'label%s' % n)
    content_object = factory.SubFactory(ArticleFactory)
