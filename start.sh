#!/usr/bin/sh

echo "Starting main app."
./src/main.py

if [ -n "DEBUG" ]; then
    echo "Application exited."
    while : ; do
        echo "Idling..."
        sleep 600
    done
fi
