from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model for Smart Order system.
    Can act as normal user or admin.
    """
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return self.username
