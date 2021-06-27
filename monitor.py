import requests
import json
import time
import schedule
from datetime import datetime
from requests import exceptions
import logging
import csv
from dd_notification import NotificationManager


class TraderMonitor:
    __monitor_session = requests.Session()

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

    def __update_trader_reload(self):
        with open('./data_monitor/traders_reload.json', 'w') as f:
            traders_dic = {"buys": self.buys, "sells": self.sells}
            traders_json = json.dumps(traders_dic)
            f.write(traders_json)

    def reload_json(self):
        with open('./data_monitor/traders.json', 'r') as f:
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
        self.__update_trader_reload()

    def trigger_log_price(self) -> None:
        self.should_log = True
        print("trigger_log_price")
        logging.info('trigger_log_price')
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
                logging.info('name_base_pro response:%s' % resp_json)
                price = resp_json.get('price')
                if self.should_log:
                    message = self.__get_time() + "\n" + " HNS current price:" + str(price)
                    NotificationManager().message_normal(message)
                    self.should_log = False
                    with open(r'./collect_data_monitor/prices.csv', 'a', encoding='utf-8') as f:
                        # date price
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
                    self.__update_trader_reload()
                    NotificationManager().message_at_subscribers(message)
                if float(price) <= float(buy_price):
                    message = self.__get_time() + "\n" + "HNS buy trigger " + str(buy_price) + ' now price is' + str(
                        price)
                    self.buys.remove(buy_price)
                    self.__update_trader_reload()
                    NotificationManager().message_at_subscribers(message)
                logging.info('******↓↓↓ current sells & buys ↓↓↓******')
                logging.info(self.sells)
                logging.info(self.buys)
                logging.info('******↑↑↑ current sells & buys ↑↑↑******')
            else:
                logging.warning('response code %d' % response.status_code)
                message = self.__get_time() + "\n" + 'HNS exception:' + str(response.status_code)
                NotificationManager().message_normal(message)
        except exceptions.Timeout as http_exceptions:
            logging.warning('Exception TIMEOUT')
            message = self.__get_time() + "\n" + 'HNS Timeout:' + str(http_exceptions)
            NotificationManager().message_normal(message)
        except exceptions.HTTPError as http_exceptions:
            logging.warning('Exception HTTPError')
            message = self.__get_time() + "\n" + 'HNS HTTPError:' + str(http_exceptions)
            NotificationManager().message_normal(message)
        except exceptions.RequestException as req_exceptions:
            logging.warning('Exception RequestException')
            message = self.__get_time() + "\n" + 'HNS RequestException:' + str(req_exceptions)
            NotificationManager().message_normal(message)
        logging.info('↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑ END REQ %s↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑' % (self.__get_time()))


if __name__ == '__main__':
    log_file = './logs_monitor/nameMonitor.log'
    if log_file is not None:
        filemode_val = 'w'
    else:
        filemode_val = 'a'
    logging.basicConfig(filename=log_file,
                        format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',
                        level=logging.DEBUG, filemode=filemode_val)
    monitor = TraderMonitor()
    monitor.get_hns_price()
    NotificationManager().message_normal('HNS 小助手上班啦！')
    schedule.every(10).seconds.do(monitor.get_hns_price)
    schedule.every(5).seconds.do(monitor.trigger_log_price)
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            logging.critical('Exception Graceful shutdown of Baleen ingestion service.')
            NotificationManager().message_at_all('HNS 小助手下线啦！\n Graceful shutdown of Baleen ingestion service.')
        except Exception as e:
            logging.critical('Exception %s' % (str(e)))
            NotificationManager().message_at_all('HNS 小助手下线啦！\n %s' % (str(e)))
