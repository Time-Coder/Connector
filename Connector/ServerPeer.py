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
