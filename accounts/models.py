from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

class User(AbstractUser):
    """ Custom user setup using email instead of username """
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    # Still require username field
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email
