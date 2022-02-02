import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from _utils import eprint

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

def _process__globals_queue_get(self, request):
	try:
		value = self._server.queues[request["data"]["name"]].get(timeout=request["data"]["timeout"], block=request["block"])
		self._respond_ok(request["session_id"], value=value)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

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

def _process__globals_queue_put(self, request):
	try:
		self._server.queues[request["data"]["name"]].put(request["data"]["value"], timeout=request["data"]["timeout"], block=request["block"])
		self._respond_ok(request["session_id"])
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

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

def _process__globals_queue_len(self, request):
	try:
		if request["data"]["name"] not in self._server.queues:
			self._respond_ok(request["session_id"], len=0)
		else:
			self._respond_ok(request["session_id"], len=self._server.queues[request["data"]["name"]].qsize())
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _globals_queue_close(self, name):
	if self._server != None:
		if name in self._server.queues:
			try:
				return self._server.queues[name].close()
			except:
				pass
	else:
		session_id = self._get_session_id()
		self._request(session_id, name=name)
		response = self._recv_response(session_id)
		
		if response["success"]:
			return response["data"]["len"]
		else:
			eprint(response["traceback"])
			raise response["exception"]

def _process__globals_queue_close(self, request):
	try:
		name = request["data"]["name"]
		if name in self._server.queues:
			try:
				self._server.queues[name].close()
			except:
				pass
		self._respond_ok(request["session_id"])
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _globals_queues_delitem(self, name):
	if self._server != None:
		del self._server.queues[name]
	else:
		session_id = self._get_session_id()
		self._request(session_id, name=name)
		response = self._recv_response(session_id)
		
		if not response["success"]:
			eprint(response["traceback"])
			raise response["exception"]

def _process__globals_queues_delitem(self, request):
	try:
		del self._server.queues[request["data"]["name"]]
		self._respond_ok(request["session_id"])
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

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

def _process__globals_queues_len(self, request):
	try:
		self._respond_ok(request["session_id"], len=self._server.queues.__len__())
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

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

def _process__globals_queues_contains(self, request):
	try:
		self._respond_ok(request["session_id"], contains=self._server.queues.__contains__(request["data"]["name"]))
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

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

def _process__globals_queues_keys(self, request):
	try:
		self._respond_ok(request["session_id"], keys=self._server.queues.keys())
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

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

def _process__globals_queues_iter(self, request):
	try:
		self._respond_ok(request["session_id"], iter=self._server.queues.__iter__())
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

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

def _process__globals_queues_clear(self, request):
	try:
		self._server.queues.clear()
		self._respond_ok(request["session_id"])
	except BaseException as e:
		self._respond_exception(request["session_id"], e)
