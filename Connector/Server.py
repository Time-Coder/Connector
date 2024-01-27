import socket
import threading
import os
from concurrent.futures import ThreadPoolExecutor

from .Node import Node
from .NodeInternalClasses import OrderedDict, QueueDict
from .CloseableQueue import CloseableQueue
from .utils import file_size, get_ip


class Server:
    def __init__(self, ip=None, port=None):
        self.connect_results = OrderedDict()
        self.disconnect_results = OrderedDict()
        self._callback_threads_pool = ThreadPoolExecutor(max_workers=5)

        self._on_connected = lambda client: None
        self._on_disconnected = lambda address: None

        self._connected_nodes = OrderedDict()
        self._global_vars = {}
        self._queue = CloseableQueue()
        self._queues = QueueDict()

        self._continue_accept = False
        self._accept_thread = None

        self.start(ip, port)

    def set_connect_callback(self, func):
        self._on_connected = func

    def set_disconnect_callback(self, func):
        self._on_disconnected = func

    def start(self, ip=None, port=None):
        if self._continue_accept:
            return

        self._connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if ip is None:
            ip = get_ip()
        if port is None:
            port = 0

        self._connection.bind((ip, port))
        self._connection.listen(5)

        self._continue_accept = True
        if self._accept_thread is None or not self._accept_thread.is_alive():
            self._accept_thread = threading.Thread(
                target=self._start, daemon=True
            )
            self._accept_thread.start()

    def close(self):
        self._continue_accept = False

        try:
            keys = self._connected_nodes.keys()
            for address in keys:
                try:
                    self._connected_nodes[address].close()
                except BaseException:
                    pass
        except BaseException:
            pass

        self._connected_nodes = OrderedDict()

        try:
            self._queues.clear()
        except BaseException:
            pass

        try:
            self._connection.close()
        except BaseException:
            pass

        self.connect_results = OrderedDict()
        self.disconnect_results = OrderedDict()
        self._callback_threads_pool.shutdown()
        self._callback_threads_pool = ThreadPoolExecutor(max_workers=5)

        self._global_vars = {}
        self._queues = QueueDict()

        if self._accept_thread is not None and self._accept_thread.is_alive():
            self._accept_thread.join()
        self._accept_thread = None

    @property
    def address(self):
        try:
            return self._connection.getsockname()
        except BaseException:
            return None

    @property
    def is_closed(self):
        return not self._continue_accept

    @property
    def clients(self):
        return self._connected_nodes

    @property
    def queues(self):
        return self._queues

    def __del__(self):
        try:
            self.close()
        except BaseException:
            pass

    def __getitem__(self, name):
        return self._global_vars[name]

    def __setitem__(self, name, value):
        self._global_vars[name] = value

    def __delitem__(self, name):
        del self._global_vars[name]

    def __iter__(self):
        return self._global_vars.__iter__()

    def __len__(self):
        return self._global_vars.__len__()

    def __contains__(self, name):
        return self._global_vars.__contains__(name)

    def keys(self):
        return self._global_vars.keys()

    def values(self):
        return self._global_vars.values()

    def items(self):
        return self._global_vars.items()

    def clear(self):
        self._global_vars.clear()

    def pop(self, name):
        return self._global_vars.pop(name)

    def get(self, timeout=None, block=True):
        return self._queue.get(timeout=timeout, block=block)

    def put(self, value, timeout=None, block=True):
        self._queue.put(value, timeout=timeout, block=block)

    def qsize(self):
        return self._queue.qsize()

    def put_file_to(self, src_filename, address_file_map):
        if not os.path.isfile(src_filename):
            raise FileNotFoundError("File " + src_filename + " is not exists.")

        block_size = 8192*1024
        sent_size = 0
        src_file_size = file_size(src_filename)
        with open(src_filename, "rb") as file:
            while sent_size < src_file_size:
                data = file.read(block_size)
                for address in address_file_map:
                    try:
                        client = self._connected_nodes[address]
                        client._write_to_file(data, address_file_map[address])
                    except BaseException:
                        pass
                sent_size += len(data)

        for address in address_file_map:
            try:
                client = self._connected_nodes[address]
                client.close_file()
            except BaseException:
                pass

    def put_folder_to(self, src_foldername, address_file_map):
        if not os.path.isdir(src_foldername):
            raise FileNotFoundError(f"Folder {src_foldername} is not exists.")

        i = len(src_foldername)-1
        while src_foldername[i] in ['/', '\\']:
            i -= 1

        block_size = 8192*1024
        for root, dirs, files in os.walk(src_foldername):
            for name in files:
                src_filename = os.path.join(root, name)

                sent_size = 0
                src_file_size = file_size(src_filename)
                with open(src_filename, "rb") as file:
                    while sent_size < src_file_size:
                        data = file.read(block_size)
                        for address in address_file_map:
                            try:
                                client = self._connected_nodes[address]
                                client._write_to_file(
                                    data, address_file_map[address]
                                )
                            except BaseException:
                                pass
                        sent_size += len(data)

        for address in address_file_map:
            try:
                client = self._connected_nodes[address]
                client._close_file()
            except BaseException:
                pass

    def hold_on(self):
        threading.Event().wait()

    def _start(self):
        while self._continue_accept:
            try:
                client_socket, address = self._connection.accept()
                node = Node(client_socket, self)
                node._start()
                self._connected_nodes[address] = node

                result = self._callback_threads_pool.submit(
                    self._on_connected, self._connected_nodes[address])
                self.connect_results[address] = result
                node._respond_ok(session_id=b'\x00'*16)
            except BaseException:
                break
