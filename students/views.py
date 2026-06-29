
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth import get_user_model
from halaqat.models import Halaqa
from .forms import  StudentEditForm,StudentCreationForm
from .models import StudentProfile




@login_required
def student_detail_view(request, pk):
    # Fetch the exact student profile or return a 404 error if not found
    student = get_object_or_404(StudentProfile.objects.select_related('user', 'halaqa'), pk=pk)
    
    records = student.daily_records.all().select_related('teacher').order_by('-date')
    
    context = {
        'student': student,
        'records': records, # 🔑 Sending the real data to the HTML template
    }
    # Placeholder for daily progress records (to be populated in Day 15)
    # history_records = student.daily_records.all().order_by('-date')
    

    return render(request, 'students/student_detail.html', context)

#------------------------------
User = get_user_model()

def is_admin(user):
    """Gatekeeper rule matching our Day 8 logic"""
    return user.is_authenticated and (user.role == 'admin' or user.is_superuser)

@login_required
@user_passes_test(is_admin, login_url='accounts:login')
def student_list(request):
    # Only pull accounts that are students
    students = User.objects.filter(role='student')
    return render(request, 'students/student_list.html', {'students': students})

@login_required
@user_passes_test(is_admin, login_url='accounts:login')
def student_create(request):
    if request.method == 'POST':
        form = StudentCreationForm(request.POST)
        if form.is_valid():
            # Save user and create profile row
            student_user = form.save()
            
            # 🔑 Grab the selected Halaqa ID from the dropdown menu
            halaqa_id = request.POST.get('assigned_halaqa')
            # Find the student's profile and save the Halaqa relation
            profile, created = StudentProfile.objects.get_or_create(user=student_user)
            if halaqa_id:
                profile.halaqa = Halaqa.objects.get(id=halaqa_id)
            else:
                profile.halaqa = None  # Handle explicit unassigned choice
            profile.save()

            messages.success(request, "Student and Profile created successfully!")
            return redirect('students:student_list')
    else:
        form = StudentCreationForm()

    halaqas = Halaqa.objects.all()
    return render(request, 'students/student_form.html', {
        'form': form,
        'title': 'Register New Student',
        'halaqas': halaqas
    })

@login_required
@user_passes_test(is_admin, login_url='accounts:login')
def student_edit(request, pk):
    # 1. We define 'student_user' right at the top. Now it exists for the WHOLE function.
    student_user = get_object_or_404(User, pk=pk, role='student')
    
    # 2. Get or create the profile linked to this user
    profile, created = StudentProfile.objects.get_or_create(user=student_user)

    if request.method == 'POST':
        # 3. Pass 'student_user' to the form
        form = StudentEditForm(request.POST, instance=student_user)
        if form.is_valid():
            form.save()

            # Capture the changed dropdown menu option
            halaqa_id = request.POST.get('assigned_halaqa')
            if halaqa_id:
                profile.halaqa = Halaqa.objects.get(id=halaqa_id)
            else:
                profile.halaqa = None
            profile.save()

            messages.success(request, f"Profile for {student_user.username} updated successfully!")
            return redirect('students:student_list')
    else:
        # 4. If it's a GET request, we also use 'student_user' here
        form = StudentEditForm(instance=student_user)

    # 5. Passing it to the template engine
    halaqas = Halaqa.objects.all()
    return render(request, 'students/student_form.html', {
        'form': form,
        'title': f'Edit Student: {student_user.username}', 
        'halaqas': halaqas,
        'current_halaqa': profile.halaqa
    })

@login_required
@user_passes_test(is_admin, login_url='accounts:login')
def student_delete(request, pk):
    student = get_object_or_404(User, pk=pk, role='student')
    if request.method == 'POST':
        student.delete()
        messages.success(request, "Student profile permanently removed.")
        return redirect('students:student_list')
    return render(request, 'students/student_confirm_delete.html', {'student': student})