import re
from leyuan.daemon_lib.push_upstream import get_dns_of_local_docker, register, deregister, wait_consul_passing
from leyuan.daemon_lib.pull_upstream import do_pull_upstream_once


def do_register(*, service: str, check: str):
    """
    注册service
      --service=?    服务名称
      --check=?      健康检查链接。例如http://aa-bb-cc/，或tcp://ip:port
    """
    assert service, 'service不能为空'
    assert check.count('://', 1), 'check必须包含协议，例如 http://'
    protocol, check = check.split('://', 1)
    check_type = 'http' if protocol in ['http', 'https'] else protocol
    protocol_head = f'{protocol}://' if check_type == 'http' else ''
    url_segs = check.split('/', 1)
    host_part, path = (url_segs[0], '') if len(url_segs) == 1 else (url_segs[0], '/' + url_segs[1])
    host = host_part
    if ':' in host_part:
        port = int(host_part.split(':', 1)[1])
        host = host_part.split(':', 1)[0]
    elif protocol == 'https':
        port = 443
    elif protocol == 'http':
        port = 80
    else:
        raise ValueError('check必须包含端口，例如 tcp://127.0.0.1:3306')
    assert host, "check的域名部分不能为空"
    map_of_docker = get_dns_of_local_docker()
    if re.match(r'^[0-9.:]+$', host) or host == 'localhost':
        check_uri = f'{protocol_head}{host_part}{path}'
    else:
        assert host in map_of_docker, f'docker未运行容器{host}'
        outer_port = map_of_docker[host].get(port)
        assert outer_port, f'docker容器{host}需暴露{port}端口'
        check_uri = f'{protocol_head}127.0.0.1:{outer_port}{path}'
    register(service, port, check_type, check_uri)


def do_deregister(*, service: str):
    """
    取消注册service
      --service=?    服务名称
    """
    assert service, 'service不能为空'
    deregister(service)


def do_wait(*, service: str, timeout: str='60', expect: str='1'):
    """
    等待服务可用
      --service=?    服务名称
      --timeout=?    等待超时秒数
      --expect=?     期望正常的示例个数
    """
    assert service, 'service不能为空'
    timeout_int = int(timeout)
    expect_int = int(expect)
    total_passing, total_second = wait_consul_passing(service, timeout_int, expect_int)
    if total_passing == expect:
        print(f'succeed in {total_second} seconds.')
    else:
        print(f'timeout exceed! total_passing={total_passing}')


def do_upstream():
    do_pull_upstream_once()
