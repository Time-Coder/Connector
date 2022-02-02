import threading
import cloudpickle
import pickle
import multiprocessing
import sys
import os
import traceback
from concurrent.futures import ThreadPoolExecutor

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
import _NodeInternalClasses

complex_request = ["get_file", "put_file",
                   "get_folder", "put_folder",
	               "eval", "exec", "system",
	               "call", "call_remote",
	               "execfile", "exec_remote_file"]

def __init__(self, connection, server = None):
	# session id:
	# request a new session id use -1
	# close, write_to_file, close_file use -2

	self._connection = connection

	self._server = server

	self._pipes = _NodeInternalClasses.Pipes(self)
	self._queues = _NodeInternalClasses.Queues(self)
	self._result_queues_for_future = _NodeInternalClasses.Queues(self, private=True)

	if self._server == None:
		self._local_vars = {}
		self._pipe = multiprocessing.Pipe()
		self._queue = _NodeInternalClasses.CloseableQueue()
		self._actual_pipes = {}
		self._actual_queues = {}
		self._actual_result_queues_for_future = {}
		self._address = self._connection.getsockname()
		self._server_address = self._connection.getpeername()
	else:
		self._next_session_id = 0
		self._address = self._connection.getpeername()
		self._server_address = server.address
		
	self._globals = _NodeInternalClasses.Globals(self)
	self._not_close = True
	self._processing_request_thread = None
	self._recving_thread = None
	self._cancel_task = {}

	self._recved_requests = _NodeInternalClasses.CloseableQueue()
	self._recved_responses = _NodeInternalClasses.QueueDict()
	self._recved_signals = _NodeInternalClasses.QueueDict()
	
	self._simple_threads_pool = None
	self._complex_threads_pool = None

	self._out_file = None

	self._start()

def __del__(self):
	try:
		self.close()
	except:
		pass

def hold_on(self):
	threading.Event().wait()

def close(self):
	if self._server == None:
		try:
			self._request(session_id=-2)
		except:
			pass

		self._not_close = False

		try:
			self._connection.close()
		except:
			pass

		try:
			self._queue.close()
		except:
			pass

		try:
			self._pipe[0].close()
		except:
			pass

		try:
			self._pipe[1].close()
		except:
			pass

		for key in self._actual_queues:
			try:
				self._actual_queues[key].close()
			except:
				pass

		for key in self._actual_pipes:
			try:
				self._actual_pipes[key][0].close()
			except:
				pass

			try:
				self._actual_pipes[key][1].close()
			except:
				pass

	else:
		self._not_close = False
		try:
			self._connection.close()
		except:
			pass

		try:
			self._server.disconnect_result[self.address] = self._server._callback_threads_pool.submit(self._server._onDisconnect, self.address)
		except:
			pass

		try:
			self._server._connected_nodes.pop(self.address)
		except:
			pass

	if self._simple_threads_pool != None:
		try:
			self._simple_threads_pool.shutdown()
		except:
			pass
		self._simple_threads_pool = None

	if self._complex_threads_pool != None:
		try:
			self._complex_threads_pool.shutdown()
		except:
			pass
		self._complex_threads_pool = None

	self._recved_requests.close()
	self._recved_signals.clear()
	self._recved_responses.clear()

def _start(self):
	self._simple_threads_pool = ThreadPoolExecutor(max_workers=5)
	self._complex_threads_pool = ThreadPoolExecutor(max_workers=1)
	if self._processing_request_thread == None or not self._processing_request_thread.is_alive():
		self._processing_request_thread = threading.Thread(target=self._processing_request, daemon=True)
		self._processing_request_thread.start()

	if self._recving_thread == None or not self._recving_thread.is_alive():
		self._recving_thread = threading.Thread(target=self._recving_loop, daemon=True)
		self._recving_thread.start()

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
			if request["type"] == "request":
				if request["func"] in complex_request:
					self._complex_threads_pool.submit(eval("self._process_" + request["func"]), request)
				else:
					if request["func"] in ["_write_to_file", "_close_file"]:
						func = eval("self._process_" + request["func"])
						func(request)
					else:
						self._simple_threads_pool.submit(eval("self._process_" + request["func"]), request)
		except:
			pass

def _send(self, value):
	if not self._not_close:
		raise ConnectionError("Connection is closed.")

	binary = cloudpickle.dumps(value, 3)
	length = len(binary)
	self._connection.sendall(length.to_bytes(4, byteorder='little', signed=False) + binary)

def _send_signal(self, session_id, **kwargs):
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
	self._send(signal)

def _request(self, session_id, **kwargs):
	block = True
	if "block" in kwargs:
		block = kwargs.pop("block")

	if "debug" in kwargs:
		print("request:", kwargs["debug"], flush=True)

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

	if "debug" in kwargs:
		print("respond:", kwargs["debug"], flush=True)

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

	if "debug" in kwargs:
		print("respond exception:", kwargs["debug"], flush=True)

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

	self._result_queues_for_future[session_id].put(result)

def _put_exception(self, session_id, exception, **kwargs):
	result = dict(success=False, return_value=None, exception=exception, traceback=self._traceback(), cancelled=False)
	for key in result:
		if key in kwargs:
			result[key] = kwargs.pop(key)
	result["data"] = kwargs

	self._result_queues_for_future[session_id].put(result)

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

	self._recved_signals[session_id].put(signal)
	
def _recv_signal(self, session_id):
	signal = self._recved_signals[session_id].get()

	if "debug" in signal["data"]:
		print("recved signal:", signal["data"]["debug"])

	return signal

def _recv_response(self, session_id):
	response = self._recved_responses[session_id].get()

	if "debug" in response["data"]:
		print("recved response:", response["data"]["debug"])

	return response

def _recv_request(self):
	request = self._recved_requests.get()

	if "debug" in request["data"]:
		print("recved request:", request["data"]["debug"])

	return request

def _recving_loop(self):
	rear_binary = b''
	while True:
		while len(rear_binary) < 4:
			try:
				rear_binary += self._connection.recv(8192)
			except:
				self.close()
				return
		var_length = int.from_bytes(rear_binary[:4], byteorder="little", signed=False)
		var_bytes = rear_binary[4:4+var_length]
		rear_binary = rear_binary[4+var_length:]
		if len(var_bytes) < var_length:
			delta_length = var_length - len(var_bytes)
			while len(rear_binary) < delta_length:
				try:
					rear_binary += self._connection.recv(8192)
				except:
					self.close()
					return
			var_bytes += rear_binary[:delta_length]
			rear_binary = rear_binary[delta_length:]
		var = pickle.loads(var_bytes)
		if isinstance(var, dict) and ("type" in var) and ("session_id" in var):
			session_id = var["session_id"]
			if var["type"] == "request":
				self._recved_requests.put(var)
			elif var["type"] == "response":
				self._recved_responses[session_id].put(var)
			elif var["type"] == "signal":
				self._recved_signals[session_id].put(var)
		else:
			print("Recved not supported var:", var)