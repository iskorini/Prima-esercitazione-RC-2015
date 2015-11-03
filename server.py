import socket
import os
import threading
import random
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

	def is_logged(self):
		return (self.__userConnected != 'EMPTY' and self.__pending_login == 0)

	def start(self):
		listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		listen_socket.bind(('', self.__port))
		listen_socket.listen(1)
		print "SERVER STARTED AT PORT "+str(self.__port) #DEBUG
		while 1:
			s, self.__address = listen_socket.accept()
			self.__active_connection = 1
			print "connection incoming by " +  ', '.join(map(str, self.__address)) #DEBUG
			s.sendall("220"+'\r\n')
			self.handle_request(s)
			s.close()

	def handle_request(self, sock):
		while self.__active_connection == 1:
			request = self.receive_request(sock)
			print "received message: "+request #DEBUG
			reply = self.analize_request(request)
			sock.sendall(reply+'\r\n')


	def receive_request( self , sock ):
		r = ""
		while not r.endswith('\r\n'):
			x = sock.recv( 1024 )
			r = r + x
		return r

	def analize_request( self, request ):
		splitted_request = request.split()
		if splitted_request[0] not in self.functionality:
			return "500 Command not recognized"
		else:
			return self.functionality[splitted_request[0]](self, splitted_request)


	def user( self, parameter ):
		if (len(parameter) == 1):
			return "501 error on parameter number"
		if parameter[1] in self.__userdata and self.__userConnected == 'EMPTY':
			self.__userConnected = self.__userdata[parameter[1]]
			self.__pending_login = 1
			return "331 Username okay" #CAMBIARE
		elif self.__pending_login == 1:
			return "530 Unexpected reply"
		elif self.__userConnected != 'EMPTY':
			return "530"
		else:
			return "430 Invalid username or password" #Corretto?

	def password(self, parameter):
		if (len(parameter) == 1):
			return "501 error on parameter number"
		if (self.__userConnected != 'EMPTY') and (self.__userConnected[0] == parameter[1]) and self.__pending_login == 1:
			self.__pending_login = 0
			try:
				os.mkdir(self.__userConnected[1])
				print "MKDIR: "+self.__userConnected[1]
			except OSError as HORROR:
				print "MKDIR: failed"
			os.chdir(self.__userConnected[1])
			return "230 User logged in, proceed. Logged out if appropriate."
		elif (self.__pending_login == 0):
			return "503 Use USER first"
		else:
			self.__pending_login = 0
			self.__userConnected = 'EMPTY'
			return "530 Invalid username or password"

	def feat(self, parameter):
		if (len(parameter) > 1):
			return "501 error on parameter number"
		if self.__pending_login == 1:
			return "530 Unexpected reply, login incorrect"
		return "211 CRLF" #EVBB

	def quit(self, parameter): #modificare nel caso di upload o download
		if (len(parameter) > 1):
			return "501 error on parameter number"
		self.__userConnected = 'EMPTY'
		self.__active_connection = 0
		return "221 bye bye"

	def syst(self, parameter):
		if (len(parameter) > 1):
			return "501 error on parameter number"
		if self.__pending_login == 1:
			return "530 Unexpected reply, login incorrect"
		return "215 UNIX Type: L8 Version"

	def PWD(self, parameter):
		if (len(parameter) > 1):
			return "501 error on parameter number"
		if self.__pending_login == 1:
			return "530 Unexpected reply, login incorrect"
		elif (self.is_logged()):
			return "257 current directory is: "+os.getcwd()
		else:
			return "530 Please log in with USER and PASS"

	def noop(self, parameter):
		if (len(parameter) > 1):
			return "501 error on parameter number"
		if self.__pending_login == 1:
			return "530 Unexpected reply, login incorrect"
		return "200 connection is alive"

	def CWD(self, parameter):
		if self.__pending_login == 1:
			return "530 Unexpected repy, login incorrect"
		if (len(parameter) != 2):
			return "501 error on parameter number"
		try:
			os.chdir(parameter[1])
			return "250 OK, new path is: " + os.getcwd()
		except:
			return "550 "+ parameter[1] +  " doesn't exist"

	def CDUP(self, parameter):
		if self.__pending_login == 1:
			return "530 Unexpected reply, login incorrect"
		if (len(parameter) > 1):
			return "501 error on parameter number"
		if (os.getcwd() == self.__userConnected[1]):
			return "250 original path reached"
		else:
			os.chdir(os.path.dirname(os.getcwd()))
			return "257 " + os.getcwd() + " is new path"

	def port(self, parameter):
		if (self.is_logged() == 0):
			return "530 Please log in with USER and PASS"
		if (self.__pending_login == 1):
			return "530 Unexpected reply, login incorrect"
		if (len(parameter)!=7):
			return "501 error on parameter number"
		new_parameter = map(lambda x: x.replace(",", ""), parameter)
		ip_address = []
		for i in range(1,5):
			ip_address.append(new_parameter[i])
		ip_address = reduce(lambda x, y: str(x)+"."+str(y), ip_address)
		port = int(parameter[5])*256+int(parameter[6])*1 #bah
		self.__data_conn = data_transfer(ip_address, port, 0)
		self.__data_conn.start()
		self.__ready_to_send = 1
		return "200 success"

	def pasv(self, parameter):
		if (self.__pending_login == 1):
			return "530 Unexpected reply, login incorrect"
		if (len(parameter)!=1):
			return "501 error on parameter number"
		if (self.is_logged() == 0):
			return "530 Please log in with USER and PASS"
		port = random.randrange(1000, 65536)
		x = port/256 #BAH
		y = port-(x*256)
		self.__data_conn = data_transfer(self.__address[0], port ,1)
		self.__data_conn.start()
		self.__ready_to_send = 1
		print "PASSIVE MODE ON PORT: "+str(port)
		return "227 entering in passive mode ("+self.__address[0].replace(".",",")+","+str(x)+","+str(y)+")"


	functionality = {
		'USER': user,
		'PASS': password,
		'FEAT': feat,
		'SYST': syst,
		'NOOP': noop,
		'QUIT': quit,
		'PWD': PWD,
		'CWD': CWD,
		'CDUP': CDUP,
		'PORT': port,
		'PASV': pasv
	}

class data_transfer(threading.Thread): #classe per trasferimenti dati
	def __init__(self, address, port, pasv):
		threading.Thread.__init__(self)
		self.__ap = (address, port)
		self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.__pasv = pasv

	def run(self):
		if (self.__pasv == 1): #Sono in PASV
			self.__sock.bind(self.__ap)
			self.__sock.listen(1)
			self.__s, address = self.__sock.accept()
			print "DATA CONNECTION IS ALIVE"
		elif (self.__pasv == 0): #Sono in attivo
			self.__sock.connect(self.__ap)
			print "DATA CONNECTION IS ALIVE"

	def send_data(self, data):
		self.__s.sendall(data)
		self.__s.close()



if __name__ == '__main__':
	user_dictionary =  {
	'admin': ('admin', '/Users/federico/Desktop/RC/Other/admin'),
	'user1': ('user1', '/Users/federico/Desktop/RC/Other/user1')
	}
	server = MyFtpServer(user_dictionary, 210)
	server.start()
