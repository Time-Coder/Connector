import threading
import os

from .utils import file_size, md5, eprint
from .Config import Config
from .NodeInternalClasses import Future, Thread


def _write_to_file(self, data, filename):
    self._request(self._get_session_id(), data=data, file_name=filename)


def _process__write_to_file(self, request):
    try:
        filename = os.path.abspath(request["data"]["file_name"])
        if self._out_file is not None and self._out_file.name != filename:
            self._out_file.close()
            self._out_file = None

        if self._out_file is None:
            if not os.path.isdir(os.path.dirname(filename)):
                os.makedirs(os.path.dirname(filename))

            self._out_file = open(filename, "wb")

        self._out_file.write(request["data"]["data"])
        self._out_file.flush()
    except BaseException:
        pass


def _close_file(self):
    self._request(self._get_session_id())


def _process__close_file(self, request):
    try:
        if self._out_file is not None:
            self._out_file.close()
            self._out_file = None
    except BaseException:
        pass


def get_file(self, src_filename, dest_filename=None, block=True):
    session_id = self._get_session_id()

    if dest_filename is None:
        dest_filename = os.path.basename(src_filename)

    self._request(
        session_id, src_filename=src_filename,
        file_size=file_size(dest_filename),
        md5=md5(dest_filename), block=block
    )

    def session():
        response = self._recv_response(session_id)
        if response["cancel"] or response["data"]["same_file"]:
            return

        if not response["success"]:
            eprint(response["traceback"])
            raise response["exception"]

        if not os.path.isdir(os.path.dirname(os.path.abspath(dest_filename))):
            os.makedirs(os.path.dirname(os.path.abspath(dest_filename)))

        try:
            file = open(dest_filename, "wb")
            self._respond_ok(session_id)
            file.close()
        except BaseException as e:
            self._respond_exception(session_id, e)
            if block:
                raise e
            else:
                return

        recved_size = 0
        full_size = response["data"]["file_size"]
        with open(dest_filename, "wb") as file:
            while recved_size < full_size:
                response = self._recv_response(session_id)
                if response["cancel"]:
                    break
                file.write(response["data"]["data"])
                file.flush()
                recved_size += len(response["data"]["data"])

    if block:
        session()
    else:
        thread = threading.Thread(target=session)
        thread.start()
        return Future(self, session_id)


def _process_get_file(self, session_id, request):
    def session():
        data = request["data"]
        src_filename = data["src_filename"]
        src_file_size = file_size(src_filename)

        same_file = (src_file_size != 0 and
                     data["file_size"] == src_file_size and
                     data["md5"] == md5(src_filename))
        try:
            file = open(src_filename, "rb")
            file.close()
            self._respond_ok(
                session_id, same_file=same_file,
                file_size=src_file_size, last_one=same_file
            )
        except BaseException as e:
            self._respond_exception(
                session_id, e, same_file=same_file, block=request["block"]
            )
            self._make_signal(session_id)
            return

        if same_file:
            if not request["block"]:
                self._put_result(session_id)
            self._make_signal(session_id)
            return

        response = self._recv_response(session_id)
        if not response["success"]:
            if not request["block"]:
                self._put_exception(session_id, response["exception"])
            self._make_signal(session_id)
            return

        block_size = 8192*1024
        sent_size = 0
        with open(src_filename, "rb") as file:
            while sent_size < src_file_size:
                data = file.read(block_size)
                sent_size += len(data)
                self._respond_ok(
                    session_id, data=data,
                    last_one=(sent_size == src_file_size)
                )

        if not request["block"]:
            self._put_result(session_id)

        self._make_signal(session_id)

    thread = Thread(target=session)
    thread.start()
    signal = self._recv_signal(session_id)
    if signal["cancel"] and thread.is_alive():
        thread.kill()
        thread.join()
        self._respond_ok(session_id, cancel=True, last_one=True)
        self._put_result(session_id, cancelled=True)
    else:
        thread.join()


def put_file(self, src_filename, dest_filename=None, block=True):
    file = open(src_filename, "rb")
    file.close()

    session_id = self._get_session_id()

    if dest_filename is None:
        dest_filename = os.path.basename(src_filename)

    src_file_size = file_size(src_filename)

    self._stop_send = False
    self._request(
        session_id, md5=md5(src_filename),
        file_size=src_file_size,
        dest_filename=dest_filename,
        block=block
    )

    def session():
        response = self._recv_response(session_id)
        if response["cancel"] or response["data"]["same_file"]:
            return

        if not response["success"]:
            eprint(response["traceback"])
            raise response["exception"]

        block_size = 8192*1024
        sent_size = 0
        with open(src_filename, "rb") as file:
            while sent_size < src_file_size:
                if self._stop_send:
                    break
                data = file.read(block_size)
                sent_size += len(data)
                self._respond_ok(
                    session_id, data=data,
                    last_one=(sent_size == src_file_size)
                )

    if block:
        session()
    else:
        thread = Thread(target=session)
        thread.start()
        return Future(self, session_id)


