#!/bin/bash

cd "$(dirname "$(type -p "$0")")"

rm db.sqlite3
./manage.py migrate
./manage.py flush --no-input
ssh pandora -t \
    docker exec -it recipes \
    ./manage.py dumpdata --all --natural-foreign --natural-primary \
                         --exclude auth.permission recipes auth \
| ./manage.py loaddata --format json -
