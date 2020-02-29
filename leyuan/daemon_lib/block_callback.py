from typing import Dict
import json
from leyuan.daemon_lib.pull_upstream import do_pull_upstream_once


DEST = '/etc/nginx/conf.d'
NGINX_BIN = 'nginx'


def do_block_once(service_name: str, node_names: str, is_block: bool):
    # 注意：不能放到do_pull_upstream_once中，会有逻辑错误
    block_dict: Dict[str, int]  # {`service_name|node_name`: 1}}
    block_filename = DEST + '/block.meta'
    try:
        block_dict = json.loads(open(block_filename).read())
    except:
        block_dict = {}
    for node_name in node_names.split(','):
        if is_block:  # 屏蔽
            block_dict[f'{service_name}|{node_name}'] = 1
        else:  # 取消屏蔽
            block_dict.pop(f'{service_name}|{node_name}', None)

    with open(block_filename, 'w') as f:
        f.write(json.dumps(block_dict))

    do_pull_upstream_once()
