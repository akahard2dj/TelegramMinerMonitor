from telegram.ext import Updater, CommandHandler

from gpu_status import GPUInfo
from miningpoolhub_api import Dashboard
from util import UtilApi

import requests
import os
from subprocess import call
import locale

import pyotp

mph_apikey = 'mingingpoolhub_apikey'
telegram_token = 'telegram_apikey'
otp_key = os.environ["OTP_CODE"]
totp = pyotp.TOTP(otp_key)

def start(bot, update):
    update.message.reply_text('Hello World!')

def hello(bot, update):
    update.message.reply_text(
        'Hello {}'.format(update.message.from_user.first_name))

def gpu_status(bot, update):
    gpu_info = GPUInfo()
    g1 = gpu_info.get_info(host='miner_ip')
    
    msg = "Requested Time = {}\n\n".format(g1["gpu_info"][0]["timestamp"])
    msg += "Miner1\n"
    msg += "Workers : {}\n".format(g1["num_gpu"])
    msg += "============================\n"
    msg += "  GPU Id, Temp, Power, Fan  \n"
    msg += "============================\n"
    for i in range(g1["num_gpu"]):
        msg += "  {}, {}, {}, {}\n".format(i, g1["gpu_info"][i]["temp"], g1["gpu_info"][i]["power"], g1["gpu_info"][i]["fan"])
    
    update.message.reply_text(msg)

def status(bot, update):
    gpu_info = GPUInfo()
   
    db_zec = Dashboard(apikey=mph_apikey)
    db_zec.request_api(coin='zcash')
    
    db_eth = Dashboard(apikey=mph_apikey)
    db_eth.request_api(coin='ethereum')
    
    bitcoin_dashboard = Dashboard(apikey=mph_apikey)
    bitcoin_dashboard.request_api(coin='bitcoin')
    btc_json = bitcoin_dashboard.get_json()
    util = UtilApi()
    
    if db_zec.get_hashrate() is not 0:
        unit = 'H/s'
        hashrate = db_zec.get_hashrate()
        res_json = db_zec.get_json()
        coin_name, coin_currency = db_zec.get_dashboard_info()
        last_credits = db_zec.get_last_credits()    
        coin_price = util.get_bitfinex(coin='zecusd')
        last_credits_price = last_credits * coin_price
        
    if db_eth.get_hashrate() is not 0:
        unit = 'MH/s'
        hashrate = db_eth.get_hashrate()
        res_json = db_eth.get_json()
        coin_name, coin_currency = db_eth.get_dashboard_info()
        last_credits = db_eth.get_last_credits()
        coin_price = util.get_bitfinex(coin='ethusd')
        last_credits_price = last_credits * coin_price
    
    currency = util.get_currency()
        
    g1 = gpu_info.get_info()
    
    msg = "Requested Time = {}\n\n".format(g1["gpu_info"][0]["timestamp"])
    msg += "Miner1\n"
    msg += "Workers : {}\n".format(g1["num_gpu"])
    msg += "============================\n"
    msg += "  GPU Id, Temp, Power, Fan  \n"
    msg += "============================\n"
    for i in range(g1["num_gpu"]):
        msg += "  {}, {}, {}, {}\n".format(i, g1["gpu_info"][i]["temp"], g1["gpu_info"][i]["power"], g1["gpu_info"][i]["fan"])
    
    msg += "\n"
    msg += "{}\n".format(coin_name)
    msg += "\n"
    msg += "Total Hashrate : {:7.2f}  {}\n\n".format(hashrate, unit)
    msg += "Last Credits : \n"
    msg += "   {} {:14.5f}\n".format(coin_currency, last_credits)
    msg += "   {} {:14.5f}\n".format("USD", last_credits_price)
    msg += "   {} {:9.0f}\n\n".format("KRW", last_credits_price * currency["KRW"])
    
    msg += "Credits - last 5 days\n"
    for i in range(5):
        msg += " {}: {} {:9.5f} / BTC {:9.5f}\n".format(res_json['getdashboarddata']['data']['recent_credits'][i]['date'], coin_currency, res_json['getdashboarddata']['data']['recent_credits'][i]['amount'], btc_json['getdashboarddata']['data']['recent_credits'][i]['amount'])

    msg += "\n"
    msg += "Total Balance : \n"
    msg += "   {} {:12.5f}\n".format("BTC", bitcoin_dashboard.get_balance())
    msg += "   {} {:12.5f}\n".format("USD", bitcoin_dashboard.get_balance() * util.get_bitfinex())
    
    update.message.reply_text(msg)

def price(bot, update):
    util = UtilApi()
    btc_bitfinex = util.get_bitfinex()
    zec_bitfinex = util.get_bitfinex(coin='zecusd')
    eth_bitfinex = util.get_bitfinex(coin='ethusd')
    currency = util.get_currency()
    coinone_price = util.get_coinone()

    msg = "Currency:\n"
    msg += "  USD     1.0\n"
    msg += "  KRW  {}\n".format(currency['KRW'])
    msg += "\n"
    msg += "Coin Price[USD]:\n"
    msg += "  Bitcoin : {:12.2f}\n".format(btc_bitfinex)
    msg += "  Ethereum: {:12.2f}\n".format(eth_bitfinex)
    msg += "  Zcash   : {:12.2f}\n".format(zec_bitfinex)
    msg += "\n"
    
    msg += "Coin Price[KRW]:\n"
    msg += "  Bitcoin\t {:8d}\n".format(int(coinone_price["btc"]["last"]))
    msg += "  Zcash  \t {:8d}\n".format(int(zec_bitfinex * currency["KRW"]))
    msg += "  Qtum   \t {:8d}\n".format(int(coinone_price["qtum"]["last"]))
    msg += "  Eth    \t {:8d}\n".format(int(coinone_price["eth"]["last"]))

    update.message.reply_text(msg)

def cmd_power_limit(bot, update, args, chat_data):
    chat_id = update.message.chat_id
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
            g1 = gpu_info.get_info()
    
            msg = "Requested Time = {}\n\n".format(g1["gpu_info"][0]["timestamp"])
            msg += "Worker : {}\n".format(g1["num_gpu"])
            msg += "============================\n"
            msg += "  GPU Id, Temp, Power, Fan  \n"
            msg += "============================\n"
            for i in range(g1["num_gpu"]):
                msg += "  {}, {}, {}, {}\n".format(i, g1["gpu_info"][i]["temp"], g1["gpu_info"][i]["power"], g1["gpu_info"][i]["fan"])
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

updater = Updater(telegram_token)

updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('hello', hello))
updater.dispatcher.add_handler(CommandHandler('status', status))
updater.dispatcher.add_handler(CommandHandler('gpu', gpu_status))
updater.dispatcher.add_handler(CommandHandler('price', price))
updater.dispatcher.add_handler(CommandHandler('cmd_pl', cmd_power_limit, pass_args=True, pass_chat_data=True))
updater.dispatcher.add_handler(CommandHandler('cmd_start', cmd_miner_start, pass_args=True, pass_chat_data=True))
updater.dispatcher.add_handler(CommandHandler('cmd_kill', cmd_miner_kill, pass_args=True, pass_chat_data=True))

updater.start_polling()
updater.idle()
