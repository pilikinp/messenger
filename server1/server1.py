
import socket
import json
import threading
import time


list = {}
i = 0
prog = \
    {
        "+" : (10, 20),
        "-" : (35, 3),
        "*" : (4.5, 10),
        "/" : (9, 4.2)
    }

server_sock = socket.socket(family = socket.AF_INET, type = socket.SOCK_STREAM, proto = 0) # TCP
server_sock.bind(("", 7777))
server_sock.listen(5)

clients = {}
# server_sock.settimeout(5)
msg_server = {
    'responce': '',
    'time': '',
    'allert': ''
}


def msg(sock, to, from_, message):

    if to in clients:
        data = json.dumps(message).encode()
        clients[to].send(data)
    else:
        msg_server['responce'] = '404'
        msg_server['allert'] = 'Not found'
        msg_server['time'] = time.time()
        data = json.dumps(msg_server).encode()
        sock.send(data)



def rec(sock):
    while True:
        msg = sock.recv(2048)
        msg = json.loads(msg.decode())
        commands[msg['action']](sock, msg['to'],msg['from'], msg['message'])




def presence(sock, account_name, status):

    if account_name in clients:
        msg_server['responce'] = '409'
        msg_server['time'] = time.time()
        msg_server['allert'] = 'Conflict'
        data = json.dumps(msg_server).encode()
        sock.send(data)



    else:
        msg_server['responce'] = '200'
        msg_server['time'] = time.time()
        msg_server['allert'] = 'Connection'
        clients[account_name] = sock
        data = json.dumps(msg_server).encode()
        sock.send(data)
        t2 = threading.Thread(target=rec, args=(sock,))
        t2.start()
        t2.join()


commands = {
    'presence': presence,
    'msg': msg
}

while True:
    sock, addr = server_sock.accept()
    msg = sock.recv(2048)
    msg = json.loads(msg.decode())
    commands[msg['action']](sock, msg['user']['account_name'], msg['user']['status'])
# list['sock {}'.format(i)]= sock
# list['addr {}'.format(i)]= addr
# i += 1



