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
if [[ "${DEBUG-0}" == "1" ]]; then # call with DEBUG=1 in the env to debug this script
    set -o xtrace
fi
# TODO check dpkg-architecture is here
export DEBIAN_FRONTEND=noninteractive
cd

install_liquidsoap() {
    # TODO 
    # detect system, architecture
    # exploit the redirection from https://github.com/savonet/liquidsoap/releases/tag/v2.1.2 (maybe wget -r -l 1 -A *.deb with filters on release/arch ?)
    
    # install on ubuntu 22 LTS (jammy jellyfish)
    echo "https://github.com/savonet/liquidsoap/releases/download/v2.1.2/liquidsoap_2.1.2-ubuntu-jammy-1_amd64.deb"

    wget $LS_URL

    # TODO detect file name - maybe ls -tr liquidsoap*.deb |tail
    sudo dpkg --force-all -i liquidsoap_2.1.2-ubuntu-jammy-1_amd64.deb
    sudo apt -y -f install
}

install_showergel() {
    sudo apt -y install python3 python3-pip python-is-python3

    mkdir -p $HOME/.local/bin
    echo "export PATH=\"$HOME/.local/bin:\$PATH\"" >> .bashrc
    export PATH="$HOME/.local/bin:$PATH"

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
    echo "  Put some files in the Music, Jingles and Shows folders : it should start playing."
    echo ""
    echo "  ${bold}Please note and keep all the lines above, you will need them."
    echo ""
}


main () {
    install_liquidsoap
    install_showergel
    setup_instance
}
