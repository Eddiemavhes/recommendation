from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=100, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    years_of_experience = models.IntegerField(default=0)
    preferred_categories = models.JSONField(default=list, blank=True)
    work_preference = models.CharField(
        max_length=20,
        choices=[('remote', 'Remote'), ('hybrid', 'Hybrid'), ('onsite', 'Onsite')],
        default='hybrid'
    )
    salary_expectations = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s profile"
