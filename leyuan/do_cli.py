import json
import requests
import socket
import time
import paho.mqtt.client as mqtt
from leyuan.consul_lib.catalog import get_leader_emqx


def pub_block_message(client_id, title, service_name, node_names: str):
    client = mqtt.Client(client_id=client_id + '-pub')
    emqx_ip = get_leader_emqx()
    print('get leader emqx_ip: ' + emqx_ip)
    assert emqx_ip, emqx_ip
    client.connect(emqx_ip, 1883, 60)
    payload = f'{service_name}|||{node_names}'
    ret = client.publish(f'nginx/{title}', payload, qos=2)
    print(ret)


def pub_exec_message(client_id, node_names: str, cmd: str):
    client = mqtt.Client(client_id=client_id + '-pub')
    emqx_ip = get_leader_emqx()
    print('get leader emqx_ip: ' + emqx_ip)
    assert emqx_ip, emqx_ip
    client.connect(emqx_ip, 1883, 60)
    payload = f'{node_names}|||{cmd}'
    ret = client.publish('docker/exec', payload, qos=2)
    print(ret)


def do_block(*, service: str, nodes: str):
    """
    使nginx屏蔽即将下线的服务
    --service=?    服务名称，例如：stage-project-api
    --nodes=?      节点列表（逗号分割）
    """
    assert service, '服务名称不能为空'
    assert nodes, '节点列表不能为空'
    client_id = socket.gethostname()
    pub_block_message(client_id, 'block', service, nodes)


def do_unblock(*, service: str, nodes: str):
    """
    使nginx取消屏蔽服务
    --service=?    服务名称，例如：stage-project-api
    --nodes=?      节点列表（逗号分割）
    """
    assert service, '服务名称不能为空'
    assert nodes, '节点列表不能为空'
    client_id = socket.gethostname()
    pub_block_message(client_id, 'unblock', service, nodes)


def do_exec(*, service: str, nodes: str, cmd: str, expect: str, timeout: str='180'):
    """
    通知nodes节点执行命令
    --service=?     服务名称，例如：stage-project-api-1
    --nodes=?       节点列表（逗号分隔）
    --cmd=?         需要执行的命令
    --expect=?      当且仅当多少服务在线后，才成功退出
    --timeout=?     超时未成功退出，则失败（默认:180，单位:秒）
    """
    assert service, '服务名称不能为空'
    assert nodes, '节点列表不能为空'
    assert cmd, '执行命令不能为空'
    assert expect, 'expect不能为空'
    expect_int = int(expect)
    timeout_int = int(timeout)
    client_id = socket.gethostname()
    pub_exec_message(client_id, nodes, cmd)
    start_at = time.time()
    total_passing = -1
    while time.time() - start_at < timeout_int:
        time.sleep(3)
        url = 'http://127.0.0.1:8500/v1/health/checks/' + service
        healthList = json.loads(requests.get(url).text)
        total_passing = sum(1 for x in healthList if x['Status'] == 'passing')
        if total_passing == expect_int:
            print('succeed in %d seconds.' % int(time.time() - start_at))
            return
    print('timeout exceed! service count: %d' % total_passing)
    exit(1)
