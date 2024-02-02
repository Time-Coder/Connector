import collections


class OrderedDict(collections.OrderedDict):

    def __init__(self, **kwargs):
        collections.OrderedDict.__init__(self, **kwargs)

    def __setitem__(self, name, value):
        if isinstance(name, int):
            name = list(self.keys())[name]

        collections.OrderedDict.__setitem__(self, name, value)

    def __getitem__(self, name):
        if isinstance(name, int):
            name = list(self.keys())[name]

        return collections.OrderedDict.__getitem__(self, name)

    def __delitem__(self, name):
        if isinstance(name, int):
            name = list(self.keys())[name]

        collections.OrderedDict.__delitem__(self, name)

    def __repr__(self):
        result = "[\n"
        i = 0
        for value in self.values():
            address = value.address
            result += f"    Client('{address[0]}', {address[1]})"
            if i != len(self)-1:
                result += ","
            result += "\n"
        result += "]"
        return result
