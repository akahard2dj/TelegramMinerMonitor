import requests
from bs4 import BeautifulSoup

class MinerAPI():
    def __init__(self, port=12345):
        self._api_port = port
        
    def get_miner_info(self, host):
        url = 'http://{}:{}'.format(host, self._api_port)
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        tbl_region = soup.find('table', {'id': 'gpu_stat'})
        data_region = tbl_region.findAll('tr')
        gpu_data = list()
        for data in data_region[2:]:
            item = dict()
            item_data = data.findAll('td')
            item['name'] = item_data[0].text
            item['temp'] = item_data[1].text
            item['power'] = item_data[2].text
            item['hash'] = item_data[3].text
            item['hash_eff'] = item_data[4].text
            item['accepted'] = item_data[5].text
            item['rejected'] = item_data[6].text
            gpu_data.append(item)
            
        return gpu_data