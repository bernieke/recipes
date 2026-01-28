#!/bin/bash

cd "$(dirname "$(type -p "$0")")" || exit

rm db.sqlite3
./manage.py migrate
./manage.py flush --no-input
ssh mnemosyne -t \
    docker exec -it recipes \
    ./manage.py dumpdata --all --natural-foreign --natural-primary \
                         --exclude auth.permission recipes auth \
| ./manage.py loaddata --format json -
