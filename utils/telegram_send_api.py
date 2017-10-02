import requests
import json


class TelegramSendMessage:
    def __init__(self, telegram_apikey, telegram_chat_id):
        self.__telegram_apikey = telegram_apikey
        self.__telegram_chat_id = telegram_chat_id
        self.__base_url = 'https://api.telegram.org/bot{}/sendMessage?chat_id={}&text='.format(self.__telegram_apikey, self.__telegram_chat_id)

    def send_message(self, message, verbose=False):
        request_url = self.__base_url + message
        res = requests.get(request_url)
        if verbose:
            output = json.loads(res.text)
            print(json.dumps(output, indent=4))