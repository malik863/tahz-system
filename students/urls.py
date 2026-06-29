# students/urls.py
from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('', views.student_list, name='student_list'),
    path('new/', views.student_create, name='student_create'),
    path('<int:pk>/edit/', views.student_edit, name='student_edit'),
    path('<int:pk>/delete/', views.student_delete, name='student_delete'),
    
    path('profile/<int:pk>/', views.student_detail_view, name='student_detail'),


]