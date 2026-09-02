from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True)

    # login with email
    # USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username