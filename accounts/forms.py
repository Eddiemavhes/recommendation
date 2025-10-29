from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, UserProfile

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
            'placeholder': 'Enter your email'
        })
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
            'placeholder': 'Choose a username'
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
            'placeholder': 'Choose a password'
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
            'placeholder': 'Confirm password'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Simplify help text
        self.fields['username'].help_text = 'Letters, digits and @ . + - _ only.'
        self.fields['password1'].help_text = 'At least 8 characters.'
        self.fields['password2'].help_text = None

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

    job_title = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
            'placeholder': 'e.g. Software Engineer'
        }),
        required=False
    )
    
    location = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
            'placeholder': 'e.g. London, UK'
        }),
        required=False
    )
    
    years_of_experience = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
            'min': '0',
            'max': '50'
        }),
        required=False
    )
    
    preferred_categories = forms.MultipleChoiceField(
        choices=JOB_CATEGORIES,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-checkbox h-4 w-4 text-blue-600'
        }),
        required=False,
        help_text='Select the job categories you\'re interested in'
    )

    WORK_PREFERENCES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('remote', 'Remote'),
        ('hybrid', 'Hybrid'),
    ]

    work_preference = forms.MultipleChoiceField(
        choices=WORK_PREFERENCES,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-checkbox h-4 w-4 text-blue-600'
        }),
        required=False,
        help_text='Select all that apply'
    )

    salary_expectations = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
            'placeholder': 'e.g. £40,000 - £60,000'
        }),
        required=False
    )

    is_available = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-checkbox h-4 w-4 text-blue-600'
        }),
        label='Available for new opportunities'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field not in ['preferred_categories', 'work_preference', 'is_available']:
                self.fields[field].widget.attrs.update({
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'
                })

    class Meta:
        model = UserProfile
        fields = [
            'job_title', 'location', 'years_of_experience',
            'preferred_categories', 'work_preference', 'salary_expectations',
            'is_available'
        ]