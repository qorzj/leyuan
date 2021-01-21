from lesscli import Application
from leyuan.utils import makedir, not_ready, assert_exe


def do_init_server(*, server_count: int=1, join_ip: str='', is_first: str='x'):
    """
    安装server环境(consul)
      --server_count=?    集群中server的总数，默认为1，推荐为3
      --join_ip=?         另一个server的内网IP，第一个server不用设置
      --is_first          是否第一个server
    """
    if is_first == 'x':
        assert join_ip, '非第一个server需要设置join_ip'
    else:
        assert not join_ip, '第一个server不用设置join_ip'

    if not_ready('consul'):
        assert_exe('wget https://h5.parsec.com.cn/arms/consul -O /usr/bin/consul', '下载失败，请检查网络环境')
        assert_exe('chmod +x /usr/bin/consul')

    assert_exe('mkdir -p /opt/consul/data')
    assert_exe('mkdir -p /etc/consul.d')
    assert_exe(
        'nohup consul agent' +
        '  -server ' +
        f'  -bootstrap-expect={server_count} ' +
        '  -bind=\'{{ GetInterfaceIP "eth0" }}\' ' +
        (f'  -join={join_ip} ' if join_ip else '') +
        '  -data-dir=/opt/consul/data ' +
        '  -config-dir=/etc/consul.d &'
    )


def do_init_client(*, join_ip: str=''):
    """
    安装client环境(consul)
      --join_ip=?         另一个server的内网IP
    """
    assert join_ip, '需要设置join_ip'

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
    assert_exe(
        'nohup consul agent' +
        '  -bind=\'{{ GetInterfaceIP "eth0" }}\' ' +
        f'  -join={join_ip} ' +
        '  -data-dir=/opt/leyuan/consul/data ' +
        '  -config-dir=/opt/leyuan/consul.d >/opt/leyuan/consul/log/consul.log 2>&1 &'
    )
    assert_exe('consul watch -type=services -shell=/opt/leyuan/watch.sh')


app = Application('初始化consul')\
    .add('server', do_init_server)\
    .add('client', do_init_client)
