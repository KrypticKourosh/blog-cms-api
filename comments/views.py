from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.filters import OrderingFilter
from .serializers import CommentSerializer, CommentUpdateSerializer
from .permissions import IsCommentAuthorOrReadOnly
from .models import Comment
from blog.models import Post

class CommentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly, IsCommentAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["post", "author", "parent"]
    ordering_fields = ["created_at"]
    ordering = ["created_at"]

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return CommentUpdateSerializer
        return CommentSerializer

    def get_queryset(self):
        '''
        Staff can see all the comments (Even inactive ones).
        
        Authenticated + Anonymous users can only see active comments.
        '''
        base_query = Comment.objects.select_related(
            'post', 'author', 'parent'
        ).prefetch_related('replies')

        # staff access
        if self.request.user.is_staff:
            return base_query

        # non-staff access
        return base_query.filter(is_active=True)

    def perform_create(self, serializer):
        '''Automatically set the author + '''
        post_slug = self.kwargs.get('post_slug')
        if not post_slug:
            raise ValidationError({
                'detail': 'Comment must be created under a post.'
            })

        post = get_object_or_404(Post, slug=post_slug)

        if post.status != Post.Status.PUBLISHED and not self.request.user.is_staff:
            raise ValidationError({
                'detail': 'You can only comment on published posts.'
            })
        
        serializer.save(author=self.request.user, post=post)