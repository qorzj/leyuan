import json
import requests
import socket
import time
import paho.mqtt.client as mqtt
from leyuan.consul_lib.catalog import get_leader_emqx


def pub_block_message(client_id, service_name, node_names: str):
    client = mqtt.Client(client_id=client_id)
    emqx_ip = get_leader_emqx()
    print('get leader emqx_ip: ' + emqx_ip)
    assert emqx_ip, emqx_ip
    client.connect(emqx_ip, 1883, 60)
    payload = f'{service_name}|||{node_names}'
    ret = client.publish('nginx/block', payload, qos=2)
    print(ret)


def pub_exec_message(client_id, node_names: str, cmd: str):
    client = mqtt.Client(client_id=client_id)
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
    --service=?    服务名称
    --nodes=?      节点列表（逗号分割）
    """
    assert service, '服务名称不能为空'
    assert nodes, '节点列表不能为空'
    client_id = socket.gethostname()
    pub_block_message(client_id, service, nodes)


def do_exec(*, service: str, nodes: str, cmd: str, barrier: str, timeout: str='180'):
    """
    通知nodes节点执行命令
    --service=?     服务名称
    --nodes=?       节点列表（逗号分隔）
    --cmd=?         需要执行的命令
    --barrier=?     最少多少服务在线后，才成功退出
    --timeout=?     超时未成功退出，则失败（默认:180，单位:秒）
    """
    assert service, '服务名称不能为空'
    assert nodes, '节点列表不能为空'
    assert cmd, '执行命令不能为空'
    assert barrier, 'barrier不能为空'
    barrier_int = int(barrier)
    timeout_int = int(timeout)
    client_id = socket.gethostname()
    pub_exec_message(client_id, nodes, cmd)
    start_at = time.time()
    while time.time() - start_at < timeout_int:
        time.sleep(3)
        url = 'http://127.0.0.1:8500/v1/agent/health/service/name/' + service
        healthList = json.loads(requests.get(url).text)
        total_passing = sum(1 for x in healthList if x['AggregatedStatus'] == 'passing')
        if total_passing >= barrier_int:
            return
    print('timeout exceed!')
    exit(1)
