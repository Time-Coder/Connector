import threading
import os
import sys

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from _utils import file_size, md5, eprint
from _NodeInternalClasses import Future, Thread

def _write_to_file(self, data, filename):
	self._request(-2, data=data, file_name=filename)

def _process__write_to_file(self, request):
	try:
		filename = os.path.abspath(request["data"]["file_name"])
		if self._out_file is not None and self._out_file.name != filename:
			self._out_file.close()
			self._out_file = None

		if self._out_file is None:
			if not os.path.isdir(os.path.dirname(filename)):
				os.makedirs(os.path.dirname(filename))

			self._out_file = open(filename, "wb")

		self._out_file.write(request["data"]["data"])
		self._out_file.flush()
	except:
		pass

def _close_file(self):
	self._request(-2)

def _process__close_file(self, request):
	try:
		if self._out_file is not None:
			self._out_file.close()
			self._out_file = None
	except:
		pass

def get_file(self, src_filename, dest_filename = None, block=True):
	session_id = self._get_session_id()

	if dest_filename is None:
		dest_filename = os.path.basename(src_filename)

	self._request(session_id, src_filename=src_filename, file_size=file_size(dest_filename), md5=md5(dest_filename), block=block)
	def session():
		response = self._recv_response(session_id)
		if response["cancel"] or response["data"]["same_file"]:
			return

		if not response["success"]:
			eprint(response["traceback"])
			raise response["exception"]
		
		if not os.path.isdir(os.path.dirname(os.path.abspath(dest_filename))):
			os.makedirs(os.path.dirname(os.path.abspath(dest_filename)))

		try:
			file = open(dest_filename, "wb")
			self._respond_ok(session_id)
			file.close()
		except BaseException as e:
			self._respond_exception(session_id, e)
			if block:
				raise e
			else:
				return

		recved_size = 0
		full_size = response["data"]["file_size"]
		with open(dest_filename, "wb") as file:
			while recved_size < full_size:
				response = self._recv_response(session_id)
				if response["cancel"]:
					break
				file.write(response["data"]["data"])
				file.flush()
				recved_size += len(response["data"]["data"])

	if block:
		session()
	else:
		thread = threading.Thread(target=session)
		thread.start()
		return Future(self, session_id)

def _process_get_file(self, request):
	session_id = request["session_id"]

	def session():
		src_filename = request["data"]["src_filename"]
		src_file_size = file_size(src_filename)

		same_file = (src_file_size != 0 and request["data"]["file_size"] == src_file_size and \
			         request["data"]["md5"] == md5(src_filename))
		try:
			file = open(src_filename, "rb")
			file.close()
			self._respond_ok(session_id, same_file=same_file, file_size=src_file_size, last_one=same_file)
		except BaseException as e:
			self._respond_exception(session_id, e, same_file=same_file, block=request["block"])
			self._make_signal(session_id)
			return

		if same_file:
			if not request["block"]:
				self._put_result(session_id)
			self._make_signal(session_id)
			return

		response = self._recv_response(session_id)
		if not response["success"]:
			if not request["block"]:
				self._put_exception(session_id, response["exception"])
			self._make_signal(session_id)
			return
		
		block_size = 8192*1024
		sent_size = 0
		with open(src_filename, "rb") as file:
			while sent_size < src_file_size:
				data = file.read(block_size)
				sent_size += len(data)
				self._respond_ok(session_id, data=data, last_one=(sent_size==src_file_size))
				
		if not request["block"]:
			self._put_result(session_id)

		self._make_signal(session_id)

	thread = Thread(target=session)
	thread.start()
	signal = self._recv_signal(session_id)
	if signal["cancel"] and thread.is_alive():
		thread.kill()
		thread.join()
		self._respond_ok(session_id, cancel=True, last_one=True)
		self._put_result(session_id, cancelled=True)
	else:
		thread.join()

