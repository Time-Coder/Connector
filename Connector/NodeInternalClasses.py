import threading
import time
import ctypes
import collections

from .CloseableQueue import CloseableQueue
from .CloseablePipe import CloseablePipe
from .utils import eprint


class OrderedDict(collections.OrderedDict):

    def __init__(self, **kwargs):
        collections.OrderedDict.__init__(self, **kwargs)

    def __setitem__(self, name, value):
        if isinstance(name, int):
            name = list(self.keys())[name]

        collections.OrderedDict.__setitem__(self, name, value)

    def __getitem__(self, name):
        if isinstance(name, int):
            name = list(self.keys())[name]

        return collections.OrderedDict.__getitem__(self, name)

    def __delitem__(self, name):
        if isinstance(name, int):
            name = list(self.keys())[name]

        collections.OrderedDict.__delitem__(self, name)


class QueueDict(dict):

    def __init__(self):
        dict.__init__(self)

    def __getitem__(self, name):
        if not dict.__contains__(self, name):
            new_queue = CloseableQueue()
            dict.__setitem__(self, name, new_queue)
        return dict.__getitem__(self, name)

    def __delitem__(self, name):
        if dict.__contains__(self, name):
            try:
                self[name].close()
            except BaseException:
                pass
            dict.__delitem__(self, name)

    def clear(self):
        for name in self:
            try:
                self[name].close()
            except BaseException:
                pass
        dict.clear(self)


class PipeDict(dict):

    def __init__(self):
        dict.__init__(self)

    def __getitem__(self, name):
        if not dict.__contains__(self, name):
            dict.__setitem__(self, name, CloseablePipe())
        return dict.__getitem__(self, name)

    def __delitem__(self, name):
        if dict.__contains__(self, name):
            try:
                self[name][0].close()
            except BaseException:
                pass

            try:
                self[name][1].close()
            except BaseException:
                pass

            dict.__delitem__(self, name)

    def clear(self):
        for name in self:
            try:
                self[name][0].close()
            except BaseException:
                pass

            try:
                self[name][1].close()
            except BaseException:
                pass

        dict.clear(self)


class Pipe:

    def __init__(self, node, name):
        self._node = node
        self._name = name

    def send(self, value):
        self._node._locals_pipe_send(self._name, value)

    def recv(self):
        return self._node._locals_pipe_recv(self._name)


class Pipes:

    def __init__(self, node):
        self._node = node

    def __getitem__(self, name):
        return Pipe(self._node, name)

    def __delitem__(self, name):
        self._node._locals_pipes_delitem(name)

    def __len__(self):
        return self._node._locals_pipes_len()

    def __contains__(self, name):
        return self._node._locals_pipes_contains(name)

    def __iter__(self):
        return self._node._locals_pipes_iter()

    def keys(self):
        return self._node._locals_pipes_keys()

    def values(self):
        values = []
        for key in self.keys():
            values.append(self[key])

        return values

    def items(self):
        items = []
        for key in self.keys():
            items.append((key, self[key]))

        return items

    def clear(self):
        self._node._locals_pipes_clear()


class Queue:

    def __init__(self, node, name, private=False):
        self._node = node
        self._name = name
        self._is_private = private

    def get(self, timeout=None, block=True):
        return self._node._locals_queue_get(
            self._name, timeout=timeout,
            block=block, is_private=self._is_private
        )

    def put(self, value, timeout=None, block=True):
        self._node._locals_queue_put(
            self._name, value,
            timeout=timeout, block=block,
            is_private=self._is_private
        )

    def qsize(self):
        return self._node._locals_queue_len(
            self._name, is_private=self._is_private
        )

    def __len__(self):
        return self._node._locals_queue_len(
            self._name, is_private=self._is_private
        )


class Queues:

    def __init__(self, node, private=False):
        self._node = node
        self._is_private = private

    def __getitem__(self, name):
        return Queue(self._node, name, private=self._is_private)

    def __delitem__(self, name):
        self._node._locals_queues_delitem(name, is_private=self._is_private)

    def __len__(self):
        return self._node._locals_queues_len(is_private=self._is_private)

    def __contains__(self, name):
        return self._node._locals_queues_contains(
            name, is_private=self._is_private
        )

    def keys(self):
        return self._node._locals_queues_keys(is_private=self._is_private)

    def values(self):
        values = []
        for key in self.keys():
            values.append(self[key])

        return values

    def items(self):
        items = []
        for key in self.keys():
            items.append((key, self[key]))
        return items

    def __iter__(self):
        return self._node._locals_queues_iter(is_private=self._is_private)

    def clear(self):
        self._node._locals_queues_clear(is_private=self._is_private)


