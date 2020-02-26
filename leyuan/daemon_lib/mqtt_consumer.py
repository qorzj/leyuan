import socket
import time
import threading
import paho.mqtt.client as mqtt
from leyuan.consul_lib.catalog import get_leader_emqx
from leyuan.utils import not_ready
from leyuan.daemon_lib.block_callback import do_block_once
from leyuan.daemon_lib.exec_callback import do_exec_once


client = None


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    if not not_ready('nginx'):
        client.subscribe("nginx/block", qos=2)
    if not not_ready('docker'):
        client.subscribe("docker/exec", qos=2)


def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    payload = msg.payload.decode()
    if msg.topic == 'nginx/block':
        print('==== nginx/block received')
        service_name, node_names = payload.split('|||', 1)
        print('block: ', service_name, node_names)
        do_block_once(service_name, node_names)
    elif msg.topic == 'docker/exec':
        print('==== docker/exec received')
        print('==== payload:', payload)
        node_names, cmd = payload.split('|||', 1)
        print('====', client.client_id, node_names)
        print('====', client.client_id, node_names.split(','))
        if client.client_id in node_names.split(','):
            print('execute:', cmd)
            do_exec_once(cmd)
    else:
        print('unknown topic: [%s]' % msg.topic)


def on_disconnect(client, userdata, rc):
    print('Disconnected with result code ' + str(rc))


def connect():
    global client
    emqx_ip = get_leader_emqx()
    print('get leader emqx_ip: ' + emqx_ip)
    if client and emqx_ip:
        client.connect(emqx_ip, 1883, 60)
        print('connected')


def reconnect():
    global client
    while not time.sleep(10):
        if client and not client.is_connected():
            print('no connected, try to re-connect...')
            connect()


def run():
    global client
    client_id = socket.gethostname()
    client = mqtt.Client(client_id=client_id)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    connect()
    threading.Thread(target=reconnect).start()
    client.loop_forever()
