import json
import requests


# 获取当前的emqx节点(取当前在线的、IP最小的节点作为leader)
def get_leader_emqx():
    leader_node_ip = ''
    serviceMaps = json.loads(requests.get('http://127.0.0.1:8500/v1/catalog/service/ly-emqx').text)
    for serviceItem in serviceMaps:
        node_ip = serviceItem.get('Address')
        if not leader_node_ip or node_ip < leader_node_ip:
            leader_node_ip = node_ip
    return leader_node_ip or '127.0.0.1'
