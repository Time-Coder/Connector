import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from _utils import eprint

def _server_get(self, timeout=None, block=True):
	session_id = self._get_session_id()
	self._request(session_id, timeout=timeout, block=block)
	response = self._recv_response(session_id)

	if response["success"]:
		return response["data"]["value"]
	else:
		eprint(response["traceback"])
		raise response["exception"]

def _process__server_get(self, request):
	try:
		value = self._parent.get(timeout=request["data"]["timeout"], block=request["block"])
		self._respond_ok(request["session_id"], value=value, last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _server_put(self, value, timeout=None, block=True):
	session_id = self._get_session_id()
	self._request(session_id, value=value, timeout=timeout, block=block, last_one=True)
	response = self._recv_response(session_id)

	if not response["success"]:
		eprint(response["traceback"])
		raise response["exception"]

def _process__server_put(self, request):
	try:
		self._parent.put(request["data"]["value"], timeout=request["data"]["timeout"], block=request["block"])
		self._respond_ok(request["session_id"], last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _server_qsize(self, timeout=None, block=True):
	session_id = self._get_session_id()
	self._request(session_id)
	response = self._recv_response(session_id)

	if response["success"]:
		return response["data"]["qsize"]
	else:
		eprint(response["traceback"])
		raise response["exception"]

def _process__server_qsize(self, request):
	try:
		qsize = self._parent.qsize()
		self._respond_ok(request["session_id"], qsize=qsize, last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _server_queue_get(self, name, timeout=None, block=True):
	session_id = self._get_session_id()
	self._request(session_id, name=name, timeout=timeout, block=block)
	response = self._recv_response(session_id)
	
	if response["success"]:
		return response["data"]["value"]
	else:
		eprint(response["traceback"])
		raise response["exception"]

def _process__server_queue_get(self, request):
	try:
		value = self._parent.queues[request["data"]["name"]].get(timeout=request["data"]["timeout"], block=request["block"])
		self._respond_ok(request["session_id"], value=value, last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _server_queue_put(self, name, value, timeout = None, block = True):
	session_id = self._get_session_id()
	self._request(session_id, name=name, value=value, timeout = timeout)
	response = self._recv_response(session_id)
	
	if not response["success"]:
		eprint(response["traceback"])
		raise response["exception"]

def _process__server_queue_put(self, request):
	try:
		self._parent.queues[request["data"]["name"]].put(request["data"]["value"], timeout=request["data"]["timeout"], block=request["block"])
		self._respond_ok(request["session_id"], last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _server_queue_len(self, name):
	session_id = self._get_session_id()
	self._request(session_id, name=name)
	response = self._recv_response(session_id)
	
	if response["success"]:
		return response["data"]["len"]
	else:
		eprint(response["traceback"])
		raise response["exception"]

def _process__server_queue_len(self, request):
	try:
		if request["data"]["name"] not in self._parent.queues:
			self._respond_ok(request["session_id"], len=0, last_one=True)
		else:
			self._respond_ok(request["session_id"], len=self._parent.queues[request["data"]["name"]].qsize(), last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _server_queues_delitem(self, name):
	session_id = self._get_session_id()
	self._request(session_id, name=name)
	response = self._recv_response(session_id)
	
	if not response["success"]:
		eprint(response["traceback"])
		raise response["exception"]

def _process__server_queues_delitem(self, request):
	try:
		del self._parent.queues[request["data"]["name"]]
		self._respond_ok(request["session_id"], last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _server_queues_len(self):
	session_id = self._get_session_id()
	self._request(session_id)
	response = self._recv_response(session_id)
	
	if response["success"]:
		return response["data"]["len"]
	else:
		eprint(response["traceback"])
		raise response["exception"]

def _process__server_queues_len(self, request):
	try:
		self._respond_ok(request["session_id"], len=self._parent.queues.__len__(), last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _server_queues_contains(self, name):
	session_id = self._get_session_id()
	self._request(session_id, name=name)
	response = self._recv_response(session_id)
	
	if response["success"]:
		return response["data"]["contains"]
	else:
		eprint(response["traceback"])
		raise response["exception"]

def _process__server_queues_contains(self, request):
	try:
		self._respond_ok(request["session_id"], contains=self._parent.queues.__contains__(request["data"]["name"]), last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _server_queues_keys(self):
	session_id = self._get_session_id()
	self._request(session_id)
	response = self._recv_response(session_id)
	
	if response["success"]:
		return response["data"]["keys"]
	else:
		eprint(response["traceback"])
		raise response["exception"]

def _process__server_queues_keys(self, request):
	try:
		self._respond_ok(request["session_id"], keys=self._parent.queues.keys(), last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _server_queues_iter(self):
	session_id = self._get_session_id()
	self._request(session_id)
	response = self._recv_response(session_id)
	
	if response["success"]:
		return response["data"]["iter"]
	else:
		eprint(response["traceback"])
		raise response["exception"]

def _process__server_queues_iter(self, request):
	try:
		self._respond_ok(request["session_id"], iter=self._parent.queues.__iter__(), last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _server_queues_clear(self):
	session_id = self._get_session_id()
	self._request(session_id)
	response = self._recv_response(session_id)
	
	if not response["success"]:
		eprint(response["traceback"])
		raise response["exception"]

def _process__server_queues_clear(self, request):
	try:
		self._parent.queues.clear()
		self._respond_ok(request["session_id"], last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)
