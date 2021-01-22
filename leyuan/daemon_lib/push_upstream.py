from typing import List, Tuple
import json
import socket
import requests
import re
import time
import docker


hostname = socket.gethostname()


def get_dns_of_local_docker():
    try:
        docker_client = docker.from_env()
        containers = docker_client.containers.list()
        ret = {}
        for container in containers:
            port_dict = {}
            for inner_port_str, outer_ports in container.ports.items():
                # inner_port_str例如：'8080/tcp'
                if not outer_ports or not inner_port_str:
                    continue
                outer_port = int(outer_ports[0]['HostPort'])
                inner_port = int(re.findall(r'\d+', inner_port_str)[0])
                port_dict[inner_port] = outer_port
            ret[container.name] = port_dict
        return ret
    except:
        return {}


def register(name, instance, port, check_type, check_uri):
    """
    如果是docker容器，instance则为容器名
    如果不是docker容器，instance则为"服务名-端口"
    """
    data = {
        "ID": f'{hostname}-{instance}',
        "Name": name,
        "Tags": ['ly', check_type],
        "Address": "",
        "Port": port,
        "Meta": {},
        "EnableTagOverride": False,
        "Weights": {
            "Passing": 10,
            "Warning": 1
        },
        "check": {
            "interval": "5s",
            "timeout": "1s"
        }
    }
    # check_type取值: http | tcp
    # check_uri取值: http://localhost:41153/api 或 localhost:6379
    data['check'][check_type] = check_uri
    print(f'register: {hostname}-{name}')
    url = 'http://127.0.0.1:8500/v1/agent/service/register'
    requests.put(url, json=data)
    print(json.dumps(data))


def deregister(name):
    """
    按服务名注销所有service
    如果name为'*'，则注销本服务器所有service（下线服务器时有用）
    """
    url = 'http://127.0.0.1:8500/v1/catalog/node/' + hostname
    serviceMap = json.loads(requests.get(url).text)
    for serviceItem in serviceMap['Services'].values():
        if 'ly' in serviceItem['Tags'] and (name == '*' or serviceItem['Service'] == name):
            service_id = serviceItem['ID']
            print(f'deregister: {service_id}')
            url = f'http://127.0.0.1:8500/v1/agent/service/deregister/{service_id}'
            requests.put(url)


def wait_consul_passing(service: str, timeout: int, expect: int) -> Tuple[int, int]:
    """
    等待consul的service数量达到expect，最多等待timeout秒。
    返回: (最终状态为passing的节点数, 最终等待秒数)
    """
    start_at = time.time()
    total_passing = -1
    while time.time() - start_at < timeout:
        time.sleep(min(3, timeout))
        url = 'http://127.0.0.1:8500/v1/health/checks/' + service
        healthList = json.loads(requests.get(url).text)
        total_passing = sum(1 for x in healthList if x['Status'] == 'passing' and x['Node'] == hostname)
        if total_passing == expect:
            break
    return total_passing, int(time.time() - start_at)
