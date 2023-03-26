import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
import _NodeBasicMethods
import _NodeLocalPipesMethods
import _NodeLocalQueuesMethods
import _NodeLocalDictMethods
import _NodeGlobalQueuesMethods
import _NodeGlobalDictMethods
import _NodeFileTransferMethods
import _NodeRPCMethods

class Node:		                   
	## methods
	# basic
	__init__ = _NodeBasicMethods.__init__
	__del__ = _NodeBasicMethods.__del__
	close = _NodeBasicMethods.close
	hold_on = _NodeBasicMethods.hold_on
	_start = _NodeBasicMethods._start
	_get_session_id = _NodeBasicMethods._get_session_id
	_traceback = _NodeBasicMethods._traceback
	_process_close = _NodeBasicMethods._process_close
	_send = _NodeBasicMethods._send
	_send_signal = _NodeBasicMethods._send_signal
	_request = _NodeBasicMethods._request
	_respond_ok = _NodeBasicMethods._respond_ok
	_respond_exception = _NodeBasicMethods._respond_exception
	_put_result = _NodeBasicMethods._put_result
	_put_exception = _NodeBasicMethods._put_exception
	_make_signal = _NodeBasicMethods._make_signal
	_recv_signal = _NodeBasicMethods._recv_signal
	_recv_response = _NodeBasicMethods._recv_response
	_recving_loop = _NodeBasicMethods._recving_loop
	_decoding_loop = _NodeBasicMethods._decoding_loop
	_close_session = _NodeBasicMethods._close_session

	# local pipes
	send = _NodeLocalPipesMethods.send
	recv = _NodeLocalPipesMethods.recv
	_locals_pipe_send = _NodeLocalPipesMethods._locals_pipe_send
	_locals_pipe_recv = _NodeLocalPipesMethods._locals_pipe_recv
	_locals_pipes_len = _NodeLocalPipesMethods._locals_pipes_len
	_locals_pipes_contains = _NodeLocalPipesMethods._locals_pipes_contains
	_locals_pipes_keys = _NodeLocalPipesMethods._locals_pipes_keys
	_locals_pipes_iter = _NodeLocalPipesMethods._locals_pipes_iter
	_locals_pipes_delitem = _NodeLocalPipesMethods._locals_pipes_delitem
	_locals_pipes_clear = _NodeLocalPipesMethods._locals_pipes_clear
	_process_send = _NodeLocalPipesMethods._process_send
	_process_recv = _NodeLocalPipesMethods._process_recv
	_process__locals_pipe_send = _NodeLocalPipesMethods._process__locals_pipe_send
	_process__locals_pipe_recv = _NodeLocalPipesMethods._process__locals_pipe_recv
	_process__locals_pipes_len = _NodeLocalPipesMethods._process__locals_pipes_len
	_process__locals_pipes_contains = _NodeLocalPipesMethods._process__locals_pipes_contains
	_process__locals_pipes_keys = _NodeLocalPipesMethods._process__locals_pipes_keys
	_process__locals_pipes_iter = _NodeLocalPipesMethods._process__locals_pipes_iter
	_process__locals_pipes_delitem = _NodeLocalPipesMethods._process__locals_pipes_delitem
	_process__locals_pipes_clear = _NodeLocalPipesMethods._process__locals_pipes_clear

	# local queues
	put = _NodeLocalQueuesMethods.put
	get = _NodeLocalQueuesMethods.get
	qsize = _NodeLocalQueuesMethods.qsize
	_used_queues = _NodeLocalQueuesMethods._used_queues
	_locals_queue_put = _NodeLocalQueuesMethods._locals_queue_put
	_locals_queue_get = _NodeLocalQueuesMethods._locals_queue_get
	_locals_queue_len = _NodeLocalQueuesMethods._locals_queue_len
	_locals_queues_len = _NodeLocalQueuesMethods._locals_queues_len
	_locals_queues_contains = _NodeLocalQueuesMethods._locals_queues_contains
	_locals_queues_keys = _NodeLocalQueuesMethods._locals_queues_keys
	_locals_queues_iter = _NodeLocalQueuesMethods._locals_queues_iter
	_locals_queues_delitem = _NodeLocalQueuesMethods._locals_queues_delitem
	_locals_queues_clear = _NodeLocalQueuesMethods._locals_queues_clear
	_process_put = _NodeLocalQueuesMethods._process_put
	_process_get = _NodeLocalQueuesMethods._process_get
	_process_qsize = _NodeLocalQueuesMethods._process_qsize
	_process__locals_queue_put = _NodeLocalQueuesMethods._process__locals_queue_put
	_process__locals_queue_get = _NodeLocalQueuesMethods._process__locals_queue_get
	_process__locals_queue_len = _NodeLocalQueuesMethods._process__locals_queue_len
	_process__locals_queues_len = _NodeLocalQueuesMethods._process__locals_queues_len
	_process__locals_queues_contains = _NodeLocalQueuesMethods._process__locals_queues_contains
	_process__locals_queues_keys = _NodeLocalQueuesMethods._process__locals_queues_keys
	_process__locals_queues_iter = _NodeLocalQueuesMethods._process__locals_queues_iter
	_process__locals_queues_delitem = _NodeLocalQueuesMethods._process__locals_queues_delitem
	_process__locals_queues_clear = _NodeLocalQueuesMethods._process__locals_queues_clear

	# local shared dict
	__getitem__ = _NodeLocalDictMethods.__getitem__
	__setitem__ = _NodeLocalDictMethods.__setitem__
	__delitem__ = _NodeLocalDictMethods.__delitem__
	__iter__ = _NodeLocalDictMethods.__iter__
	__contains__ = _NodeLocalDictMethods.__contains__
	__len__ = _NodeLocalDictMethods.__len__
	clear = _NodeLocalDictMethods.clear
	keys = _NodeLocalDictMethods.keys
	values = _NodeLocalDictMethods.values
	items = _NodeLocalDictMethods.items
	pop = _NodeLocalDictMethods.pop
	_process___getitem__ = _NodeLocalDictMethods._process___getitem__
	_process___setitem__ = _NodeLocalDictMethods._process___setitem__
	_process___delitem__ = _NodeLocalDictMethods._process___delitem__
	_process___iter__ = _NodeLocalDictMethods._process___iter__
	_process___contains__ = _NodeLocalDictMethods._process___contains__
	_process___len__ = _NodeLocalDictMethods._process___len__
	_process_clear = _NodeLocalDictMethods._process_clear
	_process_keys = _NodeLocalDictMethods._process_keys
	_process_values = _NodeLocalDictMethods._process_values
	_process_items = _NodeLocalDictMethods._process_items
	_process_pop = _NodeLocalDictMethods._process_pop

	# global queues
	_server_get = _NodeGlobalQueuesMethods._server_get
	_server_put = _NodeGlobalQueuesMethods._server_put
	_server_qsize = _NodeGlobalQueuesMethods._server_qsize
	_server_queue_get = _NodeGlobalQueuesMethods._server_queue_get
	_server_queue_put = _NodeGlobalQueuesMethods._server_queue_put
	_server_queue_len = _NodeGlobalQueuesMethods._server_queue_len
	_server_queues_len = _NodeGlobalQueuesMethods._server_queues_len
	_server_queues_delitem = _NodeGlobalQueuesMethods._server_queues_delitem
	_server_queues_contains = _NodeGlobalQueuesMethods._server_queues_contains
	_server_queues_keys = _NodeGlobalQueuesMethods._server_queues_keys
	_server_queues_iter = _NodeGlobalQueuesMethods._server_queues_iter
	_server_queues_clear = _NodeGlobalQueuesMethods._server_queues_clear
	_process__server_get = _NodeGlobalQueuesMethods._process__server_get
	_process__server_put = _NodeGlobalQueuesMethods._process__server_put
	_process__server_qsize = _NodeGlobalQueuesMethods._process__server_qsize
	_process__server_queue_get = _NodeGlobalQueuesMethods._process__server_queue_get
	_process__server_queue_put = _NodeGlobalQueuesMethods._process__server_queue_put
	_process__server_queue_len = _NodeGlobalQueuesMethods._process__server_queue_len
	_process__server_queues_len = _NodeGlobalQueuesMethods._process__server_queues_len
	_process__server_queues_delitem = _NodeGlobalQueuesMethods._process__server_queues_delitem
	_process__server_queues_contains = _NodeGlobalQueuesMethods._process__server_queues_contains
	_process__server_queues_keys = _NodeGlobalQueuesMethods._process__server_queues_keys
	_process__server_queues_iter = _NodeGlobalQueuesMethods._process__server_queues_iter
	_process__server_queues_clear = _NodeGlobalQueuesMethods._process__server_queues_clear

	# global shared dict
	_server_getitem = _NodeGlobalDictMethods._server_getitem
	_server_setitem = _NodeGlobalDictMethods._server_setitem
	_server_delitem = _NodeGlobalDictMethods._server_delitem
	_server_pop = _NodeGlobalDictMethods._server_pop
	_server_iter = _NodeGlobalDictMethods._server_iter
	_server_contains = _NodeGlobalDictMethods._server_contains
	_server_len = _NodeGlobalDictMethods._server_len
	_server_keys = _NodeGlobalDictMethods._server_keys
	_server_values = _NodeGlobalDictMethods._server_values
	_server_items = _NodeGlobalDictMethods._server_items
	_server_clear = _NodeGlobalDictMethods._server_clear
	_process__server_getitem = _NodeGlobalDictMethods._process__server_getitem
	_process__server_setitem = _NodeGlobalDictMethods._process__server_setitem
	_process__server_delitem = _NodeGlobalDictMethods._process__server_delitem
	_process__server_clear = _NodeGlobalDictMethods._process__server_clear
	_process__server_keys = _NodeGlobalDictMethods._process__server_keys
	_process__server_values = _NodeGlobalDictMethods._process__server_values
	_process__server_items = _NodeGlobalDictMethods._process__server_items
	_process__server_iter = _NodeGlobalDictMethods._process__server_iter
	_process__server_contains = _NodeGlobalDictMethods._process__server_contains
	_process__server_len = _NodeGlobalDictMethods._process__server_len
	_process__server_pop = _NodeGlobalDictMethods._process__server_pop

	# file transfer
	get_file = _NodeFileTransferMethods.get_file
	_process_get_file = _NodeFileTransferMethods._process_get_file
	put_file = _NodeFileTransferMethods.put_file
	_process_put_file = _NodeFileTransferMethods._process_put_file
	get_folder = _NodeFileTransferMethods.get_folder
	_process_get_folder = _NodeFileTransferMethods._process_get_folder
	put_folder = _NodeFileTransferMethods.put_folder
	_process_put_folder = _NodeFileTransferMethods._process_put_folder
	_write_to_file = _NodeFileTransferMethods._write_to_file
	_process__write_to_file = _NodeFileTransferMethods._process__write_to_file
	_close_file = _NodeFileTransferMethods._close_file
	_process__close_file = _NodeFileTransferMethods._process__close_file
	
	# RPC
	eval = _NodeRPCMethods.eval
	exec = _NodeRPCMethods.exec
	execfile = _NodeRPCMethods.execfile
	exec_remote_file = _NodeRPCMethods.exec_remote_file
	system = _NodeRPCMethods.system
	call = _NodeRPCMethods.call
	call_remote = _NodeRPCMethods.call_remote
	_process_system = _NodeRPCMethods._process_system
	_process_eval = _NodeRPCMethods._process_eval
	_process_exec = _NodeRPCMethods._process_exec
	_process_exec_remote_file = _NodeRPCMethods._process_exec_remote_file
	_process_call = _NodeRPCMethods._process_call
	_process_call_remote = _NodeRPCMethods._process_call_remote

	@property
	def is_closed(self):
		try:
			return self._connection._closed
		except:
			return True

	@property
	def address(self):
		try:
			if self._parent is None:
				return self._connection.getsockname()
			else:
				return self._connection.getpeername()
		except:
			return None

	@property
	def server_address(self):
		try:
			if self._parent is None:
				return self._connection.getpeername()
			else:
				return self._parent.address
		except:
			return None

	@property
	def server(self):
		return self._server_peer

	@property
	def queues(self):
		return self._queues

	@property
	def pipes(self):
		return self._pipes