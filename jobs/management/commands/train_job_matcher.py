from django.core.management.base import BaseCommand
from pathlib import Path
from ml_models.job_matcher import JobMatchingSystem

class Command(BaseCommand):
    help = 'Train and save the job matching model'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting job matching model training...')
        
        # Initialize the system
        system = JobMatchingSystem()
        
        try:
            # Load CV data
            self.stdout.write('Loading CV database...')
            success = system.load_cv_data('Resume.csv')
            if not success:
                self.stdout.write(self.style.ERROR('Failed to load CV data'))
                return
            
            # Train the system
            self.stdout.write('Training recommendation model...')
            success = system.train_system()
            if not success:
                self.stdout.write(self.style.ERROR('Failed to train system'))
                return
            
            # Save the model
            model_path = Path('ml_models/job_matching_model.pkl')
            system.save_model(str(model_path))
            
            self.stdout.write(self.style.SUCCESS('Successfully trained and saved job matching model'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error during model training: {e}'))