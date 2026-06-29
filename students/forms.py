# students/forms.py
from django import forms
from django.contrib.auth import get_user_model
from halaqat.models import Halaqa
from .models import StudentProfile

User = get_user_model()

# students/forms.py

# 🔑 Make sure this creation block is still at the top of the file!
class StudentCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), required=True)
    
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    parent_phone = forms.CharField(required=False, max_length=15)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.role = 'student'
        if commit:
            user.save()
            StudentProfile.objects.update_or_create(
                user=user,
                defaults={
                    'date_of_birth': self.cleaned_data.get('date_of_birth'),
                    'parent_phone': self.cleaned_data.get('parent_phone'),
                }
            )
        return user


# 🔑 Make sure the new choices and edit form are stacked right below it!
WARD_TARGET_CHOICES = [
    ('half_page', 'نصف صفحة'),
    ('one_page', 'صفحة كاملة'),
    ('two_pages', 'صفحتان'),
    ('quarter_juz', 'ربع حزب'),
    ('half_juz', 'نصف حزب'),
    ('juz', 'جزء كامل'),
]

class StudentEditForm(forms.ModelForm):
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    parent_phone = forms.CharField(
        required=False, 
        max_length=15, 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    halaqa = forms.ModelChoiceField(
        queryset=Halaqa.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="الحلقة"
    )
    memorization_target = forms.ChoiceField(
        choices=WARD_TARGET_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="ورد الحفظ الثابت"
    )
    revision_target = forms.ChoiceField(
        choices=WARD_TARGET_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="ورد المراجعة الثابت"
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'is_active']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'studentprofile'):
            profile = self.instance.studentprofile
            self.fields['date_of_birth'].initial = profile.date_of_birth
            self.fields['parent_phone'].initial = profile.parent_phone
            self.fields['halaqa'].initial = profile.halaqa
            self.fields['memorization_target'].initial = profile.memorization_target
            self.fields['revision_target'].initial = profile.revision_target

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            StudentProfile.objects.update_or_create(
                user=user,
                defaults={
                    'date_of_birth': self.cleaned_data.get('date_of_birth'),
                    'parent_phone': self.cleaned_data.get('parent_phone'),
                    'halaqa': self.cleaned_data.get('halaqa'),
                    'memorization_target': self.cleaned_data.get('memorization_target'),
                    'revision_target': self.cleaned_data.get('revision_target'),
                }
            )
        return user