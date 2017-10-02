#/bin/bash
echo "Scheduler job is starting"
screen -d -m -S sched_job python3.5 scheduler_message.py

echo "Telegram bot is starting"
screen -d -m -S miner_bot python3.5 main.py