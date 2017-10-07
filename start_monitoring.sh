<<<<<<< HEAD
#/bin/bash
echo "Killing previous processes"
/home/pi/Workspace/github/TelegramMinerMonitor/kill_screen.sh

=======
#!/usr/bin/env bash
>>>>>>> 29a012b856b757892fbd70c90dff5d5a85b68ea6
echo "Scheduler job is starting"
screen -d -m -S sched_job /home/pi/Workspace/github/TelegramMinerMonitor/sched_job.sh

echo "Telegram bot is starting"
screen -d -m -S miner_bot /home/pi/Workspace/github/TelegramMinerMonitor/miner_bot.sh
