from .utils import eprint


def put(self, value, timeout=None, block=True):
    if self._parent is None:
        self._queue.put(value)
    else:
        session_id = self._get_session_id()
        self._request(session_id, value=value, timeout=timeout, block=block)
        response = self._recv_response(session_id)
        if not response["success"]:
            eprint(response["traceback"])
            raise response["exception"]


def _process_put(self, session_id, request):
    try:
        data = request["data"]
        self._queue.put(
            data["value"], timeout=data["timeout"], block=request["block"]
        )
        self._respond_ok(session_id, last_one=True)
    except BaseException as e:
        self._respond_exception(session_id, e)


def get(self, timeout=None, block=True):
    if self._parent is None:
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


def _process_get(self, session_id, request):
    try:
        value = self._queue.get(
            timeout=request["data"]["timeout"], block=request["block"]
        )
        self._respond_ok(session_id, value=value, last_one=True)
    except BaseException as e:
        self._respond_exception(session_id, e)


def qsize(self):
    if self._parent is None:
        return self._queue.qsize()
    else:
        session_id = self._get_session_id()
        self._request(session_id)
        response = self._recv_response(session_id)
        if response["success"]:
            return response["data"]["qsize"]
        else:
            eprint(response["traceback"])
            raise response["exception"]


def _process_qsize(self, session_id, request):
    try:
        qsize = self._queue.qsize()
        self._respond_ok(session_id, qsize=qsize, last_one=True)
    except BaseException as e:
        self._respond_exception(session_id, e)


def _used_queues(self, is_private):
    if not is_private:
        return self._actual_queues
    else:
        return self._actual_result_queues_for_future


def _locals_queue_put(self, name, value, timeout, block, is_private):
    if self._parent is None:
        used_queue = self._used_queues(is_private)[name]
        used_queue.put(value, timeout=timeout, block=block)
    else:
        session_id = self._get_session_id()
        self._request(
            session_id, name=name, value=value, timeout=timeout,
            block=block, is_private=is_private
        )
        response = self._recv_response(session_id)
        if not response["success"]:
            eprint(response["traceback"])
            raise response["exception"]


def _process__locals_queue_put(self, session_id, request):
    try:
        data = request["data"]
        used_queue = self._used_queues(data["is_private"])[data["name"]]
        used_queue.put(
            data["value"], timeout=data["timeout"], block=request["block"]
        )
        self._respond_ok(session_id, last_one=True)
    except BaseException as e:
        self._respond_exception(session_id, e)


def _locals_queue_get(self, name, timeout, block, is_private):
    if self._parent is None:
        used_queue = self._used_queues(is_private)[name]
        return used_queue.get(timeout=timeout, block=block)
    else:
        session_id = self._get_session_id()
        self._request(
            session_id, name=name, timeout=timeout,
            block=block, is_private=is_private
        )
        response = self._recv_response(session_id)
        if response["success"]:
            return response["data"]["value"]
        else:
            eprint(response["traceback"])
            raise response["exception"]


def _process__locals_queue_get(self, session_id, request):
    try:
        data = request["data"]
        used_queue = self._used_queues(data["is_private"])[data["name"]]
        value = used_queue.get(timeout=data["timeout"], block=request["block"])
        self._respond_ok(session_id, value=value, last_one=True)
    except BaseException as e:
        self._respond_exception(session_id, e)


def _locals_queue_len(self, name, is_private):
    if self._parent is None:
        used_queues = self._used_queues(is_private)
        if name not in used_queues:
            return 0
        else:
            return used_queues[name].qsize()
    else:
        session_id = self._get_session_id()
        self._request(session_id, name=name, is_private=is_private)
        response = self._recv_response(session_id)
        if response["success"]:
            return response["data"]["len"]
        else:
            eprint(response["traceback"])
            raise response["exception"]


def _process__locals_queue_len(self, session_id, request):
    try:
        data = request["data"]
        name = data["name"]
        used_queues = self._used_queues(data["is_private"])
        queue_len = 0
        if name in used_queues:
            queue_len = used_queues[name].qsize()
        self._respond_ok(session_id, len=queue_len, last_one=True)
    except BaseException as e:
        self._respond_exception(session_id, e)


def _locals_queues_delitem(self, name, is_private):
    if self._parent is None:
        del self._used_queues(is_private)[name]
    else:
        session_id = self._get_session_id()
        self._request(session_id, name=name, is_private=is_private)
        response = self._recv_response(session_id)
        if not response["success"]:
            eprint(response["traceback"])
            raise response["exception"]


def _process__locals_queues_delitem(self, session_id, request):
    try:
        data = request["data"]
        del self._used_queues(data["is_private"])[data["name"]]
        self._respond_ok(session_id, last_one=True)
    except BaseException as e:
        self._respond_exception(session_id, e)


