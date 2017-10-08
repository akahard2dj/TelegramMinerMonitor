#!/usr/bin/env bash
echo "updating a .profile"
source /home/pi/.profile

echo "Killing previous processes"
/home/pi/Workspace/github/TelegramMinerMonitor/kill_screen.sh

echo "Scheduler job is starting"
screen -d -m -S sched_job /home/pi/Workspace/github/TelegramMinerMonitor/sched_job.sh

echo "Telegram bot is starting"
screen -d -m -S miner_bot /home/pi/Workspace/github/TelegramMinerMonitor/miner_bot.sh
