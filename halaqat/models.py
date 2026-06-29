
from django.db import models
from accounts.models import CustomUser

class Halaqa(models.Model):

    name = models.CharField(max_length=100)

    teacher = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'teacher'},
        related_name='halaqat'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name