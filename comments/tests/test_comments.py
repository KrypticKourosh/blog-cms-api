# type: ignore
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from users.tests.factories import UserFactory
from blog.tests.factories import PostFactory
from blog.models import Post
from comments.tests.factories import CommentFactory

@pytest.mark.django_db
class TestComments:

    def setup_method(self):
        self.client = APIClient()
        self.comment_author = UserFactory()
        self.other_user = UserFactory()
        self.post = PostFactory(status=Post.Status.PUBLISHED)
        self.other_post = PostFactory(status=Post.Status.PUBLISHED)
        self.comment = CommentFactory(author=self.comment_author, post=self.post)

    def test_anonymous_user_can_get_comment_by_id(self):
        url = reverse('comment-detail', kwargs={'pk': self.comment.pk})
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_anonymous_user_cannot_comment(self):
        url = reverse('post-comments', kwargs={'post_slug': self.post.slug})
        data = {
            'content': 'Comment by anonymous user'
        }
        response = self.client.post(url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED 

    def test_authenticated_user_can_comment(self):
        self.client.force_authenticate(user=self.comment_author)
        url = reverse('post-comments', kwargs={'post_slug': self.post.slug})
        data = {
            'content': 'Comment by authenticated user'
        }
        response = self.client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['content'] == 'Comment by authenticated user'
        
    def test_only_comment_author_can_delete_comment(self):
        self.client.force_authenticate(user=self.other_user)
        url = reverse('comment-detail', kwargs={'pk': self.comment.pk})
        response = self.client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_comment_author_can_delete_comment(self):
        self.client.force_authenticate(user=self.comment_author)
        url = reverse('comment-detail', kwargs={'pk': self.comment.pk})
        response = self.client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_cannot_reply_from_different_post(self):
        self.client.force_authenticate(user=self.other_user) # or user in general
        url = reverse('post-comments', kwargs={'post_slug': self.other_post.slug})
        data = {
            'content': 'Invalid reply',
            'parent': self.comment.id,
        }
        response = self.client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_can_reply_from_the_same_post(self):
        self.client.force_authenticate(user=self.other_user) # or user in general
        url = reverse('post-comments', kwargs={'post_slug': self.post.slug})
        data = {
            'content': 'valid reply',
            'parent': self.comment.id,
        }
        response = self.client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['content'] == 'valid reply'
        assert response.data['parent'] == self.comment.id