from __future__ import print_function
import socket
import threading
import cloudpickle
import pickle
import os
import subprocess
import multiprocessing
import copy
import sys
import traceback
import time
import random
import ctypes
import hashlib
from concurrent.futures import ThreadPoolExecutor
import collections
import queue

class OrderedDict(collections.OrderedDict):
	def __init__(self, **kwargs):
		collections.OrderedDict.__init__(self, **kwargs)

	def __setitem__(self, name, value):
		if isinstance(name, int):
			collections.OrderedDict.__setitem__(self, list(self.keys())[name], value)
		else:
			collections.OrderedDict.__setitem__(self, name, value)

	def __getitem__(self, name):
		if isinstance(name, int):
			return collections.OrderedDict.__getitem__(self, list(self.keys())[name])
		else:
			return collections.OrderedDict.__getitem__(self, name)

	def __delitem__(self, name):
		if isinstance(name, int):
			collections.OrderedDict.__delitem__(self, list(self.keys())[name])
		else:
			collections.OrderedDict.__delitem__(self, name)

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def md5(file_name):
	if not os.path.isfile(file_name):
		return None
	else:
		m = hashlib.md5()
		file = open(file_name, 'rb')
		while True:
			data = file.read(4096)
			if not data:
				break
			m.update(data)
		file.close()

		return m.hexdigest()

def file_size(file_name):
	if not os.path.isfile(file_name):
		return 0
	else:
		return os.path.getsize(file_name)

class Thread(threading.Thread): 
	def __init__(self, target, args=(), kwargs={}): 
		threading.Thread.__init__(self, target=target, args=args, kwargs=kwargs) 
		
	def __get_id(self): 
		if hasattr(self, '_thread_id'): 
			return self._thread_id 
		for id, thread in threading._active.items(): 
			if thread is self: 
				return id

	def kill(self):
		thread_id = self.__get_id()
		res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
			ctypes.py_object(SystemExit))
		if res > 1:
			ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
			print('Exception raise failure')

class Future:
	def __init__(self, node, session_id):
		self._node = node
		self._session_id = session_id
		self._queue_key = "__future_" + str(session_id)
		self._cancelled = False
		self._done = None
		self._result = None
		self._added_done_callback = False
		self._done_callback = None

	def cancel(self):
		if self.done():
			return False

		self._node._stop_send = True
		self._node._send_signal(self._session_id, cancel=True)

		queue_key = "__future_" + str(self._session_id)
		self._result = self._node._result_queues_for_future[queue_key].get()
		self._cancelled = True
		self._done = True
		return True

	def cancelled(self):
		return self._cancelled

	def done(self):
		if self._done != None:
			return self._done
		else:
			return (len(self._node._result_queues_for_future[self._queue_key]) != 0)

	def result(self):
		if self._result == None:
			self._result = self._node._result_queues_for_future[self._queue_key].get()

		self._done = True
		if self._result["success"]:
			return self._result["return_value"]
		else:
			eprint(self._result["traceback"])
			raise self._result["exception"]

	def exception(self):
		if self._result == None:
			self._result = self._node._result_queues_for_future[self._queue_key].get()

		self._done = True
		return self._result["exception"]

	def _get_result(self):
		if self._result == None:
			self._result = self._node._result_queues_for_future[self._queue_key].get()

		self._done_callback(self._result)

	def add_done_callback(self, func):
		if self._added_done_callback:
			raise RuntimeError("Cannot add_done_callback more than once.")

		if self.done():
			raise RuntimeError("Task already done.")

		self._done_callback = func
		self._done_callback_args = args
		self._done_callback_kwargs = kwargs

		self._monitor_done_thread = threading.Thread(target=self._get_result)
		self._monitor_done_thread.start()
		self._added_done_callback = True

