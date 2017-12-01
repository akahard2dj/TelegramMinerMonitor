import datetime
import time
import os

from apscheduler.schedulers.blocking import BlockingScheduler
from monitor.monitor_result import get_gpu_info, get_mph_info, get_whattomine_result
from monitor.gpu_status import GPUInfo

from monitor.miningpoolhub_api import Dashboard
from utils.telegram_send_api import TelegramSendMessage
from utils.util_api import UtilApi
import utils.util

'''
from database.mapping_base import session
from database.test_table import User

user_model = User()
user_model.set_entry('user', '홍길동', '1234')
session.add(user_model)
session.commit()
'''

sched = BlockingScheduler()

mph_apikey = os.environ["MPH_APIKEY"]
telegram_apikey = os.environ["TELEGRAM_APIKEY"]
telegram_chat_id = os.environ["TELEGRAM_CHAT_ID"]
hosts = ['miner1', 'miner2', 'miner3']
num_gpu_set = [6, 6, 6]
gpu_temp_thresh = 77.0

gpu_info = GPUInfo()
telegram_sender = TelegramSendMessage(telegram_apikey, telegram_chat_id)


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

#@sched.scheduled_job('interval', seconds=10)
#def deploy_test():
#    telegram_sender.send_message('test')
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
            msg += 'Warning Workeres\n'
            msg += 'Message: worker(s) are dead\n'
            msg += '{} : Workers {}/{}\n'.format(hosts[idx], num_gpu, num_gpu_set[idx])

        for idx2, gpu_data in enumerate(gpu["gpu_info"]):
            temp = gpu_data["temp"]
            if float(temp) > gpu_temp_thresh:
                msg += 'Warning Temprature\n'
                msg += 'Message: The temperature of GPU is high\n'
                msg += '{} : {} GPU temp = {}\n'.format(hosts[idx], idx2, temp)
    if msg:
        telegram_sender.send_message(msg)

if __name__ == '__main__':
    sched.start()
