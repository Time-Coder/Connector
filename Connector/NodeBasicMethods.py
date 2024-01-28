import threading
import dill
import sys
import traceback
import uuid
import socket
from concurrent.futures import ThreadPoolExecutor

from .CloseableQueue import CloseableQueue
from .CloseablePipe import CloseablePipe
from .NodeInternalClasses import Pipes, Queues, PipeDict, QueueDict, ServerPeer

complex_request = ["get_file", "put_file",
                   "get_folder", "put_folder",
                   "eval", "exec", "system",
                   "call", "call_remote",
                   "execfile", "exec_remote_file"]


def __init__(self, connection, server=None):
    self._connection = connection
    if hasattr(self, "_send_buffer"):
        self._connection.setsockopt(
            socket.SOL_SOCKET, socket.SO_SNDBUF, self._send_buffer
        )
    else:
        self._send_buffer = self._connection.getsockopt(
            socket.SOL_SOCKET, socket.SO_SNDBUF
        )

    if hasattr(self, "_recv_buffer"):
        self._connection.setsockopt(
            socket.SOL_SOCKET, socket.SO_RCVBUF, self._recv_buffer
        )
    else:
        self._recv_buffer = self._connection.getsockopt(
            socket.SOL_SOCKET, socket.SO_RCVBUF
        )

    self._parent = server
    self._pipes = Pipes(self)
    self._queues = Queues(self)
    self._result_queues_for_future = Queues(self, private=True)
    self._recved_binary_queue = CloseableQueue()

    if self._parent is None:
        self._local_vars = {}
        self._pipe = CloseablePipe()
        self._queue = CloseableQueue()
        self._actual_pipes = PipeDict()
        self._actual_queues = QueueDict()
        self._actual_result_queues_for_future = QueueDict()
        self._server_peer = ServerPeer(self)
    else:
        self._server_peer = self._parent

    self._recving_thread = None
    self._decoding_thread = None

    self._recved_responses = QueueDict()
    self._recved_signals = QueueDict()

    self._out_file = None

    self._simple_threads_pool = None
    self._complex_threads_pool = None


def _start(self):
    if self._simple_threads_pool is None:
        self._simple_threads_pool = ThreadPoolExecutor(max_workers=5)

    if self._complex_threads_pool is None:
        self._complex_threads_pool = ThreadPoolExecutor(max_workers=1)

    if self._recving_thread is None or \
       not self._recving_thread.is_alive():
        self._recving_thread = threading.Thread(
            target=self._recving_loop, daemon=True
        )
        self._recving_thread.start()

    if self._decoding_thread is None or \
       not self._decoding_thread.is_alive():
        self._decoding_thread = threading.Thread(
            target=self._decoding_loop, daemon=True
        )
        self._decoding_thread.start()


def __del__(self):
    try:
        self.close()
    except BaseException:
        pass


def hold_on(self):
    threading.Event().wait()


def close(self):
    if self._parent is None:
        try:
            self._request(session_id=self._get_session_id())
        except BaseException:
            pass

        try:
            self._connection.close()
        except BaseException:
            pass

        self._connection = None

        try:
            self._queue.close()
        except BaseException:
            pass

        try:
            self._recved_binary_queue.close()
        except BaseException:
            pass

        try:
            self._pipe[0].close()
        except BaseException:
            pass

        try:
            self._pipe[1].close()
        except BaseException:
            pass

        try:
            self._actual_queues.clear()
        except BaseException:
            pass

        try:
            self._actual_result_queues_for_future.clear()
        except BaseException:
            pass

        try:
            self._actual_pipes.clear()
        except BaseException:
            pass

    else:
        try:
            self._connection.close()
        except BaseException:
            pass

        self._connection = None

        try:
            if self.address is not None:
                result = self._parent._callback_threads_pool.submit(
                    self._parent._on_disconnected, self.address)
                self._parent.disconnect_result[self.address] = result
        except BaseException:
            pass

        try:
            self._parent._connected_nodes.pop(self.address)
        except BaseException:
            pass

    if self._simple_threads_pool is not None:
        try:
            self._simple_threads_pool.shutdown()
        except BaseException:
            pass
        self._simple_threads_pool = None

    if self._complex_threads_pool is not None:
        try:
            self._complex_threads_pool.shutdown()
        except BaseException:
            pass
        self._complex_threads_pool = None

    try:
        self._recved_signals.clear()
    except BaseException:
        pass

    try:
        self._recved_responses.clear()
    except BaseException:
        pass


def _get_session_id(self):
    return uuid.uuid4().bytes


def _close_session(self, session_id):
    if session_id in self._recved_signals:
        del self._recved_signals[session_id]

    if session_id in self._recved_responses:
        del self._recved_responses[session_id]

    if self._parent is None:
        del self._actual_result_queues_for_future[session_id]


def _traceback(self, remote=True):
    exception_list = traceback.format_stack()
    exception_list = exception_list[:-2]
    exception_list.extend(traceback.format_tb(sys.exc_info()[2]))
    exception_list.extend(
        traceback.format_exception_only(
            sys.exc_info()[0], sys.exc_info()[1]
        )
    )

    exception_str = "Traceback (most recent call last):\n"
    if remote:
        exception_str = f"Remote {self.server_address} {exception_str}"

    exception_str += "".join(exception_list)

    return exception_str


def _process_close(self, request):
    self.close()


def _send(self, session_id, type, value):
    binary = dill.dumps(value, 3)
    type_bytes = type.to_bytes(1, byteorder='little', signed=False)
    length_bytes = len(binary).to_bytes(4, byteorder='little', signed=False)
    self._connection.sendall(session_id + type_bytes + length_bytes + binary)


