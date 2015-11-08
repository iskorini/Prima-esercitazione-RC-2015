import socket
import os
import threading
import random
import re
import sys
import platform
import subprocess
import time #CANCELLARE
class MyFtpServer:

	def __init__ (self, userdata, port):
		self.__userdata = userdata
		self.__port = port
		self.__userConnected = 'EMPTY'
		self.__pending_login = 0
		self.__data_conn = ''
		self.__ready_to_send = 0
		self.__address = ''
		self.__active_connection = 0
		self.__s = ''
		self.__type = 'A'
		self.__random_port = random.randrange(1000, 65536)
		self.__pasv = 0
		self.__ip_address = ''

	def is_logged(self):
		return (self.__userConnected != 'EMPTY' and self.__pending_login == 0)

	def verify_string(self, parameter, regexp):
		result = re.compile(regexp).match(parameter)
		if (result == None):
			return 0
		elif (result.end() == len(parameter)):
			return 1
		else:
			return 0

	def start(self):
		listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		listen_socket.bind(('', self.__port))
		listen_socket.listen(1)
		print "SERVER STARTED AT PORT "+str(self.__port) #DEBUG
		while 1:
			self.__s, self.__address = listen_socket.accept()
			self.__active_connection = 1
			print "connection incoming by " +  ', '.join(map(str, self.__address)) #DEBUG
			self.__s.sendall("220"+'\r\n')
			self.handle_request(self.__s)
			self.__s.close()

	def handle_request(self, sock):
		while self.__active_connection == 1:
			request = self.receive_request(sock)
			print "received message: "+request #DEBUG
			reply = self.analize_request(request)
			sock.sendall(reply)


	def receive_request( self , sock ):
		r = ""
		while not r.endswith('\r\n'):
			x = sock.recv( 1024 )
			r = r + x
		return r

	def analize_request( self, request ):
		splitted_request = request.split()
		if splitted_request[0] not in self.functionality:
			return "500 Command not recognized\r\n"
		elif (self.verify_string(request, self.functionality[splitted_request[0]][1]) == 0 ):
			return "500\r\n"
		else:
			return self.functionality[splitted_request[0]][0](self, request)


	def user( self, parameter ):
		if (self.is_logged() == 1 and parameter[5:(len(parameter)-2)] == self.__userConnected):
			return "331 user is logged\r\n"
		elif (parameter[5:(len(parameter)-2)] in self.__userdata and self.__userConnected == 'EMPTY'):
			self.__userConnected = self.__userdata[parameter[5:(len(parameter)-2)]]
			self.__pending_login = 1
			return "331 Username okay\r\n" #CAMBIARE
		elif (self.__userConnected != 'EMPTY'):
			return "530\r\n"
		else:
			return "430 Invalid username or password\r\n" #Corretto?

	def password(self, parameter):
		if (self.__userConnected != 'EMPTY') and (self.__userConnected[0] == parameter[5:(len(parameter)-2)]) and self.__pending_login == 1:
			self.__pending_login = 0
			try:
				os.mkdir(self.__userConnected[1])
				print "MKDIR: "+self.__userConnected[1]
			except OSError as HORROR:
				print "MKDIR: failed"
			os.chdir(self.__userConnected[1])
			return "230 User logged in, proceed. Logged out if appropriate.\r\n"
		elif (self.is_logged == 1):
			return "230 user is already logged\r\n"
		elif (self.__pending_login == 0):
			return "503 Use USER first\r\n"
		else:
			self.__pending_login = 0
			self.__userConnected = 'EMPTY'
			return "530 Invalid username or password\r\n"

	def feat(self, parameter):
		if (self.is_logged() == 0):
			return "530 please log in\r\n"
		if self.__pending_login == 1:
			return "331 Unexpected reply, login incorrect\r\n"
		return "211 \r\n" #EVBB

	def quit(self, parameter): #modificare nel caso di upload o download
		self.__userConnected = 'EMPTY'
		self.__active_connection = 0
		return "221 bye bye\r\n"

	def syst(self, parameter):
		if (self.is_logged() == 0):
			return "530 please log in\r\n"
		if self.__pending_login == 1:
			return "331 Unexpected reply, login incorrect\r\n"
		return "215 "+self.system_info()+"\r\n"

	def PWD(self, parameter):
		if self.__pending_login == 1:
			return "331 Unexpected reply, login incorrect\r\n"
		elif (self.is_logged()):
			return "257 current directory is: "+os.getcwd()+"\r\n"
		else:
			return "530 Please log in with USER and PASS\r\n"

	def noop(self, parameter):
		if (self.is_logged() == 0):
			return "530 please log in\r\n"
		if self.__pending_login == 1:
			return "331 Unexpected reply, login incorrect\r\n"
		return "200 connection is alive\r\n"

	def CWD(self, parameter):
		if self.__pending_login == 1:
			return "331 Unexpected repy, login incorrect\r\n"
		try:
			os.chdir(parameter[1])
			return "250 OK, new path is: " + os.getcwd()+"\r\n"
		except:
			return "550 "+ parameter[1] +  " doesn't exist\r\n"

	def CDUP(self, parameter):
		if self.__pending_login == 1:
			return "331 Unexpected reply, login incorrect\r\n"
		if (os.getcwd() == self.__userConnected[1]):
			return "250 original path reached\r\n"
		else:
			os.chdir(os.path.dirname(os.getcwd()))
			return "257 " + os.getcwd() + " is new path\r\n"

	def port(self, parameter):
		if (self.is_logged() == 0):
			return "530 Please log in with USER and PASS\r\n"
		if (self.__pending_login == 1):
			return "331 Unexpected reply, login incorrect\r\n"
		transfer_data = parameter[5:].split(",")
		self.__ip_address = transfer_data[0:4]
		self.__ip_address = reduce(lambda x, y: str(x)+"."+str(y), ip_address)
		self.__random_port = int(transfer_data[4])*256+int(transfer_data[5])*1 #bah
		self.__ready_to_send = 1
		return "200 success\r\n"

	def pasv(self, parameter):
		if (self.__pending_login == 1):
			return "331 Unexpected reply, login incorrect\r\n"
		if (self.is_logged() == 0):
			return "530 Please log in with USER and PASS\r\n"
		port = self.__random_port
		x = port/256 #BAH
		y = port-(x*256)
		self.__pasv = 1
		self.__ready_to_send = 1
		print "PASSIVE MODE ON PORT: "+str(port)
		return "227 entering in passive mode ("+self.__address[0].replace(".",",")+","+str(x)+","+str(y)+")"+"\r\n"


	def send_list(self, parameter): #gestire casi di errore
		if (self.is_logged() == 0):
			return "530 Please log in with USER and PASS\r\n"
		if (self.__pending_login == 1):
			return "331 Unexpected reply, login incorrect\r\n"
		if self.__ready_to_send == 1:
			if (self.__pasv == 1):
				data_conn = data_transfer('', self.__random_port ,1) #self.__address[0]
			else:
				self.__data_conn = data_transfer(ip_address, self.__random_port, 0)
		data_conn.start() #avvio il thread
		self.__s.sendall('150 Opening ASCII mode data connection for \'/bin/ls\'\r\n') #MANDO
		l = parameter.split()
		if (len(l) != 1):
		    ls_comand = 'ls '+ reduce(lambda x, y: str(x)+" "+str(y), l[1:])
		else:
		    ls_comand = 'ls'
		data_to_transfer = (subprocess.check_output(ls_comand, shell = True))
		if (self.__type = 'A'):
			data_to_transfer.replace('\n','\r\n')
		data_conn.send_data(data_to_transfer)
		data_conn.join() #TERMINO IL THREAD
		return "226 transfer complete\r\n"

	def set_type(self, parameter):
		if (self.is_logged() == 0):
			return "530 please log in\r\n"
		if self.__pending_login == 1:
			return "331 Unexpected reply, login incorrect\r\n"


	def retr(self, parameter):
		if (self.is_logged() == 0):
			return "530 please log in\r\n"
		if self.__pending_login == 1:
			return "331 Unexpected reply, login incorrect\r\n"

	def system_info(self):
		plat = sys.platform
		if plat == 'darwin':
			return "OS X "+str(platform.mac_ver()[0])+"\r\n"
		elif plat == 'win32':
			return "Windows "+str(platform.version())+"\r\n"
		elif plat == 'linux' or plat == 'linux2':
			return "LINUX " +str(platform.version())+"\r\n"


	functionality = {
		'USER': (user, '\AUSER\s(\w|\s)+$'),
		'PASS': (password, '\APASS\s(\w|\s)+$'),
		'FEAT': (feat, '\AFEAT\\r\\n$'),
		'SYST': (syst, '\ASYST\\r\\n$'),
		'NOOP': (noop, '\ANOOP\\r\\n$'),
		'QUIT': (quit, '\AQUIT\\r\\n$'),
		'PWD': (PWD, '\APWD\\r\\n$'),
		'CWD': (CWD, '^CWD\s(.*/)?(?:$|(.+?)(?:(\.[^.]*$)|$))\\r\\n$'),
		'CDUP': (CDUP, '\ACDUP\\r\\n$'),
		'PORT': (port, '^PORT\s\d{1,3},\d{1,3},\d{1,3},\d{1,3},\d{1,3},\d{1,3}\\r\\n$'),
		'PASV': (pasv, '\APASV\\r\\n$'),
		'LIST': (send_list, '^LIST(\s)?((-l|-la)(\s)?)?((.*/)?(?:$|(.+?)(?:(\.[^.]*$)|$)))?\\r\\n$'),
		'TYPE': (set_type, '\ATYPE\s(A|I)\\r\\n$'),
		'RETR': (retr, '^RETR\s(.*/)?(?:$|(.+?)(?:(\.[^.]*$)|$))\\r\\n$')
	}

