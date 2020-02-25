import os
import json
import requests


DEST = '/etc/nginx/conf.d'
NGINX_BIN = 'nginx'


def do_pull_upstream_once():
    upstream_dict = {}
    identity_list = []
    nodeMaps = json.loads(requests.get('http://127.0.0.1:8500/v1/catalog/nodes').text)
    nodes = [item['Node'] for item in nodeMaps]
    for node_name in nodes:
        url = 'http://127.0.0.1:8500/v1/catalog/node/' + node_name
        serviceMap = json.loads(requests.get(url).text)
        node_ip = serviceMap['Node']['Address']
        for serviceItem in serviceMap['Services'].values():
            if 'ly' in serviceItem['Tags'] and serviceItem.get('Port'):
                service_name = serviceItem['ID']
                service_port = serviceItem['Port']
                identity_list.append([service_name, node_ip, service_port])
                upstream_dict.setdefault(service_name, [])
                upstream_dict[service_name].append('%s:%d' % (node_ip, service_port))

    identity_list.sort()
    meta_filename = DEST + '/upstream.meta'
    try:
        old_identity_list = json.loads(open(meta_filename).read())
    except:
        old_identity_list = []
    if old_identity_list != identity_list:
        with open(meta_filename, 'w') as f:
            f.write(json.dumps(identity_list))

        with open(DEST + '/upstream.list', 'w') as f:
            for key, val in upstream_dict.items():
                f.write('upstream %s {\n' % key)
                for item in val:
                    f.write('    server  %s;\n' % item)
                f.write('}\n')

        os.system('%s -s reload' % NGINX_BIN)
