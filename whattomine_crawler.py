from bs4 import BeautifulSoup
import datetime
import time
import requests

def timestamp_to_datetime(unix_time: int, date_format='%Y-%m-%d %H:%M:%S') -> str:

    if isinstance(unix_time, int):
        output = datetime.datetime.fromtimestamp(unix_time).strftime(date_format)
    elif isinstance(unix_time, str):
        output = datetime.datetime.fromtimestamp(int(unix_time)).strftime(date_format)
    else:
        output = '0000-00-00 00:00:00'

    return output

class WhatToMine:
    def __init__(self):
        #1070 6ea
        self.url = 'http://whattomine.com/coins?utf8=%E2%9C%93&adapt_q_280x=0&adapt_q_380=0&adapt_q_fury=0&adapt_q_470=0&adapt_q_480=3&adapt_q_570=0&adapt_q_580=0&adapt_q_750Ti=0&adapt_q_10606=18&adapt_q_1070=6&adapt_1070=true&adapt_q_1080=0&adapt_q_1080Ti=7&eth=true&factor%5Beth_hr%5D=180.0&factor%5Beth_p%5D=720.0&grof=true&factor%5Bgro_hr%5D=213.0&factor%5Bgro_p%5D=780.0&x11gf=true&factor%5Bx11g_hr%5D=69.0&factor%5Bx11g_p%5D=720.0&cn=true&factor%5Bcn_hr%5D=3000.0&factor%5Bcn_p%5D=600.0&eq=true&factor%5Beq_hr%5D=2580.0&factor%5Beq_p%5D=720.0&lre=true&factor%5Blrev2_hr%5D=213000.0&factor%5Blrev2_p%5D=780.0&ns=true&factor%5Bns_hr%5D=6300.0&factor%5Bns_p%5D=930.0&lbry=true&factor%5Blbry_hr%5D=1620.0&factor%5Blbry_p%5D=720.0&bk2bf=true&factor%5Bbk2b_hr%5D=9600.0&factor%5Bbk2b_p%5D=720.0&bk14=true&factor%5Bbk14_hr%5D=15000.0&factor%5Bbk14_p%5D=750.0&pas=true&factor%5Bpas_hr%5D=5640.0&factor%5Bpas_p%5D=720.0&factor%5Bskh_hr%5D=159.0&factor%5Bskh_p%5D=720.0&factor%5Bl2z_hr%5D=420.0&factor%5Bl2z_p%5D=300.0&factor%5Bcost%5D=0.1&sort=Profitability24&volume=0&revenue=24h&factor%5Bexchanges%5D%5B%5D=&factor%5Bexchanges%5D%5B%5D=bittrex&factor%5Bexchanges%5D%5B%5D=bleutrade&factor%5Bexchanges%5D%5B%5D=bter&factor%5Bexchanges%5D%5B%5D=c_cex&factor%5Bexchanges%5D%5B%5D=cryptopia&factor%5Bexchanges%5D%5B%5D=poloniex&factor%5Bexchanges%5D%5B%5D=yobit&dataset=Main&commit=Calculate'

    def get_result(self):
        r = requests.get(self.url)
        soup = BeautifulSoup(r.text, 'html.parser')
        table_items = soup.find('table', {'class': 'table table-hover table-vcenter'})
        tr_items = table_items.find_all('tr')
        coin_items = list()

        for i in range(len(tr_items)-1):
            idx = i + 1
            flag = tr_items[idx].find_all('td', {'colspan': '9'})
            if not flag:
                item = dict()
                td_items = tr_items[idx].find_all('td')

                # td[0] - coin name
                coin_name = td_items[0].find_all('div')
                num_elements = len(coin_name[1].contents)

                item_coin_name = ''
                if num_elements is 1:
                    item_coin_name = coin_name[1].contents[0].strip()
                if num_elements is 3:
                    item_coin_name = coin_name[1].find('a').text

                # td[2] - diffculty & nethash
                diffculty = td_items[2].find('strong').text.strip()
                nethash = td_items[2].find('div', {'class': 'small_text'}).text.split('\n')
                nethash_value = nethash[1].strip()
                nethash_change = nethash[2].strip()
                #print(diffculty, nethash_value, nethash_change)

                # td[3] - est. rewards
                rewards = td_items[3].text.split('\n')
                item_rewards = rewards[2].strip()
                item_rewards_24h = rewards[3].strip()

                # td[6] - btc
                btc = td_items[6].text.split('\n')
                item_btc = btc[1].strip()
                item_btc_24h = btc[2].strip()
                #print(item_btc, item_btc_24h)

                # td[7] - profit
                profit = td_items[7].text.split('\n')
                item_total_profit = profit[1].strip()
                item_eff_profit = profit[3].strip()

                #print(item_coin_name, item_rewards, item_rewards_24h, item_btc, item_btc_24h,item_total_profit, item_eff_profit)
                item['rank'] = idx
                item['name'] = item_coin_name
                item['nethash'] = nethash_value
                item['nethash_change'] = nethash_change
                item['rewards'] = float(item_rewards.replace(',', ''))
                item['rewards_24h'] = float(item_rewards_24h.replace(',', ''))
                item['btc'] = float(item_btc)
                item['btc_24h'] = float(item_btc_24h)
                item['total_profit'] = item_total_profit
                item['effective_profit'] = item_eff_profit

                coin_items.append(item)
        
        unix_time = int(time.time())
        msg = 'Requested Time = {}\n'.format(timestamp_to_datetime(unix_time))
        msg += 'WhatToMine Top 15\n'
        msg += 'Rank, Name, Profit, BTC, Rewards, Difficulty, NetHash\n'
        for item in coin_items[0:14]:
            msg += '{:2d}, {}, {}, {:7.5f}, {:9.4f}, {}, {}\n'.\
                   format(item['rank'], item['name'].ljust(18), item['effective_profit'], item['btc_24h'], item['rewards_24h'], item['nethash'], item['nethash_change'])

        return msg
