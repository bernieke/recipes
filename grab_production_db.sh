#!/bin/bash

cd "$(dirname "$(type -p "$0")")"

rm db.sqlite3
./manage.py migrate
ssh pandora -t \
    docker exec -it recipes \
    ./manage.py dumpdata \
| ./manage.py loaddata --format json -
