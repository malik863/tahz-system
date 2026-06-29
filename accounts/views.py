from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from halaqat.models import Halaqa  # Importing cleanly from your halaqat app
from .forms import TeacherCreationForm, TeacherEditForm
from django.contrib.auth.decorators import login_required, user_passes_test

from django.db.models import Count, Avg
from django.views.decorators.cache import never_cache


User = get_user_model()

@login_required
def dashboard_redirect_view(request):
    """
    Central dispatcher that checks the user's custom role 
    and sends them to their dedicated space with live analytics.
    """
    
    
    role = getattr(request.user, 'role', None)
    
    # 🏢 ROLE 1: ADMIN CONTROL DASHBOARD
    if role == 'admin' or request.user.is_superuser:
        from students.models import StudentProfile
        from django.db.models import Avg
        from datetime import date

        # 1. Fetch the average birth year directly from the database field
        avg_birth_year = StudentProfile.objects.aggregate(Avg('date_of_birth__year'))['date_of_birth__year__avg']
        
        # 2. Convert that average birth year into an actual age number
        if avg_birth_year:
            calculated_avg_age = round(date.today().year - avg_birth_year, 1)
        else:
            calculated_avg_age = 0
        # Gather live analytical statistics for our metrics display
        stats = {
            'total_students': StudentProfile.objects.count(),
            'total_teachers': User.objects.filter(role='teacher').count(),
            'total_halaqat': Halaqa.objects.count(),
            # Dynamically calculate the average age of all registered pupils
            'avg_age': calculated_avg_age }
        return render(request, 'accounts/admin_dashboard.html', {'stats': stats})
    
    # 🎓 ROLE 2: TEACHER WORKSPACE
    elif role == 'teacher':
        from django.utils.timezone import localdate
        from students.models import StudentProfile
        #from halaqat.models import Halaqa
        # Look up any circles assigned explicitly to this logged-in teacher account
        my_halaqa = Halaqa.objects.filter(teacher=request.user).first()
        my_students = None
        
        if my_halaqa:
            # Pull the list of students sitting in this specific teacher's circle
            my_students = StudentProfile.objects.filter(halaqa=my_halaqa)
            
        context = {
            'halaqa': my_halaqa,
            'students': my_students,
            'today': localdate(),
        }
        return render(request, 'accounts/teacher_dashboard.html', context)
    
    # 🛑 FALLBACK: If user role is unassigned or student
    logout(request)
    messages.error(request, "Access denied. Unknown role configuration.")
    return redirect('accounts:login')



#------------------------------


def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard_redirect')
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('accounts:dashboard_redirect')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
        
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('accounts:login')


# ==========================================
# 👨‍🏫 DAY 8: TEACHER CRUD VIEWS (ADMIN ONLY)
# ==========================================

User = get_user_model()

def is_admin(user):
    return user.is_authenticated and (user.role == 'admin' or user.is_superuser)

@login_required
@user_passes_test(is_admin, login_url='accounts:login')
def teacher_list(request):
    teachers = User.objects.filter(role='teacher')
    return render(request, 'accounts/teacher_list.html', {'teachers': teachers})

@login_required
@user_passes_test(is_admin, login_url='accounts:login')
def teacher_create(request):
    if request.method == 'POST':
        form = TeacherCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Teacher registered successfully!")
            return redirect('accounts:teacher_list')
    else:
        form = TeacherCreationForm()
    return render(request, 'accounts/teacher_form.html', {'form': form, 'title': 'Register New Teacher'})

@login_required
@user_passes_test(is_admin, login_url='accounts:login')
def teacher_edit(request, pk):
    teacher = get_object_or_404(User, pk=pk, role='teacher')
    if request.method == 'POST':
        form = TeacherEditForm(request.POST, instance=teacher)
        halaqa_id = request.POST.get('assigned_halaqa')
        
        if form.is_valid():
            form.save()
            
            # Reset old halaqas managed by this teacher using your 'halaqat' related_name
            teacher.halaqat.update(teacher=None)
            
            # Assign to the new Halaqa if selected
            if halaqa_id:
                halaqa = get_object_or_404(Halaqa, pk=halaqa_id)
                halaqa.teacher = teacher
                halaqa.save()
                
            messages.success(request, f"Teacher '{teacher.username}' profile updated successfully!")
            return redirect('accounts:teacher_list')
    else:
        form = TeacherEditForm(instance=teacher)
    
    halaqas = Halaqa.objects.all()
    current_halaqa = teacher.halaqat.first()
    
    return render(request, 'accounts/teacher_form.html', {
        'form': form, 
        'title': f"Edit Teacher: {teacher.username}",
        'halaqas': halaqas,
        'current_halaqa': current_halaqa,
        'is_edit': True
    })
@never_cache
@login_required
@user_passes_test(is_admin, login_url='accounts:login')
def teacher_delete(request, pk):
    teacher = get_object_or_404(User, pk=pk, role='teacher')
    if request.method == 'POST':
        teacher.delete()
        messages.success(request, "Teacher account permanently removed from system.")
        return redirect('accounts:teacher_list')
    return render(request, 'accounts/teacher_confirm_delete.html', {'teacher': teacher})