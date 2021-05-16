import time
import schedule
from datetime import datetime
from requests import exceptions
import logging

from monitor import NamebaseMonitor
from sawalonwatchdog import DogManager

if __name__ == '__main__':
    logging.basicConfig(filename='./logs/trader_monitor.log', format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',
                        level=logging.DEBUG)

    monitor = NamebaseMonitor()

    dog = DogManager("traders.json")
    dog.register_cb(monitor.reload_json)
    dog.start_watch()

    monitor.get_hns_price()
    monitor.dingmessage('HNS 小助手上班啦！')

    schedule.every(10).seconds.do(monitor.get_hns_price)
    schedule.every().hour.do(monitor.triger_log_price)
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        dog.stop()
        dog.join()
        logging.info('Exception Graceful shutdown of Baleen ingestion service.')
        monitor.dd_message_at('HNS 小助手下线啦！\n Graceful shutdown of Baleen ingestion service.')
    except Exception as e:
        logging.info('Exception %s' % (str(e)))
        monitor.dd_message_at('HNS 小助手下线啦！\n %s' % (str(e)))