def put_file(self, src_filename, dest_filename = None, block=True):
	file = open(src_filename, "rb")
	file.close()

	session_id = self._get_session_id()

	if dest_filename is None:
		dest_filename = os.path.basename(src_filename)

	src_file_size = file_size(src_filename)

	self._stop_send = False
	self._request(session_id, md5=md5(src_filename), file_size=src_file_size, dest_filename=dest_filename, block=block)
	
	def session():
		response = self._recv_response(session_id)
		if response["cancel"] or response["data"]["same_file"]:
			return

		if not response["success"]:
			eprint(response["traceback"])
			raise response["exception"]

		block_size = 8192*1024
		sent_size = 0
		with open(src_filename, "rb") as file:
			while sent_size < src_file_size:
				if self._stop_send:
					break
				data = file.read(block_size)
				sent_size += len(data)
				self._respond_ok(session_id, data=data, last_one=(sent_size==src_file_size))
				
	if block:
		session()
	else:
		thread = Thread(target=session)
		thread.start()
		return Future(self, session_id)

def _process_put_file(self, request):
	session_id = request["session_id"]
	def session():
		dest_filename = request["data"]["dest_filename"]
		full_size = request["data"]["file_size"]

		if full_size == file_size(dest_filename) and \
		   request["data"]["md5"] == md5(dest_filename):
			self._respond_ok(session_id, same_file=True, block=request["block"], last_one=True)
			self._make_signal(session_id)
			return
		
		if not os.path.isdir(os.path.dirname(os.path.abspath(dest_filename))):
			os.makedirs(os.path.dirname(os.path.abspath(dest_filename)))
		
		try:
			file = open(dest_filename, "wb")
			file.close()
			self._respond_ok(session_id, same_file=False)
		except BaseException as e:
			self._respond_exception(session_id, e, same_file=False, block=request["block"])
			self._make_signal(session_id)
			return

		recved_size = 0
		with open(dest_filename, "wb") as file:
			while recved_size < full_size:
				response = self._recv_response(session_id)					
				file.write(response["data"]["data"])
				file.flush()
				recved_size += len(response["data"]["data"])

		if not request["block"]:
			self._put_result(session_id)

		self._make_signal(session_id)

	thread = Thread(target=session)
	thread.start()
	signal = self._recv_signal(session_id)
	if signal["cancel"] and thread.is_alive():
		thread.kill()
		thread.join()
		self._respond_ok(session_id, cancel=True, last_one=True)
		self._put_result(session_id, cancelled=True)
	else:
		thread.join()

def get_folder(self, src_foldername, dest_foldername = None, block=True):
	session_id = self._get_session_id()
	if dest_foldername is None:
		dest_foldername = os.path.basename(src_foldername)

	self._request(session_id, src_foldername=src_foldername, block=block)
	# self._request(session_id, src_foldername=src_foldername, block=block, debug="I need folder \"" + src_foldername + "\"")
	def session():
		response = self._recv_response(session_id)
		if response["cancel"]:
			return

		if not response["success"]:
			eprint(response["traceback"])
			raise response["exception"]

		for folder in response["data"]["folders"]:
			if not os.path.isdir(dest_foldername + "/" + folder):
				try:
					os.makedirs(dest_foldername + "/" + folder)
				except:
					eprint(self._traceback(False))
		self._respond_ok(session_id)
		# self._respond_ok(session_id, debug="Created all folders. Please send files.")

		while True:
			response = self._recv_response(session_id)
			if response["cancel"] or response["data"]["finished"]:
				return

			if not response["success"]:
				eprint(response["traceback"])
				continue

			dest_filename = dest_foldername + "/" + response["data"]["file_name"]
			same_file = (response["data"]["file_size"] == file_size(dest_filename) and \
				         response["data"]["md5"] == md5(dest_filename))

			if same_file:
				self._respond_ok(session_id, same_file=same_file)
				# self._respond_ok(session_id, same_file = same_file, debug="Already have file: " + dest_filename)
				continue
			else:
				try:
					file = open(dest_filename, "wb")
					self._respond_ok(session_id, same_file=same_file)
					# self._respond_ok(session_id, same_file = same_file, debug="I don't have this file, please send me.")
					file.close()
				except BaseException as e:
					eprint(self._traceback())
					self._respond_exception(session_id, e)
					# self._respond_exception(session_id, e, debug="Error")
					continue

			recved_size = 0
			full_size = response["data"]["file_size"]
			with open(dest_filename, "wb") as file:
				while recved_size < full_size:
					response = self._recv_response(session_id)
					if response["cancel"]:
						return
					file.write(response["data"]["data"])
					file.flush()
					recved_size += len(response["data"]["data"])

	if block:
		session()
	else:
		thread = threading.Thread(target=session)
		thread.start()
		return Future(self, session_id)

