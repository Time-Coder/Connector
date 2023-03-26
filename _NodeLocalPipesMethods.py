import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from _utils import eprint

def send(self, value):
	if self._parent is None:
		self._pipe[1].send(value)
	else:
		session_id = self._get_session_id()
		self._request(session_id, value=value)
		response = self._recv_response(session_id)
		if not response["success"]:
			eprint(response["traceback"])
			raise response["exception"]

def _process_send(self, request):
	try:
		self._pipe[0].send(request["data"]["value"])
		self._respond_ok(request["session_id"], last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def recv(self):
	if self._parent is None:
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

def _process_recv(self, request):
	try:
		self._respond_ok(request["session_id"], value=self._pipe[0].recv(), last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _locals_pipe_send(self, name, value):
	if self._parent is None:
		self._actual_pipes[name][1].send(value)
	else:
		session_id = self._get_session_id()
		self._request(session_id, name=name, value=value)
		response = self._recv_response(session_id)
		if not response["success"]:
			eprint(response["traceback"])
			raise response["exception"]

def _process__locals_pipe_send(self, request):
	try:
		name = request["data"]["name"]
		self._actual_pipes[name][0].send(request["data"]["value"])
		self._respond_ok(request["session_id"], last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _locals_pipe_recv(self, name):
	if self._parent is None:
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

def _process__locals_pipe_recv(self, request):
	try:
		name = request["data"]["name"]
		self._respond_ok(request["session_id"], value=self._actual_pipes[name][0].recv(), last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _locals_pipes_delitem(self, name):
	if self._parent is None:
		del self._actual_pipes[name]
	else:
		session_id = self._get_session_id()
		self._request(session_id, name=name)
		response = self._recv_response(session_id)
		if not response["success"]:
			eprint(response["traceback"])
			raise response["exception"]

def _process__locals_pipes_delitem(self, request):
	try:
		name = request["data"]["name"]
		del self._actual_pipes[name]
		self._respond_ok(request["session_id"], last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _locals_pipes_clear(self):
	if self._parent is None:
		self._actual_pipes.clear()
	else:
		session_id = self._get_session_id()
		self._request(session_id)
		response = self._recv_response(session_id)
		if not response["success"]:
			eprint(response["traceback"])
			raise response["exception"]

def _process__locals_pipes_clear(self, request):
	try:
		self._actual_pipes.clear()
		self._respond_ok(request["session_id"], last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _locals_pipes_len(self):
	if self._parent is None:
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

def _process__locals_pipes_len(self, request):
	try:
		self._respond_ok(request["session_id"], len=len(self._actual_pipes), last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _locals_pipes_contains(self, name):
	if self._parent is None:
		return (name in self._actual_pipes)
	else:
		session_id = self._get_session_id()
		self._request(session_id, name=name)
		response = self._recv_response(session_id)
		if response["success"]:
			return response["data"]["contains"]
		else:
			eprint(response["traceback"])
			raise response["exception"]

def _process__locals_pipes_contains(self, request):
	try:
		pipes_contains = (request["data"]["name"] in self._actual_pipes)
		self._respond_ok(request["session_id"], contains=pipes_contains, last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _locals_pipes_keys(self):
	if self._parent is None:
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

def _process__locals_pipes_keys(self, request):
	try:
		self._respond_ok(request["session_id"], keys=self._actual_pipes.keys(), last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _locals_pipes_iter(self):
	if self._parent is None:
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

def _process__locals_pipes_iter(self, request):
	try:
		self._respond_ok(request["session_id"], iter=self._actual_pipes.__iter__(), last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)