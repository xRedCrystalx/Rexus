#!/bin/bash

cd $HOME/noping
git pull noping v3

if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate

pip install -r requirements.txt

clear
python3 main.py