def _locals_queues_len(self, is_private):
    if self._parent is None:
        return len(self._used_queues(is_private))
    else:
        session_id = self._get_session_id()
        self._request(session_id, is_private=is_private)
        response = self._recv_response(session_id)
        if response["success"]:
            return response["data"]["len"]
        else:
            eprint(response["traceback"])
            raise response["exception"]


def _process__locals_queues_len(self, session_id, request):
    try:
        queues_len = len(self._used_queues(request["data"]["is_private"]))
        self._respond_ok(session_id, len=queues_len, last_one=True)
    except BaseException as e:
        self._respond_exception(session_id, e)


def _locals_queues_contains(self, name, is_private):
    if self._parent is None:
        return (name in self._used_queues(is_private))
    else:
        session_id = self._get_session_id()
        self._request(session_id, name=name, is_private=is_private)
        response = self._recv_response(session_id)
        if response["success"]:
            return response["data"]["contains"]
        else:
            eprint(response["traceback"])
            raise response["exception"]


def _process__locals_queues_contains(self, session_id, request):
    try:
        data = request["data"]
        used_queues = self._used_queues(data["is_private"])
        queues_conntains = (data["name"] in used_queues)
        self._respond_ok(session_id, contains=queues_conntains, last_one=True)
    except BaseException as e:
        self._respond_exception(session_id, e)


def _locals_queues_keys(self, is_private):
    if self._parent is None:
        return self._used_queues(is_private).keys()
    else:
        session_id = self._get_session_id()
        self._request(session_id, is_private=is_private)
        response = self._recv_response(session_id)
        if response["success"]:
            return response["data"]["keys"]
        else:
            eprint(response["traceback"])
            raise response["exception"]


def _process__locals_queues_keys(self, session_id, request):
    try:
        queues_keys = self._used_queues(request["data"]["is_private"]).keys()
        self._respond_ok(session_id, keys=queues_keys, last_one=True)
    except BaseException as e:
        self._respond_exception(session_id, e)


def _locals_queues_iter(self, is_private):
    if self._parent is None:
        return self._used_queues(is_private).__iter__()
    else:
        session_id = self._get_session_id()
        self._request(session_id, is_private=is_private)
        response = self._recv_response(session_id)
        if response["success"]:
            return response["data"]["iter"]
        else:
            eprint(response["traceback"])
            raise response["exception"]


def _process__locals_queues_iter(self, session_id, request):
    try:
        used_queues = self._used_queues(request["data"]["is_private"])
        queues_iter = used_queues.__iter__()
        self._respond_ok(session_id, iter=queues_iter, last_one=True)
    except BaseException as e:
        self._respond_exception(session_id, e)


def _locals_queues_clear(self, is_private):
    if self._parent is None:
        self._used_queues(is_private).clear()
    else:
        session_id = self._get_session_id()
        self._request(session_id, is_private=is_private)
        response = self._recv_response(session_id)
        if not response["success"]:
            eprint(response["traceback"])
            raise response["exception"]


def _process__locals_queues_clear(self, session_id, request):
    try:
        self._used_queues(request["data"]["is_private"]).clear()
        self._respond_ok(session_id, last_one=True)
    except BaseException as e:
        self._respond_exception(session_id, e)


def init_local_queues_methods(cls):
    cls.put = put
    cls.get = get
    cls.qsize = qsize
    cls._used_queues = _used_queues
    cls._locals_queue_put = _locals_queue_put
    cls._locals_queue_get = _locals_queue_get
    cls._locals_queue_len = _locals_queue_len
    cls._locals_queues_len = _locals_queues_len
    cls._locals_queues_contains = _locals_queues_contains
    cls._locals_queues_keys = _locals_queues_keys
    cls._locals_queues_iter = _locals_queues_iter
    cls._locals_queues_delitem = _locals_queues_delitem
    cls._locals_queues_clear = _locals_queues_clear
    cls._process_put = _process_put
    cls._process_get = _process_get
    cls._process_qsize = _process_qsize
    cls._process__locals_queue_put = _process__locals_queue_put
    cls._process__locals_queue_get = _process__locals_queue_get
    cls._process__locals_queue_len = _process__locals_queue_len
    cls._process__locals_queues_len = _process__locals_queues_len
    cls._process__locals_queues_contains = _process__locals_queues_contains
    cls._process__locals_queues_keys = _process__locals_queues_keys
    cls._process__locals_queues_iter = _process__locals_queues_iter
    cls._process__locals_queues_delitem = _process__locals_queues_delitem
    cls._process__locals_queues_clear = _process__locals_queues_clear

    return cls
