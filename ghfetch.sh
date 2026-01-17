#!/bin/bash

read -p "GitHub username: " USERNAME
echo "$USERNAME" | python gh_scrap.py

JSON_FILE="output/${USERNAME}_stats.json"

if [[ -f "$JSON_FILE" ]]; then
    echo "$JSON_FILE" | python shell.py
fi
