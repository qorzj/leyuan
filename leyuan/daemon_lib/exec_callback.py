import os
import time
from leyuan.daemon_lib.push_upstream import push_upstream_once


def do_exec_once(cmd):
    os.system(cmd)
    time.sleep(1)
    push_upstream_once()
