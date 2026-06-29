
from django.urls import path
from . import views

app_name = 'halaqat'

urlpatterns = [
    path('', views.halaqa_list, name='halaqa_list'),
    path('create/', views.halaqa_create, name='halaqa_create'),
    path('edit/<int:pk>/', views.halaqa_edit, name='halaqa_edit'),
    path('delete/<int:pk>/', views.halaqa_delete, name='halaqa_delete'),
]