from socket import *
from select import select
import sys
from lib_client import connect_guest
address = ('localhost', 7777)

def echo_client():
    with socket(AF_INET,SOCK_STREAM) as sock:
        sock.connect(address)
        # connect_guest(sock, 'pilik')
        while True:
            msg = input('Введите сообщение: ')
            if msg == 'exit':
                break
            sock.send(msg.encode())
            data = sock.recv(1024).decode()
            print('Ответ:', data)

echo_client()


