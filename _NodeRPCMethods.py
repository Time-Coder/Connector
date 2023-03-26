import os
import sys
import subprocess

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from _NodeInternalClasses import Future, Thread, AutoSendBuffer
from _utils import eprint

def eval(self, statement, block=True):
	session_id = self._get_session_id()

	self._request(session_id, statement=statement, block=block)
	if block:
		response = self._recv_response(session_id)

		if response["success"]:
			return response["data"]["return_value"]
		else:
			eprint(response["traceback"])
			raise response["exception"]
	else:
		return Future(self, session_id)

def exec(self, code, block=True):
	session_id = self._get_session_id()

	self._request(session_id, code=code, block=block)
	if block:
		response = self._recv_response(session_id)
		if not response["success"]:
			eprint(response["traceback"])
			raise response["exception"]
	else:
		return Future(self, session_id)

def system(self, cmd, quiet=False, remote_quiet=False, once_all=False, block=True):
	session_id = self._get_session_id()

	self._request(session_id, cmd=cmd, remote_quiet=remote_quiet, once_all=once_all, block=block)
	if not once_all:
		def session(session_id, quiet):
			while True:
				response = self._recv_response(session_id)
				if response["success"]:
					if not response["data"]["end"]:
						if not quiet:
							print(response["data"]["stdout"], end="", flush=True)
					else:
						return response["data"]["return_value"]
				else:
					eprint(response["traceback"])
					raise response["exception"]

		if block:
			session(session_id, quiet)
		else:
			thread = Thread(target=session, args=(session_id, quiet))
			thread.start()
			return Future(self, session_id)
	else:
		if block:
			response = self._recv_response(session_id)
			if response["success"]:
				if not quiet:
					print(response["data"]["stdout"], end="", flush=True)
					return response["data"]["return_value"]
			else:
				eprint(response["traceback"])
				raise response["exception"]
		else:
			return Future(self, session_id)

# call local function on remote computer
def call(self, target, args=(), kwargs={}, block=True):
	session_id = self._get_session_id()

	self._request(session_id, target=target, args=args, kwargs=kwargs, block=block)
	if block:
		response = self._recv_response(session_id)
		if response["success"]:
			return response["data"]["return_value"]
		else:
			eprint(response["traceback"])
			raise response["exception"]
	else:
		return Future(self, session_id)

# call remote function on remote computer
def call_remote(self, target, args=(), kwargs={}, block=True):
	session_id = self._get_session_id()

	self._request(session_id, target=target, args=args, kwargs=kwargs, block=block)
	if block:
		response = self._recv_response(session_id)
		if response["success"]:
			return response["data"]["return_value"]
		else:
			eprint(response["traceback"])
			raise response["exception"]
	else:
		return Future(self, session_id)

def execfile(self, script_name, block=True):
	self.put_file(script_name, ".temp_scripts/" + os.path.basename(script_name))
	return self.exec_remote_file(".temp_scripts/" + os.path.basename(script_name), block=block)

def exec_remote_file(self, script_name, block=True):
	session_id = self._get_session_id()

	self._request(session_id, script_name=script_name, block=block)
	if block:
		response = self._recv_response(session_id)

		if not response["success"]:
			eprint(response["traceback"])
			raise response["exception"]
	else:
		return Future(self, session_id)

