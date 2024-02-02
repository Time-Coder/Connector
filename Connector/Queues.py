from .CloseableQueue import CloseableQueue


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
