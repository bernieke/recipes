#!/bin/sh -e

cd "$(dirname "$(type -p "$0")")"

cd recipes
../manage.py makemessages
