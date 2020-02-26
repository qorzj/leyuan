# ly::daemon  // push, pull, upstream ly daemon
import time
import threading
import random
from leyuan.daemon_lib import pull_upstream, push_upstream, mqtt_consumer
from leyuan.utils import not_ready


def pull_forever():
    while True:
        if not not_ready('nginx'):
            pull_upstream.do_pull_upstream_once()
        time.sleep(23 + random.random())


def push_forever():
    while True:
        if not not_ready('docker'):
            push_upstream.push_upstream_once()
        time.sleep(19 + random.random())


def do_daemon():
    """
    启动守护进程，负责定时push/pull、更新upstream、监听执行命令等
    """
    threading.Thread(target=pull_forever).start()
    threading.Thread(target=push_forever).start()
    mqtt_consumer.run()
