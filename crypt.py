from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA
import Crypto
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto import Random
import sys, time, json
import pickle


def create_rsa(username):
    """ функция создания пары ключей: приватного и публичного
    username - пользователь который шифрует сообщение"""

    privatekey = RSA.generate(2048)
    with open('{}privatekey.txt'.format(username), 'wb') as f:
        f.write(bytes(privatekey.exportKey('PEM')))
    publickey = privatekey.publickey()
    with open('{}publickey.txt'.format(username), 'wb') as f:
        f.write(bytes(publickey.exportKey('PEM')))
    return publickey.exportKey('PEM').decode()

def create_msg(plaintext, username, publickey):
    '''функция создания шифрованного сообщения
    plaintext - сообщение которое нужно зашифровать
    username - пользователь который шифрует сообщение
    publickey - публичный ключ пользователя, которому предназначено сообщение'''

    sessionkey = Random.new().read(32)
    iv = Random.new().read(16)# попробовать сделать без вектора инициализации (iv)
    obj = AES.new(sessionkey, AES.MODE_CFB, iv)
    ciphertext = iv + obj.encrypt(plaintext.encode())
    publickey = RSA.importKey(publickey)
    cipherrsa = PKCS1_OAEP.new(publickey)
    sessionkey = cipherrsa.encrypt(sessionkey)
    data = {'session key': sessionkey,
           'message': ciphertext}
    return data

def decript_sessionkey(sessionkey, username):
    '''функция дешифровки ключа
    sesionkey - ключ зашифрованный с помощью публичного ключа
    username - пользователь который производит дешифровку'''
    print('начинаем расшифровку ключа')
    privatekey = RSA.importKey(open('{}privatekey.txt'.format(username), 'rb').read())
    cipherrsa = PKCS1_OAEP.new(privatekey)
    print('расшифровываем')
    sessionkey = cipherrsa.decrypt(sessionkey)
    print('спех')
    return sessionkey

def decript_msg(msg, username):
    '''функция дешифровки сообщения
    msg - полученное сообщение
    username - пользователь который производит дешифровку'''
    sessionkey = decript_sessionkey(msg['session key'], username)
    print(sessionkey)
    iv = msg['message'][:16]
    obj = AES.new(sessionkey, AES.MODE_CFB, iv)
    plaintext = obj.decrypt(msg['message'])
    plaintext = plaintext[16:]
    return plaintext

def get_publickey(username):
    publickey = open('{}publickey.txt'.format(username), 'r').read()
    return publickey

if __name__ == '__main__':
    # publickey = get_publickey('pilik')
    # data = {'action': 'registration',
    #         'time': time.ctime(),
    #         'user': 'username',
    #         'password': 'wrfwefwefuih4u3ithwf23ru3u3h3h32rhu2hr3uh23ur32hi92',
    #         'publickey': publickey}
    # print(data)
    # data = json.dumps(data).encode()
    # print(sys.getsizeof(data))

    plaintext = 'qwertrewq'
    username = 'pilik'
    # signature = create_signature(plaintext, username)
    # publickey = get_publickey(username)
    publickey = open('{}publickey.txt'.format(username), 'rb').read()
    # data = create_msg(plaintext, username, publickey)
    # print(data)
    # print('########################################')
    sessionkey = Random.new().read(32)
    print(sessionkey)
    iv = Random.new().read(16)  # попробовать сделать без вектора инициализации (iv)
    obj = AES.new(sessionkey, AES.MODE_CFB, iv)
    ciphertext = iv + obj.encrypt(plaintext.encode())
    print(ciphertext, 'зашифрованный текст')
    # sig = create_signature(plaintext, username)
    # print(sig, 'подпись')
    # ciphersig = obj.encrypt(sig)  # нужен ли здесь iv
    # print(ciphersig, 'одпись')
    publickey = RSA.importKey(publickey)
    cipherrsa = PKCS1_OAEP.new(publickey)
    sessionkey = cipherrsa.encrypt(sessionkey)
    data = {'session key': sessionkey,
           'message': ciphertext}

    # data = str(data)
    # print(data['session key'])
    # data = json.dumps('ssdsdaf').encode()+ data['session key']
    # print(data)
    # data = json.loads(data.decode())
    # sessionkey = decript_sessionkey(data['session key'], username)
    ms = decript_msg(data, username)
    print(ms)
    # message = data['message']
    # sessionkey = data['session key']
    # signature = data['signature']


