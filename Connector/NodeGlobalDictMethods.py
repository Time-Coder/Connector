from .utils import eprint


def _server_getitem(self, name):
    session_id = self._get_session_id()
    self._request(session_id, name=name)
    response = self._recv_response(session_id)
    if response["success"]:
        return response["data"]["value"]
    else:
        eprint(response["traceback"])
        raise response["exception"]


def _process__server_getitem(self, session_id, request):
    try:
        value = self._parent[request["data"]["name"]]
        self._respond_ok(session_id, value=value, last_one=True)
    except BaseException as e:
        self._respond_exception(session_id, e)


def _server_setitem(self, name, value):
    session_id = self._get_session_id()
    self._request(session_id, name=name, value=value)
    response = self._recv_response(session_id)

    if not response["success"]:
        eprint(response["traceback"])
        raise response["exception"]


def _process__server_setitem(self, session_id, request):
    try:
        data = request["data"]
        self._parent[data["name"]] = data["value"]
        self._respond_ok(session_id, last_one=True)
    except BaseException as e:
        self._respond_exception(session_id, e)


def _server_delitem(self, name):
    session_id = self._get_session_id()
    self._request(session_id, name=name)
    response = self._recv_response(session_id)

    if not response["success"]:
        eprint(response["traceback"])
        raise response["exception"]


def _process__server_delitem(self, session_id, request):
    try:
        del self._parent[request["data"]["name"]]
        self._respond_ok(session_id, last_one=True)
    except BaseException as e:
        self._respond_exception(session_id, e)


def _server_pop(self, name):
    session_id = self._get_session_id()
    self._request(session_id, name=name)
    response = self._recv_response(session_id)

    if response["success"]:
        return response["data"]["value"]
    else:
        eprint(response["traceback"])
        raise response["exception"]


def _process__server_pop(self, session_id, request):
    try:
        value = self._parent.pop(request["data"]["name"])
        self._respond_ok(session_id, value=value, last_one=True)
    except BaseException as e:
        self._respond_exception(session_id, e)


def _server_iter(self):
    session_id = self._get_session_id()
    self._request(session_id)
    response = self._recv_response(session_id)

    if response["success"]:
        return response["data"]["iter"]
    else:
        eprint(response["traceback"])
        raise response["exception"]


def _process__server_iter(self, session_id, request):
    try:
        self._respond_ok(
            session_id, iter=iter(self._parent), last_one=True
        )
    except BaseException as e:
        self._respond_exception(session_id, e)


def _server_contains(self, name):
    session_id = self._get_session_id()
    self._request(session_id, name=name)
    response = self._recv_response(session_id)

    if response["success"]:
        return response["data"]["contains"]
    else:
        eprint(response["traceback"])
        raise response["exception"]


def _process__server_contains(self, session_id, request):
    try:
        contains = (request["data"]["name"] in self._parent)
        self._respond_ok(
            session_id, contains=contains, last_one=True
        )
    except BaseException as e:
        self._respond_exception(session_id, e)


def _server_len(self):
    session_id = self._get_session_id()
    self._request(session_id)
    response = self._recv_response(session_id)

    if response["success"]:
        return response["data"]["len"]
    else:
        eprint(response["traceback"])
        raise response["exception"]


def _process__server_len(self, session_id, request):
    try:
        self._respond_ok(session_id, len=self._parent.__len__(), last_one=True)
    except BaseException as e:
        self._respond_exception(session_id, e)


def _server_keys(self):
    session_id = self._get_session_id()
    self._request(session_id)
    response = self._recv_response(session_id)

    if response["success"]:
        return response["data"]["keys"]
    else:
        eprint(response["traceback"])
        raise response["exception"]


def _process__server_keys(self, session_id, request):
    try:
        self._respond_ok(session_id, keys=self._parent.keys(), last_one=True)
    except BaseException as e:
        self._respond_exception(session_id, e)


def _server_values(self):
    session_id = self._get_session_id()
    self._request(session_id)
    response = self._recv_response(session_id)

    if response["success"]:
        return response["data"]["values"]
    else:
        eprint(response["traceback"])
        raise response["exception"]


def _process__server_values(self, session_id, request):
    try:
        self._respond_ok(
            session_id, values=self._parent.values(), last_one=True
        )
    except BaseException as e:
        self._respond_exception(session_id, e)


def _server_items(self):
    session_id = self._get_session_id()
    self._request(session_id)
    response = self._recv_response(session_id)

    if response["success"]:
        return response["data"]["items"]
    else:
        eprint(response["traceback"])
        raise response["exception"]


def _process__server_items(self, session_id, request):
    try:
        self._respond_ok(session_id, items=self._parent.items(), last_one=True)
    except BaseException as e:
        self._respond_exception(session_id, e)


def _server_clear(self):
    session_id = self._get_session_id()
    self._request(session_id)
    response = self._recv_response(session_id)

    if not response["success"]:
        eprint(response["traceback"])
        raise response["exception"]


def _process__server_clear(self, session_id, request):
    try:
        self._parent.clear()
        self._respond_ok(session_id, last_one=True)
    except BaseException as e:
        self._respond_exception(session_id, e)


def init_global_dict_methods(cls):
    cls._server_getitem = _server_getitem
    cls._server_setitem = _server_setitem
    cls._server_delitem = _server_delitem
    cls._server_pop = _server_pop
    cls._server_iter = _server_iter
    cls._server_contains = _server_contains
    cls._server_len = _server_len
    cls._server_keys = _server_keys
    cls._server_values = _server_values
    cls._server_items = _server_items
    cls._server_clear = _server_clear
    cls._process__server_getitem = _process__server_getitem
    cls._process__server_setitem = _process__server_setitem
    cls._process__server_delitem = _process__server_delitem
    cls._process__server_clear = _process__server_clear
    cls._process__server_keys = _process__server_keys
    cls._process__server_values = _process__server_values
    cls._process__server_items = _process__server_items
    cls._process__server_iter = _process__server_iter
    cls._process__server_contains = _process__server_contains
    cls._process__server_len = _process__server_len
    cls._process__server_pop = _process__server_pop

    return cls
