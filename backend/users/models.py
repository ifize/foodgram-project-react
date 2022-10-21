from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    email = models.EmailField(
        blank=False,
        max_length=254,
        unique=True
    )

    class Meta:
        ordering = ['-id']
