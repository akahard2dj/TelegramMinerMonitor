import datetime
import time
import os

from apscheduler.schedulers.blocking import BlockingScheduler
from sqlalchemy import func

from monitor.monitor_result import get_gpu_info, get_mph_info, get_whattomine_result
from monitor.gpu_status import GPUInfo
from monitor.miningpoolhub_api import Dashboard

from utils.telegram_send_api import TelegramSendMessage
from utils.util_api import UtilApi
import utils.util

from database.mapping_base import session
from database.mining_history_table import MiningHistory

sched = BlockingScheduler()

mph_apikey = os.environ["MPH_APIKEY"]
telegram_apikey = os.environ["TELEGRAM_APIKEY"]
telegram_chat_id = os.environ["TELEGRAM_CHAT_ID"]
telegram_chat_id_cus = os.environ["TELEGRAM_CHAT_ID_CUSTOMER"]
hosts = ['miner1', 'miner2', 'miner3']
num_gpu_set = [6, 6, 6]
gpu_temp_thresh = 77.0

gpu_info = GPUInfo()
telegram_sender = TelegramSendMessage(telegram_apikey, telegram_chat_id)
telegram_sender_cus = TelegramSendMessage(telegram_apikey, telegram_chat_id_cus)


def get_gpu_info(unix_time: int):
    msg = 'Scheduled Message [GPU Info]\n'
    msg += 'Requested Time = {}\n'.format(utils.util.timestamp_to_datetime(unix_time))
    for host in hosts:
        gpu = gpu_info.get_info(host)
        msg += 'Host    : {}\n'.format(host)
        msg += 'Workers : {}\n'.format(gpu["num_gpu"])
        msg += '===============================\n'
        msg += '   GPU Id, Temp, Power, Fan\n'
        msg += '===============================\n'
        for idx, gpu_data in enumerate(gpu["gpu_info"]):
            msg += "{}, {}, {}, {}\n".format(idx, gpu_data["temp"], gpu_data["power"],
            gpu_data["fan"])

    return msg


def get_mph_dashboard(unix_time: int):
    db_zec = Dashboard(apikey=mph_apikey)
    db_zec.request_api(coin='zcash')
    
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

    currency = util.get_currency()
    msg = '\nScheduled Message [MPH Info]\n'
    msg += 'Requested Time = {}\n'.format(utils.util.timestamp_to_datetime(unix_time))
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

    return msg


@sched.scheduled_job('cron', hour=8, minute=55)
def db_pushing():
    yesterday = datetime.date.today() - datetime.timedelta(1)
    yesterday_str = yesterday.isoformat()

    db_zec = Dashboard(apikey=mph_apikey)
    db_zec.request_api(coin='zcash')
    zec_json = db_zec.get_json()

    bitcoin_dashboard = Dashboard(apikey=mph_apikey)
    bitcoin_dashboard.request_api(coin='bitcoin')
    btc_json = bitcoin_dashboard.get_json()

    last_credit_zec = zec_json['getdashboarddata']['data']['recent_credits']
    last_credit_btc = btc_json['getdashboarddata']['data']['recent_credits']

    btc_credit = next(item for item in last_credit_btc if item['date'] == yesterday_str)
    zec_credit = next(item for item in last_credit_zec if item['date'] == yesterday_str)

    model = MiningHistory()
    model.currency = 'ZEC'
    model.amount = zec_credit['amount']
    model.amount_btc = btc_credit['amount']
    model.timestamp = yesterday
    session.add(model)
    session.commit()


@sched.scheduled_job('cron', day_of_week='mon-sun', hour=9)
def timed_daily_report():

    unix_time = int(time.time())
    print('{} - Scheduled job[cron, day_of_week=mon-fri, hour=9]: Miner Daily Report'.format(utils.util.timestamp_to_datetime(unix_time)))
    #gpu_status_text = get_gpu_info(unix_time)
    #mph_dashboard_text = get_mph_dashboard(unix_time)
    #whattomine_report_text = get

    gpu_status_text = 'Scheduled Message [GPU Info]\n'
    gpu_status_text += get_gpu_info(unix_time)

    mph_dashboard_text = 'Scheduled Message [MPH Info]\n'
    mph_dashboard_text += get_mph_info(unix_time, mph_apikey)

    whattomine_report_text = 'Scheduled Message [WhatToMine Report]\n'
    whattomine_report_text += get_whattomine_result(unix_time)

    telegram_sender.send_message(gpu_status_text, verbose=True)
    telegram_sender.send_message(mph_dashboard_text, verbose=True)
    telegram_sender.send_message(whattomine_report_text, verbose=True)

    telegram_sender_cus.send_message(gpu_status_text, verbose=True)
    telegram_sender_cus.send_message(mph_dashboard_text, verbose=True)
    telegram_sender_cus.send_message(whattomine_report_text, verbose=True)


@sched.scheduled_job('cron', day=1, hour=8, minute=59)
def monthly_report():
    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    today = datetime.date.today()
    days = days_in_month[today.month-1]
    query_result = session.query(MiningHistory) \
        .filter(func.extract('year', MiningHistory.timestamp) == today.year) \
        .filter(func.extract('month', MiningHistory.timestamp) == today.month)

    total_amount = 0.0
    total_amount_btc = 0.0

    for query in query_result:
        total_amount += query.amount
        total_amount_btc += query.amount_btc

    fee_rate = 0.05
    owner = total_amount / 3.0 + total_amount * (2.0 / 3.0) * fee_rate
    investor = total_amount * (2 / 3) * (1.0 - fee_rate)
    msg_text = 'Monthly Report\n'
    msg_text += 'Mined Coin, Total Mined Amount, Total BTC Amount, Average BTC Per Day, Owner/Investor\n'
    msg_text += '{}, {:.6f}, {:.6f}, {:.6f}, {:.6f}/{:.6f}\n'\
        .format('ZEC', total_amount, total_amount_btc, total_amount_btc/days, owner, investor)
    telegram_sender.send_message(msg_text, verbose=True)


@sched.scheduled_job('cron', day=21, hour=9)
def alarm_rent_fee():
    telegram_sender.send_message('Today is paying for an office rent fee\n')


@sched.scheduled_job('interval', minutes=10)
def timed_warning_message():
    unix_time = int(time.time())
    print('{} - Scheduled job[interval, minutes=10]: GPU Status checking'.format(utils.util.timestamp_to_datetime(unix_time)))
    msg = ''
    # comment
    for idx, host in enumerate(hosts):
        gpu = gpu_info.get_info(host)
        num_gpu = gpu["num_gpu"]
        if num_gpu is not num_gpu_set[idx]:
            msg += 'Warning Workers\n'
            msg += 'Message: worker(s) are dead\n'
            msg += '{} : Workers {}/{}\n'.format(hosts[idx], num_gpu, num_gpu_set[idx])

        for idx2, gpu_data in enumerate(gpu["gpu_info"]):
            temp = gpu_data["temp"]
            if float(temp) > gpu_temp_thresh:
                msg += 'Warning Temperature\n'
                msg += 'Message: The temperature of GPU is high\n'
                msg += '{} : {} GPU temp = {}\n'.format(hosts[idx], idx2, temp)
    if msg:
        telegram_sender.send_message(msg)


if __name__ == '__main__':
    sched.start()
