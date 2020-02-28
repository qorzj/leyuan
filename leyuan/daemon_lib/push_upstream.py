from typing import List
import json
import socket
import requests
import re
import docker
from docker.models.containers import Container


hostname = socket.gethostname()


def is_ly_name(name: str):
    if name.count('-') < 3:  # format JOB_STAGE-GROUP-APP_NAME-INDEX only
        return False
    segs = name.split('-')
    return re.match('^[0-9]+$', segs[-1]) is not None


def get_map_of_docker(containers: List[Container]):
    ret = {}
    for container in containers:
        port80 = port8080 = port = 0  # type: int
        name = container.name  # type: str
        if is_ly_name(name):
            tags = ['ly', 'docker']
        elif name == 'emqx':
            tags = ['emqx', 'docker']
        else:
            tags = ['docker']
        for inner_port, outer_ports in container.ports.items():
            if not outer_ports:
                continue
            if inner_port == '80/tcp':
                port80 = int(outer_ports[0]['HostPort'])
            elif inner_port == '8080/tcp':
                port8080 = int(outer_ports[0]['HostPort'])
            else:
                port = max(port, int(outer_ports[0]['HostPort']))
        if port80 or port8080:
            ret[name, port80 or port8080] = tags
        elif port:
            ret[name, port] = tags
    return ret


def get_set_of_consul():
    ret = set()
    services = json.loads(requests.get('http://127.0.0.1:8500/v1/agent/services').text).values()
    for service in services:
        if 'docker' in service['Tags']:
            ret.add((service['ID'], service['Port']))
    return ret


def register(name, port, tags):
    hostname = socket.gethostname()
    data = {
        "ID": f'{hostname}-{name}',
        "Name": name,
        "Tags": tags,
        "Address": "",
        "Port": port,
        "Meta": {},
        "EnableTagOverride": False,
        "Weights": {
            "Passing": 10,
            "Warning": 1
        },
        "check": {
            "tcp": "localhost:%d" % port,
            "interval": "10s",
            "timeout": "1s"
        }
    }
    print(f'register: {hostname}-{name}')
    url = 'http://127.0.0.1:8500/v1/agent/service/register'
    requests.put(url, json=data)


def deregister(name):
    print(f'deregister: {hostname}-{name}')
    url = f'http://127.0.0.1:8500/v1/agent/service/deregister/{hostname}-{name}'
    requests.put(url)


docker_client = docker.from_env()


def push_upstream_once():
    containers = docker_client.containers.list()
    map_of_docker = get_map_of_docker(containers)
    set_of_consul = get_set_of_consul()
    for key, tags in map_of_docker.items():
        if key not in set_of_consul:
            register(key[0], key[1], tags)

    for key in set_of_consul:
        if key not in map_of_docker:
            deregister(key[0])
