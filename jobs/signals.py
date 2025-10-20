
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from jobs.services.adzuna_service import AdzunaService
from cvs.models import CV
from threading import Thread

@receiver(user_logged_in)
def load_jobs_on_login(sender, user, request, **kwargs):
    """Load jobs from Adzuna when user logs in"""
    def background_job_sync():
        current_cv = CV.objects.filter(user=user, is_current=True).first()
        search_terms = []
        if current_cv and current_cv.extracted_skills:
            search_terms = current_cv.extracted_skills[:5]
        if not search_terms:
            search_terms = ["software", "developer", "engineer"]
        adzuna = AdzunaService()
        try:
            jobs_synced = adzuna.sync_jobs(search_terms=search_terms)
            print(f"Background job sync complete. Synced {jobs_synced} new jobs for user {user.username}")
        except Exception as e:
            print(f"Error in background job sync: {e}")
    print(f"Starting background job sync for user {user.username}")
    thread = Thread(target=background_job_sync)
    thread.daemon = True
    thread.start()
