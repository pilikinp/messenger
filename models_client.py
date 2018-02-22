import time, sys
import socket
import threading

from models import JimMessage, JimAnswer
from models_repository_client import Repository, Contacts, HistoryMessage



class Client():
    username = ''
    msg_client = JimMessage()
    msg_server = JimAnswer()

    def __init__(self, host, port):
        # self._password = password
        self._host = host
        self._port = port
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.lock = threading.Lock()
        self.command_dict = {'1': self.get_contact_list,
                        '2': self.msg,
                        '3': self.msg_to,
                        '4': self.add_chat,
                        '5': self.login_chat,
                        '6': self.get_chat_list,
                        '7': self.add_contact,
                        '8':self.del_contact,
                        '9': self.exit}

    @property
    def socket(self):
        return self._sock

    def connect_guest(self, property):
        data = self.msg_client.msg(property, self.username)
        # print(data)
        self.socket.send(self.msg_client.pack(data))
        # msg_recv = self.socket.recv(1024)
        # msg_recv = self.msg_server.unpack(msg_recv)
        # print(msg_recv)
        #
        # if msg_recv['response'] == '200':
        #     print(msg_recv['alert'])
        #     self.rep = Repository(self.username)
        # elif msg_recv['response'] == '201':
        #     print(msg_recv['alert'])
        #     print('Вы зарегистрировались под ником {}'.format(self.username))
        #     self.rep = Repository(self.username)
        # elif msg_recv['response'] == '409':
        #     print(msg_recv['alert'])
        #     sys.exit()
        # else:
        #     print('Возникла ошибка {} обратитесь к справке или напишите в поддержку'.format(msg_recv['response']))
        #     sys.exit()

    def command(self,*args):
        sock = args[0]
        print('Список комманд: \n1. получить/обновить список контактов \n2. написать сообщение \n'
              '3. написать сообщение в личку \n4. создать чат \n5. войти в чат \n'
              '6. получить список чатов \n7. добавить контакт \n8. удалить контакт\n9. выход')
        while True:
            command = input()
            if command in ['1','2','3','4','5','6','7','8','9']:
                break
            else:
                print('неправильно указана команда')
        self.command_dict[command](sock)

    def action(self, sock, action):
        msg = self.msg_client.msg(action, self.username)
        msg = self.msg_client.pack(msg)
        sock.send(msg)
        data = sock.recv(1024)
        data = self.msg_server.unpack(data)
        return data

    def add_chat(self, *args):
        sock = args[0]
        data = self.action(sock, 'add_chat')
        print(data)

    def add_contact(self, *args):
        sock = args[0]
        data = self.action(sock, 'add_contact')
        print(data)
        self.get_contact_list(sock)

    def del_contact(self, *args):
        sock = args[0]
        data = self.action(sock, 'del_contact')
        print(data)
        self.get_contact_list(sock)

    def get_contact_list(self, *args):
        sock = args[0]
        self.rep.del_model(Contacts)
        data = self.action(sock, 'get_contact_list')
        print('Кол-во контактов: ',data['quantity'])
        for cont in range(data['quantity']):
            data = sock.recv(1024)
            data = self.msg_client.unpack(data)
            print('{}: {}'.format(cont+1, data['user']))
            self.rep.add_contact(data['user'])
        self.rep.session.commit()

    def get_chat_list(self, *args):
        sock = args[0]
        data = self.action(sock, 'get_chat_list')
        print('Кол-во чатов: ', data['quantity'])
        for cont in range(data['quantity']):
            data = sock.recv(1024)
            data = self.msg_client.unpack(data)
            print('{}: {}'.format(cont + 1, data['user']))

    def exit(self, *args):
        sock = args[0]
        msg = self.msg_client.msg('exit', self.username)
        msg = self.msg_client.pack(msg)
        sock.send(msg)
        sys.exit()

    def _send_message(self, *args):
        sock, action = args

        while True:
            msg = self.msg_client.msg(action, self.username)
            self.rep.add_obj(HistoryMessage(msg['time'], self.username, msg['to'], msg['message']))
            msg = self.msg_client.pack(msg)
            sock.send(msg)
            time.sleep(0.5)

    def _get_message(self, *args):
        sock = args[0]
        while True:
            with self.lock:
                data = sock.recv(1024)
                time.sleep(0.1)
            data = self.msg_server.unpack(data)
            if 'action' in data:
                print(data['time'], data['from'], data['message'])
                self.rep.add_obj(HistoryMessage(data['time'], data['from'], data['to'], data['message']))
            else:
                print('ERROR ', data['response'], data['time'], data['alert'])

    def msg(self, *args):
        sock = args[0]
        t1 = threading.Thread(target=self._send_message, args=(sock, 'msg'))
        # t2 = threading.Thread(target=self._get_message, args= (sock,))
        t1.start()
        # t2.start()
        t1.join()
        # t2.join()

    def msg_to(self, *args):
        sock = args[0]
        t1 = threading.Thread(target=self._send_message, args=(sock,'msg_to'))
        # t2 = threading.Thread(target=self._get_message, args= (sock,))
        t1.start()
        # t2.start()
        t1.join()
        # t2.join()

    def login_chat(self, *args):
        sock = args[0]
        data = self.action(sock,'login_chat')
        if data['response'] == '200':
            self.chat(sock)
        else:
            print(data)

    def chat(self, *args):
        sock = args[0]
        t1 = threading.Thread(target=self._send_message, args=(sock, 'chat'))
        # t2 = threading.Thread(target=self._get_message, args=(sock,))
        t1.start()
        # t2.start()
        t1.join()
        # t2.join()

    def run(self):
        with self.socket as sock:
            command = input('Войти или зарегестрироваться (1/2): ')
            if command.upper() == '1':
                self.username = input('Введите имя пользователя: ')
                sock.connect((self._host, self._port))
                self.connect_guest('presence')
            elif command.upper() == '2':
                self.username = input('Введите имя пользователя: ')
                sock.connect((self._host, self._port))
                self.connect_guest('registration')
            else:
                print('неверная команда')
                sys.exit()
            while True:
                t3 = threading.Thread(target=self._get_message, args= (sock,))
                t2 = threading.Thread(target=self.command(), args=(sock,))
                t2.start()
                t2.join()
                t3.start()

                t3.join()

    # добавить поток который будет постоянно слушать сервер
