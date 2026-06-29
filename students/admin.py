from django.contrib import admin
from .models import StudentProfile

# Register your models here.
#admin.site.register(StudentProfile)


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'halaqa', 'age')
    list_filter = ('halaqa',)