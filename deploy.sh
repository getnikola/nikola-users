#!/usr/bin/zsh
source /srv/users.getnikola.com/bin/activate
source local-config
./manage.py collectstatic --noinput
cd /srv/users.getnikola.com/appdata
git pull origin master
sudo systemctl restart uwsgi
