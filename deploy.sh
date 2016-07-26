#!/usr/bin/zsh
source /srv/users.getnikola.com/bin/activate
source local-config
./manage.py collectstatic --noinput
cd /home/kwpolska/git/nikola-users
git pull origin master
cd /srv/users.getnikola.com/appdata
git pull origin master
sudo systemctl restart uwsgi