class ServerPeer:

    class Queue:
        def __init__(self, node, name):
            self._node = node
            self._name = name

        def get(self, timeout=None, block=True):
            return self._node._server_queue_get(
                self._name, timeout=timeout, block=block
            )

        def put(self, value, timeout=None, block=True):
            self._node._server_queue_put(
                self._name, value, timeout=timeout, block=block
            )

        def qsize(self):
            return self._node._server_queue_len(self._name)

        def __len__(self):
            return self._node._server_queue_len(self._name)

    class Queues:
        def __init__(self, node):
            self._node = node

        def __getitem__(self, name):
            return ServerPeer.Queue(self._node, name)

        def __delitem__(self, name):
            self._node._server_queues_delitem(name)

        def __len__(self):
            return self._node._server_queues_len()

        def __contains__(self, name):
            return self._node._server_queues_contains(name)

        def keys(self):
            return self._node._server_queues_keys()

        def values(self):
            values = []
            for key in self.keys():
                values.append(self[key])
            return values

        def items(self):
            items = []
            for key in self.keys():
                items.append((key, self[key]))
            return items

        def __iter__(self):
            return self._node._server_queues_iter()

        def clear(self):
            self._node._server_queues_clear()

    def __init__(self, node):
        self._node = node
        self._queues = ServerPeer.Queues(node)

    def __setitem__(self, name, value):
        self._node._server_setitem(name, value)

    def __getitem__(self, name):
        return self._node._server_getitem(name)

    def __delitem__(self, name):
        return self._node._server_delitem(name)

    def __iter__(self):
        return self._node._server_iter()

    def __contains__(self, name):
        return self._node._server_contains(name)

    def __len__(self):
        return self._node._server_len()

    def clear(self):
        self._node._server_clear()

    def keys(self):
        return self._node._server_keys()

    def values(self):
        return self._node._server_values()

    def items(self):
        return self._node._server_items()

    def pop(self, name):
        return self._node._server_pop(name)

    def get(self, timeout=None, block=True):
        return self._node._server_get(timeout=timeout, block=block)

    def put(self, value, timeout=None, block=True):
        self._node._server_put(value, timeout=timeout, block=block)

    def qsize(self):
        return self._node._server_qsize()

    @property
    def queues(self):
        return self._queues

    @property
    def address(self):
        try:
            return self._node._connection.getpeername()
        except BaseException:
            return None


class AutoSendBuffer:

    def __init__(self, node, session_id, timeout=0.1, quiet=False):
        self._node = node
        self._session_id = session_id
        self._buffer_lock = threading.Lock()
        self._buffer = b''
        self._quiet = quiet
        self._timeout = timeout
        self._last_send_time = time.time()
        self._continue_send = True
        self._sending_thread = threading.Thread(target=self._timeout_send)
        self._sending_thread.start()

    def __del__(self):
        try:
            self.stop()
        except BaseException:
            pass

    def append(self, byte):
        with self._buffer_lock:
            self._buffer += byte

        if byte == b"\n" or len(self._buffer) >= 512:
            self.send()

    def send(self):
        with self._buffer_lock:
            if len(self._buffer) != 0:
                content = self._buffer.decode("utf-8")
                if not self._quiet:
                    print(content, end="", flush=True)
                self._node._respond_ok(
                    self._session_id, end=False, stdout=content
                )
                self._buffer = b''
                self._last_send_time = time.time()

    def stop(self):
        self._continue_send = False
        self._sending_thread.join()
        self.send()

    def _timeout_send(self):
        while self._continue_send:
            if time.time()-self._last_send_time >= self._timeout:
                self.send()
            time.sleep(1E-3)


class Thread(threading.Thread):

    def __init__(self, target, args=(), kwargs={}):
        threading.Thread.__init__(
            self, target=target,
            args=args, kwargs=kwargs
        )

    def __get_id(self):
        if hasattr(self, '_thread_id'):
            return self._thread_id

        for id, thread in threading._active.items():
            if thread is self:
                return id

    def kill(self):
        thread_id = self.__get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
            thread_id, ctypes.py_object(SystemExit)
        )
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            print('Exception raise failure')


class Future:

    def __init__(self, node, session_id):
        self._node = node
        self._session_id = session_id
        self._cancelled = False
        self._done = None
        self._result = None
        self._monitor_done_thread = None
        self._done_callbacks = []

    def cancel(self):
        if self.done():
            return False

        self._node._stop_send = True
        self._node._send_signal(self._session_id, cancel=True)
        result_queues = self._node._result_queues_for_future
        self._result = result_queues[self._session_id].get()
        self._node._close_session(self._session_id)
        self._cancelled = True
        self._done = True
        return True

    def cancelled(self):
        return self._cancelled

    def done(self):
        if self._done is not None:
            return self._done
        else:
            result_queues = self._node._result_queues_for_future
            return (len(result_queues[self._session_id]) > 0)

    def result(self):
        if self._result is None:
            result_queues = self._node._result_queues_for_future
            self._result = result_queues[self._session_id].get()
            self._node._close_session(self._session_id)

        self._done = True
        if self._result["success"]:
            return self._result["return_value"]
        else:
            eprint(self._result["traceback"])
            raise self._result["exception"]

    def exception(self):
        if self._result is None:
            result_queues = self._node._result_queues_for_future
            self._result = result_queues[self._session_id].get()
            self._node._close_session(self._session_id)

        self._done = True
        return self._result["exception"]

    def _get_result(self):
        if self._result is None:
            result_queues = self._node._result_queues_for_future
            self._result = result_queues[self._session_id].get()
            self._node._close_session(self._session_id)

        for func in self._done_callbacks:
            func(self)

    def add_done_callback(self, func):
        self._done_callbacks.append(func)

        if self._monitor_done_thread is None:
            self._monitor_done_thread = threading.Thread(
                target=self._get_result
            )
            self._monitor_done_thread.start()

    def remove_done_callback(self, func):
        try:
            self._done_callbacks.remove(func)
        except BaseException:
            pass
