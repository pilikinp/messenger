import argparse

from lib_client import chat, chat2

parser = argparse.ArgumentParser()

parser.add_argument('--ip',type = str, default= '127.0.0.1', help = 'our ip')
parser.add_argument('--port', type = int, default= 7777, help = 'our port')
parser.add_argument('-w', action = 'store_true')
parser.add_argument('-r', action = 'store_true')
parser.add_argument('-account_name', type = str, default= 'pilik')

args = parser.parse_args()


if args.w:
    chat(args.ip, args.port, args.account_name)
elif args.r:
    chat2(args.ip, args.port, args.account_name)
else:
    print('не задан обязательный аргумент')








