import select
from socket import socket, AF_INET, SOCK_STREAM

def read_requests(clients):

    requests = {}

    for sock in clients:
        try:
            data = sock.recv(1024).decode()
            requests[sock] = data
            print(type(requests))
            return requests
        except:
            print('Клиент {} {} отключился'.format(sock.fileno(), sock.getpeername()))
            clients.remove(sock)


def write_responses(requests, clients):
    for s in clients:
        if s in requests:
            try:
                resp = requests[s].encode()
                test_len = s.send(resp.upper())
            except:
                print('Клиент {} {} отключился'.format(s.fileno(), s.getpeername()))
                clients.remove(s)





def mainloop():

    address = ('', 10000)
    clients = []

    s = socket(AF_INET, SOCK_STREAM)
    s.bind(address)
    s.listen(5)
    s.settimeout(0.2)
    while True:
        try:
            conn, addr = s.accept()
        except OSError as e:
            pass
        else:
            print('Полуыен запрос на соединение')
            clients.append(conn)
        finally:
            wait = 0
            r = []
            w = []
            try:
                r,w,e = select.select(clients, clients, [], wait)
            except:
                pass
            req = read_requests(r)
            print(type(req))


            write_responses(req, clients)

print('Сервер запущен')
mainloop()






