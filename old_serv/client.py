import sys, json
import socket
import threading, time

from old_serv.lib_client import connect_guest

if len(sys.argv) == 1:
    adr = '127.0.0.1'
    port = 7777
else:
    adr, port = sys.argv[1], int(sys.argv[2])

def inp():
    while 1:
        data = input('Ваше сообщение: ')
        if data == 'exit':
            pass
        data = json.dumps(data).encode()
        sock.send(data)
        time.sleep(0.5)


def get_message():
    while True:

        with lock:
            data = sock.recv(1024)
            time.sleep(0.1)

        data = json.loads(data.decode())
        print(data)
        time.sleep(2)

with socket.socket(family = socket.AF_INET, type = socket.SOCK_STREAM, proto= 0) as sock:
    sock.connect((adr, port))
    t1 = threading.Thread(target=inp)
    t2 = threading.Thread(target=get_message)
    lock = threading.Lock()
    sock.send(b'login')

    t1.start()
    t2.start()
    t1.join()
    t2.join()