def _process_get_folder(self, request):
	session_id = request["session_id"]
	def session():
		src_foldername = request["data"]["src_foldername"]
		if not os.path.isdir(src_foldername):
			self._respond_exception(session_id, FileNotFoundError(src_foldername + " is not a folder."), block=request["block"])
			self._make_signal(session_id)
			return
		i = len(src_foldername)-1
		while src_foldername[i] in ['/', '\\']:
			i -= 1

		folders = []
		for root, dirs, files in os.walk(src_foldername):
			for name in dirs:
				folders.append(os.path.join(root, name)[i+2:])
		self._respond_ok(session_id, folders=folders)
		# self._respond_ok(session_id, folders=folders, debug="Please create folders: " + str(folders))
		response = self._recv_response(session_id)

		for root, dirs, files in os.walk(src_foldername):
			for name in files:
				src_filename = os.path.join(root, name)
				src_file_size = file_size(src_filename)
				relative_file_name = src_filename[i+2:]
				
				try:
					file = open(src_filename, "rb")
					file.close()
					self._respond_ok(session_id, finished=False, file_name=relative_file_name, file_size=src_file_size, md5=md5(src_filename))
					# self._respond_ok(session_id, finished=False, file_name=relative_file_name, file_size=src_file_size, md5=md5(src_filename), debug="Do you have file " + src_filename + "?")
				except BaseException as e:
					self._respond_exception(session_id, e)
					# self._respond_exception(session_id, e, debug="I cannot open file: " + src_filename)
					continue

				response = self._recv_response(session_id)
				if not response["success"] or response["data"]["same_file"]:
					continue

				block_size = 8192*1024
				sent_size = 0
				with open(src_filename, "rb") as file:
					while sent_size < src_file_size:
						data = file.read(block_size)
						self._respond_ok(session_id, data=data)
						# self._respond_ok(session_id, data=data, debug="Please write " + str(len(data)) + " bytes data to file " + relative_file_name)
						sent_size += len(data)

		self._respond_ok(session_id, finished=True, last_one=True)
		# self._respond_ok(session_id, finished=True, debug="Sent all files.")

		if not request["block"]:
			self._put_result(session_id)

		self._make_signal(session_id)

	thread = Thread(target=session)
	thread.start()
	signal = self._recv_signal(session_id)
	if signal["cancel"] and thread.is_alive():
		thread.kill()
		thread.join()
		self._respond_ok(session_id, cancel=True, last_one=True)
		# self._respond_ok(session_id, cancel=True, debug="Cancel.")
		self._put_result(session_id, cancelled=True)
	else:
		thread.join()