def _process_system(self, request):
	session_id = request["session_id"]

	try:
		if not request["data"]["once_all"]:
			process = subprocess.Popen(request["data"]["cmd"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
			self.__sent_end = False
			self.__did_put_result = False
			def session():
				remote_quiet = request["data"]["remote_quiet"]
				auto_send_buffer = AutoSendBuffer(self, session_id, timeout=0.1, quiet=remote_quiet)
				while True:
					byte = process.stdout.read(1)
					if byte == b'':
						break
					auto_send_buffer.append(byte)
				auto_send_buffer.stop()
				process.communicate()
				self._respond_ok(session_id, end=True, return_value=process.returncode, last_one=True)
				self.__sent_end = True
				if not request["block"]:
					self._put_result(session_id, return_value=process.returncode)
					self.__did_put_result = True
				self._make_signal(session_id)

			thread = Thread(target=session)
			thread.start()
			signal = self._recv_signal(session_id)
			if signal["cancel"] and thread.is_alive():
				process.kill()
				thread.kill()
				thread.join()
				if not self.__sent_end:
					self._respond_ok(session_id, end=True, return_value=0, block=request["block"], last_one=True)
				if not self.__did_put_result and not request["block"]:
					self._put_result(session_id, cancel=True)
			else:
				thread.join()
		else:
			process = subprocess.Popen(request["data"]["cmd"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
			def session():
				stdout, stderr = process.communicate()

				stdout = stdout.decode("utf-8")
				if not request["data"]["remote_quiet"]:
					print(stdout, end="", flush=True)

				self._respond_ok(session_id, stdout=stdout, return_value=process.returncode, block=request["block"], last_one=True)
				self._make_signal(session_id)

			thread = Thread(target=session)
			thread.start()
			signal = self._recv_signal(session_id)
			if signal["cancel"] and thread.is_alive():
				process.kill()
				thread.kill()
				thread.join()
				self._put_result(session_id, cancelled=True)
			else:
				thread.join()
			
	except BaseException as e:
		self._respond_exception(session_id, e, block=(request["block"] or not request["data"]["once_all"]))
		
def _process_eval(self, request):
	session_id = request["session_id"]

	try:
		def session():
			try:
				return_value = eval(request["data"]["statement"])
				self._respond_ok(session_id, return_value=return_value, block=request["block"], last_one=True)
			except BaseException as e:
				self._respond_exception(session_id, e, block=request["block"])
			self._make_signal(session_id)

		thread = Thread(target=session)
		thread.start()
		signal = self._recv_signal(session_id)
		if signal["cancel"] and thread.is_alive():
			thread.kill()
			thread.join()
			self._put_result(session_id, cancelled=True)
		else:
			thread.join()
		
	except BaseException as e:
		self._respond_exception(session_id, e, block=request["block"])
		
def _process_exec(self, request):
	session_id = request["session_id"]

	try:
		def session():
			try:
				exec(request["data"]["code"], globals())
				self._respond_ok(session_id, block=request["block"], last_one=True)
			except BaseException as e:
				self._respond_exception(session_id, e, block=request["block"])

			self._make_signal(session_id)

		thread = Thread(target=session)
		thread.start()
		signal = self._recv_signal(session_id)
		if signal["cancel"] and thread.is_alive():
			thread.kill()
			thread.join()
			self._put_result(session_id, cancelled=True)
		else:
			thread.join()
	except BaseException as e:
		self._respond_exception(session_id, e, block=request["block"])

def _process_call(self, request):
	session_id = request["session_id"]

	try:
		def session():
			try:
				return_value = request["data"]["target"](*request["data"]["args"], **request["data"]["kwargs"])
				self._respond_ok(session_id, return_value=return_value, block=request["block"], last_one=True)
			except BaseException as e:
				self._respond_exception(session_id, e, block=request["block"])

			self._make_signal(session_id)

		thread = Thread(target=session)
		thread.start()
		signal = self._recv_signal(session_id)
		if signal["cancel"] and thread.is_alive():
			thread.kill()
			thread.join()
			self._put_result(session_id, cancelled=True)
		else:
			thread.join()
	except BaseException as e:
		self._respond_exception(session_id, e, block=request["block"])

def _process_call_remote(self, request):
	session_id = request["session_id"]

	try:
		def session():
			try:
				return_value = eval(request["data"]["target"])(*request["data"]["args"], **request["data"]["kwargs"])
				self._respond_ok(session_id, return_value=return_value, block=request["block"], last_one=True)
			except BaseException as e:
				self._respond_exception(session_id, e, block=request["block"])

			self._make_signal(session_id)

		thread = Thread(target=session)
		thread.start()
		signal = self._recv_signal(session_id)
		if signal["cancel"] and thread.is_alive():
			thread.kill()
			thread.join()
			self._put_result(session_id, cancelled=True)
		else:
			thread.join()

	except BaseException as e:
		self._respond_exception(session_id, e, block=request["block"])

def _process_exec_remote_file(self, request):
	session_id = request["session_id"]

	try:
		def session():
			try:
				exec(open(request["data"]["script_name"]).read(), globals())
				self._respond_ok(session_id, block=request["block"], last_one=True)
			except BaseException as e:
				self._respond_exception(session_id, e, block=request["block"])
			
			self._make_signal(session_id)

		thread = Thread(target=session)
		thread.start()
		signal = self._recv_signal(session_id)
		if signal["cancel"] and thread.is_alive():
			thread.kill()
			thread.join()
			self._put_result(session_id, cancelled=True)
		else:
			thread.join()

	except BaseException as e:
		self._respond_exception(session_id, e, block=request["block"])