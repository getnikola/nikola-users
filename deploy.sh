#!/usr/bin/zsh
source /srv/users.getnikola.com/bin/activate
source local-config
cd /home/kwpolska/git/nikola-users
git pull origin master
cd /srv/users.getnikola.com/appdata
git pull origin master
./manage.py migrate
./manage.py collectstatic --noinput
sudo systemctl restart uwsgi
