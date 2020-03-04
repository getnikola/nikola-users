#!/usr/bin/zsh
cd "${0%/*}"
source /srv/users.getnikola.com/venv/bin/activate
source local-config
cd /home/kwpolska/git/nikola-users
git pull origin master
cd /srv/users.getnikola.com/appdata
git pull origin master
./manage.py migrate
./manage.py collectstatic --noinput
touch /etc/uwsgi.d/users.getnikola.com.ini
