from rest_framework import viewsets, permissions, status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q, F

from .models import (
    Category, Tag, Post, Like
)
from .serializers import (
    CategorySerializer, TagSerializer,
    PostListSerializer, PostDetailSerializer
)
from .permissions import IsAuthorOrReadOnly

class PostViewSet(viewsets.ModelViewSet):
    """
    Full CRUD for blog posts.
    - List / Retrieve: public (published posts)
    - Create: authenticated users
    - Update / Delete: only the author
    """
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrReadOnly
    ]
    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]
    filterset_fields = [
        'status',
        'category',
        'author',
        'tags',
    ]
    search_fields = [
        'title',
        'content',
        'summary',
        'author',
    ]
    ordering_fields = [
        'views_count',
        'likes_count',
    ]
    ordering = ['-created_at']
    lookup_field = 'slug' # use slug instead of IDs in the url

    def get_queryset(self):
        '''
        Different user types (staff, authenticated, anonymous)
        see different posts lists.
        '''
        user = self.request.user
        base_query = Post.objects.select_related(
            'author', 'category'
        ).prefetch_related('tags') # faster queries

        # Staff can see everything
        if user.is_staff:
            return base_query

        # Logged-in users can see all the published posts + their own drafts
        if user.is_authenticated:
            return base_query.filter(
                Q(status=Post.Status.PUBLISHED) | Q(author=user)
            )

        # Anonymous users can only see the published posts
        return base_query.filter(status=Post.Status.PUBLISHED)

    def get_serializer_class(self):
        '''Different serializers for different requests'''
        if self.action == 'list':
            return PostListSerializer
        return PostDetailSerializer

    def perform_create(self, serializer):
        '''Set the author automatically'''
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        '''Set `published_at=True` if the Post.status is 
        changed to PUBLISHED for the "first" time.'''
        instance = serializer.save()

        # if the user has changed the status to PUBLISHED (and it was not published before)
        if instance.published_at is None and instance.status == Post.Status.PUBLISHED:
            instance.published_at = timezone.now()
            instance.save(updated_fields=['published_at'])

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def publish(self, request):
        '''Publish a draft post'''
        post = self.get_object()
        if post.author != request.user and not request.user.is_staff:
            return Response(
                {'detail': 'You don\'t have permission to publish this post.'},
                status=status.HTTP_403_FORBIDDEN
            )
        post.status = Post.Status.PUBLISHED
        if not post.published_at: # post might have been published before
            post.published_at = timezone.now()
        post.save()

        # return the updated post
        serializer = self.get_serializer(post)
        return Response({
            'serializer.data': serializer.data,
            'serializer': serializer,
            'serializer_class': self.get_serializer_class(),
        })

    def retrieve(self, request, *args, **kwargs):
        '''Increment the post's `views_count`'''
        instance = self.get_object()

        # Increment views_count
        Post.objects.filter(pk=instance.pk).update(views_count=F('views_count') + 1)
        instance.refresh_from_db()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def like(self, request, slug=None):
        post = self.get_object()
        like, created = Like.objects.get_or_create(user=request.user, post=post)

        if created:
            Post.objects.filter(pk=post.pk).update(likes_count=F('likes_count') + 1)
            return Response({'status': 'liked'}, status=status.HTTP_201_CREATED)

        return Response({'status': 'already liked'}, status=status.HTTP_200_OK)
    
    @action(
        detail=True,
        methods=['post'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def unlike(self, request, slug=None):
        post = self.get_object()
        deleted, _ = Like.objects.filter(user=request.user, post=post).delete()

        if deleted:
            Post.objects.filter(pk=post.pk).update(likes_count=F('likes_count') - 1)
            return Response({'status': 'unliked'}, status=status.HTTP_200_OK)

        return Response({'status': 'not liked'}, status=status.HTTP_200_OK)

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    search_fields = ['name', 'description']

class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    lookup_field = 'slug'
    search_fields = ['name']
