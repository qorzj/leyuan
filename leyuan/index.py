from lesscli import Application
from leyuan import do_init, do_cli, do_daemon


if __name__ == '__main__':
    Application('leyuan集群管理工具')\
        .add('init', do_init.app)\
        .add('block', do_cli.do_block)\
        .add('exec', do_cli.do_exec)\
        .add('daemon', do_daemon.do_daemon)\
        .run()
