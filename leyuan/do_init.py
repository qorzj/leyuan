from lesscli import Application
from leyuan.utils import makedir, not_ready, assert_exe, exe


class ConsulAgentCtx:
    def __enter__(self):
        if not_ready('consul'):
            assert_exe('wget https://h5.parsec.com.cn/arms/consul -O /usr/bin/consul', '下载失败，请检查网络环境')
            assert_exe('chmod +x /usr/bin/consul')

        makedir('/opt/leyuan/upstream')
        makedir('/opt/leyuan/consul/data')
        makedir('/opt/leyuan/consul/log')
        makedir('/opt/leyuan/consul.d')
        with open('/opt/leyuan/watch.sh', 'w') as f:
            f.write('ly upstream')
        assert_exe('chmod +x /opt/leyuan/watch.sh')
        assert_exe('touch /opt/leyuan/upstream/upstream.list')
        assert_exe('rm -rf /opt/leyuan/consul.d/*')
        assert_exe('rm -rf /opt/leyuan/consul/data/*')

    def __exit__(self, exc_type, exc_val, exc_tb):
        assert_exe('sleep 3')
        exe('consul catalog nodes')
        assert_exe('nohup consul watch -type=services /opt/leyuan/watch.sh >/opt/leyuan/consul/log/watch.log 2>&1 &')


def do_init_server(*, server_count: int=1, join_ip: str='', is_first: str='x', bind: str='eth0'):
    """
    安装server环境(consul)
      --server_count=?    集群中server的总数，默认为1，推荐为3
      --join_ip=?         另一个server的内网IP，第一个server不用设置
      --is_first          是否第一个server
      --bind=?            本地网卡标识，默认为eth0
    """
    if is_first == 'x':
        assert join_ip, '非第一个server需要设置join_ip'
    else:
        assert not join_ip, '第一个server不用设置join_ip'
    with ConsulAgentCtx():
        assert_exe(
            'nohup consul agent' +
            '  -server ' +
            f'  -bootstrap-expect={server_count} ' +
            '  -bind=\'{{ GetInterfaceIP "' + bind + '" }}\' ' +
            (f'  -join={join_ip} ' if join_ip else '') +
            '  -data-dir=/opt/leyuan/consul/data ' +
            '  -config-dir=/opt/leyuan/consul.d >/opt/leyuan/consul/log/agent.log 2>&1 &'
        )


def do_init_client(*, join_ip: str='', bind: str='eth0'):
    """
    安装client环境(consul)
      --join_ip=?         另一个server的内网IP
      --bind=?            本地网卡标识，默认为eth0
    """
    assert join_ip, '需要设置join_ip'
    with ConsulAgentCtx():
        assert_exe(
            'nohup consul agent' +
            '  -bind=\'{{ GetInterfaceIP "' + bind + '" }}\' ' +
            f'  -join={join_ip} ' +
            '  -data-dir=/opt/leyuan/consul/data ' +
            '  -config-dir=/opt/leyuan/consul.d >/opt/leyuan/consul/log/agent.log 2>&1 &'
        )


app = Application('初始化consul')\
    .add('server', do_init_server)\
    .add('client', do_init_client)
