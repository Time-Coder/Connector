import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from _utils import eprint

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

def _process__globals_getitem(self, request):
	try:
		self._respond_ok(request["session_id"], value=self._server[request["data"]["name"]], last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _process__globals_setitem(self, request):
	try:
		self._server[request["data"]["name"]] = request["data"]["value"]
		self._respond_ok(request["session_id"], last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _process__globals_delitem(self, request):
	try:
		del self._server[request["data"]["name"]]
		self._respond_ok(request["session_id"], last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _process__globals_clear(self, request):
	try:
		self._server.clear()
		self._respond_ok(request["session_id"], last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _process__globals_keys(self, request):
	try:
		self._respond_ok(request["session_id"], keys=self._server.keys(), last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _process__globals_values(self, request):
	try:
		self._respond_ok(request["session_id"], values=self._server.values(), last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _process__globals_items(self, request):
	try:
		self._respond_ok(request["session_id"], items=self._server.items(), last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _process__globals_iter(self, request):
	try:
		self._respond_ok(request["session_id"], iter=self._server.__iter__(), last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _process__globals_contains(self, request):
	try:
		self._respond_ok(request["session_id"], contains=self._server.__contains__(request["data"]["name"]), last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _process__globals_len(self, request):
	try:
		self._respond_ok(request["session_id"], len=self._server.__len__(), last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _process__globals_pop(self, request):
	try:
		self._respond_ok(request["session_id"], value=self._server.pop(request["data"]["name"]), last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)