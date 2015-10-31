import socket
class MyFtpServer:

	def __init__ (self, userdata, port):
		self.__userdata = userdata
		self.__port = port
		self.__userConnected = 'EMPTY'
		self.__pending_request = 0


	def start(self):
		listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		listen_socket.bind(('', self.__port))
		listen_socket.listen(1)
		print "SERVER STARTED AT PORT 21" #DEBUG
		while 1:
			s, address = listen_socket.accept()
			print "connection incoming by " +  ', '.join(map(str, address)) #DEBUG
			s.sendall("120"+'\r\n') #CODICE ERRATO CORREGGERE
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
			return "503 Bad sequence of commands."
		else:
			return self.functionality[splitted_request[0]](self, splitted_request)



	def user( self, parameter ):
		if parameter[1] in self.__userdata:
			self.__userConnected = self.__userdata[parameter[1]]
			self.__pending_request = 1
			return "331 Username okay, need password."
		else:
			return "430 Invalid username or password"

	def pwd(self, parameter):
		if (self.__userConnected != 'EMPTY') and (self.__userConnected[0] == parameter[1]):
			self.__pending_request = 0
			return "230 User logged in, proceed. Logged out if appropriate."
		else:
			self.__pending_request = 0
			return "430 Invalid username or password"

	def feat(self, parameter):
		return "211 CRLF" #EVBB

	def quit(self): #modificare nel caso di upload o download
		self.__userConnected = 'EMPTY'
		return "221"


	functionality = {
		'USER': user,
		'PWD': pwd,
		'FEAT': feat
	}


if __name__ == '__main__':
	user_dictionary =  {
	'admin': ('admin', '/tmp/admin'),
	'user': ('user', '/tmp/user')
	}
	server = MyFtpServer(user_dictionary, 21)
	server.start()
