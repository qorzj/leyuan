import json
import requests


# 获取当前的emqx节点(取当前在线的、IP最小的节点作为leader)
def get_leader_emqx():
    leader_node_ip = ''
    nodeMaps = json.loads(requests.get('http://127.0.0.1:8500/v1/catalog/nodes').text)
    nodes = [item['Node'] for item in nodeMaps]
    for node_name in nodes:
        url = 'http://127.0.0.1:8500/v1/catalog/node/' + node_name
        serviceMap = json.loads(requests.get(url).text)
        node_ip = serviceMap['Node']['Address']
        for serviceItem in serviceMap['Services'].values():
            if 'emqx' in serviceItem['Tags'] and serviceItem.get('Port'):
                if not leader_node_ip or node_ip < leader_node_ip:
                    leader_node_ip = node_ip
    return leader_node_ip or '127.0.0.1'
