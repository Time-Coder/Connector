import multiprocessing
import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from _utils import eprint

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

def _process_send(self, request):
	try:
		self._pipe[0].send(request["data"]["value"])
		self._respond_ok(request["session_id"])
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

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

def _process_recv(self, request):
	try:
		self._respond_ok(request["session_id"], value=self._pipe[0].recv())
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

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

def _process__locals_pipe_send(self, request):
	try:
		name = request["data"]["name"]
		if name not in self._actual_pipes:
			self._actual_pipes[name] = multiprocessing.Pipe()

		self._actual_pipes[name][0].send(request["data"]["value"])
		self._respond_ok(request["session_id"])
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

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

def _process__locals_pipe_recv(self, request):
	try:
		name = request["data"]["name"]
		if name not in self._actual_pipes:
			self._actual_pipes[name] = multiprocessing.Pipe()

		self._respond_ok(request["session_id"], value=self._actual_pipes[name][0].recv())
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _locals_pipe_close(self, name):
	if self._server == None:
		if name not in self._actual_pipes:
			return

		try:
			self._actual_pipes[name][0].close()
		except:
			pass

		try:
			self._actual_pipes[name][1].close()
		except:
			pass
	else:
		session_id = self._get_session_id()
		self._request(session_id, name=name)
		response = self._recv_response(session_id)
		if not response["success"]:
			eprint(response["traceback"])
			raise response["exception"]

def _process__locals_pipe_close(self, request):
	try:
		name = request["data"]["name"]
		if name not in self._actual_pipes:
			self._respond_ok(request["session_id"])
			return

		try:
			self._actual_pipes[name][0].close()
		except:
			pass

		try:
			self._actual_pipes[name][1].close()
		except:
			pass

		self._respond_ok(request["session_id"])
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _locals_pipes_delitem(self, name):
	if self._server == None:
		if name not in self._actual_pipes:
			return

		try:
			self._actual_pipes[name][0].close()
		except:
			pass

		try:
			self._actual_pipes[name][1].close()
		except:
			pass

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
		if name not in self._actual_pipes:
			self._respond_ok(request["session_id"])
			return

		try:
			self._actual_pipes[request["data"]["name"]][0].close()
		except:
			pass

		try:
			self._actual_pipes[request["data"]["name"]][1].close()
		except:
			pass

		del self._actual_pipes[request["data"]["name"]]
		self._respond_ok(request["session_id"])
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _locals_pipes_clear(self):
	if self._server == None:
		for name in self._actual_pipes:
			try:
				self._actual_pipes[name][0].close()
			except:
				pass

			try:
				self._actual_pipes[name][1].close()
			except:
				pass

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
		for name in self._actual_pipes:
			try:
				self._actual_pipes[name][0].close()
			except:
				pass

			try:
				self._actual_pipes[name][1].close()
			except:
				pass

		self._actual_pipes.clear()
		self._respond_ok(request["session_id"])
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

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

def _process__locals_pipes_len(self, request):
	try:
		self._respond_ok(request["session_id"], len=self._actual_pipes.__len__())
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

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

def _process__locals_pipes_contains(self, request):
	try:
		self._respond_ok(request["session_id"], contains=self._actual_pipes.__contains__(request["data"]["name"]))
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

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

def _process__locals_pipes_keys(self, request):
	try:
		self._respond_ok(request["session_id"], keys=self._actual_pipes.keys())
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

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

def _process__locals_pipes_iter(self, request):
	try:
		self._respond_ok(request["session_id"], iter=self._actual_pipes.__iter__())
	except BaseException as e:
		self._respond_exception(request["session_id"], e)