import threading
import time


class AutoSendBuffer:

    def __init__(self, node, session_id, timeout=0.1, quiet=False):
        self._node = node
        self._session_id = session_id
        self._buffer_lock = threading.Lock()
        self._buffer = b''
        self._quiet = quiet
        self._timeout = timeout
        self._last_send_time = time.time()
        self._continue_send = True
        self._sending_thread = threading.Thread(target=self._timeout_send)
        self._sending_thread.start()

    def __del__(self):
        try:
            self.stop()
        except BaseException:
            pass

    def append(self, byte):
        with self._buffer_lock:
            self._buffer += byte

        if byte == b"\n" or len(self._buffer) >= 512:
            self.send()

    def send(self):
        with self._buffer_lock:
            if len(self._buffer) != 0:
                content = self._buffer.decode("utf-8")
                if not self._quiet:
                    print(content, end="", flush=True)
                self._node._respond_ok(
                    self._session_id, end=False, stdout=content
                )
                self._buffer = b''
                self._last_send_time = time.time()

    def stop(self):
        self._continue_send = False
        self._sending_thread.join()
        self.send()

    def _timeout_send(self):
        while self._continue_send:
            if time.time()-self._last_send_time >= self._timeout:
                self.send()
            time.sleep(1E-3)
