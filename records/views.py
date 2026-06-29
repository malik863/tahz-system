
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib import messages
from students.models import StudentProfile
from .forms import DailyRecordForm

from django.http import JsonResponse
from django.db.models import Count, Q
from django.db.models.functions import ExtractWeek, ExtractMonth
from .models import DailyRecord
from django.views.decorators.cache import never_cache

from django.contrib.auth import get_user_model


User = get_user_model()


# قفل أمان: السماح فقط للمشرفين أو الإداريين (Staff) بالوصول لهذه البيانات

@never_cache
@user_passes_test(lambda u: u.is_staff)
def admin_center_analytics_view(request):
    time_frame = request.GET.get('time_frame', 'monthly')
    all_records = DailyRecord.objects.all().order_by('date')
    
    labels = []
    active_student_counts = []
    
    # مصفوفات التتبع الزمني لكل حالة ورد
    yes_trends = []
    most_trends = []
    little_trends = []
    no_trends = []
    
    grouped_data = {}
    
    for r in all_records:
        if time_frame == 'weekly':
            period_key = f"الأسبوع {r.date.strftime('%U')}"
        else:
            month_names = {
                1: "يناير", 2: "فبراير", 3: "مارس", 4: "أبريل", 5: "مايو", 6: "يونيو",
                7: "يوليو", 8: "أغسطس", 9: "سبتمبر", 10: "أكتوبر", 11: "نوفمبر", 12: "ديسمبر"
            }
            period_key = month_names.get(r.date.month, f"شهر {r.date.month}")
            
        if period_key not in grouped_data:
            grouped_data[period_key] = {
                'students': set(),
                'yes': 0, 'most': 0, 'little': 0, 'no': 0
            }
            
        if r.attendance in ['present', 'late']:
            grouped_data[period_key]['students'].add(r.student_id)
            status = getattr(r, 'memorization_status', 'no')
            if status in ['yes', 'most', 'little', 'no']:
                grouped_data[period_key][status] += 1

    # بناء المصفوفات الزمنية المتزامنة مع الـ labels
    for period, counts in grouped_data.items():
        labels.append(period)
        active_student_counts.append(len(counts['students']))
        
        # إضافة القيم التاريخية خطوة بخطوة لرؤية الصعود والهبوط
        yes_trends.append(counts['yes'])
        most_trends.append(counts['most'])
        little_trends.append(counts['little'])
        no_trends.append(counts['no'])

    chart_payload = {
        'labels': labels,
        'trend_data': active_student_counts,
        # 🔑 حزم البيانات الزمنية الجديدة
        'yes_data': yes_trends,
        'most_data': most_trends,
        'little_data': little_trends,
        'no_data': no_trends,
    }
    
    return JsonResponse(chart_payload)

#------------------------------------
def convert_letter_to_score(letter):
    if not letter:
        return None
        
    # هنا قمنا بمطابقة الـ Keys النصية المخزنة في قاعدة بياناتك (A+, A, B, C, D)
    mapping = {
        'A+': 100,  # ممتاز
        'A': 85,    # جيد جداً
        'B': 75,    # جيد
        'C': 65,    # مقبول
        'D': 50,    # ضعيف
    }
    return mapping.get(str(letter).strip(), 0)

