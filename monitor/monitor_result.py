from monitor.miningpoolhub_api import Dashboard
from monitor.whattomine_crawler import WhatToMine
from utils.util_api import UtilApi
import utils.util


def get_gpu_info(unix_time: int, gpu_info, hosts):
    msg = ''
    msg += 'Requested Time = {}\n'.format(utils.util.timestamp_to_datetime(unix_time))
    for host in hosts:
        gpu = gpu_info.get_info(host)
        msg += 'Host    : {}\n'.format(host)
        msg += 'Workers : {}\n'.format(gpu["num_gpu"])
        msg += '===============================\n'
        msg += '   GPU Id, Temp, Power, Fan\n'
        msg += '===============================\n'
        for idx, gpu_data in enumerate(gpu["gpu_info"]):
            msg += "{}, {}, {}, {}\n".format(idx, gpu_data["temp"], gpu_data["power"], gpu_data["fan"])

    return msg

def get_mph_info(unix_time: int, mph_apikey):
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
    msg = ''
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
        msg += " {}: {} {:9.5f} / BTC {:9.5f}\n".format(
            res_json['getdashboarddata']['data']['recent_credits'][i]['date'], coin_currency,
            res_json['getdashboarddata']['data']['recent_credits'][i]['amount'],
            btc_json['getdashboarddata']['data']['recent_credits'][i]['amount'])

    msg += "\n"
    msg += "Total Balance : \n"
    msg += "   {} {:12.5f}\n".format("BTC", bitcoin_dashboard.get_balance())
    msg += "   {} {:12.5f}\n".format("USD", bitcoin_dashboard.get_balance() * util.get_bitfinex())

    return msg


def get_price(unix_time: int):
    util = UtilApi()
    btc_bitfinex = util.get_bitfinex()
    zec_bitfinex = util.get_bitfinex(coin='zecusd')
    eth_bitfinex = util.get_bitfinex(coin='ethusd')
    currency = util.get_currency()
    coinone_price = util.get_coinone()

    msg = ''
    msg += 'Requested Time = {}\n'.format(utils.util.timestamp_to_datetime(unix_time))
    msg += "Currency:\n"
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

    return msg


def get_whattomine_result(unix_time: int):
    msg = ''
    msg += 'Requested Time = {}\n'.format(utils.util.timestamp_to_datetime(unix_time))
    res = WhatToMine()
    msg += res.get_result()

    return msg