import threading
import ctypes


class KillableThread(threading.Thread):

    def __init__(self, target, args=(), kwargs={}):
        threading.Thread.__init__(
            self, target=target,
            args=args, kwargs=kwargs
        )

    def __get_id(self):
        if hasattr(self, '_thread_id'):
            return self._thread_id

        for id, thread in threading._active.items():
            if thread is self:
                return id

    def kill(self):
        thread_id = self.__get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
            thread_id, ctypes.py_object(SystemExit)
        )
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            print('Exception raise failure')
