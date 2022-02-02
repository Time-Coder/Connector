import socket
import threading
import os
import sys
import CloseableQueue
from concurrent.futures import ThreadPoolExecutor

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from _Node import Node
from _NodeInternalClasses import OrderedDict
from _utils import file_size

class Server:
	class Queues:
		def __init__(self):
			self._queue_dict = {}

		def __getitem__(self, name):
			if name not in self._queue_dict:
				self._queue_dict[name] = CloseableQueue.CloseableQueueFactory()()

			return self._queue_dict[name]

		def __delitem__(self, name):
			try:
				self._queue_dict[name].close()
			except:
				pass
			del self._queue_dict[name]

		def __len__(self):
			return len(self._queue_dict)

		def __contains__(self, name):
			return self._queue_dict.__contains__(name)

		def keys(self):
			return self._queue_dict.keys()

		def values(self):
			return self._queue_dict.values()

		def items(self):
			return self._queue_dict.items()

		def __iter__(self):
			return self._queue_dict.__iter__()

		def clear(self):
			for name in self._queue_dict:
				try:
					self._queue_dict[name].close()
				except:
					pass

			self._queue_dict.clear()

	def __init__(self, ip = None, port = None):
		self.connect_results = OrderedDict()
		self.disconnect_results = OrderedDict()
		self._callback_threads_pool = ThreadPoolExecutor(max_workers=5)

		self._onConnect = lambda client : None
		self._onDisconnect = lambda address : None

		self._connected_nodes = OrderedDict()
		self._global_vars = {}
		self._queues = Server.Queues()

		self._continue_accept = False
		self._accept_thread = None
		
		self.start(ip, port)

	def set_connect_callback(self, func):
		self._onConnect = func

	def set_disconnect_callback(self, func):
		self._onDisconnect = func

	def start(self, ip=None, port=None):
		if self._continue_accept:
			return

		self._connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		if ip == None:
			ip = [a for a in os.popen('route print').readlines() if ' 0.0.0.0 ' in a][0].split()[-2]
		if port == None:
			port = 0
		self._connection.bind((ip, port))
		self._connection.listen(5)
		
		self._continue_accept = True
		if self._accept_thread == None or not self._accept_thread.is_alive():
			self._accept_thread = threading.Thread(target=self._start, daemon=True)
			self._accept_thread.start()

	def close(self):
		self._continue_accept = False
		try:
			self._queues.clear()

			for address in self._connected_nodes:
				try:
					self._connected_nodes[address].close()
				except:
					pass
		except:
			pass

		try:
			self._connection.close()
		except:
			pass
		
		self.connect_results = OrderedDict()
		self.disconnect_results = OrderedDict()
		self._callback_threads_pool.shutdown()
		self._callback_threads_pool = ThreadPoolExecutor(max_workers=5)

		self._connected_nodes = OrderedDict()
		self._global_vars = {}
		self._queues = Server.Queues()

		self._continue_accept = False
		if self._accept_thread != None and self._accept_thread.is_alive():
			self._accept_thread.join()
		self._accept_thread = None
		self._connected_nodes = OrderedDict()

	@property	
	def address(self):
		if not self._continue_accept:
			raise ConnectionError("Connection is closed.")

		return self._connection.getsockname()

	@property
	def is_closed(self):
		return not self._continue_accept

	@property
	def clients(self):
		return self._connected_nodes

	## global queues
	@property
	def queues(self):
		return self._queues
	
	## global shared variables
	def __del__(self):
		try:
			self.close()
		except:
			pass

	def __getitem__(self, name):
		return self._global_vars[name]

	def __setitem__(self, name, value):
		self._global_vars[name] = value

	def __delitem__(self, name):
		del self._global_vars[name]

	def __iter__(self):
		return self._global_vars.__iter__()

	def __len__(self):
		return self._global_vars.__len__()

	def __contains__(self, name):
		return self._global_vars.__contains__(name)

	def keys(self):
		return self._global_vars.keys()

	def values(self):
		return self._global_vars.values()

	def items(self):
		return self._global_vars.items()

	def clear(self):
		self._global_vars.clear()

	def pop(self, name):
		return self._global_vars.pop(name)

	def put_file_to_all(self, src_filename, dest_filename = None):
		if not os.path.isfile(src_filename):
			raise FileNotFoundError("File " + src_filename + " is not exists.")

		if dest_filename == None:
			dest_filename = os.path.basename(src_filename)

		all_clients = self._connected_nodes.keys()

		block_size = 8192
		sent_size = 0
		src_file_size = file_size(src_filename)
		with open(src_filename, "rb") as file:
			while sent_size < src_file_size:
				data = file.read(block_size)
				for address in all_clients:
					try:
						client = self._connected_nodes[address]
						client._write_to_file(data, dest_filename)
					except:
						pass
				sent_size += len(data)

		for address in all_clients:
			try:
				client = self._connected_nodes[address]
				client.close_file()
			except:
				pass

	def put_folder_to_all(self, src_foldername, dest_foldername = None):
		if not os.path.isdir(src_foldername):
			raise FileNotFoundError("Folder " + src_foldername + " is not exists.")

		if dest_foldername == None:
			dest_foldername = os.path.basename(src_foldername)

		i = len(src_foldername)-1
		while src_foldername[i] in ['/', '\\']:
			i -= 1

		all_clients = self._connected_nodes.keys()
		block_size = 8192
		for root, dirs, files in os.walk(src_foldername):
			for name in files:
				src_filename = os.path.join(root, name)
				dest_filename = dest_foldername + "/" + src_filename[i+2:]

				sent_size = 0
				src_file_size = file_size(src_filename)
				with open(src_filename, "rb") as file:
					while sent_size < src_file_size:
						data = file.read(block_size)
						for address in all_clients:
							try:
								client = self._connected_nodes[address]
								client._write_to_file(data, dest_filename)
							except:
								pass
						sent_size += len(data)

		for address in all_clients:
			try:
				client = self._connected_nodes[address]
				client._close_file()
			except:
				pass

	def hold_on(self):
		threading.Event().wait()

	def _start(self):
		while self._continue_accept:
			try:
				client_socket, address = self._connection.accept()
				self._connected_nodes[address] = Node(client_socket, self)
				self.connect_results[address] = self._callback_threads_pool.submit(self._onConnect, self._connected_nodes[address])
			except BaseException as e:
				print(e)