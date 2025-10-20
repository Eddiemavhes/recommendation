from django.urls import path
from . import views

urlpatterns = [
    path('', views.application_list, name='applications'),
    path('create/<int:job_id>/', views.create_application, name='create_application'),
    path('update/<int:application_id>/', views.update_application, name='update_application'),
]