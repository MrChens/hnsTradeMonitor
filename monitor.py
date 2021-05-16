import requests
import json
import time
import schedule
from datetime import datetime
from requests import exceptions
import logging
import csv

class SawalonNamebaseMonitor():
    __monitor_session = requests.Session()
    __dingding_session = requests.Session()

    def __init__(self):
        self.sells = []
        self.buys = []
        self.reload_json()
        self.should_log = False
        pass

    def __get_time(self) -> str:
        now = datetime.now()
        format_date = now.strftime("%d/%m/%Y %H:%M:%S")
        return format_date

    def reload_json(self):
        with open('traders.json', 'r') as f:
            monitor_json_string = f.read()
            logging.info('monitor reload price json %s' % monitor_json_string)
            price_json = json.loads(monitor_json_string)
            temp_sells = price_json.get('sells')
            temp_buys = price_json.get('buys')
            # strip duplicates
            if len(temp_buys) > 0:
                self.buys.extend(temp_buys)
                temp_list = list(set(self.buys))
                # keep order
                temp_list.sort(key=self.buys.index)
                self.buys = temp_list
            if len(temp_sells) > 0:
                self.sells.extend(temp_sells)
                temp_list = list(set(self.sells))
                temp_list.sort(key=self.sells.index)
                self.sells = temp_list
            # print(self.sells)
            # print(self.buys)
            logging.info('******↓↓↓ reload sells & buys ↓↓↓******')
            logging.info(self.sells)
            logging.info(self.buys)
            logging.info('******↑↑↑ reload sells & buys ↑↑↑******')

    def __dd_message_common(self, message):
        webhook = "https://oapi.dingtalk.com/robot/send?access_token" \
                  "=7c7869c5ec3ac506ef5bcae2c2e1044439742c8d86c4197d4715c41511b2c018 "
        header = {
            "Content-Type": "application/json",
            "Charset": "UTF-8"
        }
        message_json = json.dumps(message)
        info = self.__dingding_session.post(url=webhook, data=message_json, headers=header)
        logging.info(info.text)
        pass

    def dd_message_at(self, text):
        message = {
            "msgtype": "text",
            "text": {
                "content": text
            },
            "at": {
                "atMobiles": [
                    "13107935242"
                ],
                "isAtAll": False
            }
        }
        self.__dd_message_common(message)
        pass

    def dingmessage(self, text):
        message = {

            "msgtype": "text",
            "text": {
                "content": text
            },
            "at": {
                "isAtAll": False
            }

        }
        self.__dd_message_common(message)
        pass

    def triger_log_price(self) -> None:
        self.should_log = True
        logging.info('triger_log_price')
        pass

    def get_hns_price(self):
        url = 'https://www.namebase.io/api/v0/ticker/price?symbol=HNSBTC'
        logging.info('↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓ START REQ %s↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓' % (self.__get_time()))
        try:
            headers = self.__monitor_session.headers
            headers[
                'User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, ' \
                                'like Gecko) Version/14.0.2 Safari/605.1.15 '
            response = self.__monitor_session.get(url=url, timeout=5, headers=headers)
            response.raise_for_status()
            if response.status_code == 200:
                resp_json = json.loads(response.text)
                logging.info('namebase response:%s' % resp_json)
                price = resp_json.get('price')
                if self.should_log:
                    message = self.__get_time() + "\n" + " HNS current price:" + str(price)

                    self.dingmessage(message)
                    self.should_log = False
                    with open(r'prices.csv', 'a', encoding='utf-8') as f:
                        #date price
                        writer = csv.writer(f)
                        writer.writerow([self.__get_time(), price])
                sell_price = 9999
                buy_price = 0
                if len(self.sells) > 0:
                    sell_price = min(self.sells)
                if len(self.buys) > 0:
                    buy_price = max(self.buys)
                # print(self.sells)
                # print(self.buys)
                if float(price) >= float(sell_price):
                    message = self.__get_time() + "\n" + "HNS sell trigger " + str(sell_price) + ' now price is' + str(
                        price)
                    self.sells.remove(sell_price)
                    self.dd_message_at(message)
                if float(price) <= float(buy_price):
                    message = self.__get_time() + "\n" + "HNS buy trigger " + str(buy_price) + ' now price is' + str(
                        price)
                    self.buys.remove(buy_price)
                    self.dd_message_at(message)
                logging.info('******↓↓↓ current sells & buys ↓↓↓******')
                logging.info(self.sells)
                logging.info(self.buys)
                logging.info('******↑↑↑ current sells & buys ↑↑↑******')
            else:
                logging.warning('response code %d' % response.status_code)
                message = self.__get_time() + "\n" + 'HNS exception:' + str(response.status_code)
                self.dingmessage(message)
        except exceptions.Timeout as e:
            logging.warning('Exception TIMEOUT')
            message = self.__get_time() + "\n" + 'HNS exception:' + str(e)
            self.dingmessage(message)
        except exceptions.HTTPError as e:
            logging.warning('Exception HTTPSERVER')
            message = self.__get_time() + "\n" + 'HNS exception:' + str(e)
            self.dingmessage(message)

        logging.info('↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑ END REQ %s↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑' % (self.__get_time()))


if __name__ == '__main__':
    logging.basicConfig(filename='nameMonitor.log', format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',
                        level=logging.INFO)
    monitor = SawalonNamebaseMonitor()
    monitor.get_hns_price()
    monitor.dingmessage('HNS 小助手上班啦！')
    schedule.every(10).seconds.do(monitor.get_hns_price)
    schedule.every(5).seconds.do(monitor.triger_log_price)
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            logging.critical('Exception Graceful shutdown of Baleen ingestion service.')
            monitor.dd_message_at('HNS 小助手下线啦！\n Graceful shutdown of Baleen ingestion service.')
        except Exception as e:
            logging.critical('Exception %s' % (str(e)))
            monitor.dd_message_at('HNS 小助手下线啦！\n %s' % (str(e)))