def put_folder(self, src_foldername, dest_foldername = None, block = True):
	if not os.path.isdir(src_foldername):
		raise FileNotFoundError(src_foldername + " is not a folder.")

	session_id = self._get_session_id()

	if dest_foldername is None:
		dest_foldername = os.path.basename(src_foldername)

	self._stop_send = False
	self._request(session_id, dest_foldername=dest_foldername, block=block)
	# self._request(session_id, dest_foldername=dest_foldername, block=block, debug="I will send you folder: " + dest_foldername)
	def session():
		response = self._recv_response(session_id)
		if response["cancel"]:
			return

		if not response["success"]:
			eprint(response["traceback"])
			raise response["exception"]

		i = len(src_foldername)-1
		while src_foldername[i] in ['/', '\\']:
			i -= 1

		folders = []
		for root, dirs, files in os.walk(src_foldername):
			for name in dirs:
				folders.append(os.path.join(root, name)[i+2:])
		self._respond_ok(session_id, folders=folders)
		# self._respond_ok(session_id, folders=folders, debug="Please create folders: " + str(folders))
		response = self._recv_response(session_id)
		if response["cancel"]:
			return

		for root, dirs, files in os.walk(src_foldername):
			for name in files:
				src_filename = os.path.join(root, name)
				src_file_size = file_size(src_filename)
				relative_file_name = src_filename[i+2:]
				
				try:
					file = open(src_filename, "rb")
					file.close()
					self._respond_ok(session_id, finished=False, file_name=relative_file_name, file_size=src_file_size, md5=md5(src_filename))
					# self._respond_ok(session_id, finished=False, file_name=relative_file_name, file_size=src_file_size, md5=md5(src_filename), debug="Do you have file " + relative_file_name + "?")
				except BaseException as e:
					self._respond_exception(session_id, e) # , debug="Error")
					continue

				response = self._recv_response(session_id)
				if response["cancel"]:
					return

				if not response["success"] or response["data"]["same_file"]:
					continue

				block_size = 8192*1024
				sent_size = 0
				with open(src_filename, "rb") as file:
					while sent_size < src_file_size:
						if self._stop_send:
							return
						data = file.read(block_size)
						self._respond_ok(session_id, data=data)
						# self._respond_ok(session_id, data=data, debug="Please write " + str(len(data)) + " bytes to file " + relative_file_name)
						sent_size += len(data)

		self._respond_ok(session_id, finished=True, last_one=True)
		# self._respond_ok(session_id, finished=True, debug="Sent all files.")

	if block:
		session()
	else:
		thread = threading.Thread(target=session)
		thread.start()
		return Future(self, session_id)

def _process_put_folder(self, request):
	session_id = request["session_id"]

	def session():
		dest_foldername = request["data"]["dest_foldername"]
		try:
			if not os.path.isdir(dest_foldername):
				os.makedirs(dest_foldername)
			self._respond_ok(session_id)
			# self._respond_ok(session_id, debug="Created folder " + dest_foldername)
		except BaseException as e:
			self._respond_exception(session_id, e, block=request["block"])
			# self._respond_exception(session_id, e, block=request["block"], debug="Cannot create folder " + dest_foldername)
			self._make_signal(session_id)
			return

		response = self._recv_response(session_id)
		for folder in response["data"]["folders"]:
			if not os.path.isdir(dest_foldername + "/" + folder):
				try:
					os.makedirs(dest_foldername + "/" + folder)
				except:
					pass
		self._respond_ok(session_id)
		# self._respond_ok(session_id, debug="Created all folders.")

		while True:
			response = self._recv_response(session_id)
			if not response["success"]:
				continue

			if response["data"]["finished"]:
				break

			dest_filename = dest_foldername + "/" + response["data"]["file_name"]
			same_file = (response["data"]["file_size"] == file_size(dest_filename) and \
				         response["data"]["md5"] == md5(dest_filename))

			if same_file:
				self._respond_ok(session_id, same_file=same_file)
				# self._respond_ok(session_id, same_file = same_file, debug="Already have file " + dest_filename)
				continue
			else:
				try:
					file = open(dest_filename, "wb")
					self._respond_ok(session_id, same_file=same_file)
					# self._respond_ok(session_id, same_file = same_file, debug="I don't have this file, please send me.")
					file.close()
				except BaseException as e:
					self._respond_exception(session_id, e)
					# self._respond_exception(session_id, e, debug="Error")
					continue

			recved_size = 0
			full_size = response["data"]["file_size"]
			with open(dest_filename, "wb") as file:
				while recved_size < full_size:
					response = self._recv_response(session_id)
					file.write(response["data"]["data"])
					file.flush()
					recved_size += len(response["data"]["data"])
		
		if not request["block"]:
			self._put_result(session_id)

		self._make_signal(session_id)

	thread = Thread(target=session)
	thread.start()
	signal = self._recv_signal(session_id)
	if signal["cancel"] and thread.is_alive():
		thread.kill()
		thread.join()
		self._respond_ok(session_id, cancel=True, last_one=True)
		# self._respond_ok(session_id, cancel=True, debug="Cancel.")
		self._put_result(session_id, cancelled=True)
	else:
		thread.join()