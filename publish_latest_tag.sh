#!/bin/sh

docker image rm recipes:latest
docker build . -t recipes --force-rm

IMAGE_ID=`docker image ls | grep recipes | grep latest | awk '{print $3}'`
TAG=`git tag | tail -n 1`

docker tag $IMAGE_ID bernieke/recipes:$TAG
docker push bernieke/recipes:$TAG
docker image rm bernieke/recipes:$TAG
