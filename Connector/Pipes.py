from .CloseablePipe import CloseablePipe


class PipeDict(dict):

    def __init__(self):
        dict.__init__(self)

    def __getitem__(self, name):
        if not dict.__contains__(self, name):
            dict.__setitem__(self, name, CloseablePipe())
        return dict.__getitem__(self, name)

    def __delitem__(self, name):
        if dict.__contains__(self, name):
            try:
                self[name][0].close()
            except BaseException:
                pass

            try:
                self[name][1].close()
            except BaseException:
                pass

            dict.__delitem__(self, name)

    def clear(self):
        for name in self:
            try:
                self[name][0].close()
            except BaseException:
                pass

            try:
                self[name][1].close()
            except BaseException:
                pass

        dict.clear(self)


class Pipe:

    def __init__(self, node, name):
        self._node = node
        self._name = name

    def send(self, value):
        self._node._locals_pipe_send(self._name, value)

    def recv(self):
        return self._node._locals_pipe_recv(self._name)


class Pipes:

    def __init__(self, node):
        self._node = node

    def __getitem__(self, name):
        return Pipe(self._node, name)

    def __delitem__(self, name):
        self._node._locals_pipes_delitem(name)

    def __len__(self):
        return self._node._locals_pipes_len()

    def __contains__(self, name):
        return self._node._locals_pipes_contains(name)

    def __iter__(self):
        return self._node._locals_pipes_iter()

    def keys(self):
        return self._node._locals_pipes_keys()

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

    def clear(self):
        self._node._locals_pipes_clear()
