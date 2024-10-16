#!/bin/bash

# GitHub Actions environment variables documentation:
# https://docs.github.com/en/actions/learn-github-actions/environment-variables

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export PATH=$PATH:$DIR:$DIR/ptc

# Version file (semver)
export VERSION_FILE=${GITHUB_WORKSPACE}/.version
if [ -f "$VERSION_FILE" ]; then
  export VERSION=$(cat ${VERSION_FILE})
fi

export VERSION_FILE_NOPREREL=${GITHUB_WORKSPACE}/.version-noprerel
if [ -f "$VERSION_FILE_NOPREREL" ]; then
  export VERSION_NOPREREL=$(cat ${VERSION_FILE_NOPREREL})
fi

# During initbuild we record the release level (aka the version bump from the last release)
export SEMVER_RELEASE_LEVEL_FILE=${GITHUB_WORKSPACE}/.releaselevel
if [ -f "$SEMVER_RELEASE_LEVEL_FILE" ]; then
  export SEMVER_RELEASE_LEVEL=$(cat ${SEMVER_RELEASE_LEVEL_FILE})
fi

# Docker does not support "+" characters from semvar syntax so we replace "+" with "_"
# We should not actually deploy any "+build" releases anyway
export DOCKER_TAG=$(echo "$VERSION" | sed -e's/\+/_/g')

if [ -z $BUILD_SYSTEM_ENV_LOADED ]; then
  echo "BUILD_SYSTEM_ENV_LOADED is not defined yet"
  export BUILD_SYSTEM_ENV_LOADED=1

  if [ ! -z $GITHUB_ENV ]; then
    # https://docs.github.com/en/actions/learn-github-actions/workflow-commands-for-github-actions#environment-files
    echo "GITHUB_ENV is defined, exporting properties to $GITHUB_ENV"

    echo "VERSION_FILE=$VERSION_FILE" >> $GITHUB_ENV
    echo "VERSION_FILE_NOPREREL=$VERSION_FILE_NOPREREL" >> $GITHUB_ENV
    echo "VERSION=$VERSION" >> $GITHUB_ENV
    echo "VERSION_NOPREREL=$VERSION_NOPREREL" >> $GITHUB_ENV
    echo "DOCKER_TAG=$DOCKER_TAG" >> $GITHUB_ENV

    echo "SEMVER_RELEASE_LEVEL_FILE=$SEMVER_RELEASE_LEVEL_FILE" >> $GITHUB_ENV
    echo "SEMVER_RELEASE_LEVEL=$SEMVER_RELEASE_LEVEL" >> $GITHUB_ENV

    echo "BUILD_SYSTEM_ENV_LOADED=1" >> $GITHUB_ENV
  else
    echo "GITHUB_ENV is not defined"
  fi

  echo_h1 "Build Properties"
  echo_highlight "DIR ........................ $DIR"
  echo_highlight "PATH ....................... $PATH"
  echo_highlight ""
  echo_highlight "VERSION_FILE ............... $VERSION_FILE"
  echo_highlight "VERSION_FILE_NOPREREL ...... $VERSION_FILE_NOPREREL"
  echo_highlight "VERSION .................... $VERSION"
  echo_highlight "VERSION_NOPREREL ........... $VERSION_NOPREREL"
  echo_highlight "DOCKER_TAG ................. $DOCKER_TAG"
  echo_highlight ""
  echo_highlight "SEMVER_RELEASE_LEVEL_FILE .. $SEMVER_RELEASE_LEVEL_FILE"
  echo_highlight "SEMVER_RELEASE_LEVEL ....... $SEMVER_RELEASE_LEVEL"
else
  echo "BUILD_SYSTEM_ENV_LOADED is already defined, skipping debug and export to GitHub env file"
fi


