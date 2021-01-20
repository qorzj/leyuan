from lesscli import Application
from leyuan import do_init, do_cli


def main():
    Application('leyuan集群管理工具') \
        .add('init', do_init.app) \
        .add('register', do_cli.do_register) \
        .add('deregister', do_cli.do_deregister) \
        .add('upstream', do_cli.do_upstream) \
        .add('wait', do_cli.do_wait) \
        .run()


if __name__ == '__main__':
    main()
