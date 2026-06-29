from django.db import models
from django.contrib.auth.models import AbstractUser



class CustomUser(AbstractUser):

    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )

    phone_number = models.CharField(max_length=15, blank=True)

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES
    )


    def __str__(self):
        return self.username