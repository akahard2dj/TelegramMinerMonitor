#/bin/bash
kill $(ps aux | awk '/SCREEN/ {print $2}')
