from .utils import eprint


def send(self, value):
    if self._parent is None:
        self._pipe[1].send(value)
    else:
        session_id = self._get_session_id()
        self._request(session_id, value=value)
        response = self._recv_response(session_id)
        if not response["success"]:
            eprint(response["traceback"])
            raise response["exception"]


def _process_send(self, session_id, request):
    try:
        self._pipe[0].send(request["data"]["value"])
        self._respond_ok(session_id, last_one=True)
    except BaseException as e:
        self._respond_exception(session_id, e)


def recv(self):
    if self._parent is None:
        return self._pipe[1].recv()
    else:
        session_id = self._get_session_id()
        self._request(session_id)
        response = self._recv_response(session_id)
        if response["success"]:
            return response["data"]["value"]
        else:
            eprint(response["traceback"])
            raise response["exception"]


def _process_recv(self, session_id, request):
    try:
        self._respond_ok(session_id, value=self._pipe[0].recv(), last_one=True)
    except BaseException as e:
        self._respond_exception(session_id, e)


def _locals_pipe_send(self, name, value):
    if self._parent is None:
        self._actual_pipes[name][1].send(value)
    else:
        session_id = self._get_session_id()
        self._request(session_id, name=name, value=value)
        response = self._recv_response(session_id)
        if not response["success"]:
            eprint(response["traceback"])
            raise response["exception"]


def _process__locals_pipe_send(self, session_id, request):
    try:
        data = request["data"]
        self._actual_pipes[data["name"]][0].send(data["value"])
        self._respond_ok(session_id, last_one=True)
    except BaseException as e:
        self._respond_exception(session_id, e)


def _locals_pipe_recv(self, name):
    if self._parent is None:
        return self._actual_pipes[name][1].recv()
    else:
        session_id = self._get_session_id()
        self._request(session_id, name=name)
        response = self._recv_response(session_id)
        if response["success"]:
            return response["data"]["value"]
        else:
            eprint(response["traceback"])
            raise response["exception"]


def _process__locals_pipe_recv(self, session_id, request):
    try:
        name = request["data"]["name"]
        self._respond_ok(
            session_id, value=self._actual_pipes[name][0].recv(),
            last_one=True
        )
    except BaseException as e:
        self._respond_exception(session_id, e)


def _locals_pipes_delitem(self, name):
    if self._parent is None:
        del self._actual_pipes[name]
    else:
        session_id = self._get_session_id()
        self._request(session_id, name=name)
        response = self._recv_response(session_id)
        if not response["success"]:
            eprint(response["traceback"])
            raise response["exception"]


def _process__locals_pipes_delitem(self, session_id, request):
    try:
        del self._actual_pipes[request["data"]["name"]]
        self._respond_ok(session_id, last_one=True)
    except BaseException as e:
        self._respond_exception(session_id, e)


def _locals_pipes_clear(self):
    if self._parent is None:
        self._actual_pipes.clear()
    else:
        session_id = self._get_session_id()
        self._request(session_id)
        response = self._recv_response(session_id)
        if not response["success"]:
            eprint(response["traceback"])
            raise response["exception"]


def _process__locals_pipes_clear(self, session_id, request):
    try:
        self._actual_pipes.clear()
        self._respond_ok(session_id, last_one=True)
    except BaseException as e:
        self._respond_exception(session_id, e)


def _locals_pipes_len(self):
    if self._parent is None:
        return len(self._actual_pipes)
    else:
        session_id = self._get_session_id()
        self._request(session_id)
        response = self._recv_response(session_id)
        if response["success"]:
            return response["data"]["len"]
        else:
            eprint(response["traceback"])
            raise response["exception"]


def _process__locals_pipes_len(self, session_id, request):
    try:
        self._respond_ok(
            session_id, len=len(self._actual_pipes), last_one=True
        )
    except BaseException as e:
        self._respond_exception(session_id, e)


def _locals_pipes_contains(self, name):
    if self._parent is None:
        return (name in self._actual_pipes)
    else:
        session_id = self._get_session_id()
        self._request(session_id, name=name)
        response = self._recv_response(session_id)
        if response["success"]:
            return response["data"]["contains"]
        else:
            eprint(response["traceback"])
            raise response["exception"]


def _process__locals_pipes_contains(self, session_id, request):
    try:
        pipes_contains = (request["data"]["name"] in self._actual_pipes)
        self._respond_ok(session_id, contains=pipes_contains, last_one=True)
    except BaseException as e:
        self._respond_exception(session_id, e)


def _locals_pipes_keys(self):
    if self._parent is None:
        return self._actual_pipes.keys()
    else:
        session_id = self._get_session_id()
        self._request(session_id)
        response = self._recv_response(session_id)
        if response["success"]:
            return response["data"]["keys"]
        else:
            eprint(response["traceback"])
            raise response["exception"]


def _process__locals_pipes_keys(self, session_id, request):
    try:
        self._respond_ok(
            session_id, keys=self._actual_pipes.keys(), last_one=True
        )
    except BaseException as e:
        self._respond_exception(session_id, e)


def _locals_pipes_iter(self):
    if self._parent is None:
        return self._actual_pipes.__iter__()
    else:
        session_id = self._get_session_id()
        self._request(session_id)
        response = self._recv_response(session_id)
        if response["success"]:
            return response["data"]["iter"]
        else:
            eprint(response["traceback"])
            raise response["exception"]


def _process__locals_pipes_iter(self, session_id, request):
    try:
        self._respond_ok(
            session_id, iter=self._actual_pipes.__iter__(), last_one=True
        )
    except BaseException as e:
        self._respond_exception(session_id, e)


def init_local_pipes_methods(cls):
    cls.send = send
    cls.recv = recv
    cls._locals_pipe_send = _locals_pipe_send
    cls._locals_pipe_recv = _locals_pipe_recv
    cls._locals_pipes_len = _locals_pipes_len
    cls._locals_pipes_contains = _locals_pipes_contains
    cls._locals_pipes_keys = _locals_pipes_keys
    cls._locals_pipes_iter = _locals_pipes_iter
    cls._locals_pipes_delitem = _locals_pipes_delitem
    cls._locals_pipes_clear = _locals_pipes_clear
    cls._process_send = _process_send
    cls._process_recv = _process_recv
    cls._process__locals_pipe_send = _process__locals_pipe_send
    cls._process__locals_pipe_recv = _process__locals_pipe_recv
    cls._process__locals_pipes_len = _process__locals_pipes_len
    cls._process__locals_pipes_contains = _process__locals_pipes_contains
    cls._process__locals_pipes_keys = _process__locals_pipes_keys
    cls._process__locals_pipes_iter = _process__locals_pipes_iter
    cls._process__locals_pipes_delitem = _process__locals_pipes_delitem
    cls._process__locals_pipes_clear = _process__locals_pipes_clear

    return cls
