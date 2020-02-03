#!/bin/sh
cd "${0%/*}"
source ./local-config
DJANGO_LOG_PATH='/tmp/django.log' ../bin/python ./manage.py collectstatic --noinput
rm /tmp/django.log
