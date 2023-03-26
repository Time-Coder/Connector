import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from _utils import eprint

def __getitem__(self, name):
	if self._parent is None:
		return self._local_vars[name]
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
	if self._parent is None:
		self._local_vars[name] = value
	else:
		session_id = self._get_session_id()
		self._request(session_id, name=name, value=value)
		response = self._recv_response(session_id)
		if not response["success"]:
			eprint(response["traceback"])
			raise response["exception"]

def __delitem__(self, name):
	if self._parent is None:
		del self._local_vars[name]
	else:
		session_id = self._get_session_id()
		self._request(session_id, name=name)
		response = self._recv_response(session_id)
		if not response["success"]:
			eprint(response["traceback"])
			raise response["exception"]

def __iter__(self):
	if self._parent is None:
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
	if self._parent is None:
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
	if self._parent is None:
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
	if self._parent is None:
		self._local_vars.clear()
	else:
		session_id = self._get_session_id()

		self._request(session_id)
		response = self._recv_response(session_id)
		
		if not response["success"]:
			eprint(response["traceback"])
			raise response["exception"]

def keys(self):
	if self._parent is None:
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
	if self._parent is None:
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
	if self._parent is None:
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
	if self._parent is None:
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

def _process___getitem__(self, request):
	try:
		self._respond_ok(request["session_id"], value=self._local_vars[request["data"]["name"]], last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _process___setitem__(self, request):
	try:
		self._local_vars[request["data"]["name"]] = request["data"]["value"]
		self._respond_ok(request["session_id"], last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _process___delitem__(self, request):
	try:
		del self._local_vars[request["data"]["name"]]
		self._respond_ok(request["session_id"], last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _process___iter__(self, request):
	try:
		self._respond_ok(request["session_id"], iter=self._local_vars.__iter__(), last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _process___contains__(self, request):
	try:
		self._respond_ok(request["session_id"], contains=self._local_vars.__contains__(request["data"]["name"]), last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _process___len__(self, request):
	try:
		self._respond_ok(request["session_id"], len=self._local_vars.__len__(), last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _process_clear(self, request):
	try:
		self._local_vars.clear()
		self._respond_ok(request["session_id"], last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _process_keys(self, request):
	try:
		self._respond_ok(request["session_id"], keys=self._local_vars.keys(), last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _process_values(self, request):
	try:
		self._respond_ok(request["session_id"], values=self._local_vars.values(), last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _process_items(self, request):
	try:
		self._respond_ok(request["session_id"], items=self._local_vars.items(), last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _process_pop(self, request):
	try:
		self._respond_ok(request["session_id"], value=self._local_vars.pop(request["data"]["name"]), last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)