#!/usr/bin/env bash

# fail fast settings from https://dougrichardson.org/2018/08/03/fail-fast-bash-scripting.html
set -euov pipefail


# Check presence of environment variables
TRAVIS_BRANCH="${TRAVIS_BRANCH:-develop}"
TRAVIS_BRANCH=${TRAVIS_BRANCH##*/} # Drop the "feature/<whatever>" from tagging
TRAVIS_BUILD_NUMBER="${TRAVIS_BUILD_NUMBER:-0}"

# Create a Docker image and tag it as 'travis_<build number>'
buildTag=travis_${TRAVIS_BRANCH}_$TRAVIS_BUILD_NUMBER

docker build -t eoepca/$1 .
docker tag eoepca/$1 $DOCKER_USERNAME/$1:$buildTag

echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin

docker push $DOCKER_USERNAME/$1:$buildTag   # defaults to docker hub

