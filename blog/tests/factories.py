import factory
from django.utils import timezone

from comments.models import Comment
from blog.models import Post, Category, Tag, Like
from users.tests.factories import UserFactory

class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.declarations.Sequence(lambda n: f'Category {n}')

class TagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tag

    name = factory.declarations.Sequence(lambda n: f'Tag {n}')

class PostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Post

    title = factory.declarations.Sequence(lambda n: f'Test Post {n}')
    content = factory.faker.Faker('paragraph')
    summary = factory.faker.Faker('sentence')
    author = factory.declarations.SubFactory(UserFactory)
    status = Post.Status.PUBLISHED
    published_at = factory.declarations.LazyFunction(timezone.now)

class LikeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Like

    user = factory.declarations.SubFactory(UserFactory)
    post = factory.declarations.SubFactory(PostFactory)