from .Client import Client
from .Server import Server
from .Config import Config

import gc
import atexit


@atexit.register
def close_all():
    for obj in gc.get_objects():
        if isinstance(obj, Client):
            obj.close()

    for obj in gc.get_objects():
        if isinstance(obj, Server):
            obj.close()
