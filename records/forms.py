from django import forms
from .models import DailyRecord

class DailyRecordForm(forms.ModelForm):
    class Meta:
        model = DailyRecord
        fields = [
            'attendance', 
            'memorization_surah', 'memorization_status', 'memorization_grade',
            'revision_surah', 'revision_status', 'revision_grade',
            'behavior_grade', 'notes'
        ]
        widgets = {
            # 🛑 حقل الحضور كأزرار اختيار دائرية (Radio Buttons) مصممة أفقياً بجانب بعضها
            'attendance': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            
            # 📖 حقول الحفظ الجديد
            'memorization_surah': forms.Select(attrs={'class': 'form-select'}),
            'memorization_status': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'memorization_grade': forms.Select(attrs={'class': 'form-select'}),
            
            # 🔄 حقول المراجعة اليومية
            'revision_surah': forms.Select(attrs={'class': 'form-select'}),
            'revision_status': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'revision_grade': forms.Select(attrs={'class': 'form-select'}),
            
            # 🧠 السلوك والملاحظات
            'behavior_grade': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'اكتب أي ملاحظات تخص قراءة الطالب أو سلوكه اليوم هنا...'}),
        }