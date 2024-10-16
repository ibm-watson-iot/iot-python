#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# COLOR_RED=`tput setaf 1`
# COLOR_GREEN=`tput setaf 2`
# COLOR_YELLOW=`tput setaf 3`
# COLOR_BLUE=`tput setaf 4`
# COLOR_MAGENTA=`tput setaf 5`
# COLOR_CYAN=`tput setaf 6`
# TEXT_RESET=`tput sgr0`

# tput doesn't work in GitHub actions
# TODO: Integrate properly with GitHub actions to annotate the output as errors etc
COLOR_RED=""
COLOR_GREEN=""
COLOR_YELLOW=""
COLOR_BLUE=""
COLOR_MAGENTA=""
COLOR_CYAN=""
TEXT_RESET=""


function echo_h1() {
  echo "${COLOR_YELLOW}================================================================================"
  echo "${COLOR_YELLOW}$1"
  echo "${COLOR_YELLOW}================================================================================"
}


function echo_h2() {
  echo "${COLOR_YELLOW}$1"
  echo "${COLOR_YELLOW}--------------------------------------------------------------------------------"
}


function echo_warning() {
  echo "${COLOR_RED}$1"
}


function echo_highlight() {
  echo "${COLOR_MAGENTA}$1"
}


# Install yq
# ----------
function install_yq() {
  python -m pip install yq || exit 1
}


# These should be loaded already, but just incase!
# ------------------------------------------------
if [[ -z "$BUILD_SYSTEM_ENV_LOADED" ]]; then
  source $DIR/.env.sh
fi


# Upload a file to Artifactory
# -----------------------------------------------------------------------------
# Usage example:
#  artifactory_upload $FILE_PATH $TARGET_URL
#
function artifactory_upload() {
  if [ ! -e $1 ]; then
    echo_warning "Artifactory upload failed - $1 does not exist"
    exit 1
  fi

  md5Value="`md5sum "$1"`"
  md5Value="${md5Value:0:32}"

  sha1Value="`sha1sum "$1"`"
  sha1Value="${sha1Value:0:40}"

  echo "Uploading $1 to $2"
  curl -H "Authorization:Bearer $ARTIFACTORY_TOKEN"  -H "X-Checksum-Md5: $md5Value" -H "X-Checksum-Sha1: $sha1Value" -T $1 $2 || exit 1
}
