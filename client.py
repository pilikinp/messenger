import argparse

from lib_client import chat, chat2

parser = argparse.ArgumentParser()

parser.add_argument('--ip',type = str, default= '127.0.0.1', help = 'our ip')
parser.add_argument('--port', type = int, default= 7771, help = 'our port')
parser.add_argument('-w', action = 'store_true')
parser.add_argument('-r', action = 'store_true')

args = parser.parse_args()


if args.w:
    chat(args.ip, args.port)
elif args.r:
    chat2(args.ip, args.port)
else:
    print('не задан обязательный аргумент')








