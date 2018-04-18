import time, sys
import socket
import threading, queue
import hashlib

from jim.models import JimMessage, JimAnswer
from repository.models_repository_client import Repository, Contacts, HistoryMessage, User

import crypt.crypt as crypt


class Client():
    username = ''
    msg_client = JimMessage()
    msg_server = JimAnswer()

    def __init__(self, host, port):
        self._host = host
        self._port = port
        self.lock = threading.Lock()
        self.recv_queue = queue.Queue()
        self.secret = 'secretkey'

    @property
    def socket(self):
        return self._sock

    def connect_guest(self, action, password, file):
        pas = hashlib.sha256()
        pas.update(self.username.encode())
        pas.update(password.encode())
        pas.update(self.secret.encode())
        password = pas.hexdigest()
        if action == 'registration':
            publickey = crypt.create_rsa(self.username)
        else:
            publickey = crypt.get_publickey(self.username)
            #если на компе нет публичного ключа добавить его создание
        data = {'action': action,
                'time': time.ctime(),
                'data':{'user': self.username,
                'password': password,
                'publickey': publickey,
                'avatar': file}}
        self.socket.send(self.msg_client.pack(data))
        print('сообщение отправлено')
        # ##################################
        # data = b''
        # while True:
        #     packet = self.socket.recv(24)
        #     print(packet)
        #     if not packet:
        #         break
        #     data += packet
        #     print(data)
        # msg_recv = self.msg_server.unpack(data)
        ##############################################
        msg_recv = self.socket.recv(4096000)
        msg_recv = self.msg_server.unpack(msg_recv)

        print(msg_recv)
        if msg_recv['response'] == '102':
            print(msg_recv['data']['alert'])
            self.rep = Repository(self.username)
            self.msg()
            print('запускаю получение контактов')
            self.get_contact_list(self.socket)
            time.sleep(0.2)# непонятная задержка которая нужна при JSON
            # self.get_chat_list()
        elif msg_recv['response'] == '201':
            print(msg_recv['data']['alert'])
            print('Вы зарегистрировались под ником {}'.format(self.username))
            self.rep = Repository(self.username)
            self.rep.add_obj(User(self.username, avatar=file))
            self.msg()
            # self.get_contact_list(self.socket)
        # else:
        #     print('Возникла ошибка {} обратитесь к справке или напишите в поддержку'.format(msg_recv['response']))
        self.recv_queue.put(msg_recv)

    def add_chat(self, chat_name):
        sock = self.socket
        msg = {'action': 'add_chat',
                'time': time.ctime(),
               'chat': chat_name}
        self.msg_client.pack(msg)
        sock.send(msg)


    def add_contact(self, contact):
        sock = self.socket
        msg = {'action': 'add_contact',
               'time': time.ctime(),
               'data':{'user': self.username,
               'contact': contact}}
        msg = self.msg_client.pack(msg)
        sock.send(msg)

    def del_contact(self, contact):
        sock = self.socket
        msg = {'action': 'del_contact',
               'time': time.ctime(),
               'data':{'user': self.username,
               'contact': contact}}
        msg = self.msg_client.pack(msg)
        sock.send(msg)

    def get_contact_list(self, *args):
        # cont_l = []
        sock = args[0]
        self.rep.del_model(Contacts)
        msg = {'action': 'get_contact_list',
                          'time': time.ctime(),
                          'data':{'user': self.username}}
        msg = self.msg_client.pack(msg)
        sock.send(msg)
        print('get_contacts')

    def search_contact(self, text):
        # некоректно работает поиск, требуется переделать!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        data = {'users': {}}
        sock = self.socket
        for contact in self.rep.contacts_list():
            if text.lower() in contact.contact_name.lower():
                # data['users'].append(contact.contact_name)
                data['users']['{}'.format(contact.contact_name)]=['',contact.avatar]
        if data['users']:
            self.recv_queue.put(data)
        else:
            msg = {'action': 'search_contact',
                   'time': time.ctime(),
                   'data':{'contact': text}}
            msg = self.msg_client.pack(msg)
            time.sleep(0.2)# непонятная задержка которая нужна при JSON
            sock.send(msg)


    def get_chat_list(self):
        sock = self.socket
        msg = {'action': 'get_chat_list',
               'time': time.ctime(),
               'user': self.username}
        msg = self.msg_client.pack(msg)
        sock.send(msg)

    def exit(self, *args):
        sock = args[0]
        msg = self.msg_client.msg('exit', self.username)
        msg = self.msg_client.pack(msg)
        sock.send(msg)
        sys.exit()

    def _send_message(self, *args):
        sock, to_, message, username, flag = args
        sessionkey = ''
        self.rep.add_obj(HistoryMessage(time.ctime(), username, to_, message))
        if flag:
            publickey = self.rep.get_publickey(to_)
            data = crypt.create_msg(message, publickey)
            print(data)
            message = data['message']
            sessionkey = data['session key']
            # signature = data['signature']
        msg = {'action': 'msg',
               'time': time.ctime(),
               'data':{'to': to_,
               'from': username,
               'message': message,
               'session key': sessionkey,
               'flag': flag}}
        # self.rep.add_obj(HistoryMessage(msg['time'], msg['from'], msg['to'], msg['message']))
        msg = self.msg_client.pack(msg)
        sock.send(msg)


    def _get_message(self):
        sock = self.socket
        cont_l = []
        while True:
            try:
                sock.settimeout(12)
                data_recv = sock.recv(1024000)
                data_recv = self.msg_server.unpack(data_recv)
                data = data_recv['data']
                print(data_recv)
                if 'action' in data_recv:
                    if data_recv['action'] == 'msg' and data['flag']:
                        dec = crypt.decript_msg(data_recv, self.username)
                        data['message'] = dec.decode()
                        self.rep.add_obj(HistoryMessage(data_recv['time'], data['from'], data['to'], data['message']))
                    else:
                        print(data_recv['time'], data['from'], data['message'])
                        self.rep.add_obj(HistoryMessage(data_recv['time'], data['from'], data['to'], data['message']))
                elif 'response' in data_recv:
                    print(data_recv['response'], data_recv['time'], data_recv['data']['alert'])
                elif 'users' in data_recv:
                    print('Кол-во контактов: ',len(data_recv['users']))
                    # for cont in data['users']:
                    #     self.rep.add_contact(cont)
                    for name, d in data_recv['users'].items():
                        self.rep.add_contact(name, d[0], d[1])
                    self.rep.session.commit()
                elif 'found_users' in data_recv:
                    data_recv['users'] = data_recv['found_users']
                self.recv_queue.put(data_recv)
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

    def run(self, name, password, file, action):
        self.username = name
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self._host, self._port))
        self.connect_guest(action, password, file)




# что за ошибка JSONDecodeError("Extra data", s, end)