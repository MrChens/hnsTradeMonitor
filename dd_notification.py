import requests
import json
import logging


class DDNotification:
    __dingding_session = requests.Session()
    __mobile_subscribers = ""

    def __init__(self):
        with open('subscribers.json', 'r') as f:
            notifier_json_string = f.read()
            logging.info('dd_message_notification reload notifications json %s' % notifier_json_string)
            self.__mobile_subscribers = json.loads(notifier_json_string)
        pass

    def send_message(self, message):
        webhook = "https://oapi.dingtalk.com/robot/send?access_token" \
                  "=7c7869c5ec3ac506ef5bcae2c2e1044439742c8d86c4197d4715c41511b2c018"
        header = {
            "Content-Type": "application/json",
            "Charset": "UTF-8"
        }
        message_json = json.dumps(message)
        info = self.__dingding_session.post(url=webhook, data=message_json, headers=header)
        logging.info(info.text)
        pass

    def dd_message_at_subsribers(self, text):
        message_dic = {"msgtype": "text", "text": {
            "content": text
        }, "at": self.__mobile_subscribers}
        self.send_message(message_dic)
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
        self.send_message(message)
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
        self.send_message(message)
        pass


if __name__ == '__main__':
    logging.basicConfig(filename='dd_message.log', format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',
                        level=logging.DEBUG)
    dd_message_notification = DDNotification()
    # dd_message_notification.dd_message_at_subsribers("HNS dd_message test")
    dd_message_notification.dd_message_at_all("HNS dd_message test")
    dd_message_notification.dd_message_normal("HNS hahah")