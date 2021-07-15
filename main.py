import logging
from monitor import TraderMonitor
from trader_watchdog import DogManager
from dd_notification import NotificationManager
import time
import schedule
from datetime import datetime
import random

if __name__ == '__main__':
    log_file = './logs_monitor/trader.log'
    logging.basicConfig(filename=log_file,
                        format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',
                        level=logging.INFO)
    monitor = TraderMonitor()
    dog = DogManager()
    dog.schedule(filename="traders.json", monitor_path="./data_monitor/")
    dog.register_cb(monitor.reload_json)
    dog.start_watch()
    now = datetime.now()
    message = now.strftime("%d/%m/%Y %H:%M:%S") + "\nHNS 小助手上班啦！"
    NotificationManager().message_normal(message)
    schedule.every(1).seconds.do(monitor.get_hns_price)
    schedule.every().hour.do(monitor.trigger_log_price)
    try:
        while True:
            schedule.run_pending()
            sleep_time = random.randint(1, 2)
            time.sleep(sleep_time)
    except (KeyboardInterrupt, SystemExit):
        logging.info('Exception Graceful shutdown of Baleen ingestion service.')
        NotificationManager().message_at_all('HNS 小助手下线啦！\n Graceful shutdown of Baleen ingestion service.')
        dog.stop()
        dog.join()
    except Exception as e:
        logging.info('Exception %s' % (str(e)))
        NotificationManager().message_at_all('HNS 小助手下线啦！\n %s' % (str(e)))
#        dog.stop()
#        dog.join()
#        dog.start_watch()
