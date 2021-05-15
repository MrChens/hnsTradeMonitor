#!/usr/bin/python
import time
from typing import Any
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


def nothing():
    print("nothing")
    pass


class DogHandler(FileSystemEventHandler):
    def __init__(self):
        pass

    def on_modified(self, event):
        # print(f"event type: {event.event_type} path :{event.src_path} modified")
        paths = event.src_path.rsplit("/", 1)
        dog_manager = DogManager()
        for index in range(len(paths)):
            if dog_manager.watch_file_name == paths[index]:
                print(paths[index])
                file = paths[index]
                dog_manager.triger_cb(file)
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
    path = '.'
    dog_handler = DogHandler()
    watch_file_name = ""

    def __init__(self, filename):
        logging.info("DogManager __init__")
        self.dog.schedule(event_handler=self.dog_handler, path=self.path, recursive=True)
        self.watch_file_name = filename
        pass

    def register_cb(self, func):
        logging.info("doge register_cb")
        self.dog_handler = func
        pass

    def triger_cb(self, file_name: Any) -> None:
        logging.info("dog triger_cb find file name:%s" % file_name)
        self.dog_handler()
        pass

    def start_watch(self):
        logging.info("dog start_watch")
        self.dog.start()
        pass

    def stop(self):
        logging.info("dog stoped")
        self.dog.stop()
        pass

    def join(self):
        logging.info("dog join")
        self.dog.join()
        pass


if __name__ == '__main__':
    def call_back():
        print("xxxxx")
        pass


    dog = DogManager("traders.json")
    dog.register_cb(call_back)
    dog.start_watch()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        dog.stop()
    dog.join()