def _process_put_file(self, session_id, request):
    def session():
        dest_filename = request["data"]["dest_filename"]
        full_size = request["data"]["file_size"]

        if full_size == file_size(dest_filename) and \
           request["data"]["md5"] == md5(dest_filename):
            self._respond_ok(
                session_id, same_file=True,
                block=request["block"], last_one=True
            )
            self._make_signal(session_id)
            return

        if not os.path.isdir(os.path.dirname(os.path.abspath(dest_filename))):
            os.makedirs(os.path.dirname(os.path.abspath(dest_filename)))

        try:
            file = open(dest_filename, "wb")
            file.close()
            self._respond_ok(session_id, same_file=False)
        except BaseException as e:
            self._respond_exception(
                session_id, e, same_file=False, block=request["block"]
            )
            self._make_signal(session_id)
            return

        recved_size = 0
        with open(dest_filename, "wb") as file:
            while recved_size < full_size:
                response = self._recv_response(session_id)
                file.write(response["data"]["data"])
                file.flush()
                recved_size += len(response["data"]["data"])

        if not request["block"]:
            self._put_result(session_id)

        self._make_signal(session_id)

    thread = Thread(target=session)
    thread.start()
    signal = self._recv_signal(session_id)
    if signal["cancel"] and thread.is_alive():
        thread.kill()
        thread.join()
        self._respond_ok(session_id, cancel=True, last_one=True)
        self._put_result(session_id, cancelled=True)
    else:
        thread.join()


def get_folder(self, src_foldername, dest_foldername=None, block=True):
    session_id = self._get_session_id()
    if dest_foldername is None:
        dest_foldername = os.path.basename(src_foldername)

    if Config.debug:
        self._request(session_id, src_foldername=src_foldername, block=block,
                      debug=f"I need folder {src_foldername}")
    else:
        self._request(session_id, src_foldername=src_foldername, block=block)

    def session():
        response = self._recv_response(session_id)
        if response["cancel"]:
            return

        if not response["success"]:
            eprint(response["traceback"])
            raise response["exception"]

        for folder in response["data"]["folders"]:
            if not os.path.isdir(dest_foldername + "/" + folder):
                try:
                    os.makedirs(dest_foldername + "/" + folder)
                except BaseException:
                    eprint(self._traceback(False))

        if Config.debug:
            self._respond_ok(session_id,
                             debug="Created all folders. Please send files.")
        else:
            self._respond_ok(session_id)

        while True:
            response = self._recv_response(session_id)
            data = response["data"]
            if response["cancel"] or data["finished"]:
                return

            if not response["success"]:
                eprint(response["traceback"])
                continue

            dest_filename = dest_foldername + "/" + data["file_name"]
            same_file = (data["file_size"] == file_size(dest_filename) and
                         data["md5"] == md5(dest_filename))

            if same_file:
                if Config.debug:
                    self._respond_ok(
                        session_id, same_file=same_file,
                        debug=f"Already have file: {dest_filename}"
                    )
                else:
                    self._respond_ok(session_id, same_file=same_file)

                continue
            else:
                try:
                    file = open(dest_filename, "wb")
                    if Config.debug:
                        self._respond_ok(
                            session_id, same_file=same_file,
                            debug="I don't have this file, please send me."
                        )
                    else:
                        self._respond_ok(session_id, same_file=same_file)

                    file.close()
                except BaseException as e:
                    eprint(self._traceback())
                    if Config.debug:
                        self._respond_exception(session_id, e,
                                                debug="Error")
                    else:
                        self._respond_exception(session_id, e)
                    continue

            recved_size = 0
            full_size = response["data"]["file_size"]
            with open(dest_filename, "wb") as file:
                while recved_size < full_size:
                    response = self._recv_response(session_id)
                    if response["cancel"]:
                        return
                    file.write(response["data"]["data"])
                    file.flush()
                    recved_size += len(response["data"]["data"])

    if block:
        session()
    else:
        thread = threading.Thread(target=session)
        thread.start()
        return Future(self, session_id)


