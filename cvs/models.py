from django.db import models
from django.conf import settings
from ml_models.job_matcher import JobMatcher
from django.core.exceptions import ValidationError
import os

def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.pdf']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Only PDF files are supported.')

class CV(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cvs')
    file = models.FileField(upload_to='cvs/', validators=[validate_file_extension])
    extracted_text = models.TextField(blank=True)
    extracted_skills = models.JSONField(default=list)
    is_current = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s CV - {self.created_at.date()}"
