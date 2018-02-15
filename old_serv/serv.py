import json
import socket
import select
import logging
import time


from lib_decoratorr import log
import log_config

app_log = logging.getLogger('app')

msg_server = {
    'response': '',
    'time': '',
    'allert': ''
}

clients = {}
clients_list = []


def read(cl):
    requests = {}
    for sock in cl:
        try:
            data = sock.recv(1024)
            requests[sock] = data
            print(data)
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
                    print(resp)
                    sock.send(resp)
                except: # конкретизировать исключение возникающее при отключении клиента
                    print('Клиент {} отключился'.format(sock.fileno()))
                    app_log.warning('client logout {} {}'.format(sock.fileno(), sock.getpeername()))
                    clients_list.remove(sock)





commands = {

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
            clients_list.append(sock)
            print(msg)

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




if __name__ == '__main__':
    main_loop()