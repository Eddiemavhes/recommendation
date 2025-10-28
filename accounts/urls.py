from django.urls import path
from . import views
from . import auth_views

urlpatterns = [
    path('login/', auth_views.login_view, name='login'),
    path('logout/', auth_views.logout_view, name='logout'),
    path('register/', auth_views.register_view, name='register'),
    path('profile/', views.profile, name='profile'),
    path('password/change/', auth_views.password_change_view, name='password_change'),
]