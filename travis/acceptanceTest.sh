#!/usr/bin/env bash

# fail fast settings from https://dougrichardson.org/2018/08/03/fail-fast-bash-scripting.html
set -euov pipefail

# Check presence of environment variables
TRAVIS_BRANCH="${TRAVIS_BRANCH:-develop}"
TRAVIS_BRANCH=${TRAVIS_BRANCH##*/} # Drop the "feature/<whatever>" from tagging
TRAVIS_BUILD_NUMBER="${TRAVIS_BUILD_NUMBER:-0}"

docker run --rm -d -p $2:$3 --name $1 ${DOCKER_USERNAME}/$1:travis_${TRAVIS_BRANCH}_${TRAVIS_BUILD_NUMBER}

sleep 15 # wait until the container is running

# INSERT BELOW THE ACCEPTANCE TEST:
#curl -s http://localhost:$2/search # trivial smoke test
