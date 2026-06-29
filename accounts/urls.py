from django.urls import path
from . import views

# We use an app_name to clean up reverse routing (e.g., 'accounts:login')
app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('redirect-dashboard/', views.dashboard_redirect_view, name='dashboard_redirect'),

    # Day 8 Teacher Management URLs
    path('teachers/', views.teacher_list, name='teacher_list'),
    path('teachers/new/', views.teacher_create, name='teacher_create'),
    path('teachers/<int:pk>/edit/', views.teacher_edit, name='teacher_edit'),
    path('teachers/<int:pk>/delete/', views.teacher_delete, name='teacher_delete'),
]