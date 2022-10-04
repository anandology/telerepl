#! /bin/bash

cd `dirname $0`
git pull
cp config/replbot.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl restart replbot
