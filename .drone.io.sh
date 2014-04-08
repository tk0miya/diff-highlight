#!/bin/sh
sudo add-apt-repository ppa:fkrull/deadsnakes
sudo apt-get update
sudo apt-get install python2.4 python2.4-dev python2.5 python2.5-dev python2.6 python2.6-dev python3.4 python3.4-dev

virtualenv old_pythons
old_pythons/bin/pip install pip==1.3 virtualenv==1.7.2 tox==1.4
old_pythons/bin/tox -e py24,py25

pip install --use-mirrors --upgrade detox misspellings
find src/ -name "*.py" | misspellings -f -
detox
