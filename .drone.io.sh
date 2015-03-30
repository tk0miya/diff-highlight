#!/bin/sh
sudo add-apt-repository ppa:fkrull/deadsnakes
sudo apt-get update
sudo apt-get install python2.6 python2.6-dev python3.4 python3.4-dev

pip install --use-mirrors --upgrade detox misspellings docutils
pip install https://bitbucket.org/hpk42/detox/get/tip.zip
find src/ -name "*.py" | misspellings -f -
detox
