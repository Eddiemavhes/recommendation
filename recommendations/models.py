from django.db import models
from django.conf import settings
from jobs.models import Job
from cvs.models import CV

class Recommendation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recommendations')
    cv = models.ForeignKey(CV, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    match_score = models.FloatField()
    content_similarity = models.FloatField()
    skills_overlap = models.FloatField()
    experience_compatibility = models.FloatField()
    category_match = models.BooleanField(default=False)
    matching_skills = models.JSONField(default=list)
    missing_skills = models.JSONField(default=list)
    explanation = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'job')
        ordering = ['-match_score']

    def __str__(self):
        return f"{self.user.username} - {self.job.title} ({self.match_score}%)"
