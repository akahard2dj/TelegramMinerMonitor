#!/usr/bin/env bash
screen -wipe
kill $(ps aux | awk '/SCREEN/ {print $2}')