def _send_signal(self, session_id, **kwargs):
    cancel = False
    if "cancel" in kwargs:
        cancel = kwargs.pop("cancel")

    signal = {
        "cancel": cancel,
        "data": kwargs
    }
    self._send(session_id, 2, signal)  # signal


def _request(self, session_id, **kwargs):
    block = True
    if "block" in kwargs:
        block = kwargs.pop("block")

    if "debug" in kwargs:
        print("request:", kwargs["debug"], flush=True)

    func = sys._getframe().f_back.f_code.co_name
    if "func" in kwargs:
        func = kwargs.pop("func")

    request = {
        "func": func,
        "block": block,
        "data": kwargs
    }
    self._send(session_id, 0, request)


def _respond_ok(self, session_id, **kwargs):
    block = True
    if "block" in kwargs:
        block = kwargs.pop("block")

    cancel = False
    if "cancel" in kwargs:
        cancel = kwargs.pop("cancel")

    last_one = False
    if "last_one" in kwargs:
        last_one = kwargs.pop("last_one")

    if "debug" in kwargs:
        print("respond:", kwargs["debug"], flush=True)

    if block:
        response = {
            "success": (not cancel),
            "cancel": cancel,
            "last_one": last_one,
            "data": kwargs
        }
        self._send(session_id, 1, response)
        if last_one:
            self._close_session(session_id)
    else:
        self._put_result(session_id, **kwargs)


def _respond_exception(self, session_id, exception, **kwargs):
    block = True
    if "block" in kwargs:
        block = kwargs.pop("block")

    if "debug" in kwargs:
        print("respond exception:", kwargs["debug"], flush=True)

    if block:
        response = {
            "success": False,
            "exception": exception,
            "traceback": self._traceback(),
            "last_one": True,
            "data": kwargs
        }
        self._send(session_id, 1, response)
        self._close_session(session_id)
    else:
        self._put_exception(session_id, exception, **kwargs)


def _put_result(self, session_id, **kwargs):
    result = {
        "success": True,
        "return_value": None,
        "exception": None,
        "traceback": None,
        "cancelled": False
    }
    for key in result:
        if key in kwargs:
            result[key] = kwargs.pop(key)
    result["data"] = kwargs

    self._result_queues_for_future[session_id].put(result)


def _put_exception(self, session_id, exception, **kwargs):
    result = {
        "success": False,
        "return_value": None,
        "exception": exception,
        "traceback": self._traceback(),
        "cancelled": False
    }
    for key in result:
        if key in kwargs:
            result[key] = kwargs.pop(key)
    result["data"] = kwargs

    self._result_queues_for_future[session_id].put(result)


def _make_signal(self, session_id, **kwargs):
    cancel = False
    if "cancel" in kwargs:
        cancel = kwargs.pop("cancel")

    signal = {
        "cancel": cancel,
        "data": kwargs
    }
    self._recved_signals[session_id].put(signal)


def _recv_signal(self, session_id):
    signal = self._recved_signals[session_id].get()

    if "debug" in signal["data"]:
        print("recved signal:", signal["data"]["debug"])

    return signal


def _recv_response(self, session_id):
    response = self._recved_responses[session_id].get()

    if "debug" in response["data"]:
        print("recved response:", response["data"]["debug"])

    if response["last_one"]:
        self._close_session(session_id)

    return response


def _recving_loop(self):
    while True:
        try:
            recved_binary = self._connection.recv(self.recv_buffer)
            self._recved_binary_queue.put(recved_binary)
        except BaseException:
            self.close()
            return


def _decoding_loop(self):
    buffer = b''
    while True:
        while len(buffer) < 21:
            try:
                buffer += self._recved_binary_queue.get()
            except BaseException:
                return
        session_id = buffer[:16]
        message_type = buffer[16]
        var_length = int.from_bytes(
            buffer[17:21], byteorder="little", signed=False
        )
        stop = 21 + var_length
        while len(buffer) < stop:
            try:
                buffer += self._recved_binary_queue.get()
            except BaseException:
                return

        var_bytes = buffer[21:stop]
        buffer = buffer[stop:]
        var = dill.loads(var_bytes)
        if message_type == 0:  # request
            try:
                print(var["data"]["debug"])
            except BaseException:
                pass

            var_func = var["func"]
            process_func = getattr(self, "_process_" + var_func)
            if var_func in complex_request:
                self._complex_threads_pool.submit(
                    process_func, session_id, var
                )
            else:
                if var_func in ["_write_to_file", "_close_file"]:
                    process_func(session_id, var)
                else:
                    self._simple_threads_pool.submit(
                        process_func, session_id, var
                    )
        elif message_type == 1:  # response
            self._recved_responses[session_id].put(var)
        elif message_type == 2:  # signal
            self._recved_signals[session_id].put(var)


def init_basic_methods(cls):
    cls.__init__ = __init__
    cls.__del__ = __del__
    cls.close = close
    cls.hold_on = hold_on
    cls._start = _start
    cls._get_session_id = _get_session_id
    cls._traceback = _traceback
    cls._process_close = _process_close
    cls._send = _send
    cls._send_signal = _send_signal
    cls._request = _request
    cls._respond_ok = _respond_ok
    cls._respond_exception = _respond_exception
    cls._put_result = _put_result
    cls._put_exception = _put_exception
    cls._make_signal = _make_signal
    cls._recv_signal = _recv_signal
    cls._recv_response = _recv_response
    cls._recving_loop = _recving_loop
    cls._decoding_loop = _decoding_loop
    cls._close_session = _close_session
    return cls
