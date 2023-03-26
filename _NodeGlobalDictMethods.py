import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from _utils import eprint

def _server_getitem(self, name):
	session_id = self._get_session_id()
	self._request(session_id, name=name)
	response = self._recv_response(session_id)
	if response["success"]:
		return response["data"]["value"]
	else:
		eprint(response["traceback"])
		raise response["exception"]

def _server_setitem(self, name, value):
	session_id = self._get_session_id()
	self._request(session_id, name=name, value=value)
	response = self._recv_response(session_id)
	
	if not response["success"]:
		eprint(response["traceback"])
		raise response["exception"]

def _server_delitem(self, name):
	session_id = self._get_session_id()
	self._request(session_id, name=name)
	response = self._recv_response(session_id)
	
	if not response["success"]:
		eprint(response["traceback"])
		raise response["exception"]

def _server_pop(self, name):
	session_id = self._get_session_id()
	self._request(session_id, name=name)
	response = self._recv_response(session_id)
	
	if response["success"]:
		return response["data"]["value"]
	else:
		eprint(response["traceback"])
		raise response["exception"]

def _server_iter(self):
	session_id = self._get_session_id()
	self._request(session_id)
	response = self._recv_response(session_id)
	
	if response["success"]:
		return response["data"]["iter"]
	else:
		eprint(response["traceback"])
		raise response["exception"]

def _server_contains(self, name):
	session_id = self._get_session_id()
	self._request(session_id, name=name)
	response = self._recv_response(session_id)
	
	if response["success"]:
		return response["data"]["contains"]
	else:
		eprint(response["traceback"])
		raise response["exception"]

def _server_len(self):
	session_id = self._get_session_id()
	self._request(session_id)
	response = self._recv_response(session_id)
	
	if response["success"]:
		return response["data"]["len"]
	else:
		eprint(response["traceback"])
		raise response["exception"]

def _server_keys(self):
	session_id = self._get_session_id()
	self._request(session_id)
	response = self._recv_response(session_id)
	
	if response["success"]:
		return response["data"]["keys"]
	else:
		eprint(response["traceback"])
		raise response["exception"]

def _server_values(self):
	session_id = self._get_session_id()
	self._request(session_id)
	response = self._recv_response(session_id)
	
	if response["success"]:
		return response["data"]["values"]
	else:
		eprint(response["traceback"])
		raise response["exception"]

def _server_items(self):
	session_id = self._get_session_id()
	self._request(session_id)
	response = self._recv_response(session_id)
	
	if response["success"]:
		return response["data"]["items"]
	else:
		eprint(response["traceback"])
		raise response["exception"]

def _server_clear(self):
	session_id = self._get_session_id()
	self._request(session_id)
	response = self._recv_response(session_id)
	
	if not response["success"]:
		eprint(response["traceback"])
		raise response["exception"]

def _process__server_getitem(self, request):
	try:
		self._respond_ok(request["session_id"], value=self._parent[request["data"]["name"]], last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _process__server_setitem(self, request):
	try:
		self._parent[request["data"]["name"]] = request["data"]["value"]
		self._respond_ok(request["session_id"], last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _process__server_delitem(self, request):
	try:
		del self._parent[request["data"]["name"]]
		self._respond_ok(request["session_id"], last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _process__server_clear(self, request):
	try:
		self._parent.clear()
		self._respond_ok(request["session_id"], last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _process__server_keys(self, request):
	try:
		self._respond_ok(request["session_id"], keys=self._parent.keys(), last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _process__server_values(self, request):
	try:
		self._respond_ok(request["session_id"], values=self._parent.values(), last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _process__server_items(self, request):
	try:
		self._respond_ok(request["session_id"], items=self._parent.items(), last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _process__server_iter(self, request):
	try:
		self._respond_ok(request["session_id"], iter=self._parent.__iter__(), last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _process__server_contains(self, request):
	try:
		self._respond_ok(request["session_id"], contains=self._parent.__contains__(request["data"]["name"]), last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _process__server_len(self, request):
	try:
		self._respond_ok(request["session_id"], len=self._parent.__len__(), last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _process__server_pop(self, request):
	try:
		self._respond_ok(request["session_id"], value=self._parent.pop(request["data"]["name"]), last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)