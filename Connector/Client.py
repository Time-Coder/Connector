import socket

from .Node import Node
from .utils import get_ip


class Client(Node):

    def __init__(self, ip=None, port=None):
        if ip is None:
            ip = get_ip()
        if port is None:
            port = 0

        self._ip = ip
        self._port = port

        self._connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._connection.bind((ip, port))
        Node.__init__(self, self._connection)

    def connect(self, ip, port=None):
        if port is None:
            port = ip[1]
            ip = ip[0]

        server_address = self.server_address
        try:
            if server_address[0] == ip and \
               server_address[1] == port and \
               not self.is_closed:
                return
        except BaseException:
            pass

        if server_address is not None and not self.is_closed:
            self.close()

        if self._connection is None:
            self._connection = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM
            )
            self._connection.bind((self._ip, self._port))

        self._connection.connect((ip, port))
        Node.__init__(self, self._connection)
        self._start()
        self._recv_response(session_id=b'\x00'*16)
