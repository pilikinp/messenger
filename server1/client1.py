import sys
import socket
from tkinter import *
import threading
import json
import time

from lib_client import connect_guest

if len(sys.argv) == 1:
    adr = '127.0.0.1'
    port = 7777
else:
    adr, port = sys.argv[1], int(sys.argv[2])



msg_client1 = {
    "action": 'msg',
    "time": time.time(),
    "to": '',
    "from": '',
    'encoding': 'ascii',
    'message': ''
}
################################
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


def rec():
    while True:
        data = sock.recv(1024)
        data = json.loads(data.decode())
        print(data)

def writ():
    while True:
        print('введите получателя')
        to = input()
        print('введите сообщение')
        msg = input()
        msg_client1["to"] = to
        msg_client1['message'] = msg
        data = json.dumps(msg_client1).encode()
        sock.send(data)

##############################################

sock = socket.socket(family = socket.AF_INET, type = socket.SOCK_STREAM, proto= 0)
sock.connect((adr, port))

connect_guest(sock, 'pilik')

# connect_guest(sock, 'pilik1')
# sock.send(b'123')
# while True:
#     print(sock.recv(1024))


# root = Tk()
# root.title('Messenger')
# e = Entry(root, width = 25)
# e.grid(row=1, column=1, padx=(1, 1))


t1 = threading.Thread(target=writ)
t2 = threading.Thread(target=rec)
t1.start()
t2.start()
t1.join()
t2.join()

# def run_tr():
#     text = e.get()
#     # text = text.encode()
#     t2 = threading.Thread(target= writ, args=(b'text'))
#     t2.start()
#     t2.join()

# b = Button(root, text='send',bg= 'white', fg = 'black', font = 'Arial', width = 22, height = 1, command = run_tr)
# b.grid(row = 2, column = 1, padx = (1, 1))
# root.mainloop()



