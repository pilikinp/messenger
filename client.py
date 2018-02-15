import argparse

import models_client

parser = argparse.ArgumentParser()

parser.add_argument('--ip',type = str, default= '127.0.0.1', help = 'our ip')
parser.add_argument('--port', type = int, default= 7777, help = 'our port')

parser.add_argument('-account_name', type = str, default= 'pilik')

args = parser.parse_args()

client = models_client.Client(args.account_name, args.ip, args.port)
client.run()




