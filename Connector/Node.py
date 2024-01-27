from .NodeBasicMethods import init_basic_methods
from .NodeLocalPipesMethods import init_local_pipes_methods
from .NodeLocalQueuesMethods import init_local_queues_methods
from .NodeLocalDictMethods import init_local_dict_methods
from .NodeGlobalQueuesMethods import init_global_queues_methods
from .NodeGlobalDictMethods import init_global_dict_methods
from .NodeFileTransferMethods import init_file_transfer_methods
from .NodeRPCMethods import init_rpc_methods


@init_rpc_methods
@init_file_transfer_methods
@init_global_dict_methods
@init_global_queues_methods
@init_local_dict_methods
@init_local_queues_methods
@init_local_pipes_methods
@init_basic_methods
class Node:

    @property
    def is_closed(self):
        try:
            return self._connection._closed
        except BaseException:
            return True

    @property
    def address(self):
        try:
            if self._parent is None:
                return self._connection.getsockname()
            else:
                return self._connection.getpeername()
        except BaseException:
            return None

    @property
    def server_address(self):
        try:
            if self._parent is None:
                return self._connection.getpeername()
            else:
                return self._parent.address
        except BaseException:
            return None

    @property
    def server(self):
        return self._server_peer

    @property
    def queues(self):
        return self._queues

    @property
    def pipes(self):
        return self._pipes
