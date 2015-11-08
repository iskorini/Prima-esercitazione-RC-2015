import os
import threading
import socket
string = 'USER admin\r\n'
username = string[5:]
print username
user_dictionary =  {
'admin': ('admin', '/Users/federico/Desktop/RC/Other/admin'),
'user1': ('user1', '/Users/federico/Desktop/RC/Other/user1')
}
print user_dictionary[string[5:len(string)-2]]
print string[5:len(string)-2] in user_dictionary

print "------------------------------------------------"

test1 = "PORT 2,124,54,1,4,1"
transfer_data = test1[5:].split(",")
ip_address = transfer_data[0:4]
ip_address = reduce(lambda x, y: str(x)+"."+str(y), ip_address)
print ip_address
port = int(transfer_data[4])*256+int(transfer_data[5])*1
print port

print "---------------------------------"
x = os.system("ls -la")
print str(x)

print "----------------------------------"
semaphore = threading.Semaphore(1)

semaphore.acquire()
print("DIOMERDA")

print "--------------------"

print os.listdir(os.getcwd())

print "----------------------"

#list0 = "LIST"
#list0 = "LIST -la"
list0 = "LIST -l /Users/Federico/blabla"
print list0
l = list0.split()
if (len(list0) != 4):
    ls_comand = 'ls '+ reduce(lambda x, y: str(x)+" "+str(y), l[1:])
else:
    ls_comand = 'ls'
print ls_comand

print "-----------------"
socket1 = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
socket2 = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
socket1.bind(('', 9000))
socket2.bind(('', 9001))
socket1.listen(1)
socket2.listen(1)
socket1.accept()
socket2.accept()
