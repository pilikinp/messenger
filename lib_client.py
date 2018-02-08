import time
import json
from socket import *
from multiprocessing import Process



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
    print(msg_server)

# def chat(addr, port, account_name = 'pilik'):
#     with socket(AF_INET, SOCK_STREAM) as sock:
#         sock.connect((addr, port))
#         connect_guest(sock, account_name)
#         while True:
#             msg = input('Ваше сообщение: ')
#             if msg == 'exit':
#                 break
#             sock.send(msg.encode())
#             data = sock.recv(1024).decode()
#             print(data)

def chat(addr, port, account_name = 'pilik'):
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
            print(data)
            msg_client['from'] = account_name
            msg_client['time'] = time.time()
            msg_client['message'] = data
            msg = json.dumps(msg_client).encode()
            sock.send(msg)

def chat2(addr, port, account_name = 'pilik'):
    with socket(AF_INET, SOCK_STREAM) as sock:
        sock.connect((addr, port))
        connect_guest(sock, account_name)
        while True:
            data = sock.recv(1024)
            msg_serv = json.loads(data.decode())
            print(msg_serv['time'], msg_serv['from'], msg_serv['message'])
#
# def rec(sock):
#     while True:
#         data = sock.recv(1024)
#         data = json.loads(data.decode())
#         print(data)
#
# def writ(sock):
#     while True:
#         print('введите получателя')
#         to = input()
#         print('введите сообщение')
#         msg = input()
#         if msg == 'exit':
#             break
#         msg_client1["to"] = to
#         msg_client1['message'] = msg
#         data = json.dumps(msg).encode()
#         sock.send(data)