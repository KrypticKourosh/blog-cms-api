# type: ignore
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from users.tests.factories import UserFactory
from .factories import PostFactory, LikeFactory
from blog.models import Post, Like

@pytest.mark.django_db
class TestLikes:

    def setup_method(self):
        self.user = UserFactory()
        self.client = APIClient()
        self.post = PostFactory(status=Post.Status.PUBLISHED)

    def test_user_can_like_post(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('post-like', kwargs={'slug': self.post.slug})
        response = self.client.post(url)
        assert response.status_code == status.HTTP_201_CREATED
        self.post.refresh_from_db()
        assert self.post.likes_count == 1

    def test_user_cannont_like_post_twice(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('post-like', kwargs={'slug': self.post.slug})
        self.client.post(url) # first like
        response = self.client.post(url) # second like
        assert response.status_code == status.HTTP_200_OK
        self.post.refresh_from_db()
        assert self.post.likes_count == 1 # still one

    def test_user_can_unlike_post(self):
        LikeFactory(user=self.user, post=self.post)
        self.post.likes_count = 1
        self.post.save()
        self.client.force_authenticate(user=self.user)
        url = reverse('post-unlike', kwargs={'slug': self.post.slug})
        response = self.client.post(url)
        assert response.status_code == status.HTTP_200_OK
        self.post.refresh_from_db()
        assert self.post.likes_count == 0