def _process_get_folder(self, session_id, request):
    def session():
        src_foldername = request["data"]["src_foldername"]
        if not os.path.isdir(src_foldername):
            e = FileNotFoundError(f"{src_foldername} is not a folder.")
            self._respond_exception(session_id, e, block=request["block"])
            self._make_signal(session_id)
            return
        i = len(src_foldername)-1
        while src_foldername[i] in ['/', '\\']:
            i -= 1

        folders = []
        for root, dirs, files in os.walk(src_foldername):
            for name in dirs:
                folders.append(os.path.join(root, name)[i+2:])
        if Config.debug:
            self._respond_ok(session_id, folders=folders,
                             debug=f"Please create folders: {folders}")
        else:
            self._respond_ok(session_id, folders=folders)

        response = self._recv_response(session_id)

        for root, dirs, files in os.walk(src_foldername):
            for name in files:
                src_filename = os.path.join(root, name)
                src_file_size = file_size(src_filename)
                file_name = src_filename[i+2:]

                try:
                    file = open(src_filename, "rb")
                    file.close()
                    if Config.debug:
                        self._respond_ok(
                            session_id, finished=False,
                            file_name=file_name,
                            file_size=src_file_size, md5=md5(src_filename),
                            debug=f"Do you have file {src_filename} ?"
                        )
                    else:
                        self._respond_ok(
                            session_id, finished=False,
                            file_name=file_name,
                            file_size=src_file_size, md5=md5(src_filename)
                        )
                except BaseException as e:
                    if Config.debug:
                        self._respond_exception(
                            session_id, e,
                            debug=f"I cannot open file: {src_filename}"
                        )
                    else:
                        self._respond_exception(session_id, e)
                    continue

                response = self._recv_response(session_id)
                if not response["success"] or response["data"]["same_file"]:
                    continue

                block_size = 8192*1024
                sent_size = 0
                with open(src_filename, "rb") as file:
                    while sent_size < src_file_size:
                        data = file.read(block_size)
                        if Config.debug:
                            message = f"Please write {len(data)} bytes data to file {file_name}"
                            self._respond_ok(
                                session_id, data=data,
                                debug=message
                            )
                        else:
                            self._respond_ok(session_id, data=data)
                        sent_size += len(data)

        if Config.debug:
            self._respond_ok(session_id, finished=True, last_one=True,
                             debug="Sent all files.")
        else:
            self._respond_ok(session_id, finished=True, last_one=True)

        if not request["block"]:
            self._put_result(session_id)

        self._make_signal(session_id)

    thread = Thread(target=session)
    thread.start()
    signal = self._recv_signal(session_id)
    if signal["cancel"] and thread.is_alive():
        thread.kill()
        thread.join()
        if Config.debug:
            self._respond_ok(session_id, cancel=True, last_one=True,
                             debug="Cancel.")
        else:
            self._respond_ok(session_id, cancel=True, last_one=True)

        self._put_result(session_id, cancelled=True)
    else:
        thread.join()


def put_folder(self, src_foldername, dest_foldername=None, block=True):
    if not os.path.isdir(src_foldername):
        raise FileNotFoundError(src_foldername + " is not a folder.")

    session_id = self._get_session_id()

    if dest_foldername is None:
        dest_foldername = os.path.basename(src_foldername)

    self._stop_send = False
    if Config.debug:
        self._request(session_id, dest_foldername=dest_foldername, block=block,
                      debug=f"I will send you folder: {dest_foldername}")
    else:
        self._request(session_id, dest_foldername=dest_foldername, block=block)

    def session():
        response = self._recv_response(session_id)
        if response["cancel"]:
            return

        if not response["success"]:
            eprint(response["traceback"])
            raise response["exception"]

        i = len(src_foldername)-1
        while src_foldername[i] in ['/', '\\']:
            i -= 1

        folders = []
        for root, dirs, files in os.walk(src_foldername):
            for name in dirs:
                folders.append(os.path.join(root, name)[i+2:])
        if Config.debug:
            self._respond_ok(session_id, folders=folders,
                             debug=f"Please create folders: {folders}")
        else:
            self._respond_ok(session_id, folders=folders)

        response = self._recv_response(session_id)
        if response["cancel"]:
            return

        for root, dirs, files in os.walk(src_foldername):
            for name in files:
                src_filename = os.path.join(root, name)
                src_file_size = file_size(src_filename)
                file_name = src_filename[i+2:]

                try:
                    file = open(src_filename, "rb")
                    file.close()
                    if Config.debug:
                        self._respond_ok(
                            session_id, finished=False,
                            file_name=file_name,
                            file_size=src_file_size, md5=md5(src_filename),
                            debug=f"Do you have file {file_name} ?"
                        )
                    else:
                        self._respond_ok(
                            session_id, finished=False,
                            file_name=file_name,
                            file_size=src_file_size, md5=md5(src_filename)
                        )

                except BaseException as e:
                    if Config.debug:
                        self._respond_exception(session_id, e,
                                                debug="Error")
                    else:
                        self._respond_exception(session_id, e)

                    continue

                response = self._recv_response(session_id)
                if response["cancel"]:
                    return

                if not response["success"] or response["data"]["same_file"]:
                    continue

                block_size = 8192*1024
                sent_size = 0
                with open(src_filename, "rb") as file:
                    while sent_size < src_file_size:
                        if self._stop_send:
                            return
                        data = file.read(block_size)
                        if Config.debug:
                            message = f"Please write {len(data)} bytes to file {file_name}"
                            self._respond_ok(
                                session_id, data=data,
                                debug=message
                            )
                        else:
                            self._respond_ok(session_id, data=data)

                        sent_size += len(data)

        if Config.debug:
            self._respond_ok(
                session_id, finished=True, last_one=True,
                debug="Sent all files."
            )
        else:
            self._respond_ok(session_id, finished=True, last_one=True)

    if block:
        session()
    else:
        thread = threading.Thread(target=session)
        thread.start()
        return Future(self, session_id)


