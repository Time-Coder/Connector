from .utils import eprint


def _server_get(self, timeout=None, block=True):
    session_id = self._get_session_id()
    self._request(session_id, timeout=timeout, block=block)
    response = self._recv_response(session_id)

    if response["success"]:
        return response["data"]["value"]
    else:
        eprint(response["traceback"])
        raise response["exception"]


def _process__server_get(self, session_id, request):
    try:
        value = self._parent.get(
            timeout=request["data"]["timeout"], block=request["block"]
        )
        self._respond_ok(session_id, value=value, last_one=True)
    except BaseException as e:
        self._respond_exception(session_id, e)


def _server_put(self, value, timeout=None, block=True):
    session_id = self._get_session_id()
    self._request(
        session_id, value=value,
        timeout=timeout, block=block, last_one=True
    )
    response = self._recv_response(session_id)

    if not response["success"]:
        eprint(response["traceback"])
        raise response["exception"]


def _process__server_put(self, session_id, request):
    try:
        data = request["data"]
        self._parent.put(
            data["value"], timeout=data["timeout"], block=request["block"]
        )
        self._respond_ok(session_id, last_one=True)
    except BaseException as e:
        self._respond_exception(session_id, e)


def _server_qsize(self, timeout=None, block=True):
    session_id = self._get_session_id()
    self._request(session_id)
    response = self._recv_response(session_id)

    if response["success"]:
        return response["data"]["qsize"]
    else:
        eprint(response["traceback"])
        raise response["exception"]


def _process__server_qsize(self, session_id, request):
    try:
        qsize = self._parent.qsize()
        self._respond_ok(session_id, qsize=qsize, last_one=True)
    except BaseException as e:
        self._respond_exception(session_id, e)


def _server_queue_get(self, name, timeout=None, block=True):
    session_id = self._get_session_id()
    self._request(session_id, name=name, timeout=timeout, block=block)
    response = self._recv_response(session_id)

    if response["success"]:
        return response["data"]["value"]
    else:
        eprint(response["traceback"])
        raise response["exception"]


def _process__server_queue_get(self, session_id, request):
    try:
        data = request["data"]
        value = self._parent.queues[data["name"]].get(
            timeout=data["timeout"], block=request["block"]
        )
        self._respond_ok(session_id, value=value, last_one=True)
    except BaseException as e:
        self._respond_exception(session_id, e)


def _server_queue_put(self, name, value, timeout=None, block=True):
    session_id = self._get_session_id()
    self._request(
        session_id, name=name, value=value,
        timeout=timeout, block=block
    )
    response = self._recv_response(session_id)

    if not response["success"]:
        eprint(response["traceback"])
        raise response["exception"]


def _process__server_queue_put(self, session_id, request):
    try:
        data = request["data"]
        self._parent.queues[data["name"]].put(
            data["value"], timeout=data["timeout"], block=request["block"]
        )
        self._respond_ok(session_id, last_one=True)
    except BaseException as e:
        self._respond_exception(session_id, e)


def _server_queue_len(self, name):
    session_id = self._get_session_id()
    self._request(session_id, name=name)
    response = self._recv_response(session_id)

    if response["success"]:
        return response["data"]["len"]
    else:
        eprint(response["traceback"])
        raise response["exception"]


def _process__server_queue_len(self, session_id, request):
    try:
        length = 0
        name = request["data"]["name"]
        if name in self._parent.queues:
            length = self._parent.queues[name].qsize()

        self._respond_ok(session_id, len=length, last_one=True)
    except BaseException as e:
        self._respond_exception(session_id, e)


def _server_queues_delitem(self, name):
    session_id = self._get_session_id()
    self._request(session_id, name=name)
    response = self._recv_response(session_id)

    if not response["success"]:
        eprint(response["traceback"])
        raise response["exception"]


def _process__server_queues_delitem(self, session_id, request):
    try:
        del self._parent.queues[request["data"]["name"]]
        self._respond_ok(session_id, last_one=True)
    except BaseException as e:
        self._respond_exception(session_id, e)


def _server_queues_len(self):
    session_id = self._get_session_id()
    self._request(session_id)
    response = self._recv_response(session_id)

    if response["success"]:
        return response["data"]["len"]
    else:
        eprint(response["traceback"])
        raise response["exception"]


def _process__server_queues_len(self, session_id, request):
    try:
        self._respond_ok(
            session_id, len=len(self._parent.queues), last_one=True
        )
    except BaseException as e:
        self._respond_exception(session_id, e)


def _server_queues_contains(self, name):
    session_id = self._get_session_id()
    self._request(session_id, name=name)
    response = self._recv_response(session_id)

    if response["success"]:
        return response["data"]["contains"]
    else:
        eprint(response["traceback"])
        raise response["exception"]


def _process__server_queues_contains(self, session_id, request):
    try:
        contains = (request["data"]["name"] in self._parent.queues)
        self._respond_ok(
            session_id, contains=contains, last_one=True
        )
    except BaseException as e:
        self._respond_exception(session_id, e)


def _server_queues_keys(self):
    session_id = self._get_session_id()
    self._request(session_id)
    response = self._recv_response(session_id)

    if response["success"]:
        return response["data"]["keys"]
    else:
        eprint(response["traceback"])
        raise response["exception"]


def _process__server_queues_keys(self, session_id, request):
    try:
        self._respond_ok(
            session_id, keys=self._parent.queues.keys(), last_one=True
        )
    except BaseException as e:
        self._respond_exception(session_id, e)


def _server_queues_iter(self):
    session_id = self._get_session_id()
    self._request(session_id)
    response = self._recv_response(session_id)

    if response["success"]:
        return response["data"]["iter"]
    else:
        eprint(response["traceback"])
        raise response["exception"]


def _process__server_queues_iter(self, session_id, request):
    try:
        self._respond_ok(
            session_id, iter=iter(self._parent.queues), last_one=True
        )
    except BaseException as e:
        self._respond_exception(session_id, e)


def _server_queues_clear(self):
    session_id = self._get_session_id()
    self._request(session_id)
    response = self._recv_response(session_id)

    if not response["success"]:
        eprint(response["traceback"])
        raise response["exception"]


def _process__server_queues_clear(self, session_id, request):
    try:
        self._parent.queues.clear()
        self._respond_ok(session_id, last_one=True)
    except BaseException as e:
        self._respond_exception(session_id, e)


def init_global_queues_methods(cls):
    cls._server_get = _server_get
    cls._server_put = _server_put
    cls._server_qsize = _server_qsize
    cls._server_queue_get = _server_queue_get
    cls._server_queue_put = _server_queue_put
    cls._server_queue_len = _server_queue_len
    cls._server_queues_len = _server_queues_len
    cls._server_queues_delitem = _server_queues_delitem
    cls._server_queues_contains = _server_queues_contains
    cls._server_queues_keys = _server_queues_keys
    cls._server_queues_iter = _server_queues_iter
    cls._server_queues_clear = _server_queues_clear
    cls._process__server_get = _process__server_get
    cls._process__server_put = _process__server_put
    cls._process__server_qsize = _process__server_qsize
    cls._process__server_queue_get = _process__server_queue_get
    cls._process__server_queue_put = _process__server_queue_put
    cls._process__server_queue_len = _process__server_queue_len
    cls._process__server_queues_len = _process__server_queues_len
    cls._process__server_queues_delitem = _process__server_queues_delitem
    cls._process__server_queues_contains = _process__server_queues_contains
    cls._process__server_queues_keys = _process__server_queues_keys
    cls._process__server_queues_iter = _process__server_queues_iter
    cls._process__server_queues_clear = _process__server_queues_clear

    return cls