class data_transfer(threading.Thread): #classe per trasferimenti dati
	def __init__(self, address, port, pasv):
		threading.Thread.__init__(self)
		self.__ap = (address, port)
		self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.__pasv = pasv
		self.__semaphore = threading.Semaphore(0)
		self.__s = ''

	def run(self):
		if (self.__pasv == 1): #Sono in PASV
			self.__sock.bind(self.__ap)
			self.__sock.listen(1)
			self.__s, address = self.__sock.accept()
			print "DATA CONNECTION IS ALIVE"
		elif (self.__pasv == 0): #Sono in attivo
			self.__sock.connect(self.__ap)
			print "DATA CONNECTION IS ALIVE"
		self.__semaphore.release()
	def send_data(self, data):
		self.__semaphore.acquire()
		if (self.__pasv == 1):
			self.__s.sendall(data)
			self.__s.close()
		else:
			self.__sock.sendall(data)
			self.__sock.close()




if __name__ == '__main__':
	user_dictionary =  {
	'admin': ('admin', '/Users/federico/Desktop/RC/Other/admin'),
	'user1': ('user1', '/Users/federico/Desktop/RC/Other/user1'),
	'user 666':('user 666', '/Users/federico/Desktop/RC/Other/user 666')
	}
	server = MyFtpServer(user_dictionary, 210)
	server.start()
