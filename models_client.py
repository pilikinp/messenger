import time, sys
import socket
import threading, queue

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
        self.lock = threading.Lock()
        self.recv_queue = queue.Queue()

        # self.command_dict = {
        #     '1': self.get_contact_list,
        #     '2': self.msg,
        #     '3': self.msg_to,
        #     '4': self.add_chat,
        #     '5': self.login_chat,
        #     '6': self.get_chat_list,
        #     '7': self.add_contact,
        #     '8':self.del_contact,
        #     '9': self.exit}

    @property
    def socket(self):
        return self._sock

    def connect_guest(self, action):
        data = {'action': action,
                'time': time.ctime(),
                'user': self.username}
        # print(data)
        self.socket.send(self.msg_client.pack(data))
        msg_recv = self.socket.recv(1024)
        msg_recv = self.msg_server.unpack(msg_recv)
        print(msg_recv)
        if msg_recv['response'] == '200':
            print(msg_recv['alert'])
            self.rep = Repository(self.username)
            self.msg()
            self.get_contact_list(self.socket)
        elif msg_recv['response'] == '201':
            print(msg_recv['alert'])
            print('Вы зарегистрировались под ником {}'.format(self.username))
            self.rep = Repository(self.username)
            self.msg()
            self.get_contact_list(self.socket)
        else:
            print('Возникла ошибка {} обратитесь к справке или напишите в поддержку'.format(msg_recv['response']))
        self.recv_queue.put(msg_recv)

    def reg_guest(self):
        data = {'action': 'registration',
                'time': time.ctime(),
                'user': self.username}
        self.socket.send(self.msg_client.pack(data))
        msg_recv = self.socket.recv(1024)
        msg_recv = self.msg_server.unpack(msg_recv)
        print(msg_recv)
        if msg_recv['response'] == '201':
            print(msg_recv['alert'])
            print('Вы зарегистрировались под ником {}'.format(self.username))
            self.rep = Repository(self.username)
        else:
            print('Возникла ошибка {} обратитесь к справке или напишите в поддержку'.format(msg_recv['response']))
            sys.exit()

    # def command(self,*args):
    #     sock = args[0]
    #     print('Список комманд: \n1. получить/обновить список контактов \n2. написать сообщение \n'
    #           '3. написать сообщение в личку \n4. создать чат \n5. войти в чат \n'
    #           '6. получить список чатов \n7. добавить контакт \n8. удалить контакт\n9. выход')
    #     while True:
    #         command = input()
    #         if command in ['1','2','3','4','5','6','7','8','9']:
    #             break
    #         else:
    #             print('неправильно указана команда')
    #     self.command_dict[command](sock)
    #
    # def action(self, sock, action):
    #     msg = self.msg_client.msg(action, self.username)
    #     msg = self.msg_client.pack(msg)
    #     sock.send(msg)
    #     data = sock.recv(1024)
    #     data = self.msg_server.unpack(data)
    #     return data

    def add_chat(self, *args):
        sock = args[0]
        data = self.action(sock, 'add_chat')
        print(data)


    def add_contact(self, contact):
        sock = self.socket

        msg = {'action': 'add_contact',
               'time': time.ctime(),
               'user': self.username,
               'contact': contact}
        msg = self.msg_client.pack(msg)
        sock.send(msg)

    def del_contact(self, contact):
        sock = self.socket
        msg = {'action': 'del_contact',
               'time': time.ctime(),
               'user': self.username,
               'contact': contact}
        msg = self.msg_client.pack(msg)
        sock.send(msg)

    def get_contact_list(self, *args):
        # cont_l = []
        sock = args[0]
        self.rep.del_model(Contacts)
        msg = {'action': 'get_contact_list',
                          'time': time.ctime(),
                          'user': self.username}
        msg = self.msg_client.pack(msg)
        sock.send(msg)

    def search_contact(self, text):
        data = {'users': []}
        sock = self.socket
        for contact in self.rep.contacts_list():
            if text.lower() in contact.contact_name.lower():
                data['users'].append(contact.contact_name)
        if data['users']:
            self.recv_queue.put(data)
        else:
            msg = {'action': 'search_contact',
                   'contact': text}
            msg = self.msg_client.pack(msg)
            time.sleep(0.2)
            sock.send(msg)


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
        sock, to_, message, username = args
        msg = {'action': 'msg',
               'time': time.ctime(),
               'to': to_,
               'from': username,
               'message': message}
        self.rep.add_obj(HistoryMessage(msg['time'], msg['from'], msg['to'], msg['message']))
        msg = self.msg_client.pack(msg)
        sock.send(msg)

    def _get_message(self):
        sock = self.socket
        cont_l = []
        while True:
            try:
                sock.settimeout(2)
                data = sock.recv(1024)
                data = self.msg_server.unpack(data)
                print(data)
                if 'action' in data:
                    print(data['time'], data['from'], data['message'])
                    self.rep.add_obj(HistoryMessage(data['time'], data['from'], data['to'], data['message']))
                elif 'response' in data:
                    print(data['response'], data['time'], data['alert'])
                elif 'users' in data:
                    print('Кол-во контактов: ',len(data['users']))
                    for cont in data['users']:
                        self.rep.add_contact(cont)
                    self.rep.session.commit()
                elif 'found_users' in data:
                    data['users'] = data['found_users']
                self.recv_queue.put(data)
            except socket.timeout:
                pass

    def msg(self):
        t2 = threading.Thread(target=self._get_message)
        t2.daemon = True
        t2.start()

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
        t2 = threading.Thread(target=self._get_message, args=(sock,))
        t1.start()
        t2.start()
        t1.join()
        t2.join()

    def run(self, name, action):
        self.username = name
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self._host, self._port))
        self.connect_guest(action)




