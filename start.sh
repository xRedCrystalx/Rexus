#!/bin/bash

cd $HOME/NoPing
echo "Updating from git.."
git pull noping v3

if [ ! -d ".venv" ]; then
    echo ".venv folder does not exist in the current directory, creating a new one."
    python3 -m venv .venv
else
    echo ".venv folder exists in the current directory. Ignoring."
fi
echo "Activating virtual env and updating requirements."

source .venv/bin/activate
pip install -r requirements.txt

clear
python3 main.py
