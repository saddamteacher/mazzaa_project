#!/usr/bin/env bash
# Сборка для хостинга (Render и аналоги): зависимости, статика, миграции, базовые справочники.
set -o errexit
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate --noinput
python manage.py init_site
