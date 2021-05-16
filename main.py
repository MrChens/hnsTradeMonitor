import time
import schedule
from datetime import datetime
from requests import exceptions
import logging

from monitor import NamebaseMonitor
from sawalonwatchdog import DogManager
from dd_notification import NotificationManager
if __name__ == '__main__':
    logging.basicConfig(filename='./logs/trader_monitor.log', format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',
                        level=logging.DEBUG)

    monitor = NamebaseMonitor()

    dog = DogManager("traders.json")
    dog.register_cb(monitor.reload_json)
    dog.start_watch()

    monitor.get_hns_price()
    NotificationManager().message_normal('HNS 小助手上班啦！')

    schedule.every(10).seconds.do(monitor.get_hns_price)
    schedule.every().hour.do(monitor.trigger_log_price)
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        dog.stop()
        dog.join()
        logging.info('Exception Graceful shutdown of Baleen ingestion service.')
        NotificationManager().message_at_all('HNS 小助手下线啦！\n Graceful shutdown of Baleen ingestion service.')
    except Exception as e:
        logging.info('Exception %s' % (str(e)))
        NotificationManager().message_at_all('HNS 小助手下线啦！\n %s' % (str(e)))
