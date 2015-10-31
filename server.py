import socket
class MyFtpServer:
	self.__userConnected = 0
	self.__funcionality = {
	'USER': user,
	'FEAT': "211 CRLF"
	}
	def __init__ (self, userdata, port): 
		self.__userdata = userdata
		self.__port = port

	def start(self):
		listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		listen_socket.bind(('', self.__port))
		listen_socket.listen(1)
		while 1:
			s, address = listen_socket.accept()
			self.handle_request(s)

	def handle_request(self, sock):
		request = self.receive_request(sock)
		print request

	
	def receive_request( self , sock ):
		r = ""
		while not r.endswith('\r\n'):
			x = sock.recv( 1024 )
			r = r + x
		return r

	def analize_request(self, request):

	def user(self, parameter):
		if parameter in self.__userdata:
			return "331 Username okay, need password."


if __name__ == '__main__':
	user_dictionary =  {
	'admin': ('admin', '/tmp/admin'), 
	'user': ('user', '/tmp/user')
	}
	server = MyFtpServer(user_dictionary, 21)
	server.start()