class Node:
	class Pipe:
		def __init__(self, node, name):
			self._node = node
			self._name = name

		def send(self, value):
			self._node._locals_pipe_send(self._name, value)

		def recv(self):
			return self._node._locals_pipe_recv(self._name)

	class Pipes:
		def __init__(self, node):
			self._node = node

		def __getitem__(self, name):
			return Node.Pipe(self._node, name)

		# def __delitem__(self, name):
		# 	self._node._locals_pipes_delitem(name)

		def __len__(self):
			return self._node._locals_pipes_len()

		def __contains__(self, name):
			return self._node._locals_pipes_contains(name)

		def keys(self):
			return self._node._locals_pipes_keys()

		def values(self):
			values = []
			for key in self.keys():
				values.append(self[key])

			return values

		def items(self):
			items = []
			for key in self.keys():
				items.append((key, self[key]))

			return values

		def __iter__(self):
			return self._node._locals_pipes_iter()

		# def clear(self):
		# 	self._node._locals_pipes_clear()

	class Queue:
		def __init__(self, node, name, private=False):
			self._node = node
			self._name = name
			self._is_private = private

		def get(self, timeout = None, block = True):
			return self._node._locals_queue_get(self._name, timeout=timeout, block=block, is_private=self._is_private)

		def put(self, value, timeout = None, block = True):
			self._node._locals_queue_put(self._name, value, timeout=timeout, block=block, is_private=self._is_private)

		def __len__(self):
			return self._node._locals_queue_len(self._name, is_private=self._is_private)

	class Queues:
		def __init__(self, node, private=False):
			self._node = node
			self._is_private = private

		def __getitem__(self, name):
			return Node.Queue(self._node, name, private=self._is_private)

		# def __delitem__(self, name):
		# 	self._node._locals_queues_delitem(name, is_private=self._is_private)

		def __len__(self):
			return self._node._locals_queues_len(is_private=self._is_private)

		def __contains__(self, name):
			return self._node._locals_queues_contains(name, is_private=self._is_private)

		def keys(self):
			return self._node._locals_queues_keys(is_private=self._is_private)

		def values(self):
			values = []
			for key in self.keys():
				values.append(self[key])

			return values

		def items(self):
			items = []
			for key in self.keys():
				items.append((key, self[key]))
			return items

		def __iter__(self):
			return self._node._locals_queues_iter(is_private=self._is_private)

		# def clear(self):
		# 	self._node._locals_queues_clear(is_private=self._is_private)

	class Globals:
		class Queue:
			def __init__(self, node, name):
				self._node = node
				self._name = name

			def get(self, timeout = None, block = True):
				return self._node._globals_queue_get(self._name, timeout=timeout, block=block)

			def put(self, value, timeout = None, block = True):
				self._node._globals_queue_put(self._name, value, timeout=timeout, block=block)

			def __len__(self):
				return self._node._globals_queue_len(self._name)

		class Queues:
			def __init__(self, node):
				self._node = node

			def __getitem__(self, name):
				return Node.Globals.Queue(self._node, name)

			# def __delitem__(self, name):
			# 	self._node._globals_queues_delitem(name)

			def __len__(self):
				return self._node._globals_queues_len()

			def __contains__(self, name):
				return self._node._globals_queue_contains(name)

			def keys(self):
				return self._node._globals_queues_keys()

			def values(self):
				values = []
				for key in self.keys():
					values.append(self[key])
				return values

			def items(self):
				items = []
				for key in self.keys():
					items.append((key, self[key]))
				return items

			def __iter__(self):
				return self._node._globals_queues_iter()

			# def clear(self):
			# 	self._node._globals_queues_clear()

		def __init__(self, node):
			self._node = node
			self._queues = Node.Globals.Queues(node)

		def __setitem__(self, name, value):
			self._node._globals_setitem(name, value)

		def __getitem__(self, name):
			return self._node._globals_getitem(name)

		def __delitem__(self, name):
			return self._node._globals_delitem(name)

		def __iter__(self):
			return self._node._globals_iter()

		def __contains__(self, name):
			return self._node._globals_contains(name)

		def __len__(self):
			return self._node._globals_len()

		def clear(self):
			self._node._globals_clear()

		def keys(self):
			return self._node._globals_keys()

		def values(self):
			return self._node._globals_values()

		def items(self):
			return self._node._globals_items()

		def pop(self, name):
			return self._node._globals_pop(name)

		@property
		def queues(self):
			return self._queues
		
	complex_request = ["get_file", "put_file",
	                   "eval", "exec", "system",
	                   "call", "call_remote",
	                   "run", "run_remote"]
	def __init__(self, connection, server = None):
		# session id:
		# request a new session id use -1
		# close use -2

		self._connection = connection

		self._server = server

		self._pipes = Node.Pipes(self)
		self._queues = Node.Queues(self)
		self._result_queues_for_future = Node.Queues(self, private=True)

		if self._server == None:
			self._local_vars = {}
			self._pipe = multiprocessing.Pipe()
			self._queue = queue.Queue()
			self._actual_pipes = {}
			self._actual_queues = {}
			self._actual_result_queues_for_future = {}
			self._address = self._connection.getsockname()
			self._server_address = self._connection.getpeername()
		else:
			self._next_session_id = 0
			self._address = self._connection.getpeername()
			self._server_address = server.address
			
		self._globals = Node.Globals(self)
		self._not_close = True
		self._processing_request_thread = None
		self._recving_thread = None
		self._decoding_thread = None
		self._cancel_task = {}

		self._binary_buffer_lock = threading.Lock()
		self._binary_buffer = b''

		self._recved_vars_lock = threading.Lock()
		self._recved_vars = []
		
		self._simple_threads_pool = None
		self._complex_threads_pool = None

		self._start()

	def __del__(self):
		try:
			self.close()
		except:
			pass

	def close(self):
		try:
			if self._server == None:
				self._request(session_id=-2)
				self._not_close = False
				self._connection.close()
			else:
				self._not_close = False
				self._connection.close()
				self._server.disconnect_result[self.address] = self._server._onDisconnect(self.address)
				self._server._connected_nodes.pop(self.address)
		except:
			self._not_close = False
			try:
				self._connection.close()
			except:
				pass

		if self._simple_threads_pool != None:
			self._simple_threads_pool.shutdown()
			self._simple_threads_pool = None

		if self._complex_threads_pool != None:
			self._complex_threads_pool.shutdown()
			self._complex_threads_pool = None

	@property
	def is_closed(self):
		return not self._not_close

	@property
	def address(self):
		return self._address

	@property
	def server_address(self):
		return self._server_address

	@property
	def locals(self):
		return self

	@property
	def globals(self):
		return self._globals

	@property
	def queues(self):
		return self._queues

	@property
	def pipes(self):
		return self._pipes
	
	## local main pipe
	def send(self, value):
		if self._server == None:
			self._pipe[1].send(value)
		else:
			session_id = self._get_session_id()
			self._request(session_id, value=value)
			response = self._recv_response(session_id)
			if not response["success"]:
				eprint(response["traceback"])
				raise response["exception"]

	def recv(self):
		if self._server == None:
			return self._pipe[1].recv()
		else:
			session_id = self._get_session_id()
			self._request(session_id)
			response = self._recv_response(session_id)
			if response["success"]:
				return response["data"]["value"]
			else:
				eprint(response["traceback"])
				raise response["exception"]

	## local pipes
	def _locals_pipe_send(self, name, value):
		if self._server == None:
			if name not in self._actual_pipes:
				self._actual_pipes[name] = multiprocessing.Pipe()

			self._actual_pipes[name][1].send(value)
		else:
			session_id = self._get_session_id()
			self._request(session_id, name=name, value=value)
			response = self._recv_response(session_id)
			if not response["success"]:
				eprint(response["traceback"])
				raise response["exception"]

	def _locals_pipe_recv(self, name):
		if self._server == None:
			if name not in self._actual_pipes:
				self._actual_pipes[name] = multiprocessing.Pipe()

			return self._actual_pipes[name][1].recv()
		else:
			session_id = self._get_session_id()
			self._request(session_id, name=name)
			response = self._recv_response(session_id)
			if response["success"]:
				return response["data"]["value"]
			else:
				eprint(response["traceback"])
				raise response["exception"]

	# def _locals_pipes_delitem(self, name):
	# 	if self._server == None:
	# 		self._actual_pipes[name][0].close()
	# 		self._actual_pipes[name][1].close()
	# 		del self._actual_pipes[name]
	# 	else:
	# 		session_id = self._get_session_id()
	# 		self._request(session_id, name=name)
	# 		response = self._recv_response(session_id)
	# 		if not response["success"]:
	# 			eprint(response["traceback"])
	# 			raise response["exception"]

	def _locals_pipes_len(self):
		if self._server == None:
			return len(self._actual_pipes)
		else:
			session_id = self._get_session_id()
			self._request(session_id)
			response = self._recv_response(session_id)
			if response["success"]:
				return response["data"]["len"]
			else:
				eprint(response["traceback"])
				raise response["exception"]

	def _locals_pipes_contains(self, name):
		if self._server == None:
			return self._actual_pipes.__contains__(name)
		else:
			session_id = self._get_session_id()
			self._request(session_id, name=name)
			response = self._recv_response(session_id)
			if response["success"]:
				return response["data"]["contains"]
			else:
				eprint(response["traceback"])
				raise response["exception"]

	def _locals_pipes_keys(self):
		if self._server == None:
			return self._actual_pipes.keys()
		else:
			session_id = self._get_session_id()
			self._request(session_id)
			response = self._recv_response(session_id)
			if response["success"]:
				return response["data"]["keys"]
			else:
				eprint(response["traceback"])
				raise response["exception"]

	def _locals_pipes_iter(self):
		if self._server == None:
			return self._actual_pipes.__iter__()
		else:
			session_id = self._get_session_id()
			self._request(session_id)
			response = self._recv_response(session_id)
			if response["success"]:
				return response["data"]["iter"]
			else:
				eprint(response["traceback"])
				raise response["exception"]

	def _locals_pipes_clear(self):
		if self._server == None:
			for name in self._actual_pipes:
				self._actual_pipes[name][0].close()
				self._actual_pipes[name][1].close()
			self._actual_pipes.clear()
		else:
			session_id = self._get_session_id()
			self._request(session_id)
			response = self._recv_response(session_id)
			if not response["success"]:
				eprint(response["traceback"])
				raise response["exception"]

	## local main queue
	def put(self, value, timeout=None, block=True):
		if self._server == None:
			self._queue.put(value)
		else:
			session_id = self._get_session_id()
			self._request(session_id, value=value, timeout=timeout, block=block)
			response = self._recv_response(session_id)
			if not response["success"]:
				eprint(response["traceback"])
				raise response["exception"]

	def get(self, timeout=None, block=True):
		if self._server == None:
			return self._queue.get()
		else:
			session_id = self._get_session_id()
			self._request(session_id, timeout=timeout, block=block)
			response = self._recv_response(session_id)
			if response["success"]:
				return response["data"]["value"]
			else:
				eprint(response["traceback"])
				raise response["exception"]

	## local queue
	def _locals_queue_put(self, name, value, timeout, block, is_private):
		if self._server == None:
			if not is_private:
				if name not in self._actual_queues:
					self._actual_queues[name] = queue.Queue()
				self._actual_queues[name].put(value, timeout=timeout, block=block)
			else:
				if name not in self._actual_result_queues_for_future:
					self._actual_result_queues_for_future[name] = queue.Queue()
				self._actual_result_queues_for_future[name].put(value, timeout=timeout, block=block)
		else:
			session_id = self._get_session_id()
			self._request(session_id, name=name, value=value, timeout=timeout, block=block, is_private=is_private)
			response = self._recv_response(session_id)
			if not response["success"]:
				eprint(response["traceback"])
				raise response["exception"]

	def _locals_queue_get(self, name, timeout, block, is_private):
		if self._server == None:
			if not is_private:
				if name not in self._actual_queues:
					self._actual_queues[name] = queue.Queue()
				return self._actual_queues[name].get(timeout=timeout, block=block)
			else:
				if name not in self._actual_result_queues_for_future:
					self._actual_result_queues_for_future[name] = queue.Queue()
				return self._actual_result_queues_for_future[name].get(timeout=timeout, block=block)
		else:
			session_id = self._get_session_id()
			self._request(session_id, name=name, timeout=timeout, block=block, is_private=is_private)
			response = self._recv_response(session_id)
			if response["success"]:
				return response["data"]["value"]
			else:
				eprint(response["traceback"])
				raise response["exception"]

	def _locals_queue_len(self, name, is_private):
		if self._server == None:
			if not is_private:
				if name not in self._actual_queues:
					return 0
				else:
					return self._actual_queues[name].qsize()
			else:
				if name not in self._actual_result_queues_for_future:
					return 0
				else:
					return self._actual_result_queues_for_future[name].qsize()
		else:
			session_id = self._get_session_id()
			self._request(session_id, name=name, is_private=is_private)
			response = self._recv_response(session_id)
			if response["success"]:
				return response["data"]["len"]
			else:
				eprint(response["traceback"])
				raise response["exception"]

	# def _locals_queues_delitem(self, name, is_private):
	# 	if self._server == None:
	# 		if not is_private:
	# 			self._actual_queues[name].close()
	# 			del self._actual_queues[name]
	# 		else:
	# 			self._actual_result_queues_for_future[name].close()
	# 			del self._actual_result_queues_for_future[name]
	# 	else:
	# 		session_id = self._get_session_id()
	# 		self._request(session_id, name=name, is_private=is_private)
	# 		response = self._recv_response(session_id)
	# 		if not response["success"]:
	# 			eprint(response["traceback"])
	# 			raise response["exception"]

	def _locals_queues_len(self, is_private):
		if self._server == None:
			if not is_private:
				return self._actual_queues.__len__()
			else:
				return self._actual_result_queues_for_future.__len__()
		else:
			session_id = self._get_session_id()
			self._request(session_id, is_private=is_private)
			response = self._recv_response(session_id)
			if response["success"]:
				return response["data"]["len"]
			else:
				eprint(response["traceback"])
				raise response["exception"]

	def _locals_queues_contains(self, name, is_private):
		if self._server == None:
			if not is_private:
				return self._actual_queues.__contains__(name)
			else:
				return self._actual_result_queues_for_future.__contains__(name)
		else:
			session_id = self._get_session_id()
			self._request(session_id, name=name, is_private=is_private)
			response = self._recv_response(session_id)
			if response["success"]:
				return response["data"]["contains"]
			else:
				eprint(response["traceback"])
				raise response["exception"]

	def _locals_queues_keys(self, is_private):
		if self._server == None:
			if not is_private:
				return self._actual_queues.keys()
			else:
				return self._actual_result_queues_for_future.keys()
		else:
			session_id = self._get_session_id()
			self._request(session_id, is_private=is_private)
			response = self._recv_response(session_id)
			if response["success"]:
				return response["data"]["keys"]
			else:
				eprint(response["traceback"])
				raise response["exception"]

	def _locals_queues_iter(self, is_private):
		if self._server == None:
			if not is_private:
				return self._actual_queues.__iter__()
			else:
				return self._actual_result_queues_for_future.__iter__()
		else:
			session_id = self._get_session_id()
			self._request(session_id, is_private=is_private)
			response = self._recv_response(session_id)
			if response["success"]:
				return response["data"]["iter"]
			else:
				eprint(response["traceback"])
				raise response["exception"]

	def _locals_queues_clear(self, is_private):
		if self._server == None:
			if not is_private:
				for name in self._actual_queues:
					self._actual_queues[name].close()
				self._actual_queues.clear()
			else:
				for name in self._actual_result_queues_for_future:
					self._actual_result_queues_for_future[name].close()
				self._actual_result_queues_for_future.clear()
		else:
			session_id = self._get_session_id()
			self._request(session_id, is_private=is_private)
			response = self._recv_response(session_id)
			if not response["success"]:
				eprint(response["traceback"])
				raise response["exception"]

	## local shared variables
	def __getitem__(self, name):
		if self._server == None:
			return copy.deepcopy(self._local_vars[name])
		else:
			session_id = self._get_session_id()
			self._request(session_id, name=name)
			response = self._recv_response(session_id)
			if response["success"]:
				return response["data"]["value"]
			else:
				eprint(response["traceback"])
				raise response["exception"]

	def __setitem__(self, name, value):
		if self._server == None:
			self._local_vars[name] = value
		else:
			session_id = self._get_session_id()
			self._request(session_id, name=name, value=value)
			response = self._recv_response(session_id)
			if not response["success"]:
				eprint(response["traceback"])
				raise response["exception"]

	def __delitem__(self, name):
		if self._server == None:
			del self._local_vars[name]
		else:
			session_id = self._get_session_id()
			self._request(session_id, name=name)
			response = self._recv_response(session_id)
			if not response["success"]:
				eprint(response["traceback"])
				raise response["exception"]

	def __iter__(self):
		if self._server == None:
			return self._local_vars.__iter__()
		else:
			session_id = self._get_session_id()
			self._request(session_id)
			response = self._recv_response(session_id)
			if response["success"]:
				return response["data"]["iter"]
			else:
				eprint(response["traceback"])
				raise response["exception"]

	def __contains__(self, name):
		if self._server == None:
			return self._local_vars.__contains__(name)
		else:
			session_id = self._get_session_id()
			self._request(session_id, name=name)
			response = self._recv_response(session_id)
			if response["success"]:
				return response["data"]["contains"]
			else:
				eprint(response["traceback"])
				raise response["exception"]

	def __len__(self):
		if self._server == None:
			return self._local_vars.__len__()
		else:
			session_id = self._get_session_id()
			self._request(session_id)
			response = self._recv_response(session_id)
			if response["success"]:
				return response["data"]["len"]
			else:
				eprint(response["traceback"])
				raise response["exception"]

	def clear(self):
		if self._server == None:
			self._local_vars.clear()
		else:
			session_id = self._get_session_id()

			self._request(session_id)
			response = self._recv_response(session_id)
			
			if not response["success"]:
				eprint(response["traceback"])
				raise response["exception"]

	def keys(self):
		if self._server == None:
			return self._local_vars.keys()
		else:
			session_id = self._get_session_id()

			self._request(session_id)
			response = self._recv_response(session_id)
			
			if response["success"]:
				return response["data"]["keys"]
			else:
				eprint(response["traceback"])
				raise response["exception"]

	def values(self):
		if self._server == None:
			return self._local_vars.values()
		else:
			session_id = self._get_session_id()

			self._request(session_id)
			response = self._recv_response(session_id)
			
			if response["success"]:
				return response["data"]["values"]
			else:
				eprint(response["traceback"])
				raise response["exception"]

	def items(self):
		if self._server == None:
			return self._local_vars.items()
		else:
			session_id = self._get_session_id()

			self._request(session_id)
			response = self._recv_response(session_id)
			
			if response["success"]:
				return response["data"]["items"]
			else:
				eprint(response["traceback"])
				raise response["exception"]

	def pop(self, name):
		if self._server == None:
			return self._local_vars.pop(name)
		else:
			session_id = self._get_session_id()

			self._request(session_id, name=name)
			response = self._recv_response(session_id)

			if response["success"]:
				return response["data"]["value"]
			else:
				eprint(response["traceback"])
				raise response["exception"]

	## global shared variables
	def _globals_getitem(self, name):
		if self._server != None:
			return self._server[name]
		else:
			session_id = self._get_session_id()
			self._request(session_id, name=name)
			response = self._recv_response(session_id)
			if response["success"]:
				return response["data"]["value"]
			else:
				eprint(response["traceback"])
				raise response["exception"]

	def _globals_setitem(self, name, value):
		if self._server != None:
			self._server[name] = value
		else:
			session_id = self._get_session_id()
			self._request(session_id, name=name, value=value)
			response = self._recv_response(session_id)
			
			if not response["success"]:
				eprint(response["traceback"])
				raise response["exception"]

	def _globals_delitem(self, name):
		if self._server != None:
			del self._server[name]
		else:
			session_id = self._get_session_id()
			self._request(session_id, name=name)
			response = self._recv_response(session_id)
			
			if not response["success"]:
				eprint(response["traceback"])
				raise response["exception"]

	def _globals_pop(self, name):
		if self._server != None:
			return self._server.pop(name)
		else:
			session_id = self._get_session_id()
			self._request(session_id, name=name)
			response = self._recv_response(session_id)
			
			if response["success"]:
				return response["data"]["value"]
			else:
				eprint(response["traceback"])
				raise response["exception"]

	def _globals_iter(self):
		if self._server != None:
			return self._server.__iter__()
		else:
			session_id = self._get_session_id()
			self._request(session_id)
			response = self._recv_response(session_id)
			
			if response["success"]:
				return response["data"]["iter"]
			else:
				eprint(response["traceback"])
				raise response["exception"]

	def _globals_contains(self, name):
		if self._server != None:
			return self._server.__contains__(name)
		else:
			session_id = self._get_session_id()
			self._request(session_id, name=name)
			response = self._recv_response(session_id)
			
			if response["success"]:
				return response["data"]["contains"]
			else:
				eprint(response["traceback"])
				raise response["exception"]

	def _globals_len(self):
		if self._server != None:
			return self._server.__len__()
		else:
			session_id = self._get_session_id()
			self._request(session_id)
			response = self._recv_response(session_id)
			
			if response["success"]:
				return response["data"]["len"]
			else:
				eprint(response["traceback"])
				raise response["exception"]

	def _globals_keys(self):
		if self._server != None:
			return self._server.keys()
		else:
			session_id = self._get_session_id()
			self._request(session_id)
			response = self._recv_response(session_id)
			
			if response["success"]:
				return response["data"]["keys"]
			else:
				eprint(response["traceback"])
				raise response["exception"]

	def _globals_values(self):
		if self._server != None:
			return self._server.values()
		else:
			session_id = self._get_session_id()
			self._request(session_id)
			response = self._recv_response(session_id)
			
			if response["success"]:
				return response["data"]["values"]
			else:
				eprint(response["traceback"])
				raise response["exception"]

	def _globals_items(self):
		if self._server != None:
			return self._server.items()
		else:
			session_id = self._get_session_id()
			self._request(session_id)
			response = self._recv_response(session_id)
			
			if response["success"]:
				return response["data"]["items"]
			else:
				eprint(response["traceback"])
				raise response["exception"]

	def _globals_clear(self):
		if self._server != None:
			self._server.clear()
		else:
			session_id = self._get_session_id()
			self._request(session_id)
			response = self._recv_response(session_id)
			
			if not response["success"]:
				eprint(response["traceback"])
				raise response["exception"]

	## global queue
	def _globals_queue_get(self, name, timeout = None, block = True):
		if self._server != None:
			return self._server.queues[name].get(timeout=timeout, block=block)
		else:
			session_id = self._get_session_id()
			self._request(session_id, name=name, timeout=timeout)
			response = self._recv_response(session_id)
			
			if response["success"]:
				return response["data"]["value"]
			else:
				eprint(response["traceback"])
				raise response["exception"]

	def _globals_queue_put(self, name, value, timeout = None, block = True):
		if self._server != None:
			self._server.queues[name].put(value, timeout = timeout, block=block)
		else:
			session_id = self._get_session_id()
			self._request(session_id, name=name, value=value, timeout = timeout)
			response = self._recv_response(session_id)
			
			if not response["success"]:
				eprint(response["traceback"])
				raise response["exception"]

	def _globals_queue_len(self, name):
		if self._server != None:
			if name not in self._server.queues:
				return 0
			else:
				return self._server.queues[name].qsize()
		else:
			session_id = self._get_session_id()
			self._request(session_id, name=name)
			response = self._recv_response(session_id)
			
			if response["success"]:
				return response["data"]["len"]
			else:
				eprint(response["traceback"])
				raise response["exception"]

	# def _globals_queues_delitem(self, name):
	# 	if self._server != None:
	# 		del self._server.queues[name]
	# 	else:
	# 		session_id = self._get_session_id()
	# 		self._request(session_id, name=name)
	# 		response = self._recv_response(session_id)
			
	# 		if not response["success"]:
	# 			eprint(response["traceback"])
	# 			raise response["exception"]

	def _globals_queues_len(self):
		if self._server != None:
			return len(self._server.queues)
		else:
			session_id = self._get_session_id()
			self._request(session_id)
			response = self._recv_response(session_id)
			
			if response["success"]:
				return response["data"]["len"]
			else:
				eprint(response["traceback"])
				raise response["exception"]

	def _globals_queues_contains(self, name):
		if self._server != None:
			return self._server.queues.__contains__(name)
		else:
			session_id = self._get_session_id()
			self._request(session_id, name=name)
			response = self._recv_response(session_id)
			
			if response["success"]:
				return response["data"]["contains"]
			else:
				eprint(response["traceback"])
				raise response["exception"]

	def _globals_queues_keys(self):
		if self._server != None:
			return self._server.queues.keys()
		else:
			session_id = self._get_session_id()
			self._request(session_id)
			response = self._recv_response(session_id)
			
			if response["success"]:
				return response["data"]["keys"]
			else:
				eprint(response["traceback"])
				raise response["exception"]

	def _globals_queues_iter(self):
		if self._server != None:
			return self._server.queues.__iter__()
		else:
			session_id = self._get_session_id()
			self._request(session_id)
			response = self._recv_response(session_id)
			
			if response["success"]:
				return response["data"]["iter"]
			else:
				eprint(response["traceback"])
				raise response["exception"]

	def _globals_queues_clear(self):
		if self._server != None:
			self._server.queues.clear()
		else:
			session_id = self._get_session_id()
			self._request(session_id)
			response = self._recv_response(session_id)
			
			if not response["success"]:
				eprint(response["traceback"])
				raise response["exception"]
			
	## file transfer
	def get_file(self, src_filename, dest_filename = None, block=True):
		session_id = self._get_session_id()

		if dest_filename == None:
			dest_filename = os.path.basename(src_filename)

		self._request(session_id, src_filename=src_filename, file_size=file_size(dest_filename), md5=md5(dest_filename), block=block)
		def session():
			response = self._recv_response(session_id)
			if not response["success"]:
				eprint(response["traceback"])
				raise response["exception"]

			if response["data"]["same_file"] or response["cancel"]:
				return

			if not os.path.isdir(os.path.dirname(os.path.abspath(dest_filename))):
				os.makedirs(os.path.dirname(os.path.abspath(dest_filename)))

			try:
				file = open(dest_filename, "wb")
				self._respond_ok(session_id)
				file.close()
			except BaseException as e:
				self._respond_exception(session_id, e)
				raise e

			recved_size = 0
			full_size = response["data"]["file_size"]
			with open(dest_filename, "wb") as file:
				while recved_size < full_size:
					response = self._recv_response(session_id)
					if response["cancel"]:
						break
					file.write(response["data"]["data"])
					file.flush()
					recved_size += len(response["data"]["data"])

		if block:
			session()
		else:
			thread = threading.Thread(target=session)
			thread.start()
			return Future(self, session_id)

	def put_file(self, src_filename, dest_filename = None, block=True):
		session_id = self._get_session_id()

		try:
			file = open(src_filename, "rb")
			file.close()
		except BaseException as e:
			if not block:
				self._put_exception(session_id, e)
			raise e

		if dest_filename == None:
			dest_filename = os.path.basename(src_filename)

		src_file_size = file_size(src_filename)

		self._stop_send = False
		self._request(session_id, func="put_file", md5=md5(src_filename), file_size=src_file_size, dest_filename=dest_filename, block=block)
		
		def session():
			response = self._recv_response(session_id)

			if response["data"]["same_file"] or response["cancel"]:
				return

			if not response["success"]:
				eprint(response["traceback"])
				raise response["exception"]

			block_size = 1024
			sent_size = 0
			with open(src_filename, "rb") as file:
				while sent_size < src_file_size:
					if self._stop_send:
						break
					data = file.read(block_size)
					self._respond_ok(session_id, data=data)
					sent_size += len(data)

		if block:
			session()
		else:
			thread = Thread(target=session)
			thread.start()
			return Future(self, session_id)

	## remote operation
	def eval(self, statement, block=True):
		session_id = self._get_session_id()

		self._request(session_id, statement=statement, block=block)
		if block:
			response = self._recv_response(session_id)

			if response["success"]:
				return response["data"]["return_value"]
			else:
				eprint(response["traceback"])
				raise response["exception"]
		else:
			return Future(self, session_id)

	def exec(self, code, block=True):
		session_id = self._get_session_id()

		self._request(session_id, code=code, block=block)
		if block:
			response = self._recv_response(session_id)
			if not response["success"]:
				eprint(response["traceback"])
				raise response["exception"]
		else:
			return Future(self, session_id)

	def system(self, cmd, quiet=False, remote_quiet=False, once_all=False, block=True):
		session_id = self._get_session_id()

		self._request(session_id, cmd=cmd, remote_quiet=remote_quiet, once_all=once_all, block=block)
		if not once_all:
			def session(session_id, quiet):
				while True:
					response = self._recv_response(session_id)
					if response["success"]:
						if not response["data"]["end"]:
							if not quiet:
								print(response["data"]["stdout"], end="", flush=True)
						else:
							return response["data"]["return_value"]
					else:
						eprint(response["traceback"])
						raise response["exception"]

			if block:
				session(session_id, quiet)
			else:
				thread = Thread(target=session, args=(session_id, quiet))
				thread.start()
				return Future(self, session_id)
		else:
			if block:
				response = self._recv_response(session_id)
				if response["success"]:
					if not quiet:
						print(response["data"]["stdout"], end="", flush=True)
						return response["data"]["return_value"]
				else:
					eprint(response["traceback"])
					raise response["exception"]
			else:
				return Future(self, session_id)

	# call local function on remote computer
	def call(self, target, args=(), kwargs={}, block=True):
		session_id = self._get_session_id()

		self._request(session_id, target=target, args=args, kwargs=kwargs, block=block)
		if block:
			response = self._recv_response(session_id)
			if response["success"]:
				return response["data"]["return_value"]
			else:
				eprint(response["traceback"])
				raise response["exception"]
		else:
			return Future(self, session_id)

	# call remote function on remote computer
	def call_remote(self, target, args=(), kwargs={}, block=True):
		session_id = self._get_session_id()

		self._request(session_id, target=target, args=args, kwargs=kwargs, block=block)
		if block:
			response = self._recv_response(session_id)
			if response["success"]:
				return response["data"]["return_value"]
			else:
				eprint(response["traceback"])
				raise response["exception"]
		else:
			return Future(self, session_id)

	def run(self, script_name, block=True):
		self.put_file(script_name, ".temp_scripts/" + os.path.basename(script_name))
		return self.run_remote(".temp_scripts/" + os.path.basename(script_name), block=block)

	def run_remote(self, script_name, block=True):
		session_id = self._get_session_id()

		self._request(session_id, script_name=script_name, block=block)
		if block:
			response = self._recv_response(session_id)

			if not response["success"]:
				eprint(response["traceback"])
				raise response["exception"]
		else:
			return Future(self, session_id)

	def _start(self):
		if not self._not_close:
			raise ConnectionError("Closed connection cannot reconnect again.")

		self._simple_threads_pool = ThreadPoolExecutor(max_workers=5)
		self._complex_threads_pool = ThreadPoolExecutor(max_workers=1)
		if self._processing_request_thread == None or not self._processing_request_thread.is_alive():
			self._processing_request_thread = threading.Thread(target=self._processing_request, daemon=True)
			self._processing_request_thread.start()

		if self._recving_thread == None or not self._recving_thread.is_alive():
			self._recving_thread = threading.Thread(target=self._recving_loop, daemon=True)
			self._recving_thread.start()

		if self._decoding_thread == None or not self._decoding_thread.is_alive():
			self._decoding_thread = threading.Thread(target=self._decoding_loop, daemon=True)
			self._decoding_thread.start()

	def _get_session_id(self):
		if self._server != None:
			session_id = self._next_session_id
			self._next_session_id += 1
			if self._next_session_id >= 1024:
				self._next_session_id = 0
			return session_id
		else:
			self._request(session_id=-1)
			response = self._recv_response(session_id=-1)
			return response["data"]["target_session_id"]

	def _traceback(self, remote=True):
		exception_list = traceback.format_stack()
		exception_list = exception_list[:-2]
		exception_list.extend(traceback.format_tb(sys.exc_info()[2]))
		exception_list.extend(traceback.format_exception_only(sys.exc_info()[0], sys.exc_info()[1]))

		exception_str = "Traceback (most recent call last):\n"
		if remote:
			exception_str = "Remote"+str(self._server_address) + " " + exception_str

		exception_str += "".join(exception_list)

		return exception_str

	## locals
	## local main pipe
	def _process_send(self, request):
		try:
			self._pipe[0].send(request["data"]["value"])
			self._respond_ok(request["session_id"])
		except BaseException as e:
			self._respond_exception(request["session_id"], e)
		
	def _process_recv(self, request):
		try:
			self._respond_ok(request["session_id"], value=self._pipe[0].recv())
		except BaseException as e:
			self._respond_exception(request["session_id"], e)

	## local pipes
	def _process__locals_pipe_send(self, request):
		try:
			name = request["data"]["name"]
			if name not in self._actual_pipes:
				self._actual_pipes[name] = multiprocessing.Pipe()

			self._actual_pipes[name][0].send(request["data"]["value"])
			self._respond_ok(request["session_id"])
		except BaseException as e:
			self._respond_exception(request["session_id"], e)

	def _process__locals_pipe_recv(self, request):
		try:
			name = request["data"]["name"]
			if name not in self._actual_pipes:
				self._actual_pipes[name] = multiprocessing.Pipe()

			self._respond_ok(request["session_id"], value=self._actual_pipes[name][0].recv())
		except BaseException as e:
			self._respond_exception(request["session_id"], e)

	# def _process__locals_pipes_delitem(self, request):
	# 	try:
	# 		self._actual_pipes[request["data"]["name"]][0].close()
	# 		self._actual_pipes[request["data"]["name"]][1].close()
	# 		del self._actual_pipes[request["data"]["name"]]
	# 		self._respond_ok(request["session_id"])
	# 	except BaseException as e:
	# 		self._respond_exception(request["session_id"], e)

	def _process__locals_pipes_len(self, request):
		try:
			self._respond_ok(request["session_id"], len=self._actual_pipes.__len__())
		except BaseException as e:
			self._respond_exception(request["session_id"], e)

	def _process__locals_pipes_contains(self, request):
		try:
			self._respond_ok(request["session_id"], contains=self._actual_pipes.__contains__(request["data"]["name"]))
		except BaseException as e:
			self._respond_exception(request["session_id"], e)

	def _process__locals_pipes_keys(self, request):
		try:
			self._respond_ok(request["session_id"], keys=self._actual_pipes.keys())
		except BaseException as e:
			self._respond_exception(request["session_id"], e)

	def _process__locals_pipes_iter(self, request):
		try:
			self._respond_ok(request["session_id"], iter=self._actual_pipes.__iter__())
		except BaseException as e:
			self._respond_exception(request["session_id"], e)

	# def _process__locals_pipes_clear(self, request):
	# 	try:
	# 		for name in self._actual_pipes:
	# 			self._actual_pipes[name][0].close()
	# 			self._actual_pipes[name][1].close()
	# 		self._actual_pipes.clear()
	# 		self._respond_ok(request["session_id"])
	# 	except BaseException as e:
	# 		self._respond_exception(request["session_id"], e)

	## local main queue
	def _process_put(self, request):
		try:
			self._queue.put(request["data"]["value"], timeout=request["data"]["timeout"], block=request["block"])
			self._respond_ok(request["session_id"])
		except BaseException as e:
			self._respond_exception(request["session_id"], e)

	def _process_get(self, request):
		try:
			value = self._queue.get(timeout=request["data"]["timeout"], block=request["block"])
			self._respond_ok(request["session_id"], value=value)
		except BaseException as e:
			self._respond_exception(request["session_id"], e)

	## local queues
	def _process__locals_queue_put(self, request):
		try:
			name = request["data"]["name"]
			if not request["data"]["is_private"]:
				if name not in self._actual_queues:
					self._actual_queues[name] = queue.Queue()

				self._actual_queues[name].put(request["data"]["value"], timeout=request["data"]["timeout"], block=request["block"])
			else:
				if name not in self._actual_result_queues_for_future:
					self._actual_result_queues_for_future[name] = queue.Queue()

				self._actual_result_queues_for_future[name].put(request["data"]["value"], timeout=request["data"]["timeout"], block=request["block"])

			self._respond_ok(request["session_id"])
		except BaseException as e:
			self._respond_exception(request["session_id"], e)

	def _process__locals_queue_get(self, request):
		try:
			name = request["data"]["name"]
			if not request["data"]["is_private"]:
				if name not in self._actual_queues:
					self._actual_queues[name] = queue.Queue()

				value = self._actual_queues[request["data"]["name"]].get(timeout=request["data"]["timeout"], block=request["block"])
			else:
				if name not in self._actual_result_queues_for_future:
					self._actual_result_queues_for_future[name] = queue.Queue()

				value = self._actual_result_queues_for_future[request["data"]["name"]].get(timeout=request["data"]["timeout"], block=request["block"])
			self._respond_ok(request["session_id"], value=value)
		except BaseException as e:
			self._respond_exception(request["session_id"], e)

	def _process__locals_queue_len(self, request):
		try:
			if not request["data"]["is_private"]:
				if request["data"]["name"] not in self._actual_queues:
					self._respond_ok(request["session_id"], len=0)
				else:
					self._respond_ok(request["session_id"], len=self._actual_queues[request["data"]["name"]].qsize())
			else:
				if request["data"]["name"] not in self._actual_result_queues_for_future:
					self._respond_ok(request["session_id"], len=0)
				else:
					self._respond_ok(request["session_id"], len=self._actual_result_queues_for_future[request["data"]["name"]].qsize())
		except BaseException as e:
			self._respond_exception(request["session_id"], e)

	# def _process__locals_queues_delitem(self, request):
	# 	try:
	# 		if not request["data"]["is_private"]:
	# 			self._actual_queues[request["data"]["name"]].close()
	# 			del self._actual_queues[request["data"]["name"]]
	# 		else:
	# 			self._actual_result_queues_for_future[request["data"]["name"]].close()
	# 			del self._actual_result_queues_for_future[request["data"]["name"]]
	# 		self._respond_ok(request["session_id"])
	# 	except BaseException as e:
	# 		self._respond_exception(request["session_id"], e)

	def _process__locals_queues_len(self, request):
		try:
			if not request["data"]["is_private"]:
				self._respond_ok(request["session_id"], len=self._actual_queues.__len__())
			else:
				self._respond_ok(request["session_id"], len=self._actual_result_queues_for_future.__len__())
		except BaseException as e:
			self._respond_exception(request["session_id"], e)

	def _process__locals_queues_contains(self, request):
		try:
			if not request["data"]["is_private"]:
				self._respond_ok(request["session_id"], contains=self._actual_queues.__contains__(request["data"]["name"]))
			else:
				self._respond_ok(request["session_id"], contains=self._actual_result_queues_for_future.__contains__(request["data"]["name"]))
		except BaseException as e:
			self._respond_exception(request["session_id"], e)

	def _process__locals_queues_keys(self, request):
		try:
			if not request["data"]["is_private"]:
				self._respond_ok(request["session_id"], keys=self._actual_queues.keys())
			else:
				self._respond_ok(request["session_id"], keys=self._actual_result_queues_for_future.keys())
		except BaseException as e:
			self._respond_exception(request["session_id"], e)

	def _process__locals_queues_iter(self, request):
		try:
			if not request["data"]["is_private"]:
				self._respond_ok(request["session_id"], iter=self._actual_queues.__iter__())
			else:
				self._respond_ok(request["session_id"], iter=self._actual_result_queues_for_future.__iter__())
		except BaseException as e:
			self._respond_exception(request["session_id"], e)

	# def _process__locals_queues_clear(self, request):
	# 	try:
	# 		if not request["data"]["is_private"]:
	# 			for name in self._actual_queues:
	# 				self._actual_queues[name].close()
	# 			self._actual_queues.clear()
	# 		else:
	# 			for name in self._actual_result_queues_for_future:
	# 				self._actual_result_queues_for_future[name].close()
	# 			self._actual_result_queues_for_future.clear()

	# 		self._respond_ok(request["session_id"])
	# 	except BaseException as e:
	# 		self._respond_exception(request["session_id"], e)

	## local shared variables
	def _process___getitem__(self, request):
		try:
			self._respond_ok(request["session_id"], value=self._local_vars[request["data"]["name"]])
		except BaseException as e:
			self._respond_exception(request["session_id"], e)

	def _process___setitem__(self, request):
		try:
			self._local_vars[request["data"]["name"]] = request["data"]["value"]
			self._respond_ok(request["session_id"])
		except BaseException as e:
			self._respond_exception(request["session_id"], e)

	def _process___delitem__(self, request):
		try:
			del self._local_vars[request["data"]["name"]]
			self._respond_ok(request["session_id"])
		except BaseException as e:
			self._respond_exception(request["session_id"], e)

	def _process___iter__(self, request):
		try:
			self._respond_ok(request["session_id"], iter=self._local_vars.__iter__())
		except BaseException as e:
			self._respond_exception(request["session_id"], e)

	def _process___contains__(self, request):
		try:
			self._respond_ok(request["session_id"], contains=self._local_vars.__contains__(request["data"]["name"]))
		except BaseException as e:
			self._respond_exception(request["session_id"], e)

	def _process___len__(self, request):
		try:
			self._respond_ok(request["session_id"], len=self._local_vars.__len__())
		except BaseException as e:
			self._respond_exception(request["session_id"], e)

	def _process_clear(self, request):
		try:
			self._local_vars.clear()
			self._respond_ok(request["session_id"])
		except BaseException as e:
			self._respond_exception(request["session_id"], e)

	def _process_keys(self, request):
		try:
			self._respond_ok(request["session_id"], keys=self._local_vars.keys())
		except BaseException as e:
			self._respond_exception(request["session_id"], e)

	def _process_values(self, request):
		try:
			self._respond_ok(request["session_id"], values=self._local_vars.values())
		except BaseException as e:
			self._respond_exception(request["session_id"], e)

	def _process_items(self, request):
		try:
			self._respond_ok(request["session_id"], items=self._local_vars.items())
		except BaseException as e:
			self._respond_exception(request["session_id"], e)

	def _process_pop(self, request):
		try:
			self._respond_ok(request["session_id"], value=self._local_vars.pop(request["data"]["name"]))
		except BaseException as e:
			self._respond_exception(request["session_id"], e)

	## globals
	## global shared variables
	def _process__globals_getitem(self, request):
		try:
			self._respond_ok(request["session_id"], value=self._server[request["data"]["name"]])
		except BaseException as e:
			self._respond_exception(request["session_id"], e)

	def _process__globals_setitem(self, request):
		try:
			self._server[request["data"]["name"]] = request["data"]["value"]
			self._respond_ok(request["session_id"])
		except BaseException as e:
			self._respond_exception(request["session_id"], e)

	def _process__globals_delitem(self, request):
		try:
			del self._server[request["data"]["name"]]
			self._respond_ok(request["session_id"])
		except BaseException as e:
			self._respond_exception(request["session_id"], e)

	def _process__globals_clear(self, request):
		try:
			self._server.clear()
			self._respond_ok(request["session_id"])
		except BaseException as e:
			self._respond_exception(request["session_id"], e)

	def _process__globals_keys(self, request):
		try:
			self._respond_ok(request["session_id"], keys=self._server.keys())
		except BaseException as e:
			self._respond_exception(request["session_id"], e)

	def _process__globals_values(self, request):
		try:
			self._respond_ok(request["session_id"], values=self._server.values())
		except BaseException as e:
			self._respond_exception(request["session_id"], e)

	def _process__globals_items(self, request):
		try:
			self._respond_ok(request["session_id"], items=self._server.items())
		except BaseException as e:
			self._respond_exception(request["session_id"], e)

	def _process__globals_iter(self, request):
		try:
			self._respond_ok(request["session_id"], iter=self._server.__iter__())
		except BaseException as e:
			self._respond_exception(request["session_id"], e)

	def _process__globals_contains(self, request):
		try:
			self._respond_ok(request["session_id"], contains=self._server.__contains__(request["data"]["name"]))
		except BaseException as e:
			self._respond_exception(request["session_id"], e)

	def _process__globals_len(self, request):
		try:
			self._respond_ok(request["session_id"], len=self._server.__len__())
		except BaseException as e:
			self._respond_exception(request["session_id"], e)

	def _process__globals_pop(self, request):
		try:
			self._respond_ok(request["session_id"], value=self._server.pop(request["data"]["name"]))
		except BaseException as e:
			self._respond_exception(request["session_id"], e)

	# global queue
	def _process__globals_queue_get(self, request):
		try:
			value = self._server.queues[request["data"]["name"]].get(timeout=request["data"]["timeout"], block=request["block"])
			self._respond_ok(request["session_id"], value=value)
		except BaseException as e:
			self._respond_exception(request["session_id"], e)

	def _process__globals_queue_put(self, request):
		try:
			self._server.queues[request["data"]["name"]].put(request["data"]["value"], timeout=request["data"]["timeout"], block=request["block"])
			self._respond_ok(request["session_id"])
		except BaseException as e:
			self._respond_exception(request["session_id"], e)

	def _process__globals_queue_len(self, request):
		try:
			if request["data"]["name"] not in self._server.queues:
				self._respond_ok(request["session_id"], len=0)
			else:
				self._respond_ok(request["session_id"], len=self._server.queues[request["data"]["name"]].qsize())
		except BaseException as e:
			self._respond_exception(request["session_id"], e)

	# def _process__globals_queues_delitem(self, request):
	# 	try:
	# 		del self._server.queues[request["data"]["name"]]
	# 		self._respond_ok(request["session_id"])
	# 	except BaseException as e:
	# 		self._respond_exception(request["session_id"], e)

	def _process__globals_queues_len(self, request):
		try:
			self._respond_ok(request["session_id"], len=self._server.queues.__len__())
		except BaseException as e:
			self._respond_exception(request["session_id"], e)

	def _process__globals_queues_contains(self, request):
		try:
			self._respond_ok(request["session_id"], contains=self._server.queues.__contains__(request["data"]["name"]))
		except BaseException as e:
			self._respond_exception(request["session_id"], e)

	def _process__globals_queues_keys(self, request):
		try:
			self._respond_ok(request["session_id"], keys=self._server.queues.keys())
		except BaseException as e:
			self._respond_exception(request["session_id"], e)

	def _process__globals_queues_iter(self, request):
		try:
			self._respond_ok(request["session_id"], iter=self._server.queues.__iter__())
		except BaseException as e:
			self._respond_exception(request["session_id"], e)

	# def _process__globals_queues_clear(self):
	# 	try:
	# 		self._server.queues.clear()
	# 		self._respond_ok(request["session_id"])
	# 	except BaseException as e:
	# 		self._respond_exception(request["session_id"], e)
 
	class AutoSendBuffer:
		def __init__(self, node, session_id, timeout=0.1, quiet=False):
			self._node = node
			self._session_id = session_id
			self._buffer_lock = threading.Lock()
			self._buffer = b''
			self._quiet = quiet
			self._timeout = timeout
			self._last_send_time = time.time()
			self._continue_send = True
			self._sending_thread = threading.Thread(target=self._timeout_send)
			self._sending_thread.start()

		def __del__(self):
			try:
				self.stop()
			except:
				pass

		def append(self, byte):
			with self._buffer_lock:
				self._buffer += byte

			if byte == b"\n" or len(self._buffer) >= 512:
				self.send()

		def send(self):
			with self._buffer_lock:
				if len(self._buffer) != 0:
					content = self._buffer.decode("utf-8")
					if not self._quiet:
						print(content, end="", flush=True)
					self._node._respond_ok(self._session_id, end=False, stdout=content)
					self._buffer = b''
					self._last_send_time = time.time()

		def stop(self):
			self._continue_send = False
			self._sending_thread.join()
			self.send()

		def _timeout_send(self):
			while self._continue_send:
				if time.time()-self._last_send_time >= self._timeout:
					self.send()
				time.sleep(1E-3)

	def _process_system(self, request):
		session_id = request["session_id"]

		try:
			if not request["data"]["once_all"]:
				process = subprocess.Popen(request["data"]["cmd"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
				self.__sent_end = False
				self.__did_put_result = False
				def session():
					remote_quiet = request["data"]["remote_quiet"]
					auto_send_buffer = Node.AutoSendBuffer(self, session_id, timeout=0.1, quiet=remote_quiet)
					while True:
						byte = process.stdout.read(1)
						if byte == b'':
							break
						auto_send_buffer.append(byte)
					auto_send_buffer.stop()
					process.communicate()
					self._respond_ok(session_id, end=True, return_value=process.returncode)
					self.__sent_end = True
					if not request["block"]:
						self._put_result(session_id, return_value=process.returncode)
						self.__did_put_result = True
					self._make_signal(session_id, cancel=False)

				thread = Thread(target=session)
				thread.start()
				signal = self._recv_signal(session_id)
				if signal["cancel"] and thread.is_alive():
					process.kill()
					thread.kill()
					thread.join()
					if not self.__sent_end:
						self._respond_ok(session_id, end=True, return_value=0, block=request["block"])
					if not self.__did_put_result and not request["block"]:
						self._put_result(session_id, cancel=True)
				else:
					thread.join()
			else:
				process = subprocess.Popen(request["data"]["cmd"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
				def session():
					stdout, stderr = process.communicate()

					stdout = stdout.decode("utf-8")
					if not request["data"]["remote_quiet"]:
						print(stdout, end="", flush=True)

					self._respond_ok(session_id, stdout=stdout, return_value=process.returncode, block=request["block"])
					self._make_signal(session_id, cancel=False)

				thread = Thread(target=session)
				thread.start()
				signal = self._recv_signal(session_id)
				if signal["cancel"] and thread.is_alive():
					process.kill()
					thread.kill()
					thread.join()
					self._put_result(session_id, cancelled=True)
				else:
					thread.join()
				
		except BaseException as e:
			self._respond_exception(session_id, e, block=(request["block"] or not request["data"]["once_all"]))
			
	def _process_eval(self, request):
		session_id = request["session_id"]

		try:
			def session():
				try:
					return_value = eval(request["data"]["statement"])
					self._respond_ok(session_id, return_value=return_value, block=request["block"])
				except BaseException as e:
					self._respond_exception(session_id, e, block=request["block"])
				self._make_signal(session_id, cancel=False)

			thread = Thread(target=session)
			thread.start()
			signal = self._recv_signal(session_id)
			if signal["cancel"] and thread.is_alive():
				thread.kill()
				thread.join()
				self._put_result(session_id, cancelled=True)
			else:
				thread.join()
			
		except BaseException as e:
			self._respond_exception(session_id, e, block=request["block"])
			
	def _process_exec(self, request):
		session_id = request["session_id"]

		try:
			def session():
				try:
					exec(request["data"]["code"], globals())
					self._respond_ok(session_id, block=request["block"])
				except BaseException as e:
					self._respond_exception(session_id, e, block=request["block"])

				self._make_signal(session_id, cancel=False)

			thread = Thread(target=session)
			thread.start()
			signal = self._recv_signal(session_id)
			if signal["cancel"] and thread.is_alive():
				thread.kill()
				thread.join()
				self._put_result(session_id, cancelled=True)
			else:
				thread.join()
		except BaseException as e:
			self._respond_exception(session_id, e, block=request["block"])

	def _process_call(self, request):
		session_id = request["session_id"]

		try:
			def session():
				try:
					return_value = request["data"]["target"](*request["data"]["args"], **request["data"]["kwargs"])
					self._respond_ok(session_id, return_value=return_value, block=request["block"])
				except BaseException as e:
					self._respond_exception(session_id, e, block=request["block"])

				self._make_signal(session_id, cancel=False)

			thread = Thread(target=session)
			thread.start()
			signal = self._recv_signal(session_id)
			if signal["cancel"] and thread.is_alive():
				thread.kill()
				thread.join()
				self._put_result(session_id, cancelled=True)
			else:
				thread.join()
		except BaseException as e:
			self._respond_exception(session_id, e, block=request["block"])

	def _process_call_remote(self, request):
		session_id = request["session_id"]

		try:
			def session():
				try:
					return_value = eval(request["data"]["target"])(*request["data"]["args"], **request["data"]["kwargs"])
					self._respond_ok(session_id, return_value=return_value, block=request["block"])
				except BaseException as e:
					self._respond_exception(session_id, e, block=request["block"])

				self._make_signal(session_id, cancel=False)

			thread = Thread(target=session)
			thread.start()
			signal = self._recv_signal(session_id)
			if signal["cancel"] and thread.is_alive():
				thread.kill()
				thread.join()
				self._put_result(session_id, cancelled=True)
			else:
				thread.join()

		except BaseException as e:
			self._respond_exception(session_id, e, block=request["block"])

	def _process_run_remote(self, request):
		session_id = request["session_id"]

		try:
			def session():
				try:
					exec(open(request["data"]["script_name"]).read(), globals())
					self._respond_ok(session_id, block=request["block"])
				except BaseException as e:
					self._respond_exception(session_id, e, block=request["block"])
				
				self._make_signal(session_id, cancel=False)

			thread = Thread(target=session)
			thread.start()
			signal = self._recv_signal(session_id)
			if signal["cancel"] and thread.is_alive():
				thread.kill()
				thread.join()
				self._put_result(session_id, cancelled=True)
			else:
				thread.join()

		except BaseException as e:
			self._respond_exception(session_id, e, block=request["block"])

	def _process_put_file(self, request):
		session_id = request["session_id"]
		def session():
			dest_filename = request["data"]["dest_filename"]
			full_size = request["data"]["file_size"]

			if full_size == file_size(dest_filename) and \
			   request["data"]["md5"] == md5(dest_filename):
				self._respond_ok(session_id, same_file=True, block=request["block"])
				self._make_signal(session_id, cancel=False)
				return
			
			if not os.path.isdir(os.path.dirname(os.path.abspath(dest_filename))):
				os.makedirs(os.path.dirname(os.path.abspath(dest_filename)))
			
			try:
				file = open(dest_filename, "wb")
				file.close()
				self._respond_ok(session_id, same_file=False)
			except BaseException as e:
				self._respond_exception(session_id, e, same_file=False, block=request["block"])
				self._make_signal(session_id, cancel=False)
				return

			recved_size = 0
			with open(dest_filename, "wb") as file:
				while recved_size < full_size:
					response = self._recv_response(session_id)					
					file.write(response["data"]["data"])
					file.flush()
					recved_size += len(response["data"]["data"])

			if not request["block"]:
				self._put_result(session_id)

			self._make_signal(session_id, cancel=False)

		thread = Thread(target=session)
		thread.start()
		signal = self._recv_signal(session_id)
		if signal["cancel"] and thread.is_alive():
			thread.kill()
			thread.join()
			self._put_result(session_id, cancelled=True)
		else:
			thread.join()

	def _process_get_file(self, request):
		session_id = request["session_id"]

		def session():
			src_filename = request["data"]["src_filename"]
			src_file_size = file_size(src_filename)

			same_file = (src_file_size != 0 and request["data"]["file_size"] == src_file_size and \
				         request["data"]["md5"] == md5(src_filename))
			try:
				file = open(src_filename, "rb")
				file.close()
				self._respond_ok(session_id, same_file=same_file, file_size=src_file_size)
			except BaseException as e:
				self._respond_exception(session_id, e, same_file=same_file, block=request["block"])
				self._make_signal(session_id, cancel=False)
				return

			if same_file:
				if not request["block"]:
					self._put_result(session_id)
				self._make_signal(session_id, cancel=False)
				return

			response = self._recv_response(session_id)
			if not response["success"]:
				if not request["block"]:
					self._put_exception(session_id, response["exception"])
				self._make_signal(session_id, cancel=False)
				return
			
			block_size = 1024
			sent_size = 0
			with open(src_filename, "rb") as file:
				while sent_size < src_file_size:
					data = file.read(block_size)
					self._respond_ok(session_id, data=data)
					sent_size += len(data)

			if not request["block"]:
				self._put_result(session_id)

			self._make_signal(session_id, cancel=False)

		thread = Thread(target=session)
		thread.start()
		signal = self._recv_signal(session_id)
		if signal["cancel"] and thread.is_alive():
			thread.kill()
			thread.join()
			self._respond_ok(session_id, cancel=True)
			self._put_result(session_id, cancelled=True)
		else:
			thread.join()

	def _process__get_session_id(self, request):
		self._respond_ok(session_id=-1, target_session_id=self._next_session_id)
		self._next_session_id += 1
		if self._next_session_id >= 1024:
			self._next_session_id = 0

	def _process_close(self, request):
		self.close()

	def _processing_request(self):
		while self._not_close:
			try:
				request = self._recv_request()
			except:
				break

			if request["type"] == "request":
				if request["func"] in Node.complex_request:
					self._complex_threads_pool.submit(eval("self._process_" + request["func"]), request)
				else:
					self._simple_threads_pool.submit(eval("self._process_" + request["func"]), request)

	def _send(self, value):
		if not self._not_close:
			raise ConnectionError("Connection is closed.")

		binary = cloudpickle.dumps(value)
		length = len(binary)
		self._connection.sendall(length.to_bytes(4, byteorder='little', signed=False) + binary)

	def _send_signal(self, session_id, **kwargs):
		cancel = kwargs["cancel"]
		if "cancel" in kwargs:
			cancel = kwargs.pop("cancel")

		signal = \
		{
			"session_id": session_id,
			"type": "signal",
			"cancel": cancel,
			"data": kwargs
		}
		self._send(signal)

	def _request(self, session_id, **kwargs):
		block = True
		if "block" in kwargs:
			block = kwargs.pop("block")

		func = sys._getframe().f_back.f_code.co_name
		if "func" in kwargs:
			func = kwargs.pop("func")

		request = \
		{
			"session_id": session_id,
			"type": "request",
			"func": func,
			"block": block,
			"data": kwargs
		}
		self._send(request)

	def _respond_ok(self, session_id, **kwargs):
		block = True
		if "block" in kwargs:
			block = kwargs.pop("block")
		cancel = False
		if "cancel" in kwargs:
			cancel = kwargs.pop("cancel")

		if block:
			response = \
			{
				"session_id": session_id,
				"type": "response",
				"success": (not cancel),
				"cancel": cancel,
				"data": kwargs
			}
			self._send(response)
		else:
			self._put_result(session_id, **kwargs)

	def _respond_exception(self, session_id, exception, **kwargs):
		block = True
		if "block" in kwargs:
			block = kwargs.pop("block")

		if block:
			response = \
			{
				"session_id": session_id,
				"type": "response",
				"success": False,
				"exception": exception,
				"traceback": self._traceback(),
				"data": kwargs
			}
			self._send(response)
		else:
			self._put_exception(session_id, exception, **kwargs)

	def _put_result(self, session_id, **kwargs):
		result = dict(success=True, return_value=None, exception=None, traceback=None, cancelled=False)
		for key in result:
			if key in kwargs:
				result[key] = kwargs.pop(key)
		result["data"] = kwargs

		queue_key = "__future_" + str(session_id)
		self._result_queues_for_future[queue_key].put(result)

	def _put_exception(self, session_id, exception, **kwargs):
		result = dict(success=False, return_value=None, exception=exception, traceback=self._traceback(), cancelled=False)
		for key in result:
			if key in kwargs:
				result[key] = kwargs.pop(key)
		result["data"] = kwargs

		queue_key = "__future_" + str(session_id)
		self._result_queues_for_future[queue_key].put(result)

	def _make_signal(self, session_id, **kwargs):
		cancel = False
		if "cancel" in kwargs:
			cancel = kwargs.pop("cancel")

		signal = \
		{
			"session_id": session_id,
			"type": "signal",
			"cancel": cancel,
			"data": kwargs
		}

		self._recved_vars.append(signal)
		
	def _recv_signal(self, session_id):
		signal = None
		need_pop_i = -1

		while True:
			if not self._not_close:
				raise ConnectionError("Connection is closed.")

			with self._recved_vars_lock:
				for i in range(len(self._recved_vars)):
					if self._recved_vars[i]["session_id"] == session_id and self._recved_vars[i]["type"] == "signal":
						need_pop_i = i
						signal = self._recved_vars[i]
						break

			if need_pop_i != -1:
				self._recved_vars.pop(need_pop_i)
				break
			time.sleep(1E-3*random.random())

		return signal

	def _recv_response(self, session_id):
		response = None
		need_pop_i = -1

		while True:
			if not self._not_close:
				raise ConnectionError("Connection is closed.")

			with self._recved_vars_lock:
				for i in range(len(self._recved_vars)):
					if self._recved_vars[i]["session_id"] == session_id and self._recved_vars[i]["type"] == "response":
						need_pop_i = i
						response = self._recved_vars[i]
						break

			if need_pop_i != -1:
				self._recved_vars.pop(need_pop_i)
				break
			time.sleep(1E-3*random.random())

		return response

	def _recv_request(self):
		request = None
		need_pop_i = -1
		while True:
			if not self._not_close:
				raise ConnectionError("Connection is closed.")

			with self._recved_vars_lock:
				for i in range(len(self._recved_vars)):
					if self._recved_vars[i]["type"] == "request":
						need_pop_i = i
						request = self._recved_vars[i]
						break

			if need_pop_i != -1:
				self._recved_vars.pop(need_pop_i)
				break
			time.sleep(1E-3*random.random())

		return request

	def _recving_loop(self):
		while self._not_close:
			try:
				recved_binary = self._connection.recv(4096)
				with self._binary_buffer_lock:
					self._binary_buffer += recved_binary
			except BaseException as e:
				self.close()
			time.sleep(1E-3*random.random())

	def _decoding_loop(self):
		while self._not_close:
			try:
				with self._binary_buffer_lock:
					_copy_binary_buffer = copy.deepcopy(self._binary_buffer)
					self._binary_buffer = b''

				length = len(_copy_binary_buffer)
				pos = 0
				with self._recved_vars_lock:
					while pos < length:
						var_length = int.from_bytes(_copy_binary_buffer[pos:pos+4], byteorder="little", signed=False)
						var_bytes = _copy_binary_buffer[pos+4:pos+4+var_length]
						if var_length > len(var_bytes):
							length_delta = var_length - len(var_bytes)
							while True:
								if not self._not_close:
									raise ConnectionError("Connection is closed.")
								with self._binary_buffer_lock:
									if len(self._binary_buffer) >= length_delta:
										var_bytes += self._binary_buffer[:length_delta]
										self._binary_buffer = self._binary_buffer[length_delta:]
										break
								time.sleep(1E-3*random.random())
						self._recved_vars.append(pickle.loads(var_bytes))
						pos += (4 + var_length)
			except BaseException as e:
				self.close()
			time.sleep(1E-3*random.random())

class Client(Node):
	def __init__(self):
		self._not_close = False

	def connect(self, ip, port = None):
		if self._not_close != False:
			self.close()

		server_address = ip
		if port != None:
			server_address = (ip, port)

		self._connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self._connection.connect(server_address)
		Node.__init__(self, self._connection)

class Server:
	class Queues:
		def __init__(self):
			self._queue_dict = {}

		def __getitem__(self, name):
			if name not in self._queue_dict:
				self._queue_dict[name] = queue.Queue()

			return self._queue_dict[name]

		# def __delitem__(self, name):
		# 	self._queue_dict[name].close()
		# 	del self._queue_dict[name]

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

		# def clear(self):
		# 	for name in self._queue_dict:
		# 		self._queue_dict[name].close()

		# 	self._queue_dict.clear()

	def __init__(self, onConnect = lambda client : None, onDisconnect = lambda address : None):
		self.connect_results = OrderedDict()
		self.disconnect_results = OrderedDict()
		self._onConnect = onConnect
		self._onDisconnect = onDisconnect

		self._connected_nodes = OrderedDict()
		self._global_vars = {}
		self._queues = Server.Queues()

		self._continue_accept = False
		self._accept_thread = None
		self.start()

	def start(self):
		if self._continue_accept == False:
			self._connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			# ip = socket.gethostbyname(socket.gethostname())
			ip = [a for a in os.popen('route print').readlines() if ' 0.0.0.0 ' in a][0].split()[-2]
			self._connection.bind((ip, 0))
			self._connection.listen(5)
			
			self._continue_accept = True
			if self._accept_thread == None or not self._accept_thread.is_alive():
				self._accept_thread = threading.Thread(target=self._start, daemon=True)
				self._accept_thread.start()

	def close(self):
		self._continue_accept = False
		try:
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
			
		self._connected_nodes = {}

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

	def _start(self):
		while self._continue_accept:
			try:
				client_socket, address = self._connection.accept()
				self._connected_nodes[address] = Node(client_socket, self)
				self.connect_results[address] = self._onConnect(self._connected_nodes[address])
			except:
				pass