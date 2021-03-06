#!/bin/bash

cd "$(dirname "$(type -p "$0")")"

python3 manage.py collectstatic --no-input
python3 manage.py migrate

if [[ "$GUNICORN" == "1" ]]
then
    gunicorn recipes.wsgi --config gunicorn.conf --bind=0.0.0.0:8000
else
    DEBUG=1 /usr/local/bin/python3 manage.py runserver 0.0.0.0:8000
fi
