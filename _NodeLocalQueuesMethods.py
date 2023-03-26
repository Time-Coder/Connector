import sys
import os

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from _utils import eprint

def put(self, value, timeout=None, block=True):
	if self._parent is None:
		self._queue.put(value)
	else:
		session_id = self._get_session_id()
		self._request(session_id, value=value, timeout=timeout, block=block)
		response = self._recv_response(session_id)
		if not response["success"]:
			eprint(response["traceback"])
			raise response["exception"]

def get(self, timeout=None, block=True):
	if self._parent is None:
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

def qsize(self):
	if self._parent is None:
		return self._queue.qsize()
	else:
		session_id = self._get_session_id()
		self._request(session_id)
		response = self._recv_response(session_id)
		if response["success"]:
			return response["data"]["qsize"]
		else:
			eprint(response["traceback"])
			raise response["exception"]

def _used_queues(self, is_private):
	if not is_private:
		return self._actual_queues
	else:
		return self._actual_result_queues_for_future

def _locals_queue_put(self, name, value, timeout, block, is_private):
	if self._parent is None:
		self._used_queues(is_private)[name].put(value, timeout=timeout, block=block)
	else:
		session_id = self._get_session_id()
		self._request(session_id, name=name, value=value, timeout=timeout, block=block, is_private=is_private)
		response = self._recv_response(session_id)
		if not response["success"]:
			eprint(response["traceback"])
			raise response["exception"]

def _locals_queue_get(self, name, timeout, block, is_private):
	if self._parent is None:
		return self._used_queues(is_private)[name].get(timeout=timeout, block=block)
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
	if self._parent is None:
		used_queues = self._used_queues(is_private)
		if name not in used_queues:
			return 0
		else:
			return used_queues[name].qsize()
	else:
		session_id = self._get_session_id()
		self._request(session_id, name=name, is_private=is_private)
		response = self._recv_response(session_id)
		if response["success"]:
			return response["data"]["len"]
		else:
			eprint(response["traceback"])
			raise response["exception"]

def _locals_queues_delitem(self, name, is_private):
	if self._parent is None:
		del self._used_queues(is_private)[name]
	else:
		session_id = self._get_session_id()
		self._request(session_id, name=name, is_private=is_private)
		response = self._recv_response(session_id)
		if not response["success"]:
			eprint(response["traceback"])
			raise response["exception"]

def _locals_queues_len(self, is_private):
	if self._parent is None:
		return len(self._used_queues(is_private))
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
	if self._parent is None:
		return (name in self._used_queues(is_private))
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
	if self._parent is None:
		return self._used_queues(is_private).keys()
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
	if self._parent is None:
		return self._used_queues(is_private).__iter__()
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
	if self._parent is None:
		self._used_queues(is_private).clear()
	else:
		session_id = self._get_session_id()
		self._request(session_id, is_private=is_private)
		response = self._recv_response(session_id)
		if not response["success"]:
			eprint(response["traceback"])
			raise response["exception"]

def _process_put(self, request):
	try:
		self._queue.put(request["data"]["value"], timeout=request["data"]["timeout"], block=request["block"])
		self._respond_ok(request["session_id"], last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _process_get(self, request):
	try:
		value = self._queue.get(timeout=request["data"]["timeout"], block=request["block"])
		self._respond_ok(request["session_id"], value=value, last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _process_qsize(self, request):
	try:
		qsize = self._queue.qsize()
		self._respond_ok(request["session_id"], qsize=qsize, last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _process__locals_queue_put(self, request):
	try:
		name = request["data"]["name"]
		used_queue = self._used_queues(request["data"]["is_private"])[name]
		used_queue.put(request["data"]["value"], timeout=request["data"]["timeout"], block=request["block"])
		self._respond_ok(request["session_id"], last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _process__locals_queue_get(self, request):
	try:
		name = request["data"]["name"]
		used_queue = self._used_queues(request["data"]["is_private"])[name]
		value = used_queue.get(timeout=request["data"]["timeout"], block=request["block"])
		self._respond_ok(request["session_id"], value=value, last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _process__locals_queue_len(self, request):
	try:
		name = request["data"]["name"]
		used_queues = self._used_queues(request["data"]["is_private"])
		queue_len = 0
		if name in used_queues:
			queue_len = used_queues[name].qsize()
		self._respond_ok(request["session_id"], len=queue_len, last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _process__locals_queues_delitem(self, request):
	try:
		name = request["data"]["name"]
		del self._used_queues(request["data"]["is_private"])[name]
		self._respond_ok(request["session_id"], last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _process__locals_queues_len(self, request):
	try:
		queues_len = len(self._used_queues(request["data"]["is_private"]))
		self._respond_ok(request["session_id"], len=queues_len, last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _process__locals_queues_contains(self, request):
	try:
		name = request["data"]["name"]
		is_private = request["data"]["is_private"]
		queues_conntains = (name in self._used_queues(is_private))
		self._respond_ok(request["session_id"], contains=queues_conntains, last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _process__locals_queues_keys(self, request):
	try:
		queues_keys = self._used_queues(request["data"]["is_private"]).keys()
		self._respond_ok(request["session_id"], keys=queues_keys, last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _process__locals_queues_iter(self, request):
	try:
		queues_iter = self._used_queues(request["data"]["is_private"]).__iter__()
		self._respond_ok(request["session_id"], iter=queues_iter, last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _process__locals_queues_clear(self, request):
	try:
		self._used_queues(request["data"]["is_private"]).clear()
		self._respond_ok(request["session_id"], last_one=True)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)