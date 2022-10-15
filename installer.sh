#!/bin/bash

export DEBIAN_FRONTEND=noninteractive

cd

# install on ubuntu 22 LTS (jammy jellyfish)
LS_URL="https://github.com/savonet/liquidsoap/releases/download/v2.1.2/liquidsoap_2.1.2-ubuntu-jammy-1_amd64.deb"
wget $LS_URL

sudo dpkg --force-all -i liquidsoap_2.1.2-ubuntu-jammy-1_amd64.deb

sudo apt -y -f install

sudo apt -y install python3 python3-pip python-is-python3

mkdir -p $HOME/.local/bin
echo "export PATH=\"$HOME/.local/bin:\$PATH\"" >> .bashrc
export PATH="$HOME/.local/bin:$PATH"

pip install --pre showergel

mkdir -p showergel
cd showergel
SHOWERGEL_FOLDER="$PWD"

wget https://raw.githubusercontent.com/martinkirch/showergel/main/docs/_static/quickstart.liq
mv quickstart.liq radio.liq
sed -i "/MUSIC = /c\MUSIC = \"$PWD/Music\"" radio.liq
sed -i "/JINGLES = /c\JINGLES = \"$PWD/Jingles\"" radio.liq
sed -i "/SHOWS = /c\SHOWS = \"$PWD/Shows\"" radio.liq

mkdir Music
mkdir Jingles
mkdir Shows

showergel install --basename radio --port 2345 --bind-with-script "$PWD/radio.liq" --enable-at-boot

sed -i "/method = /c\method = \"telnet\"" radio.toml

echo "Put some files in the Music, Jingles and Shows folders, then start the showergel service, the the liquidsoap service !"
echo "Then Showergel will be available at http://localhost:2345/"
