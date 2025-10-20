# Job Recommendation System

A Django-based job recommendation system that matches CVs with job listings using natural language processing and machine learning techniques.

## Features

- CV parsing and skill extraction
- Job matching based on skills and experience
- Integration with Adzuna API for real-time job listings
- User authentication and profile management
- Dashboard with personalized job recommendations
- Application tracking system

## Tech Stack

- Python 3.13
- Django 4.2+
- NLTK for Natural Language Processing
- Tailwind CSS for styling
- SQLite for development database
- PyPDF2 and pdfplumber for PDF processing

## Setup

1. Clone the repository
```bash
git clone https://github.com/yourusername/job-recommendation-system.git
cd job-recommendation-system
```

2. Create and activate virtual environment
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Configure environment variables
Create a `.env` file in the root directory with:
```
DJANGO_SECRET_KEY=your_secret_key
ADZUNA_APP_ID=your_adzuna_app_id
ADZUNA_API_KEY=your_adzuna_api_key
```

5. Apply database migrations
```bash
python manage.py migrate
```

6. Run the development server
```bash
python manage.py runserver
```

## Usage

1. Register a new account
2. Upload your CV (PDF format)
3. View matched job recommendations on your dashboard
4. Apply to jobs through the platform
5. Track your applications in the dashboard

## Project Structure

- `accounts/` - User authentication and profile management
- `jobs/` - Job listing and recommendation logic
- `cvs/` - CV upload and processing
- `applications/` - Job application tracking
- `dashboard/` - User dashboard views
- `ml_models/` - Machine learning models for job matching
- `templates/` - HTML templates
- `static/` - Static files (CSS, JS, images)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.