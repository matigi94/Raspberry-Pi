#!/bin/bash

echo "Lywsd02"
pip3 install lywsd02
echo "service"


mkdir /usr/local/src/Czujniki
cp czujniki.py /usr/local/src/Czujniki/
cp czujniki.xml /usr/local/src/Czujniki/
cp mijia /usr/local/src/Czujniki/ -r



rm /etc/systemd/system/czujniki.service
cp czujniki.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo service czujniki start