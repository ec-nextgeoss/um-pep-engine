#!/usr/bin/env bash

# fail fast settings from https://dougrichardson.org/2018/08/03/fail-fast-bash-scripting.html
set -euov pipefail

# Check presence of environment variables
TRAVIS_BRANCH="${TRAVIS_BRANCH:-develop}"
TRAVIS_BRANCH=${TRAVIS_BRANCH##*/} # Drop the "feature/<whatever>" from tagging
TRAVIS_BUILD_NUMBER="${TRAVIS_BUILD_NUMBER:-0}"

echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
docker pull eoepca/$1:travis_${TRAVIS_BRANCH}_$TRAVIS_BUILD_NUMBER  # have to pull locally in order to tag as a release

# Tag and push as a Release
docker tag eoepca/$1:travis_${TRAVIS_BRANCH}_$TRAVIS_BUILD_NUMBER eoepca/$1:release_$TRAVIS_TAG
docker push eoepca/$1:release_$TRAVIS_TAG

# Tag and push as `latest`
docker tag eoepca/$1:travis_${TRAVIS_BRANCH}_$TRAVIS_BUILD_NUMBER eoepca/$1:latest
docker push eoepca/$1:latest
