from .CloseableQueue import CloseableQueue


class CloseablePipePeer:

    def __init__(self):
        self._other_peer = None
        self._queue = CloseableQueue()

    def send(self, var, block=True, timeout=None):
        self._other_peer._queue.put(var, block, timeout)

    def recv(self, block=True, timeout=None):
        return self._queue.get(block, timeout)

    def close(self):
        self._queue.close()
        self._other_peer._queue.close()

    def closed(self):
        return self._queue.closed()


def CloseablePipe():
    peer1 = CloseablePipePeer()
    peer2 = CloseablePipePeer()
    peer1._other_peer = peer2
    peer2._other_peer = peer1
    return peer1, peer2
