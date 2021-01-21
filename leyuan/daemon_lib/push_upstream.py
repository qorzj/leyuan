from typing import List, Tuple
import json
import socket
import requests
import re
import time
import docker


hostname = socket.gethostname()
docker_client = docker.from_env()


def get_dns_of_local_docker():
    try:
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


def register(name, port, check_type, check_uri):
    data = {
        "ID": f'{hostname}-{name}',
        "Name": name,
        "Tags": ['ly'],
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
    service_id = f'{hostname}-{name}'
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
        time.sleep(3)
        url = 'http://127.0.0.1:8500/v1/health/checks/' + service
        healthList = json.loads(requests.get(url).text)
        total_passing = sum(1 for x in healthList if x['Status'] == 'passing')
        if total_passing == expect:
            break
    return total_passing, int(time.time() - start_at)
