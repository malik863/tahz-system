from django import forms
from .models import Halaqa

class HalaqaForm(forms.ModelForm):
    class Meta:
        model = Halaqa
        fields = ['name', 'teacher']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Imam Nafie Circle'}),
            'teacher': forms.Select(attrs={'class': 'form-control'}),
        }