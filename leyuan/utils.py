import os
from pathlib import Path


def exe(cmd: str):
    print(cmd)
    ret = os.system(cmd)
    return ret == 0


def not_ready(cmd: str):
    return os.system("which " + cmd) != 0


def assert_exe(cmd: str, message=''):
    if not exe(cmd):
        print(message)
        exit(1)


def makedir(real_path):
    Path(real_path).mkdir(parents=True, exist_ok=True)
