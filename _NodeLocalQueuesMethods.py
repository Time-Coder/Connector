import CloseableQueue
import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from _utils import eprint

def put(self, value, timeout=None, block=True):
	if self._server == None:
		self._queue.put(value)
	else:
		session_id = self._get_session_id()
		self._request(session_id, value=value, timeout=timeout, block=block)
		response = self._recv_response(session_id)
		if not response["success"]:
			eprint(response["traceback"])
			raise response["exception"]

def get(self, timeout=None, block=True):
	if self._server == None:
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

def _locals_queue_put(self, name, value, timeout, block, is_private):
	if self._server == None:
		if not is_private:
			if name not in self._actual_queues:
				self._actual_queues[name] = CloseableQueue.CloseableQueueFactory()()
			self._actual_queues[name].put(value, timeout=timeout, block=block)
		else:
			if name not in self._actual_result_queues_for_future:
				self._actual_result_queues_for_future[name] = CloseableQueue.CloseableQueueFactory()()
			self._actual_result_queues_for_future[name].put(value, timeout=timeout, block=block)
	else:
		session_id = self._get_session_id()
		self._request(session_id, name=name, value=value, timeout=timeout, block=block, is_private=is_private)
		response = self._recv_response(session_id)
		if not response["success"]:
			eprint(response["traceback"])
			raise response["exception"]

def _locals_queue_get(self, name, timeout, block, is_private):
	if self._server == None:
		if not is_private:
			if name not in self._actual_queues:
				self._actual_queues[name] = CloseableQueue.CloseableQueueFactory()()
			return self._actual_queues[name].get(timeout=timeout, block=block)
		else:
			if name not in self._actual_result_queues_for_future:
				self._actual_result_queues_for_future[name] = CloseableQueue.CloseableQueueFactory()()
			return self._actual_result_queues_for_future[name].get(timeout=timeout, block=block)
	else:
		session_id = self._get_session_id()
		self._request(session_id, name=name, timeout=timeout, block=block, is_private=is_private)
		response = self._recv_response(session_id)
		if response["success"]:
			return response["data"]["value"]
		else:
			eprint(response["traceback"])
			raise response["exception"]

def _locals_queue_close(self, name, is_private):
	if self._server == None:
		if not is_private:
			if name not in self._actual_queues:
				return
			self._actual_queues[name].close()
		else:
			if name not in self._actual_result_queues_for_future:
				return
			self._actual_result_queues_for_future[name].close()
	else:
		session_id = self._get_session_id()
		self._request(session_id, name=name, is_private=is_private)
		response = self._recv_response(session_id)
		if not response["success"]:
			eprint(response["traceback"])
			raise response["exception"]

def _locals_queue_len(self, name, is_private):
	if self._server == None:
		if not is_private:
			if name not in self._actual_queues:
				return 0
			else:
				return self._actual_queues[name].qsize()
		else:
			if name not in self._actual_result_queues_for_future:
				return 0
			else:
				return self._actual_result_queues_for_future[name].qsize()
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
	if self._server == None:
		if not is_private:
			self._actual_queues[name].close()
			del self._actual_queues[name]
		else:
			self._actual_result_queues_for_future[name].close()
			del self._actual_result_queues_for_future[name]
	else:
		session_id = self._get_session_id()
		self._request(session_id, name=name, is_private=is_private)
		response = self._recv_response(session_id)
		if not response["success"]:
			eprint(response["traceback"])
			raise response["exception"]

