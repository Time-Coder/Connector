import threading

from .utils import eprint


class Future:

    def __init__(self, node, session_id):
        self._node = node
        self._session_id = session_id
        self._cancelled = False
        self._done = None
        self._result = None
        self._monitor_done_thread = None
        self._done_callbacks = []

    def cancel(self):
        if self.done():
            return False

        self._node._stop_send = True
        self._node._send_signal(self._session_id, cancel=True)
        result_queues = self._node._result_queues_for_future
        self._result = result_queues[self._session_id].get()
        self._node._close_session(self._session_id)
        self._cancelled = True
        self._done = True
        return True

    def cancelled(self):
        return self._cancelled

    def done(self):
        if self._done is not None:
            return self._done
        else:
            result_queues = self._node._result_queues_for_future
            return (len(result_queues[self._session_id]) > 0)

    def result(self):
        if self._result is None:
            result_queues = self._node._result_queues_for_future
            self._result = result_queues[self._session_id].get()
            self._node._close_session(self._session_id)

        self._done = True
        if self._result["success"]:
            return self._result["return_value"]
        else:
            eprint(self._result["traceback"])
            raise self._result["exception"]

    def exception(self):
        if self._result is None:
            result_queues = self._node._result_queues_for_future
            self._result = result_queues[self._session_id].get()
            self._node._close_session(self._session_id)

        self._done = True
        return self._result["exception"]

    def _get_result(self):
        if self._result is None:
            result_queues = self._node._result_queues_for_future
            self._result = result_queues[self._session_id].get()
            self._node._close_session(self._session_id)

        for func in self._done_callbacks:
            func(self)

    def add_done_callback(self, func):
        self._done_callbacks.append(func)

        if self._monitor_done_thread is None:
            self._monitor_done_thread = threading.Thread(
                target=self._get_result
            )
            self._monitor_done_thread.start()

    def remove_done_callback(self, func):
        try:
            self._done_callbacks.remove(func)
        except BaseException:
            pass
