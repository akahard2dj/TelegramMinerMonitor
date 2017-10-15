import os
import time
from subprocess import call
from time import sleep

import pyotp
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler

from monitor.gpu_status import GPUInfo
from monitor.miner_api import MinerAPI
from monitor.monitor_result import get_gpu_info, get_mph_info, get_price, get_whattomine_result, get_miner_report


mph_apikey = os.environ["MPH_APIKEY"]
telegram_apikey = os.environ["TELEGRAM_APIKEY"]
otp_key = os.environ["OTP_CODE"]
exec_folder = os.environ["EXEC_FOLDER"]
totp = pyotp.TOTP(otp_key)
hosts = ['miner1', 'miner2']
gpu_info = GPUInfo()
miner_api = MinerAPI()


def miner_status(bot: Bot, update: Update):
    unix_time = int(time.time())
    msg = get_miner_report(unix_time, miner_api, hosts)

    update.message.reply_text(msg)


def gpu_status(bot, update):
    unix_time = int(time.time())
    msg = get_gpu_info(unix_time, gpu_info, hosts)
    
    update.message.reply_text(msg)


def status(bot, update):
    unix_time = int(time.time())
    msg = get_mph_info(unix_time, mph_apikey)
    
    update.message.reply_text(msg)


def price(bot, update):
    unix_time = int(time.time())
    msg = get_price(unix_time)

    update.message.reply_text(msg)


def mine_rank(bot, update):
    unix_time = int(time.time())
    msg = get_whattomine_result(unix_time)

    update.message.reply_text(msg)


def deploy(bot, update, args, chat_data):
    chat_id = update.message.chat_id
    unix_time = int(time.time())
    try:
        code = args[0]
        if not code.isdigit():
            update.message.reply_text('Invalid auth code')
            return

        if totp.verify(int(code)):
            cmd1 = '{}deploy.sh'.format(exec_folder)
            cmd2 = '{}start_monitoring.sh'.format(exec_folder)
            update.message.reply_text('git pulling...5 seconds sleep')    
            call(['bash', '{}'.format(cmd1)])
            sleep(5.0)
            update.message.reply_text('restarting bot...')
            call(['bash', '{}'.format(cmd2)])

        else:
            update.message.reply_text('Invalid auth code')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /deploy <authcode>')


def cmd_power_limit(bot, update, args, chat_data):
    chat_id = update.message.chat_id
    unix_time = int(time.time())
    try:
        code = args[0]
        if not code.isdigit():
            update.message.reply_text('Invalid auth code')
            return

        if totp.verify(int(code)):
            #logging.warning('Someone get an authentication from server')
            update.message.reply_text('Successfully changed power limit "{} : {}W"'.format(args[1], args[2]))
            call(['ssh', 'miner@{}'.format(args[1]), "sudo", "nvidia-smi", "-pl", args[2]])
            gpu_info = GPUInfo()
            msg = get_gpu_info(unix_time, gpu_info, hosts)
            update.message.reply_text(msg)
        else:
            update.message.reply_text('Invalid auth code')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /cmd_pl <authcode> hostname power')


def cmd_miner_start(bot, update, args, chat_data):
    chat_id = update.message.chat_id
    try:
        code = args[0]
        if not code.isdigit():
            update.message.reply_text('Invalid auth code')
            return

        if totp.verify(int(code)):
            #logging.warning('Someone get an authentication from server')
            call(['ssh', 'miner@miner1', "./kill_miner.sh"])
            if args[1] == 'zec':            
                call(['ssh', 'miner@miner1', "./screen_start.sh", "zec"])
                update.message.reply_text('Zcash mining is starting...')
            elif args[1] == 'eth':
                call(['ssh', 'miner@miner1', "./screen_start.sh", "eth"])
                update.message.reply_text('Ethereum mining is starting...')
            else:
                update.message.reply_text('Invalid coin. [zec|eth]')       
            
        else:
            update.message.reply_text('Invalid auth code')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /cmd_start <authcode> [ZEC|ETH]')


def cmd_miner_kill(bot, update, args, chat_data):
    chat_id = update.message.chat_id
    try:
        code = args[0]
        if not code.isdigit():
            update.message.reply_text('Invalid auth code')
            return

        if totp.verify(int(code)):
            #logging.warning('Someone get an authentication from server')
            call(['ssh', 'miner@miner1', "./kill_miner.sh"])
            update.message.reply_text('All miners are killed.')       
            
        else:
            update.message.reply_text('Invalid auth code')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /cmd_kill <authcode>')


updater = Updater(telegram_apikey)

updater.dispatcher.add_handler(CommandHandler('status', status))
updater.dispatcher.add_handler(CommandHandler('gpu', gpu_status))
updater.dispatcher.add_handler(CommandHandler('miner', miner_status))
updater.dispatcher.add_handler(CommandHandler('price', price))
updater.dispatcher.add_handler(CommandHandler('minerank', mine_rank))
updater.dispatcher.add_handler(CommandHandler('deploy', deploy, pass_args=True, pass_chat_data=True))
updater.dispatcher.add_handler(CommandHandler('cmd_pl', cmd_power_limit, pass_args=True, pass_chat_data=True))
updater.dispatcher.add_handler(CommandHandler('cmd_start', cmd_miner_start, pass_args=True, pass_chat_data=True))
updater.dispatcher.add_handler(CommandHandler('cmd_kill', cmd_miner_kill, pass_args=True, pass_chat_data=True))

updater.start_polling()
updater.idle()
