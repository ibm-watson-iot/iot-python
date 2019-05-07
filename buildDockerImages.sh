#!/bin/bash

# If BUILD_DOCKER_IMAGES is defined then build the docker container for the sample and upload it to dockerhub
# We only build this on the python 3.7 branch, and we don't build for PRs
if [ -n "$BUILD_DOCKER_IMAGES" ]; then
    echo "Building docker images"

    IMAGE_NAME=wiotp/psutil
    IMAGE_SRC=samples/psutil

    docker build -t ${IMAGE_NAME}:$TRAVIS_BRANCH ${IMAGE_SRC}
    if [ "$TRAVIS_PULL_REQUEST" == "false" ]; then
        if [ "$TRAVIS_BRANCH" == "master" ]; then
            docker tag ${IMAGE_NAME}:$TRAVIS_BRANCH ${IMAGE_NAME}:latest
            docker push ${IMAGE_NAME}:latest
        else
            docker push ${IMAGE_NAME}:$TRAVIS_BRANCH
        fi
    fi
else
    echo "Skipped docker image building"
fi
