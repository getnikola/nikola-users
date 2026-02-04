#!/bin/bash
/venv/bin/python manage.py collectstatic --noinput
/venv/bin/python manage.py migrate
exec /venv/bin/python -m gunicorn --bind 0.0.0.0:6868 nikolausers.asgi:application -k uvicorn_worker.UvicornWorker
