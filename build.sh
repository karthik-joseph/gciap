#!/usr/bin/env bash
# build.sh — Render.com build script
set -o errexit   # exit on any error

pip install --upgrade pip
pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate
