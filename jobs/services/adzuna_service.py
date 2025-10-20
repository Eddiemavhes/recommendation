
import requests
from django.conf import settings
from django.utils import timezone
from datetime import datetime
from ..models import Job

class AdzunaService:
    BASE_URL = "https://api.adzuna.com/v1/api/jobs"
    COUNTRIES = ["gb", "us", "za", "au", "br", "ca", "de", "fr", "in", "it", "nl", "nz", "pl", "ru", "sg"]
    API_VERSION = "v1"

    def __init__(self):
        self.app_id = settings.ADZUNA_APP_ID
        self.api_key = settings.ADZUNA_API_KEY

    def search_jobs(self, what=None, where=None, country="gb", page=1, results_per_page=1):
        search_what = what if what else ""
        params = {
            "app_id": self.app_id,
            "app_key": self.api_key,
            "results_per_page": results_per_page
        }
        if search_what:
            params["what"] = search_what
        if where:
            params["where"] = where
        headers = {
            "Accept": "application/json",
            "User-Agent": "JobMatcher/1.0"
        }
        country = country.lower()
        if country not in self.COUNTRIES:
            country = "gb"
        url = f"{self.BASE_URL}/{country}/search/{page}"
        try:
            print(f"Adzuna request: {url} params={params}")
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            if hasattr(e, "response") and e.response is not None:
                print(f"Adzuna response status: {e.response.status_code}")
                print(f"Adzuna response body: {e.response.text}")
            print(f"Error fetching jobs from Adzuna: {e}")
            return None

    def sync_jobs(self, search_terms=None, countries=None):
        latest_job = Job.objects.order_by("-created_at").first()
        if latest_job and (timezone.now() - latest_job.created_at).total_seconds() < 3600:
            print("Recent sync found, fetching minimal jobs...")
            countries = ["gb"]
            results_per_page = 10
        else:
            if not countries:
                countries = ["gb", "us"]
            results_per_page = 25
        if not search_terms:
            search_terms = [""]
        jobs_synced = 0
        for country in countries:
            print(f"\nSyncing jobs for country: {country}")
            for term in search_terms:
                if term:
                    print(f"Searching for: {term}")
                else:
                    print("Fetching all available jobs")
                results = self.search_jobs(what=term, country=country, results_per_page=results_per_page)
                if results and "results" in results:
                    for job_data in results["results"]:
                        try:
                            job_category = job_data.get("category", {}).get("label", "Uncategorized")
                            job, created = Job.objects.update_or_create(
                                job_id=str(job_data.get("id")),
                                defaults={
                                    "title": job_data.get("title", ""),
                                    "company": job_data.get("company", {}).get("display_name", "Unknown"),
                                    "location": job_data.get("location", {}).get("display_name", ""),
                                    "description": job_data.get("description", ""),
                                    "category": job_category,
                                    "salary_min": job_data.get("salary_min"),
                                    "salary_max": job_data.get("salary_max"),
                                    "job_type": self._get_job_type(job_data),
                                    "is_remote": "remote" in job_data.get("description", "").lower(),
                                    "external_url": job_data.get("redirect_url", ""),
                                    "posted_date": datetime.strptime(
                                        job_data.get("created", ""),
                                        "%Y-%m-%dT%H:%M:%SZ"
                                    ).astimezone()
                                }
                            )
                            if created:
                                jobs_synced += 1
                                if jobs_synced % 10 == 0:
                                    print(f"Synced {jobs_synced} jobs so far...")
                        except Exception as e:
                            print(f"Error processing job {job_data.get('id')}: {e}")
                            continue
        return jobs_synced

    def _get_job_type(self, job_data):
        description = job_data.get("description", "").lower()
        contract_type = job_data.get("contract_type", "").lower()
        if "part time" in description or "part-time" in description:
            return "part_time"
        elif "contract" in contract_type or "contract" in description:
            return "contract"
        elif "temporary" in contract_type or "temporary" in description:
            return "temporary"
        else:
            return "full_time"
