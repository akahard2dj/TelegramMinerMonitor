#!/usr/bin/env bash
kill $(ps aux | awk '/SCREEN/ {print $2}')
