from .utils import eprint


def __getitem__(self, name):
    if self._parent is None:
        return self._local_vars[name]
    else:
        session_id = self._get_session_id()
        self._request(session_id, name=name)
        response = self._recv_response(session_id)
        if response["success"]:
            return response["data"]["value"]
        else:
            eprint(response["traceback"])
            raise response["exception"]


def _process___getitem__(self, session_id, request):
    try:
        value = self._local_vars[request["data"]["name"]]
        self._respond_ok(session_id, value=value, last_one=True)
    except BaseException as e:
        self._respond_exception(session_id, e)


def __setitem__(self, name, value):
    if self._parent is None:
        self._local_vars[name] = value
    else:
        session_id = self._get_session_id()
        self._request(session_id, name=name, value=value)
        response = self._recv_response(session_id)
        if not response["success"]:
            eprint(response["traceback"])
            raise response["exception"]


def _process___setitem__(self, session_id, request):
    try:
        data = request["data"]
        self._local_vars[data["name"]] = data["value"]
        self._respond_ok(session_id, last_one=True)
    except BaseException as e:
        self._respond_exception(session_id, e)


def __delitem__(self, name):
    if self._parent is None:
        del self._local_vars[name]
    else:
        session_id = self._get_session_id()
        self._request(session_id, name=name)
        response = self._recv_response(session_id)
        if not response["success"]:
            eprint(response["traceback"])
            raise response["exception"]


def _process___delitem__(self, session_id, request):
    try:
        del self._local_vars[request["data"]["name"]]
        self._respond_ok(session_id, last_one=True)
    except BaseException as e:
        self._respond_exception(session_id, e)


def __iter__(self):
    if self._parent is None:
        return self._local_vars.__iter__()
    else:
        session_id = self._get_session_id()
        self._request(session_id)
        response = self._recv_response(session_id)
        if response["success"]:
            return response["data"]["iter"]
        else:
            eprint(response["traceback"])
            raise response["exception"]


def _process___iter__(self, session_id, request):
    try:
        self._respond_ok(
            session_id, iter=iter(self._local_vars), last_one=True
        )
    except BaseException as e:
        self._respond_exception(session_id, e)


def __contains__(self, name):
    if self._parent is None:
        return self._local_vars.__contains__(name)
    else:
        session_id = self._get_session_id()
        self._request(session_id, name=name)
        response = self._recv_response(session_id)
        if response["success"]:
            return response["data"]["contains"]
        else:
            eprint(response["traceback"])
            raise response["exception"]


def _process___contains__(self, session_id, request):
    try:
        contains = (request["data"]["name"] in self._local_vars)
        self._respond_ok(session_id, contains=contains, last_one=True)
    except BaseException as e:
        self._respond_exception(session_id, e)


def __len__(self):
    if self._parent is None:
        return self._local_vars.__len__()
    else:
        session_id = self._get_session_id()
        self._request(session_id)
        response = self._recv_response(session_id)
        if response["success"]:
            return response["data"]["len"]
        else:
            eprint(response["traceback"])
            raise response["exception"]


def _process___len__(self, session_id, request):
    try:
        self._respond_ok(
            session_id, len=len(self._local_vars), last_one=True
        )
    except BaseException as e:
        self._respond_exception(session_id, e)


def clear(self):
    if self._parent is None:
        self._local_vars.clear()
    else:
        session_id = self._get_session_id()

        self._request(session_id)
        response = self._recv_response(session_id)

        if not response["success"]:
            eprint(response["traceback"])
            raise response["exception"]


def _process_clear(self, session_id, request):
    try:
        self._local_vars.clear()
        self._respond_ok(session_id, last_one=True)
    except BaseException as e:
        self._respond_exception(session_id, e)


def keys(self):
    if self._parent is None:
        return self._local_vars.keys()
    else:
        session_id = self._get_session_id()

        self._request(session_id)
        response = self._recv_response(session_id)

        if response["success"]:
            return response["data"]["keys"]
        else:
            eprint(response["traceback"])
            raise response["exception"]


def _process_keys(self, session_id, request):
    try:
        self._respond_ok(
            session_id, keys=self._local_vars.keys(), last_one=True
        )
    except BaseException as e:
        self._respond_exception(session_id, e)


def values(self):
    if self._parent is None:
        return self._local_vars.values()
    else:
        session_id = self._get_session_id()

        self._request(session_id)
        response = self._recv_response(session_id)

        if response["success"]:
            return response["data"]["values"]
        else:
            eprint(response["traceback"])
            raise response["exception"]


def _process_values(self, session_id, request):
    try:
        self._respond_ok(
            session_id, values=self._local_vars.values(), last_one=True
        )
    except BaseException as e:
        self._respond_exception(session_id, e)


def items(self):
    if self._parent is None:
        return self._local_vars.items()
    else:
        session_id = self._get_session_id()

        self._request(session_id)
        response = self._recv_response(session_id)

        if response["success"]:
            return response["data"]["items"]
        else:
            eprint(response["traceback"])
            raise response["exception"]


def _process_items(self, session_id, request):
    try:
        self._respond_ok(
            session_id, items=self._local_vars.items(), last_one=True
        )
    except BaseException as e:
        self._respond_exception(session_id, e)


def pop(self, name):
    if self._parent is None:
        return self._local_vars.pop(name)
    else:
        session_id = self._get_session_id()

        self._request(session_id, name=name)
        response = self._recv_response(session_id)

        if response["success"]:
            return response["data"]["value"]
        else:
            eprint(response["traceback"])
            raise response["exception"]


def _process_pop(self, session_id, request):
    try:
        self._respond_ok(
            session_id, value=self._local_vars.pop(request["data"]["name"]),
            last_one=True
        )
    except BaseException as e:
        self._respond_exception(session_id, e)


def init_local_dict_methods(cls):
    cls.__getitem__ = __getitem__
    cls.__setitem__ = __setitem__
    cls.__delitem__ = __delitem__
    cls.__iter__ = __iter__
    cls.__contains__ = __contains__
    cls.__len__ = __len__
    cls.clear = clear
    cls.keys = keys
    cls.values = values
    cls.items = items
    cls.pop = pop
    cls._process___getitem__ = _process___getitem__
    cls._process___setitem__ = _process___setitem__
    cls._process___delitem__ = _process___delitem__
    cls._process___iter__ = _process___iter__
    cls._process___contains__ = _process___contains__
    cls._process___len__ = _process___len__
    cls._process_clear = _process_clear
    cls._process_keys = _process_keys
    cls._process_values = _process_values
    cls._process_items = _process_items
    cls._process_pop = _process_pop

    return cls
