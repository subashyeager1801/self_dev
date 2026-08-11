#!/bin/bash
echo "=== Installing dependencies for Vercel ==="
python3.11 -m pip install --break-system-packages -r requirements.txt || python3 -m pip install --break-system-packages -r requirements.txt || pip install -r requirements.txt

echo "=== Collecting static files ==="
python3.11 manage.py collectstatic --noinput --clear || python3 manage.py collectstatic --noinput --clear || python manage.py collectstatic --noinput --clear
