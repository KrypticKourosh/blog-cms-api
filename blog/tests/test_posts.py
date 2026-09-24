# type: ignore
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from users.tests.factories import UserFactory
from .factories import PostFactory
from blog.models import Post

@pytest.mark.django_db
class TestPostPermissions:

    def setup_method(self):
        self.client = APIClient() # anonymous user by default
        self.author = UserFactory()
        self.other_user = UserFactory() # not author
        self.published_post = PostFactory(author=self.author, status=Post.Status.PUBLISHED)
        self.draft_post = PostFactory(author=self.author, status=Post.Status.DRAFT)

    def test_anonymous_can_list_only_published_posts(self):
        url = reverse('post-list')
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        slugs = [post['slug'] for post in response.data['results']] 
        assert self.published_post.slug in slugs
        assert self.draft_post.slug not in slugs

    def test_author_can_see_own_draft(self):
        self.client.force_authenticate(user=self.author)
        url = reverse('post-list')
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        slugs = [post['slug'] for post in response.data['results']]
        assert self.draft_post.slug in slugs

    def test_other_user_cannot_see_draft_post_list(self):
        self.client.force_authenticate(user=self.other_user)
        url = reverse('post-list')
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK 
        slugs = [post['slug'] for post in response.data['results']]
        assert self.draft_post.slug not in slugs

    def test_other_user_cannot_see_draft_post_detail(self):
        self.client.force_authenticate(user=self.other_user)
        url = reverse('post-detail', kwargs={'slug': self.draft_post.slug})
        response = self.client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_only_author_can_update_post(self):
        self.client.force_authenticate(user=self.other_user)
        url = reverse('post-detail', kwargs={'slug': self.published_post.slug})
        response = self.client.patch(url, {'title': 'Illegal title'}) # or put method
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_author_can_update_own_post(self):
        self.client.force_authenticate(user=self.author)
        url = reverse('post-detail', kwargs={'slug': self.published_post.slug})
        response = self.client.patch(url, {'title': 'Updated title'}) # or put method
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Updated title'

    def test_view_count_increase_on_retrieve(self):
        url = reverse('post-detail', kwargs={'slug': self.published_post.slug})

        # first call
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['views_count'] == 1

        # second call
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['views_count'] == 2

    def test_author_can_publish_draft(self):
        self.client.force_authenticate(user=self.author)
        url = reverse('post-publish', kwargs={'slug': self.draft_post.slug})
        response = self.client.post(url)
        assert response.status_code == status.HTTP_200_OK
        self.draft_post.refresh_from_db()
        assert self.draft_post.status == Post.Status.PUBLISHED
        assert self.draft_post.published_at is not None

    def test_other_user_cannot_publish_draft(self):
        self.client.force_authenticate(user=self.other_user)
        url = reverse('post-publish', kwargs={'slug': self.draft_post.slug})
        response = self.client.post(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND