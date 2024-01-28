import socket
import threading
import os
from concurrent.futures import ThreadPoolExecutor

from .Node import Node
from .NodeInternalClasses import OrderedDict
from .utils import file_size, get_ip


class Peer(Node):
    def __init__(self, ip=None, port=None):
        self.connect_results = OrderedDict()
        self.disconnect_results = OrderedDict()
        self._callback_threads_pool = ThreadPoolExecutor(max_workers=5)

        self._on_connected = lambda client: None
        self._on_disconnect = lambda address: None

        self._connected_nodes = OrderedDict()

        self._continue_accept = False
        self._accept_thread = None

        if ip is None:
            ip = get_ip()
        if port is None:
            port = 0

        self._ip = ip
        self._port = port

        self._connection1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._connection1.bind((ip, 0))
        Node.__init__(self, self._connection1)

        self.start()

    @property
    def address(self):
        try:
            return self._connection2.getsockname()
        except BaseException:
            return None

    def set_connected_callback(self, func):
        self._on_connected = func

    def set_disconnected_callback(self, func):
        self._on_disconnected = func

    def connect(self, ip, port=None):
        server_address = ip
        if port is not None:
            server_address = (ip, port)

        if self._connection1 is None:
            self._connection1 = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM
            )
            self._connection1.bind((self._ip, 0))

        self._connection1.connect(server_address)
        Node._start(self)

    def start(self, ip=None, port=None):
        if self._continue_accept:
            return

        if ip is None:
            ip = self._ip
        if port is None:
            port = self._port

        if ip is None:
            ip = get_ip()
        if port is None:
            port = 0

        self._ip = ip
        self._port = port

        self._connection2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._connection2.bind((self._ip, self._port))
        self._connection2.listen(5)

        self._continue_accept = True
        if self._accept_thread is None or not self._accept_thread.is_alive():
            self._accept_thread = threading.Thread(
                target=self._accepting_loop, daemon=True
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

        self.connect_results = OrderedDict()
        self.disconnect_results = OrderedDict()
        self._callback_threads_pool.shutdown()
        self._callback_threads_pool = ThreadPoolExecutor(max_workers=5)

        if self._accept_thread is not None and self._accept_thread.is_alive():
            self._accept_thread.join()
        self._accept_thread = None

        try:
            Node.close(self)
        except BaseException:
            pass

        try:
            self._connection2.close()
        except BaseException:
            pass

    @property
    def clients(self):
        return self._connected_nodes

    def __del__(self):
        try:
            self.close()
        except BaseException:
            pass

    def put_file_to(self, src_file_name, address_file_map):
        if not os.path.isfile(src_file_name):
            raise FileNotFoundError(f"File {src_file_name} is not exists.")

        sent_size = 0
        src_file_size = file_size(src_file_name)
        with open(src_file_name, "rb") as file:
            while sent_size < src_file_size:
                data = file.read(self.send_buffer)
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

    def put_folder_to(self, src_folder_name, address_file_map):
        if not os.path.isdir(src_folder_name):
            raise FileNotFoundError(f"Folder {src_folder_name} is not exists.")

        i = len(src_folder_name)-1
        while src_folder_name[i] in ['/', '\\']:
            i -= 1

        for root, dirs, files in os.walk(src_folder_name):
            for name in files:
                src_file_name = os.path.join(root, name)

                sent_size = 0
                src_file_size = file_size(src_file_name)
                with open(src_file_name, "rb") as file:
                    while sent_size < src_file_size:
                        data = file.read(self.send_buffer)
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

    def _accepting_loop(self):
        while self._continue_accept:
            try:
                client_socket, address = self._connection2.accept()
                node = Node(client_socket, self)
                node._start()
                self._connected_nodes[address] = node

                result = self._callback_threads_pool.submit(
                    self._on_connected, self._connected_nodes[address])
                self.connect_results[address] = result
            except BaseException:
                break
