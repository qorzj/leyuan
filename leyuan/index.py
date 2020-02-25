"""
ly::init::server  // consul, mqtt ly init server
ly::init::docker_client  // consul ly init docker_client
ly::daemon  // push, pull, upstream ly daemon
ly::cli::block  // ly block --shard=?
ly::cli::exec  // ly exec --shard=? --cmd=? --barrier=? --timeout=180
"""
from lesscli import Application
from leyuan import do_init


if __name__ == '__main__':
    Application('leyuan集群管理工具')\
        .add('init', do_init.app)\
        .run()
