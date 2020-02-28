import socket
import time
import threading
import paho.mqtt.client as mqtt
from leyuan.consul_lib.catalog import get_leader_emqx
from leyuan.utils import not_ready
from leyuan.daemon_lib.block_callback import do_block_once
from leyuan.daemon_lib.exec_callback import do_exec_once


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    if not not_ready('nginx'):
        client.subscribe("nginx/+", qos=2)
    if not not_ready('docker'):
        client.subscribe("docker/exec", qos=2)


def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    payload = msg.payload.decode()
    if msg.topic == 'nginx/block':
        service_name, node_names = payload.split('|||', 1)
        print('block: ', service_name, node_names)
        do_block_once(service_name, node_names, True)
    elif msg.topic == 'nginx/unblock':
        service_name, node_names = payload.split('|||', 1)
        print('unblock: ', service_name, node_names)
        do_block_once(service_name, node_names, False)
    elif msg.topic == 'docker/exec':
        node_names, cmd = payload.split('|||', 1)
        if socket.gethostname() in node_names.split(','):  # 注意：不能使用client.client_id，否则会莫名退出
            print('execute:', cmd)
            do_exec_once(cmd)
    else:
        print('unknown topic: [%s]' % msg.topic)


def on_disconnect(client, userdata, rc):
    print('Disconnected with result code ' + str(rc))


def run():
    cur_emqx_ip = ''
    client_id = socket.gethostname()
    client = mqtt.Client(client_id=client_id)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    client.loop_start()  # 启动监听线程
    while True:
        emqx_ip = get_leader_emqx()
        print(f'cur_emqx_ip={cur_emqx_ip} emqx_ip={emqx_ip}')
        if cur_emqx_ip != emqx_ip:
            print('get leader emqx_ip: ' + emqx_ip)
            try:
                if client.is_connected():  # 重连之前先断开连接
                    client.disconnect()
                client.connect(emqx_ip, 1883, 60)
                time.sleep(10)
                if not client.is_connected():  # 如果连接失败则需要reinit
                    client.disconnect()
                    client.reinitialise(client_id=client_id)
                    client.on_connect = on_connect
                    client.on_message = on_message
                    client.on_disconnect = on_disconnect
                    print('reinit done')
                    client.connect(emqx_ip, 1883, 60)
                    time.sleep(10)
                    print('connected:', client.is_connected())
                cur_emqx_ip = emqx_ip
            except Exception as e:
                print('connect failed:', e)
        time.sleep(120)
