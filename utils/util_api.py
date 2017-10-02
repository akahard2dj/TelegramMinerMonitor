import requests
import json

class UtilApi:
    def __init__(self):
        self.url_currency = 'http://api.fixer.io/latest?symbols=KRW,EUR,JPY,CNY&base=USD'
        self.url_bitfinex = 'https://api.bitfinex.com/v1/pubticker/'
        self.currency = None

        self._request_api()

    def _request_api(self):
        res = requests.get(self.url_currency)
        self.currency = json.loads(res.text)

    def get_currency(self):
        return self.currency["rates"]

    def get_bitfinex(self, coin='btcusd'):
        url = self.url_bitfinex + coin
        res = requests.get(url)
        price = json.loads(res.text)
        return float(price["last_price"])

    def get_coinone(self, coin='btc'):
        url = 'https://api.coinone.co.kr/ticker?currency=all'
        res = requests.get(url)
        price = json.loads(res.text)
        return price