def _locals_queues_len(self, is_private):
	if self._server == None:
		if not is_private:
			return self._actual_queues.__len__()
		else:
			return self._actual_result_queues_for_future.__len__()
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
	if self._server == None:
		if not is_private:
			return self._actual_queues.__contains__(name)
		else:
			return self._actual_result_queues_for_future.__contains__(name)
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
	if self._server == None:
		if not is_private:
			return self._actual_queues.keys()
		else:
			return self._actual_result_queues_for_future.keys()
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
	if self._server == None:
		if not is_private:
			return self._actual_queues.__iter__()
		else:
			return self._actual_result_queues_for_future.__iter__()
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
	if self._server == None:
		if not is_private:
			for name in self._actual_queues:
				self._actual_queues[name].close()
			self._actual_queues.clear()
		else:
			for name in self._actual_result_queues_for_future:
				self._actual_result_queues_for_future[name].close()
			self._actual_result_queues_for_future.clear()
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
		self._respond_ok(request["session_id"])
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _process_get(self, request):
	try:
		value = self._queue.get(timeout=request["data"]["timeout"], block=request["block"])
		self._respond_ok(request["session_id"], value=value)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _process__locals_queue_put(self, request):
	try:
		name = request["data"]["name"]
		if not request["data"]["is_private"]:
			if name not in self._actual_queues:
				self._actual_queues[name] = CloseableQueue.CloseableQueueFactory()()

			self._actual_queues[name].put(request["data"]["value"], timeout=request["data"]["timeout"], block=request["block"])
		else:
			if name not in self._actual_result_queues_for_future:
				self._actual_result_queues_for_future[name] = CloseableQueue.CloseableQueueFactory()()

			self._actual_result_queues_for_future[name].put(request["data"]["value"], timeout=request["data"]["timeout"], block=request["block"])

		self._respond_ok(request["session_id"])
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _process__locals_queue_get(self, request):
	try:
		name = request["data"]["name"]
		if not request["data"]["is_private"]:
			if name not in self._actual_queues:
				self._actual_queues[name] = CloseableQueue.CloseableQueueFactory()()

			value = self._actual_queues[request["data"]["name"]].get(timeout=request["data"]["timeout"], block=request["block"])
		else:
			if name not in self._actual_result_queues_for_future:
				self._actual_result_queues_for_future[name] = CloseableQueue.CloseableQueueFactory()()

			value = self._actual_result_queues_for_future[request["data"]["name"]].get(timeout=request["data"]["timeout"], block=request["block"])
		self._respond_ok(request["session_id"], value=value)
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _process__locals_queue_len(self, request):
	try:
		if not request["data"]["is_private"]:
			if request["data"]["name"] not in self._actual_queues:
				self._respond_ok(request["session_id"], len=0)
			else:
				self._respond_ok(request["session_id"], len=self._actual_queues[request["data"]["name"]].qsize())
		else:
			if request["data"]["name"] not in self._actual_result_queues_for_future:
				self._respond_ok(request["session_id"], len=0)
			else:
				self._respond_ok(request["session_id"], len=self._actual_result_queues_for_future[request["data"]["name"]].qsize())
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _process__locals_queue_close(self, request):
	try:
		name = request["data"]["name"]
		if not request["data"]["is_private"]:
			try:
				self._actual_queues[name].close()
			except:
				pass
		else:
			try:
				self._actual_result_queues_for_future[name].close()
			except:
				pass
		self._respond_ok(request["session_id"])
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _process__locals_queues_delitem(self, request):
	try:
		name = request["data"]["name"]
		if not request["data"]["is_private"]:
			try:
				self._actual_queues[name].close()
			except:
				pass

			del self._actual_queues[name]
		else:
			try:
				self._actual_result_queues_for_future[name].close()
			except:
				pass
			del self._actual_result_queues_for_future[name]
		self._respond_ok(request["session_id"])
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _process__locals_queues_len(self, request):
	try:
		if not request["data"]["is_private"]:
			self._respond_ok(request["session_id"], len=self._actual_queues.__len__())
		else:
			self._respond_ok(request["session_id"], len=self._actual_result_queues_for_future.__len__())
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _process__locals_queues_contains(self, request):
	try:
		if not request["data"]["is_private"]:
			self._respond_ok(request["session_id"], contains=self._actual_queues.__contains__(request["data"]["name"]))
		else:
			self._respond_ok(request["session_id"], contains=self._actual_result_queues_for_future.__contains__(request["data"]["name"]))
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _process__locals_queues_keys(self, request):
	try:
		if not request["data"]["is_private"]:
			self._respond_ok(request["session_id"], keys=self._actual_queues.keys())
		else:
			self._respond_ok(request["session_id"], keys=self._actual_result_queues_for_future.keys())
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _process__locals_queues_iter(self, request):
	try:
		if not request["data"]["is_private"]:
			self._respond_ok(request["session_id"], iter=self._actual_queues.__iter__())
		else:
			self._respond_ok(request["session_id"], iter=self._actual_result_queues_for_future.__iter__())
	except BaseException as e:
		self._respond_exception(request["session_id"], e)

def _process__locals_queues_clear(self, request):
	try:
		if not request["data"]["is_private"]:
			for name in self._actual_queues:
				try:
					self._actual_queues[name].close()
				except:
					pass
			self._actual_queues.clear()
		else:
			for name in self._actual_result_queues_for_future:
				try:
					self._actual_result_queues_for_future[name].close()
				except:
					pass
			self._actual_result_queues_for_future.clear()

		self._respond_ok(request["session_id"])
	except BaseException as e:
		self._respond_exception(request["session_id"], e)