from django.urls import path
from .views import CommentViewSet

urlpatterns = [
    path(
        'comments/<int:pk>/',
        CommentViewSet.as_view({
            'get': 'retrieve',
            'put': 'update',
            'patch': 'partial_update',
            'delete': 'destroy',
            # /POST/ method was moved to blog endpoints, see blog.urls
        },
        name='comment-detail')    
    ),
]