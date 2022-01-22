#!/bin/bash

git submodule update
cp extra/push.c dwm_src/
pip uninstall pydwm
rm -rf build/ dist/ pydwm.egg-info/
python setup.py build
python setup.py install
