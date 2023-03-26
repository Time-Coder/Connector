import threading
import dill
import sys
import os
import traceback
import uuid
from concurrent.futures import ThreadPoolExecutor

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from _CloseableQueue import CloseableQueue
from _CloseablePipe import CloseablePipe
import _NodeInternalClasses

complex_request = ["get_file", "put_file",
                   "get_folder", "put_folder",
	               "eval", "exec", "system",
	               "call", "call_remote",
	               "execfile", "exec_remote_file"]

def __init__(self, connection, server = None):
	self._is_Node_init = True
	self._connection = connection
	self._parent = server
	self._pipes = _NodeInternalClasses.Pipes(self)
	self._queues = _NodeInternalClasses.Queues(self)
	self._result_queues_for_future = _NodeInternalClasses.Queues(self, private=True)
	self._recved_binary_queue = CloseableQueue()

	if self._parent is None:
		self._local_vars = {}
		self._pipe = CloseablePipe()
		self._queue = CloseableQueue()
		self._actual_pipes = _NodeInternalClasses.PipeDict()
		self._actual_queues = _NodeInternalClasses.QueueDict()
		self._actual_result_queues_for_future = _NodeInternalClasses.QueueDict()
		self._server_peer = _NodeInternalClasses.ServerPeer(self)
	else:
		self._server_peer = self._parent
		
	self._recving_thread = None
	self._decoding_thread = None

	self._recved_responses = _NodeInternalClasses.QueueDict()
	self._recved_signals = _NodeInternalClasses.QueueDict()

	self._out_file = None

	self._simple_threads_pool = None
	self._complex_threads_pool = None
	
def _start(self):
	if self._simple_threads_pool is None:
		self._simple_threads_pool = ThreadPoolExecutor(max_workers=5)

	if self._complex_threads_pool is None:
		self._complex_threads_pool = ThreadPoolExecutor(max_workers=1)

	if self._recving_thread is None or not self._recving_thread.is_alive():
		self._recving_thread = threading.Thread(target=self._recving_loop, daemon=True)
		self._recving_thread.start()

	if self._decoding_thread is None or not self._decoding_thread.is_alive():
		self._decoding_thread = threading.Thread(target=self._decoding_loop, daemon=True)
		self._decoding_thread.start()

def __del__(self):
	try:
		self.close()
	except:
		pass

def hold_on(self):
	threading.Event().wait()

def close(self):
	if self._parent is None:
		try:
			self._request(session_id=-2)
		except:
			pass

		try:
			self._connection.close()
		except:
			pass

		self._connection = None

		try:
			self._queue.close()
		except:
			pass

		try:
			self._recved_binary_queue.close()
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

		try:
			self._actual_queues.clear()
		except:
			pass

		try:
			self._actual_result_queues_for_future.clear()
		except:
			pass

		try:
			self._actual_pipes.clear()
		except:
			pass

	else:
		try:
			self._connection.close()
		except:
			pass

		self._connection = None
		
		try:
			if self.address is not None:
				self._parent.disconnect_result[self.address] = self._parent._callback_threads_pool.submit(self._parent._on_disconnected, self.address)
		except:
			pass

		try:
			self._parent._connected_nodes.pop(self.address)
		except:
			pass

	if self._simple_threads_pool is not None:
		try:
			self._simple_threads_pool.shutdown()
		except:
			pass
		self._simple_threads_pool = None

	if self._complex_threads_pool is not None:
		try:
			self._complex_threads_pool.shutdown()
		except:
			pass
		self._complex_threads_pool = None

	try:
		self._recved_signals.clear()
	except:
		pass

	try:
		self._recved_responses.clear()
	except:
		pass

def _get_session_id(self):
	return str(uuid.uuid1())

def _close_session(self, sid):	
	if sid in self._recved_signals:
		del self._recved_signals[sid]

	if sid in self._recved_responses:
		del self._recved_responses[sid]

	if self._parent is None:
		del self._actual_result_queues_for_future[sid]

def _traceback(self, remote=True):
	exception_list = traceback.format_stack()
	exception_list = exception_list[:-2]
	exception_list.extend(traceback.format_tb(sys.exc_info()[2]))
	exception_list.extend(traceback.format_exception_only(sys.exc_info()[0], sys.exc_info()[1]))

	exception_str = "Traceback (most recent call last):\n"
	if remote:
		exception_str = "Remote" + str(self.server_address) + " " + exception_str

	exception_str += "".join(exception_list)

	return exception_str

def _process_close(self, request):
	self.close()

def _send(self, value):
	binary = dill.dumps(value, 3)
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

	last_one = False
	if "last_one" in kwargs:
		last_one = kwargs.pop("last_one")

	if "debug" in kwargs:
		print("respond:", kwargs["debug"], flush=True)

	if block:
		response = \
		{
			"session_id": session_id,
			"type": "response",
			"success": (not cancel),
			"cancel": cancel,
			"last_one": last_one,
			"data": kwargs
		}
		self._send(response)
		if last_one:
			self._close_session(session_id)
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
			"last_one": True,
			"data": kwargs
		}
		self._send(response)
		self._close_session(session_id)
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

	if response["last_one"]:
		self._close_session(session_id)

	return response

def _recving_loop(self):
	while True:
		try:
			recved_binary = self._connection.recv(8192*1024)
			self._recved_binary_queue.put(recved_binary)
		except:
			self.close()
			return

def _decoding_loop(self):
	rear_binary = bytearray()
	while True:
		while len(rear_binary) < 4:
			try:
				rear_binary.extend(self._recved_binary_queue.get())
			except:
				return
		var_length = int.from_bytes(rear_binary[:4], byteorder="little", signed=False)
		var_bytes = rear_binary[4:4+var_length]
		rear_binary = rear_binary[4+var_length:]
		if len(var_bytes) < var_length:
			delta_length = var_length - len(var_bytes)
			while len(rear_binary) < delta_length:
				try:
					rear_binary.extend(self._recved_binary_queue.get())
				except:
					return
			var_bytes += rear_binary[:delta_length]
			rear_binary = rear_binary[delta_length:]
		var = dill.loads(var_bytes)
		if isinstance(var, dict) and ("type" in var) and ("session_id" in var):
			session_id = var["session_id"]
			if var["type"] == "request":
				if "debug" in var["data"]:
					print(var["data"]["debug"])

				if var["func"] in complex_request:
					self._complex_threads_pool.submit(eval("self._process_" + var["func"]), var)
				else:
					if var["func"] in ["_write_to_file", "_close_file"]:
						func = eval("self._process_" + var["func"])
						func(var)
					else:
						self._simple_threads_pool.submit(eval("self._process_" + var["func"]), var)
			elif var["type"] == "response":
				self._recved_responses[session_id].put(var)
			elif var["type"] == "signal":
				self._recved_signals[session_id].put(var)
		else:
			print("Recved not supported var:", var)