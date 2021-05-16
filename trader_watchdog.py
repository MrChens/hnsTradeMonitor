#!/usr/bin/python
import time
from typing import Any
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class DogHandler(FileSystemEventHandler):
    def __init__(self):
        print("Dog handler init")
        pass

    def on_modified(self, event):
        logging.info(f"on_modified: {event.event_type} path :{event.src_path} modified")
        paths = event.src_path.rsplit("/", 1)
        dog_manager = DogManager()
        for index in range(len(paths)):
            if dog_manager.watch_file_name == paths[index]:
                print(paths[index])
                file = paths[index]
                dog_manager.trigger_cb(file)
        pass

    def on_closed(self, event):
        pass

    def on_created(self, event):
        pass

    def on_deleted(self, event):
        pass

    def on_moved(self, event):
        pass


def singleton(class_):
    instances = {}

    def inner(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return inner


@singleton
class DogManager(object):
    dog = Observer()
    dog_handler = DogHandler()
    watch_file_name = ""

    def __init__(self):
        print("DogManager init call..........")
        pass

    def schedule(self, filename, monitor_path):
        logging.info("DogManager schedule filename:%s" % filename)
        print("DogManager schedule filename:%s" % filename)
        self.watch_file_name = filename
        self.dog.schedule(event_handler=self.dog_handler, path=monitor_path, recursive=True)
        pass

    def register_cb(self, func):
        logging.info("doge register_cb")
        self.dog_handler = func
        pass

    def trigger_cb(self, file_name: Any) -> None:
        logging.info("dog trigger_cb find file name:%s" % file_name)
        print("trigger file: %s" % file_name)
        self.dog_handler()
        pass

    def start_watch(self):
        logging.info("dog start_watch")
        self.dog.start()
        pass

    def stop(self):
        logging.info("dog stopped")
        self.dog.stop()
        pass

    def join(self):
        logging.info("dog join")
        self.dog.join()
        pass


if __name__ == '__main__':
    def call_back():
        print("call back test")
        pass

    logging.basicConfig(filename='./logs_monitor/watchdog.log', format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',
                        level=logging.DEBUG)
    dog = DogManager()
    dog.schedule(filename="traders.json", monitor_path="./data_monitor/")
    dog.register_cb(call_back)
    dog.start_watch()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        dog.stop()
    dog.join()
