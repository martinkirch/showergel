#!/usr/bin/env bash

###################  Liquidsoap installer script ########################
#
#   Copyright © 2022 Martin Kirchgessner <martin.kirch@gmail.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.


#   Usage : just run the script of a freshly installed system


# Start by setting a comfy environment
set -o errexit
set -o nounset
set -o pipefail
if [[ "${DEBUG-0}" == "1" ]] # call with DEBUG=1 in the env to debug this script
then
    set -o xtrace
fi
if [[ ! "$(which dpkg-architecture)" ]]
then
    printf "\n\nThis installer only works on Ubuntu or Debian (or its derivatives).\n\n"
    exit 1
fi
printf "This installer needs admin rights to install Liquidsoap and related packages :\n"
if ! sudo -v
then
    printf "\nWe need to be able to 'sudo' - aborting install.\n"
fi
export DEBIAN_FRONTEND=noninteractive
cd


install_liquidsoap() {
    # just to be sure
    sudo apt install -y curl wget ffmpeg
    sudo -v

    local ARCH="$(dpkg-architecture -q DEB_BUILD_ARCH)" # amd64, etc.
    source /etc/os-release # comes with a few variables : we'll use ID and VERSION_CODENAME

    # workaround GitHub's redirection and javascripts
    local LATEST=$(curl -w '%{redirect_url}' https://github.com/savonet/liquidsoap/releases/latest)
    local ASSETS_URL=${LATEST/tag/expanded_assets}
    wget -nd -r -l 1 -R '*dbgsym*' -A "liquidsoap*$ID*$VERSION_CODENAME*$ARCH.deb" "$ASSETS_URL"

    local PACKAGE=$(ls -tr liquidsoap*.deb |tail)
    printf "\n\n************ downloaded $PACKAGE **************\n"

    sudo dpkg --force-depends -i ./$PACKAGE
    sudo -v
    # add -o Debug::pkgProblemResolver=true if something goes wrong below. APT can decide to *remove* liquidsoap if a dependency is not available.
    sudo apt -y install -f

    printf "Installed "
    liquidsoap --version
}

install_liquidsoap
