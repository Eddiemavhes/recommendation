#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Python version:"
python --version

echo "Current working directory:"
pwd

echo "Installing dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "Database URL (censored):"
echo ${DATABASE_URL:0:20}...

echo "Collecting static files..."
export DJANGO_SETTINGS_MODULE=job_matcher.production
echo "Creating staticfiles directory..."
mkdir -p staticfiles
python manage.py collectstatic --no-input -v 2

echo "Testing database connection..."
python manage.py shell -c "
import psycopg2
import os
try:
    conn = psycopg2.connect('postgresql://job_matcher_user:3AvZ3UDbTTI66biUpBNippV0K0ajLg3y@dpg-d3sdt7s9c44c73co21vg-a/job_matcher')
    print('PostgreSQL connection successful!')
    conn.close()
except Exception as e:
    print('PostgreSQL connection failed:', e)
"

echo "Running database migrations..."
python manage.py makemigrations --verbosity 2
python manage.py migrate --verbosity 2

echo "Verifying migrations..."
python manage.py showmigrations

echo "Testing Django database connection..."
python manage.py shell -c "
from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
        print('Django database connection successful!')
except Exception as e:
    print('Django database connection failed:', e)
"
python manage.py showmigrations
python manage.py migrate --plan
python manage.py migrate