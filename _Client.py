import socket
import os
import sys

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from _Node import Node

class Client(Node):
	def __init__(self, ip = None, port = None):
		self._is_Node_init = False
		if ip == None:
			ip = [a for a in os.popen('route print').readlines() if ' 0.0.0.0 ' in a][0].split()[-2]
		if port == None:
			port = 0

		self._ip = ip
		self._port = port

		self._connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self._connection.bind((ip, port))
		self._address = self._connection.getsockname()

	def connect(self, ip, port = None):
		if self._is_Node_init and not self.is_closed:
			self.close()

		server_address = ip
		if port != None:
			server_address = (ip, port)

		if self._connection == None:
			self._connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self._connection.bind((self._ip, self._port))
			self._address = self._connection.getsockname()

		self._connection.connect(server_address)
		Node.__init__(self, self._connection)