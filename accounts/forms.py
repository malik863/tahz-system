
# accounts/forms.py
from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class TeacherCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), help_text="Set a secure initial password.")
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'teacher'  # Automatically force the role to teacher
        user.set_password(self.cleaned_data["password"])  # Hash password safely
        if commit:
            user.save()
        return user

class TeacherEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'is_active']