import time, sys
import socket
import threading

from models import JimMessage, JimAnswer
from models_repository_client import Repository, Contacts, HistoryMessage



class Client():
    username = ''

    def __init__(self, host, port):
        # self._password = password
        self._host = host
        self._port = port
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.lock = threading.Lock()
        self.command_dict = {'1': self.get_contact_list,
                        '2': self.chat,
                        '3': self.mes,
                        '4': '',
                        '5': '',
                        '6': ''}


    @property
    def socket(self):
        return self._sock

    def connect_guest(self, property):

        msg_client = JimMessage()
        msg_server = JimAnswer()
        data = msg_client.msg(property, self.username)
        # print(data)
        self.socket.send(msg_client.pack(data))
        msg_recv = self.socket.recv(1024)
        msg_recv = msg_server.unpack(msg_recv)
        print(msg_recv)

        if msg_recv['response'] == '200':
            print(msg_recv['alert'])
            self.rep = Repository(self.username)
        elif msg_recv['response'] == '201':
            print(msg_recv['alert'])
            print('Вы зарегистрировались под ником {}'.format(self.username))
            self.rep = Repository(self.username)
        elif msg_recv['response'] == '409':
            print(msg_recv['alert'])
            sys.exit()
        else:
            print('Возникла ошибка {} обратитесь к справке или напишите в поддержку'.format(msg_recv['response']))
            sys.exit()

    def command(self,sock):
        print('Список комманд: \n1. получить/обновить список контактов \n2. написать сообщение \n3. написать сообщение в личку \n4. создать чат \n5. войти в чат \n6. получить список чатов \n'
              '7. добавить контакт \n8. удалить контакт')
        while True:
            command = input()
            if command in ['1','2','3','4','5','6']:
                break
            else:
                print('неправильно указана команда')
        self.command_dict[command](sock)

    def get_contact_list(self, sock):
        self.rep.del_model(Contacts)
        msg_client = JimMessage()
        msg= msg_client.msg('get_contact_list', self.username)
        msg = msg_client.pack(msg)
        sock.send(msg)
        data = sock.recv(1024)
        data = msg_client.unpack(data)
        print('Кол-во контактов: ',data['quantity'])
        for cont in range(data['quantity']):
            data = sock.recv(1024)
            data = msg_client.unpack(data)
            print('{}: {}'.format(cont+1, data['user']))
            self.rep.add_obj(Contacts(data['user']))

        # написать команды: получить список контактов, войти в чат, создать чат, получить список чатов, написать сообщение

    def _send_message(self, *args):
        sock, action = args
        msg_client = JimMessage()
        while True:
            msg = msg_client.msg(action, self.username)
            msg = msg_client.pack(msg)
            sock.send(msg)
            time.sleep(0.5)

    def _get_message(self, sock):
        msg_server = JimMessage()
        while True:
            with self.lock:
                data = sock.recv(1024)
                time.sleep(0.1)
            data = msg_server.unpack(data)
            if 'action' in data:
                print(data['time'], data['from'], data['message'])
            else:
                print('ERROR ', data['response'], data['time'], data['alert'])

    def chat(self, sock):
        t1 = threading.Thread(target=self._send_message, args=(sock, 'msg'))
        t2 = threading.Thread(target=self._get_message, args= (sock,))
        t1.start()
        t2.start()
        t1.join()
        t2.join()

    def mes(self, sock):
        t1 = threading.Thread(target=self._send_message, args=(sock,'msg_to'))
        t2 = threading.Thread(target=self._get_message, args= (sock,))
        t1.start()
        t2.start()
        t1.join()
        t2.join()
    # def run(self):
    #     with self.socket as sock:
    #         command = input('Войти или зарегестрироваться (В/Р): ')
    #         if command.upper() == 'В':
    #             self.username = input('Введите имя пользователя: ')
    #             sock.connect((self._host, self._port))
    #             self.connect_guest('presence')
    #             t1 = threading.Thread(target=self._send_message, args=(sock,))
    #             t2 = threading.Thread(target=self._get_message, args= (sock,))
    #             t1.start()
    #             t2.start()
    #             t1.join()
    #             t2.join()
    #         elif command.upper() == 'Р':
    #             self.username = input('Введите имя пользователя: ')
    #             sock.connect((self._host, self._port))
    #             self.connect_guest('registration')
    #             t1 = threading.Thread(target=self._send_message, args=(sock,))
    #             t2 = threading.Thread(target=self._get_message, args=(sock,))
    #             t1.start()
    #             t2.start()
    #             t1.join()
    #             t2.join()

    def run(self):
        with self.socket as sock:
            command = input('Войти или зарегестрироваться (В/Р): ')
            if command.upper() == 'В':
                self.username = input('Введите имя пользователя: ')
                sock.connect((self._host, self._port))
                self.connect_guest('presence')
            elif command.upper() == 'Р':
                self.username = input('Введите имя пользователя: ')
                sock.connect((self._host, self._port))
                self.connect_guest('registration')
            else:
                print('неверная команда')
                sys.exit()
            while True:
                self.command(sock)