from django.urls import path
from . import views

app_name = 'records'

urlpatterns = [
    path('entry/<int:student_id>/', views.record_entry_view, name='record_entry'),

    path('api/analytics/student/<int:student_id>/', views.student_analytics_data_view, name='student_analytics_api'),
    path('api/analytics/center-trends/', views.admin_center_analytics_view, name='admin_center_analytics_api'),


]
