from socket import *
from select import select
import sys
address = ('localhost', 10000)

def echo_client():
    with socket(AF_INET,SOCK_STREAM) as sock:
        sock.connect(address)
        while True:
            msg = input('Введите сообщение: ')
            if msg == 'exit':
                break
            sock.send(msg.encode())
            data = sock.recv(1024).decode()
            print('Ответ:', data)

echo_client()