@login_required
def student_analytics_data_view(request, student_id):
    student = get_object_or_404(StudentProfile, id=student_id)
    time_frame = request.GET.get('time_frame', 'monthly')
    
    records = DailyRecord.objects.filter(student=student).order_by('date')
    
    labels = []
    attendance_rates = []
    behavior_averages = []
    memorization_averages = []
    
    grouped_data = {}
    pie_data_by_period = {}

    for r in records:
        if time_frame == 'weekly':
            period_key = f"الأسبوع {r.date.strftime('%U')}"
        else:
            month_names = {
                1: "يناير", 2: "فبراير", 3: "مارس", 4: "أبريل", 5: "مايو", 6: "يونيو",
                7: "يوليو", 8: "أغسطس", 9: "سبتمبر", 10: "أكتوبر", 11: "نوفمبر", 12: "ديسمبر"
            }
            period_key = month_names.get(r.date.month, f"شهر {r.date.month}")

        if period_key not in grouped_data:
            grouped_data[period_key] = {
                'total': 0, 'present': 0,
                'behavior_total': 0, 'behavior_count': 0,
                'memo_total': 0, 'memo_count': 0
            }
        
        if period_key not in pie_data_by_period:
            pie_data_by_period[period_key] = {'yes': 0, 'most': 0, 'little': 0, 'no': 0}

        grouped_data[period_key]['total'] += 1
        
        if r.attendance == 'present':
            grouped_data[period_key]['present'] += 1
            
            # 🔑 تحويل الدرجات الحرفية من الموديل الخاص بك إلى أرقام بشكل آمن
            b_score = convert_letter_to_score(r.behavior_grade)
            m_score = convert_letter_to_score(r.memorization_grade)

            if b_score is not None:
                grouped_data[period_key]['behavior_total'] += b_score
                grouped_data[period_key]['behavior_count'] += 1

            if m_score is not None:
                grouped_data[period_key]['memo_total'] += m_score
                grouped_data[period_key]['memo_count'] += 1
            
            status = r.memorization_status
            if status in pie_data_by_period[period_key]:
                pie_data_by_period[period_key][status] += 1

    # استخراج البيانات وحساب المعدلات بشكل سليم
    for period, counts in grouped_data.items():
        labels.append(period)
        
        # نسبة الحضور
        rate = (counts['present'] / counts['total']) * 100 if counts['total'] > 0 else 0
        attendance_rates.append(round(rate, 1))
        
        # معدل السلوك
        b_avg = (counts['behavior_total'] / counts['behavior_count']) if counts['behavior_count'] > 0 else 0
        behavior_averages.append(round(b_avg, 1))
        
        # معدل الحفظ
        m_avg = (counts['memo_total'] / counts['memo_count']) if counts['memo_count'] > 0 else 0
        memorization_averages.append(round(m_avg, 1))

    latest_period = labels[-1] if labels else None
    if latest_period and latest_period in pie_data_by_period:
        current_pie = pie_data_by_period[latest_period]
    else:
        current_pie = {'yes': 0, 'most': 0, 'little': 0, 'no': 0}

    chart_payload = {
        'labels': labels,
        'attendance_data': attendance_rates,
        'behavior_data': behavior_averages,
        'memorization_data': memorization_averages,
        'pie_labels': ['نعم', 'أغلبه', 'قليلاً منه', 'لا'],
        'pie_data': [current_pie['yes'], current_pie['most'], current_pie['little'], current_pie['no']]
    }

    return JsonResponse(chart_payload)
#-------------------
@login_required
def record_entry_view(request, student_id):
    # Ensure the student profile exists
    student = get_object_or_404(StudentProfile.objects.select_related('user', 'halaqa'), id=student_id)
    
    if request.method == 'POST':
        form = DailyRecordForm(request.POST)
        if form.is_valid():
            # Commit=False holds the record in memory before writing to the database
            daily_log = form.save(commit=False)
            daily_log.student = student
            daily_log.teacher = request.user  # Automatically link the active teacher
            
            try:
                daily_log.save()
                messages.success(request, f"تم تسجيل الورد اليومي بنجاح للطالب {student.user.get_full_name()}")
                return redirect('accounts:dashboard_redirect')
            except:
                # Triggers if unique_together constraint fails (i.e., double submission)
                messages.error(request, "تنبيه: تم تسجيل ورد هذا الطالب لهذا اليوم مسبقاً!")
    else:
        form = DailyRecordForm()
        
    context = {
        'student': student,
        'form': form
    }
    return render(request, 'records/record_entry.html', context)