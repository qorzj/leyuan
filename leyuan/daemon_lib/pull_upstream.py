from typing import Dict, List
import os
import json
import requests


DEST = '/etc/nginx/conf.d'
NGINX_BIN = 'nginx'


def do_pull_upstream_once():
    block_dict: Dict[str, int]  # {`service_name|node_name`: 1}}
    block_filename = DEST + '/block.meta'
    try:
        block_dict = json.loads(open(block_filename).read())
    except:
        block_dict = {}

    upstream_dict: Dict[str, List[str]] = {}  # {"app-doc-admin": ["192.168.0.105:10988", ...]], "app-momentum-h5": ["192.168.0.105:29364", ...], ...}
    nodeMaps = json.loads(requests.get('http://127.0.0.1:8500/v1/catalog/nodes').text)
    nodes = [item['Node'] for item in nodeMaps]
    for node_name in nodes:
        url = 'http://127.0.0.1:8500/v1/catalog/node/' + node_name
        serviceMap = json.loads(requests.get(url).text)
        node_ip = serviceMap['Node']['Address']
        for serviceItem in serviceMap['Services'].values():
            if 'ly' in serviceItem['Tags'] and serviceItem.get('Port'):
                service_name = serviceItem['Service'].rsplit('-', 1)[0]
                if f'{service_name}|{node_name}' in block_dict:  # blocked
                    continue
                service_port = serviceItem['Port']
                upstream_dict.setdefault(service_name, [])
                upstream_dict[service_name].append('%s:%d' % (node_ip, service_port))

    for key in upstream_dict:
        upstream_dict[key].sort()
    meta_filename = DEST + '/upstream.meta'
    try:
        old_upstream_dict = json.loads(open(meta_filename).read())
    except:
        old_upstream_dict = {}
    if old_upstream_dict != upstream_dict:
        with open(meta_filename, 'w') as f:
            f.write(json.dumps(upstream_dict))

        with open(DEST + '/upstream.list', 'w') as f:
            for key, val in upstream_dict.items():
                f.write('upstream %s {\n' % key)
                for item in val:
                    f.write('    server  %s;\n' % item)
                f.write('}\n')

        os.system('%s -s reload' % NGINX_BIN)
