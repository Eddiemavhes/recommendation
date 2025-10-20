from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, UserProfile

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UserProfileForm(forms.ModelForm):
    # Define available job categories
    JOB_CATEGORIES = [
        ('IT Jobs', 'IT & Software Development'),
        ('Engineering Jobs', 'Engineering'),
        ('Healthcare & Nursing Jobs', 'Healthcare & Medical'),
        ('Finance Jobs', 'Finance & Banking'),
        ('Sales Jobs', 'Sales'),
        ('Marketing Jobs', 'Marketing'),
        ('Education Jobs', 'Education & Teaching'),
        ('HR Jobs', 'Human Resources'),
        ('Admin Jobs', 'Administrative'),
        ('Legal Jobs', 'Legal'),
        ('Creative Jobs', 'Creative & Design'),
        ('Science Jobs', 'Science & Research'),
        ('Manufacturing Jobs', 'Manufacturing'),
        ('Retail Jobs', 'Retail'),
        ('Construction Jobs', 'Construction'),
    ]

    preferred_categories = forms.MultipleChoiceField(
        choices=JOB_CATEGORIES,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-checkbox h-4 w-4 text-blue-600'
        }),
        required=False
    )

    class Meta:
        model = UserProfile
        fields = [
            'phone', 'location', 'job_title', 'years_of_experience',
            'preferred_categories', 'work_preference', 'salary_expectations',
            'is_available'
        ]
        widgets = {
            'work_preference': forms.Select(attrs={'class': 'form-select'}),
        }