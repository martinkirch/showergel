#!/usr/bin/env bash

################  Liquidsoap & Showergel installer script #####################
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
if [[ ! "$(which dpkg)" ]]
then
    printf "\n\nThis installer only works on Ubuntu or Debian (or its derivatives).\n\n"
    exit 1
fi
printf "This installer needs admin rights to install Liquidsoap and related packages :\n"
if ! sudo -v
then
    printf "\nWe need to be able to 'sudo' - aborting install.\n"
    exit 1
fi
export DEBIAN_FRONTEND=noninteractive
cd


install_liquidsoap() {
    # just to be sure
    sudo apt install -y curl wget ffmpeg
    sudo -v

    local ARCH="$(dpkg --print-architecture)" # amd64, etc.
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

install_showergel() {
    sudo apt -y install python3 python3-pip python-is-python3

    mkdir -p $HOME/.local/bin
    echo "export PATH=\"$HOME/.local/bin:\$PATH\"" >> .bashrc
    export PATH="$HOME/.local/bin:$PATH"

    # TODO remove --pre !
    pip install --pre showergel
}

setup_instance() {
    mkdir -p showergel
    cd showergel
    SHOWERGEL_FOLDER="$PWD"

    wget https://raw.githubusercontent.com/martinkirch/showergel/main/docs/_static/quickstart.liq
    mv quickstart.liq radio.liq
    mkdir Music
    sed -i "/MUSIC = /c\MUSIC = \"$SHOWERGEL_FOLDER/Music\"" radio.liq
    mkdir Jingles
    sed -i "/JINGLES = /c\JINGLES = \"$SHOWERGEL_FOLDER/Jingles\"" radio.liq
    mkdir Shows
    sed -i "/SHOWS = /c\SHOWS = \"$SHOWERGEL_FOLDER/Shows\"" radio.liq

    showergel install --basename radio --port 2345 --bind-with-script "$SHOWERGEL_FOLDER/radio.liq" --enable-at-boot

    sed -i "/method = /c\method = \"telnet\"" radio.toml

    systemctl --user start radio_gel
    systemctl --user start radio_soap

    # TODO note about output tuning ?
    bold=$(tput bold)
    echo ""
    echo "  🧴 Showergel is installed and running on http://localhost:2345/ 🚀"
    echo ""
    echo "  Put some files in the Music, Jingles and Shows folders : they should playing right away."
    echo ""
    echo "  ${bold}Please note and keep all the lines above, you will need them."
    echo ""
}

install_liquidsoap
install_showergel
setup_instance
