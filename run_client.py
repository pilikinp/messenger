from subprocess import Popen, CREATE_NEW_CONSOLE

p_list = []
while True:
    user = input()
    if user == 'q':
        break
    for i in range(int(user)):
        p_list.append(Popen('python client.py -w -account_name pilik{}'.format(i), creationflags= CREATE_NEW_CONSOLE))
        p_list.append(Popen('python client.py -r -account_name pluh{}'.format(i), creationflags=CREATE_NEW_CONSOLE))
