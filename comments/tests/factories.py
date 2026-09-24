import factory
from comments.models import Comment
from blog.tests.factories import PostFactory
from users.tests.factories import UserFactory

class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Comment

    post = factory.declarations.SubFactory(PostFactory)
    author = factory.declarations.SubFactory(UserFactory)
    content = factory.faker.Faker('paragraph')