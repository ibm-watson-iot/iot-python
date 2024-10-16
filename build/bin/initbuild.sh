#!/bin/bash

# Simplified port of a portion of the MAS common build system for public GitHub
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PATH=$PATH:$DIR

pip install --quiet pyyaml yamllint

# 1. Set up semantic versioning
# -----------------------------------------------------------------------------
VERSION_FILE=$GITHUB_WORKSPACE/.version
VERSION_FILE_NOPREREL=$GITHUB_WORKSPACE/.version-noprerel

if [[ "${GITHUB_REF_TYPE}" == "tag" ]]; then
  echo "Note: non-branch build for a tag named '${GITHUB_REF_NAME}'"
  TAG_BASED_RELEASE=true

  SEMVER_XYZ="(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)"
  SEMVER_PRE="(-(0|[1-9][0-9]*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(\.(0|[1-9][0-9]*|[0-9]*[a-zA-Z-][0-9a-zA-Z-]*))*)?"
  SEMVER_BUILD="(\+[0-9a-zA-Z-]+(\.[0-9a-zA-Z-]+)*)?"
  SEMVER_REGEXP="^${SEMVER_XYZ}${SEMVER_PRE}${SEMVER_BUILD}$"

  if [[ ! $GITHUB_REF_NAME =~ $SEMVER_REGEXP ]]; then
    echo "Aborting release build.  Tag '$GITHUB_REF_NAME' does not match a valid semantic version string"
    exit 1
  fi

  echo "${GITHUB_REF_NAME}" > $VERSION_FILE
else
  # Finds the most recent tag that is reachable from a commit. If the tag points
  # to the commit, then only the tag is shown. Otherwise, it suffixes the tag name with the number
  # of additional commits on top of the tagged object and the abbreviated object name of the most
  # recent commit.
  echo "npm install of git-latest-semver-tag starting"
  npm install -g git-latest-semver-tag@1.0.2
  echo "- npm install complete"
  SEMVER_LAST_TAG=$(git-latest-semver-tag 2>/dev/null)

  echo "LAST TAG = ${SEMVER_LAST_TAG}"

  if [ -z $SEMVER_LAST_TAG ]; then
    SEMVER_LAST_TAG="1.0.0"
    SEMVER_RELEASE_LEVEL="initial"
    echo "Creating $GITHUB_WORKSPACE/.changelog"
    # Obtain a list of commits since dawn of time
    git log --oneline -1 --pretty=%B > $GITHUB_WORKSPACE/.changelog
  else
    echo "Creating $GITHUB_WORKSPACE/.changelog (${SEMVER_LAST_TAG}..HEAD)"
    # Obtain a list of commits since ${SEMVER_LAST_TAG}
    git log ${SEMVER_LAST_TAG}..HEAD --oneline --pretty=%B > $GITHUB_WORKSPACE/.changelog

    echo "Changelog START:##################################################################"
    cat $GITHUB_WORKSPACE/.changelog
    echo "Changelog DONE:###################################################################"

    # Work out what has changed
    MAJOR_COUNT=`grep -ciF '[major]' $GITHUB_WORKSPACE/.changelog`
    echo "Major commits : ${MAJOR_COUNT}"

    MINOR_COUNT=`grep -ciF '[minor]' $GITHUB_WORKSPACE/.changelog`
    echo "Minor commits : ${MINOR_COUNT}"

    PATCH_COUNT=`grep -ciF '[patch]' $GITHUB_WORKSPACE/.changelog`
    echo "Patch commits : ${PATCH_COUNT}"

    if [ "$MAJOR_COUNT" -gt "0" ]; then
      SEMVER_RELEASE_LEVEL="major"
    elif [ "$MINOR_COUNT" -gt "0" ]; then
      SEMVER_RELEASE_LEVEL="minor"
    elif [ "$PATCH_COUNT" -gt "0" ]; then
      SEMVER_RELEASE_LEVEL="patch"
    fi
  fi

  echo "RELEASE LEVEL = ${SEMVER_RELEASE_LEVEL}"
  echo "${SEMVER_RELEASE_LEVEL}" > $GITHUB_WORKSPACE/.releaselevel

  # See: https://github.com/fsaintjacques/semver-tool/blob/master/src/semver
  if [ "${SEMVER_RELEASE_LEVEL}" == "initial" ]; then
    echo "1.0.0" > $VERSION_FILE
    echo "Configuring semver for initial release of $(cat $VERSION_FILE)"
  elif [[ "${SEMVER_RELEASE_LEVEL}" =~ ^(major|minor|patch)$ ]]; then
    semver bump ${SEMVER_RELEASE_LEVEL} ${SEMVER_LAST_TAG} > $VERSION_FILE
    echo "Configuring semver for ${SEMVER_RELEASE_LEVEL} bump from ${SEMVER_LAST_TAG} to $(cat $VERSION_FILE)"
  else
    # Default to a patch revision
    semver bump patch ${SEMVER_LAST_TAG} > $VERSION_FILE
    echo "Configuring semver for rebuild of ${SEMVER_LAST_TAG}: $(cat $VERSION_FILE)"
  fi
fi


# 2. Tweak version string for pre-release builds
# -----------------------------------------------------------------------------
cp $VERSION_FILE $VERSION_FILE_NOPREREL
if [[ "${GITHUB_REF_TYPE}" == "branch" ]]; then
    semver bump prerel pre.$GITHUB_REF_NAME $(cat $VERSION_FILE) > $VERSION_FILE
    echo "Pre-release build: $(cat $VERSION_FILE)"
fi

echo "Semantic versioning system initialized: $(cat $VERSION_FILE)"


# 3. Version python modules (if they exist)
# -----------------------------------------------------------------------------
if [ -f ${GITHUB_WORKSPACE}/setup.py ]; then
  sed -i "s/version='1.0.0'/version='${VERSION}'/" setup.py
fi


exit 0
