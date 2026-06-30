#!/usr/bin/env bash
# Sai imediatamente se qualquer comando falhar.
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate
