import requests
import json
import logging


class DDNotification:
    __notification_session = requests.Session()
    __mobile_subscribers = ""
    __notification_url = "https://oapi.dingtalk.com/robot/send?access_token" \
                         "=7c7869c5ec3ac506ef5bcae2c2e1044439742c8d86c4197d4715c41511b2c018"

    def __init__(self):
        with open('./data_monitor/subscribers.json', 'r') as f:
            notifier_json_string = f.read()
            self.__mobile_subscribers = json.loads(notifier_json_string)
        pass

    def __send_message(self, message):
        header = {
            "Content-Type": "application/json",
            "Charset": "UTF-8"
        }
        message_json = json.dumps(message)
        info = self.__notification_session.post(url=self.__notification_url, data=message_json, headers=header)
        logging.info(info.text)
        pass

    def dd_message_at_subscribers(self, text):
        message_dic = {"msgtype": "text", "text": {
            "content": text
        }, "at": self.__mobile_subscribers}
        self.__send_message(message_dic)
        pass

    def dd_message_normal(self, text):
        message = {
            "msgtype": "text",
            "text": {
                "content": text
            },
            "at": {
                "isAtAll": "False"
            }
        }
        self.__send_message(message)
        pass

    def dd_message_at_all(self, text):
        message = {
            "msgtype": "text",
            "text": {
                "content": text
            },
            "at": {
                "isAtAll": "True"
            }
        }
        self.__send_message(message)
        pass


def singleton(class_):
    instances = {}
    def inner(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return inner


@singleton
class NotificationManager(object):
    notification = DDNotification()

    def __init__(self):
        pass

    def message_normal(self, message):
        self.notification.dd_message_normal(message)
        pass

    def message_at_subscribers(self, message):
        self.notification.dd_message_at_subscribers(message)
        pass

    def message_at_all(self, message):
        self.notification.dd_message_at_all(message)
        pass


if __name__ == '__main__':
    logging.basicConfig(filename='./logs_monitor/notification.log', format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',
                        level=logging.INFO)
    logging.debug("hello dd_notification debug")
    logging.info("hello dd_notification info")
    notificationManager = NotificationManager()
    notificationManager1 = NotificationManager()
    NotificationManager().message_at_subscribers("HNS hallo")
    notificationManager.message_at_subscribers("HNS dd_message test")
    notificationManager.message_at_all("HNS dd_message test")
    notificationManager.message_normal("HNS hello")
