import time
import json
from socket import *




def connect_guest(sock, account_name, status = 'Yep, I am here'):
    msg_client = {
        "action": 'presence',
        "time": time.time(),
        "type": 'status',
        "user": {
            'account_name': account_name,
            'status': status
        }
    }
    data = json.dumps(msg_client).encode()
    sock.send(data)
    msg_server = sock.recv(2048)
    msg_server = json.loads(msg_server.decode())
    if msg_server['responce'] == '200':
        print(msg_server)
    elif msg_server['responce'] == '409':
        print('Данный ник занят')
        sys.exit()
    else:
        print('Возникла ошибка {} обратитесь к справке или напишите в поддержку'.format(msg_server['responce']))
        sys.exit()


def chat(addr, port, account_name):
    with socket(AF_INET, SOCK_STREAM) as sock:
        sock.connect((addr, port))
        connect_guest(sock, account_name)
        msg_client = {
            'action': 'msg',
            'time': '',
            'to': 'account_name',
            'from': 'account_name',
            'encoding':'ascii',
            'message':''
        }
        while True:
            data = input('Ваше сообщение: ')
            if data == 'exit':
                break
            msg_client['from'] = account_name
            msg_client['time'] = time.time()
            msg_client['message'] = data
            msg = json.dumps(msg_client).encode()
            sock.send(msg)

def chat2(addr, port, account_name):
    with socket(AF_INET, SOCK_STREAM) as sock:
        sock.connect((addr, port))
        connect_guest(sock, account_name)
        while True:
            data = sock.recv(1024)
            msg_serv = json.loads(data.decode())
            print(msg_serv['time'], msg_serv['from'], msg_serv['message'])
