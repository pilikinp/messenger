from subprocess import Popen, CREATE_NEW_CONSOLE

p_list = []
while True:
    user = input()
    if user == 'q':
        break
    for _ in range(int(user)):
        p_list.append(Popen('python client.py -w', creationflags= CREATE_NEW_CONSOLE))
        p_list.append(Popen('python client.py -r', creationflags=CREATE_NEW_CONSOLE))
