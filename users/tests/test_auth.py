# type: ignore
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .factories import UserFactory

@pytest.mark.django_db
class TestAuthentication:
    def setup_method(self):
        self.client = APIClient()

    def test_user_registration(self):
        url = reverse('register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'string1234',
            'password2': 'string1234',
        }
        response = self.client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert 'username' in response.data

    def test_user_login(self):
        user = UserFactory()
        url = reverse('token-obtain-pair')
        data = {
            'username': user.username,
            'password': 'string1234' # user.password is hashed
        }
        response = self.client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data 

    def test_authenticated_user_can_get_profile(self):
        user = UserFactory()
        self.client.force_authenticate(user=user)
        url = reverse('profile')
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == user.username
        assert response.data['email'] == user.email

    def test_anonymouse_user_cannot_get_profile(self):
        url = reverse('profile')
        response = self.client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        