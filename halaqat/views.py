from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Halaqa
from .forms import HalaqaForm
# Create your views here.


# Security check: only allow admins
def is_admin(user):
    return user.is_authenticated and user.role == 'admin'

# 1. LIST ALL HALAQAT
@login_required
@user_passes_test(is_admin, login_url='accounts:login')
def halaqa_list(request):
    # Fetch all circles and optimize query performance
    halaqas = Halaqa.objects.all().select_related('teacher')
    return render(request, 'halaqat/halaqa_list.html', {'halaqas': halaqas})

# 2. CREATE NEW HALAQA
@login_required
@user_passes_test(is_admin, login_url='accounts:login')
def halaqa_create(request):
    if request.method == 'POST':
        form = HalaqaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "New Halaqa created successfully!")
            return redirect('halaqat:halaqa_list')
    else:
        form = HalaqaForm()
    return render(request, 'halaqat/halaqa_form.html', {'form': form, 'title': 'Create New Halaqa'})

# 3. EDIT HALAQA
@login_required
@user_passes_test(is_admin, login_url='accounts:login')
def halaqa_edit(request, pk):
    halaqa = get_object_or_404(Halaqa, pk=pk)
    if request.method == 'POST':
        form = HalaqaForm(request.POST, instance=halaqa)
        if form.is_valid():
            form.save()
            messages.success(request, f"{halaqa.name} updated successfully!")
            return redirect('halaqat:halaqa_list')
    else:
        form = HalaqaForm(instance=halaqa)
    return render(request, 'halaqat/halaqa_form.html', {'form': form, 'title': f'Edit Halaqa: {halaqa.name}'})

# 4. DELETE HALAQA
@login_required
@user_passes_test(is_admin, login_url='accounts:login')
def halaqa_delete(request, pk):
    halaqa = get_object_or_404(Halaqa, pk=pk)
    if request.method == 'POST':
        halaqa.delete()
        messages.success(request, "Halaqa deleted successfully!")
        return redirect('halaqat:halaqa_list')
    return render(request, 'halaqat/halaqa_confirm_delete.html', {'halaqa': halaqa})