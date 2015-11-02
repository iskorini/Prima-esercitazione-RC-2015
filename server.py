import socket
import os
import threading

class MyFtpServer:

	def __init__ (self, userdata, port):
		self.__userdata = userdata
		self.__port = port
		self.__userConnected = 'EMPTY'
		self.__pending_login = 0

	def is_logged(self):
		return (self.__userConnected != 'EMPTY' and self.__pending_login == 0)

	def start(self):
		listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		listen_socket.bind(('', self.__port))
		listen_socket.listen(1)
		print "SERVER STARTED AT PORT "+str(self.__port) #DEBUG
		while 1:
			s, address = listen_socket.accept()
			print "connection incoming by " +  ', '.join(map(str, address)) #DEBUG
			s.sendall("220"+'\r\n')
			last_reply = self.handle_request(s)
			s.sendall(last_reply+'\r\n')
			s.close()

	def handle_request(self, sock):
		while 1:
			request = self.receive_request(sock)
			print "received message: "+request #DEBUG
			if request == 'QUIT\r\n':
				return self.quit()
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

	def quit(self): #modificare nel caso di upload o download
		if (len(parameter) > 1):
			return "501 error on parameter number"
		self.__userConnected = 'EMPTY'
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
			return "530 Unexpected repy, login incorrect"
		if (len(parameter) > 1):
			return "501 error on parameter number"
		if (os.getcwd() == self.__userConnected[1]):
			return "250 original path reached"
		else:
			os.chdir(os.path.dirname(os.getcwd()))
			return "257 " + os.getcwd() + " is new path"

	functionality = {
		'USER': user,
		'PASS': password,
		'FEAT': feat,
		'SYST': syst,
		'NOOP': noop,
		'QUIT': quit,
		'PWD': PWD,
		'CWD': CWD,
		'CDUP': CDUP
	}


if __name__ == '__main__':
	user_dictionary =  {
	'admin': ('admin', '/Users/federico/Desktop/RC/Other/admin'),
	'user1': ('user1', '/Users/federico/Desktop/RC/Other/user1')
	}
	server = MyFtpServer(user_dictionary, 210)
	server.start()
