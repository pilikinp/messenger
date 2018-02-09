import json
import socket
import select
import logging
import time


from lib_decoratorr import log


app_log = logging.getLogger('app')

msg_server = {
    'responce': '',
    'time': '',
    'allert': ''
}

clients = {}
clients_list = []

@log
def presence(sock, account_name, status):

    if account_name in clients:
        msg_server['responce'] = '409'
        msg_server['time'] = time.time()
        msg_server['allert'] = 'Conflict'
        data = json.dumps(msg_server).encode()
        sock.send(data)
        app_log.debug('send error 409')



    else:
        msg_server['responce'] = '200'
        msg_server['time'] = time.time()
        msg_server['allert'] = 'Connection'
        clients[account_name] = sock
        data = json.dumps(msg_server).encode()
        sock.send(data)
        clients_list.append(sock)
        app_log.debug('send presence')

# def msg(sock, to, from_, message):
#
#     if to in clients:
#         data = json.dumps(message).encode()
#         clients[to].send(data)
#     else:
#         msg_server['responce'] = '404'
#         msg_server['allert'] = 'Not found'
#         msg_server['time'] = time.time()
#         data = json.dumps(msg_server).encode()
#         sock.send(data)

def read(cl):
    requests = {}
    for sock in cl:
        try:
            data = sock.recv(1024)
            requests[sock] = data
        except:   # конкретизировать исключение возникающее при отключении клиента
            print ('Клиент {} {} откл'.format(sock.fileno(), sock.getpeername()))
            app_log.warning('client logout {} {}'.format(sock.fileno(), sock.getpeername()))
            clients_list.remove(sock)
            print('текущий лист', clients_list)
    return requests

def write(requests, cl):
    for sock in clients_list:
        if sock in requests:
            resp = requests[sock]
            print(resp)
            for sock in cl:
                try:
                    sock.send(resp)
                except: # конкретизировать исключение возникающее при отключении клиента
                    print('Клиент {} отключился'.format(sock.fileno()))
                    app_log.warning('client logout {} {}'.format(sock.fileno(), sock.getpeername()))
                    clients_list.remove(sock)





commands = {
    'presence': presence,
    'msg': 'msg'
}



def main_loop():
    server_sock = socket.socket(family = socket.AF_INET, type = socket.SOCK_STREAM, proto = 0) # TCP
    server_sock.bind(("", 7777))
    server_sock.listen(5)
    server_sock.settimeout(0.2)


    while True:
        try:
            sock, addr = server_sock.accept()
        except OSError as e:
            pass                                                                  #timeout вышел
        else:
            msg = sock.recv(2048)
            msg = json.loads(msg.decode())
            commands[msg['action']](sock, msg['user']['account_name'], msg['user']['status'])
        finally:
            wait = 0
            r = []
            w = []
            try:
                r, w, e = select.select(clients_list, clients_list, [], wait)
            except:
                pass #сделать обработку ошибок
            print(clients_list)
            req = read(r)
            if req is not None:
                write(req, w)



# def rec(sock):
#     while True:
#         msg = sock.recv(2048)
#         msg = json.loads(msg.decode())
#         commands[msg['action']](sock, msg['to'],msg['from'], msg['message'])



