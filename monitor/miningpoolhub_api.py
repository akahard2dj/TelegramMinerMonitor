import requests
import json


class Dashboard:
    def __init__(self, apikey):
        self.__apikey = apikey
        self.result = ''
        self._result_json = None

    def request_api(self, coin='zcash', action='getdashboarddata'):
        url = 'https://{}.miningpoolhub.com/index.php?page=api&action={}&api_key={}'.format(coin, action, self.__apikey)
        res = requests.get(url)
        self._result_json = json.loads(res.text)        

    def get_json(self):
        return self._result_json
    
    def get_balance(self):
        return self._result_json["getdashboarddata"]["data"]["balance"]["confirmed"]

    def get_dashboard_info(self):
        name = self._result_json["getdashboarddata"]["data"]["pool"]["info"]["name"]
        currency = self._result_json["getdashboarddata"]["data"]["pool"]["info"]["currency"]
        return name, currency

    def get_last_credits(self):
        return self._result_json["getdashboarddata"]["data"]["recent_credits_24hours"]["amount"]

    def get_hashrate(self):
        return self._result_json["getdashboarddata"]["data"]["personal"]["hashrate"]