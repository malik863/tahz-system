from django.db import models
#from accounts.models import CustomUser
#from halaqat.models import Halaqa
from datetime import date
from django.conf import settings
# Use settings.AUTH_USER_MODEL when linking your ForeignKeys!


WARD_TARGET_CHOICES = [
    ('half_page', 'نصف صفحة'),
    ('one_page', 'صفحة كاملة'),
    ('two_pages', 'صفحتان'),
    ('quarter_juz', 'ربع حزب'),
    ('half_juz', 'نصف حزب'),
    ('juz', 'جزء كامل'),
]

class StudentProfile(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,  # 🔑 Only keep this reference!
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'}
    )

    # 🔑 By wrapping 'halaqat.Halaqa' in quotes, Django lazy-loads it.
    # This prevents your apps from locking up during startup!
    halaqa = models.ForeignKey(
        'halaqat.Halaqa',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students'
    )

    date_of_birth = models.DateField(null=True, blank=True)
    parent_phone = models.CharField(max_length=15, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    memorization_target = models.CharField(
        max_length=20,
        choices=WARD_TARGET_CHOICES,
        default='one_page',
        verbose_name="ورد الحفظ الثابت"
    )
    revision_target = models.CharField(
        max_length=20,
        choices=WARD_TARGET_CHOICES,
        default='one_page',
        verbose_name="ورد المراجعة الثابت"
    )

    @property
    def age(self):
        if not self.date_of_birth:
            return None
        
        today = date.today()
        calculated_age = today.year - self.date_of_birth.year
        
        has_birthday_passed = (today.month, today.day) >= (self.date_of_birth.month, self.date_of_birth.day)
        if not has_birthday_passed:
            calculated_age -= 1
            
        return calculated_age

    def __str__(self):
        return self.user.username
    

#------------------------
