#!/bin/sh
set -e

echo "Waiting for database..."
until python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()
from django.db import connection
connection.ensure_connection()
" 2>/dev/null; do
  echo "Database unavailable - sleeping"
  sleep 2
done
echo "Database is up."

python manage.py makemigrations --noinput
python manage.py migrate --noinput

exec "$@"