def _process_put_folder(self, session_id, request):
    def session():
        dest_foldername = request["data"]["dest_foldername"]
        try:
            if not os.path.isdir(dest_foldername):
                os.makedirs(dest_foldername)
            if Config.debug:
                self._respond_ok(session_id,
                                 debug=f"Created folder {dest_foldername}")
            else:
                self._respond_ok(session_id)

        except BaseException as e:
            if Config.debug:
                self._respond_exception(
                    session_id, e, block=request["block"],
                    debug=f"Cannot create folder {dest_foldername}"
                )
            else:
                self._respond_exception(session_id, e, block=request["block"])

            self._make_signal(session_id)
            return

        response = self._recv_response(session_id)
        for folder in response["data"]["folders"]:
            if not os.path.isdir(dest_foldername + "/" + folder):
                try:
                    os.makedirs(dest_foldername + "/" + folder)
                except BaseException:
                    pass

        if Config.debug:
            self._respond_ok(session_id,
                             debug="Created all folders.")
        else:
            self._respond_ok(session_id)

        while True:
            response = self._recv_response(session_id)
            if not response["success"]:
                continue

            data = response["data"]
            if data["finished"]:
                break

            dest_filename = dest_foldername + "/" + data["file_name"]
            same_file = (data["file_size"] == file_size(dest_filename) and
                         data["md5"] == md5(dest_filename))

            if same_file:
                if Config.debug:
                    self._respond_ok(
                        session_id, same_file=same_file,
                        debug=f"Already have file {dest_filename}"
                    )
                else:
                    self._respond_ok(session_id, same_file=same_file)

                continue
            else:
                try:
                    file = open(dest_filename, "wb")
                    if Config.debug:
                        self._respond_ok(
                            session_id, same_file=same_file,
                            debug="I don't have this file, please send me."
                        )
                    else:
                        self._respond_ok(session_id, same_file=same_file)

                    file.close()
                except BaseException as e:
                    if Config.debug:
                        self._respond_exception(session_id, e,
                                                debug="Error")
                    else:
                        self._respond_exception(session_id, e)

                    continue

            recved_size = 0
            full_size = response["data"]["file_size"]
            with open(dest_filename, "wb") as file:
                while recved_size < full_size:
                    response = self._recv_response(session_id)
                    file.write(response["data"]["data"])
                    file.flush()
                    recved_size += len(response["data"]["data"])

        if not request["block"]:
            self._put_result(session_id)

        self._make_signal(session_id)

    thread = Thread(target=session)
    thread.start()
    signal = self._recv_signal(session_id)
    if signal["cancel"] and thread.is_alive():
        thread.kill()
        thread.join()
        if Config.debug:
            self._respond_ok(session_id, cancel=True, last_one=True,
                             debug="Cancel.")
        else:
            self._respond_ok(session_id, cancel=True, last_one=True)

        self._put_result(session_id, cancelled=True)
    else:
        thread.join()


def init_file_transfer_methods(cls):
    cls.get_file = get_file
    cls._process_get_file = _process_get_file
    cls.put_file = put_file
    cls._process_put_file = _process_put_file
    cls.get_folder = get_folder
    cls._process_get_folder = _process_get_folder
    cls.put_folder = put_folder
    cls._process_put_folder = _process_put_folder
    cls._write_to_file = _write_to_file
    cls._process__write_to_file = _process__write_to_file
    cls._close_file = _close_file
    cls._process__close_file = _process__close_file

    return cls
