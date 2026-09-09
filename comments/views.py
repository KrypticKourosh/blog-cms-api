from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .serializers import CommentSerializer, CommentUpdateSerializer
from .permissions import IsCommentAuthorOrReadOnly
from .models import Comment

class CommentViewSet(viewsets.ModelViewSet):
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        IsCommentAuthorOrReadOnly
    ]

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return CommentUpdateSerializer
        return CommentSerializer

    def get_queryset(self):
        '''
        Staff can see all the comments (Even inactive ones).
        
        Authenticated + Anonymous users can only see active comments.
        '''
        # staff access
        if self.request.user.is_staff:
            return Comment.objects.select_related(
            'post', 'author', 'parent'
        ).prefetch_related('replies')

        # non-staff access
        return Comment.objects.filter(is_active=True).select_related(
            'post', 'author', 'parent'
        ).prefetch_related('replies')

    def perform_create(self, serializer):
        '''Automatically set the author'''
        serializer.save(author=self.request.user)