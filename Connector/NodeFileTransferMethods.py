import threading
import os

from .utils import file_size, md5, eprint
from .Config import Config
from .NodeInternalClasses import Future, Thread


def _write_to_file(self, data, file_name):
    self._request(self._get_session_id(), data=data, file_name=file_name)


def _process__write_to_file(self, request):
    try:
        file_name = os.path.abspath(request["data"]["file_name"])
        if self._out_file is not None and self._out_file.name != file_name:
            self._out_file.close()
            self._out_file = None

        if self._out_file is None:
            folder_path = os.path.dirname(file_name)
            if not os.path.isdir(folder_path):
                os.makedirs(folder_path)

            self._out_file = open(file_name, "wb")

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


def get_file(self, src_file_name, dest_file_name=None, block=True):
    session_id = self._get_session_id()

    if dest_file_name is None:
        dest_file_name = os.path.basename(src_file_name)

    self._request(
        session_id, src_file_name=src_file_name,
        file_size=file_size(dest_file_name),
        md5=md5(dest_file_name), block=block
    )

    def session():
        response = self._recv_response(session_id)
        if response["cancel"] or response["data"]["same_file"]:
            return

        if not response["success"]:
            eprint(response["traceback"])
            raise response["exception"]

        folder_path = os.path.dirname(os.path.abspath(dest_file_name))
        if not os.path.isdir(folder_path):
            os.makedirs(folder_path)

        try:
            file = open(dest_file_name, "wb")
            self._respond_ok(session_id)
        except BaseException as e:
            self._respond_exception(session_id, e)
            if block:
                raise e
            else:
                return

        recved_size = 0
        full_size = response["data"]["file_size"]
        while recved_size < full_size:
            response = self._recv_response(session_id)
            if response["cancel"]:
                break
            data = response["data"]["data"]
            file.write(data)
            file.flush()
            recved_size += len(data)
        file.close()

    if block:
        session()
    else:
        thread = threading.Thread(target=session)
        thread.start()
        return Future(self, session_id)


def _process_get_file(self, session_id, request):
    def session():
        data = request["data"]
        src_file_name = data["src_file_name"]
        src_file_size = file_size(src_file_name)

        same_file = (src_file_size != 0 and
                     data["file_size"] == src_file_size and
                     data["md5"] == md5(src_file_name))
        try:
            file = open(src_file_name, "rb")
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

        sent_size = 0
        while sent_size < src_file_size:
            data = file.read(self.send_buffer)
            sent_size += len(data)
            self._respond_ok(
                session_id, data=data,
                last_one=(sent_size == src_file_size)
            )
        file.close()

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


def put_file(self, src_file_name, dest_file_name=None, block=True):
    file = open(src_file_name, "rb")
    session_id = self._get_session_id()

    if dest_file_name is None:
        dest_file_name = os.path.basename(src_file_name)

    src_file_size = file_size(src_file_name)

    self._stop_send = False
    self._request(
        session_id, md5=md5(src_file_name),
        file_size=src_file_size,
        dest_file_name=dest_file_name,
        block=block
    )

    def session():
        response = self._recv_response(session_id)
        if response["cancel"] or response["data"]["same_file"]:
            return

        if not response["success"]:
            eprint(response["traceback"])
            raise response["exception"]

        sent_size = 0
        while sent_size < src_file_size:
            if self._stop_send:
                break
            data = file.read(self.send_buffer)
            sent_size += len(data)
            self._respond_ok(
                session_id, data=data,
                last_one=(sent_size == src_file_size)
            )
        file.close()

    if block:
        session()
    else:
        thread = Thread(target=session)
        thread.start()
        return Future(self, session_id)


def _process_put_file(self, session_id, request):
    def session():
        data = request["data"]
        dest_file_name = data["dest_file_name"]
        full_size = data["file_size"]

        if full_size == file_size(dest_file_name) and \
           data["md5"] == md5(dest_file_name):
            self._respond_ok(
                session_id, same_file=True,
                block=request["block"], last_one=True
            )
            self._make_signal(session_id)
            return

        folder_path = os.path.dirname(os.path.abspath(dest_file_name))
        if not os.path.isdir(folder_path):
            os.makedirs(folder_path)

        try:
            file = open(dest_file_name, "wb")
            self._respond_ok(session_id, same_file=False)
        except BaseException as e:
            self._respond_exception(
                session_id, e, same_file=False, block=request["block"]
            )
            self._make_signal(session_id)
            return

        recved_size = 0
        while recved_size < full_size:
            response = self._recv_response(session_id)
            if response["cancel"]:
                break
            data = response["data"]["data"]
            file.write(data)
            file.flush()
            recved_size += len(data)
        file.close()

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


def get_folder(self, src_folder_name, dest_folder_name=None, block=True):
    session_id = self._get_session_id()
    if dest_folder_name is None:
        dest_folder_name = os.path.basename(src_folder_name)

    if Config.debug:
        self._request(session_id, src_folder_name=src_folder_name, block=block,
                      debug=f"I need folder {src_folder_name}")
    else:
        self._request(session_id, src_folder_name=src_folder_name, block=block)

    def session():
        response = self._recv_response(session_id)
        if response["cancel"]:
            return

        if not response["success"]:
            eprint(response["traceback"])
            raise response["exception"]

        for folder in response["data"]["folders"]:
            folder_path = dest_folder_name + "/" + folder
            if not os.path.isdir(folder_path):
                try:
                    os.makedirs(folder_path)
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

            dest_file_name = dest_folder_name + "/" + data["file_name"]
            same_file = (data["file_size"] == file_size(dest_file_name) and
                         data["md5"] == md5(dest_file_name))

            if same_file:
                if Config.debug:
                    self._respond_ok(
                        session_id, same_file=same_file,
                        debug=f"Already have file: {dest_file_name}"
                    )
                else:
                    self._respond_ok(session_id, same_file=same_file)

                continue
            else:
                try:
                    file = open(dest_file_name, "wb")
                    if Config.debug:
                        self._respond_ok(
                            session_id, same_file=same_file,
                            debug="I don't have this file, please send me."
                        )
                    else:
                        self._respond_ok(session_id, same_file=same_file)
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
            while recved_size < full_size:
                response = self._recv_response(session_id)
                if response["cancel"]:
                    return
                data = response["data"]["data"]
                file.write(data)
                file.flush()
                recved_size += len(data)
            file.close()

    if block:
        session()
    else:
        thread = threading.Thread(target=session)
        thread.start()
        return Future(self, session_id)


def _process_get_folder(self, session_id, request):
    def session():
        src_folder_name = request["data"]["src_folder_name"]
        if not os.path.isdir(src_folder_name):
            e = FileNotFoundError(f"{src_folder_name} is not a folder.")
            self._respond_exception(session_id, e, block=request["block"])
            self._make_signal(session_id)
            return
        i = len(src_folder_name)-1
        while src_folder_name[i] in ['/', '\\']:
            i -= 1

        folders = []
        for root, dirs, files in os.walk(src_folder_name):
            for name in dirs:
                folders.append(os.path.join(root, name)[i+2:])
        if Config.debug:
            self._respond_ok(session_id, folders=folders,
                             debug=f"Please create folders: {folders}")
        else:
            self._respond_ok(session_id, folders=folders)

        response = self._recv_response(session_id)

        for root, dirs, files in os.walk(src_folder_name):
            for name in files:
                src_file_name = os.path.join(root, name)
                src_file_size = file_size(src_file_name)
                file_name = src_file_name[i+2:]

                try:
                    file = open(src_file_name, "rb")
                    if Config.debug:
                        self._respond_ok(
                            session_id, finished=False,
                            file_name=file_name,
                            file_size=src_file_size, md5=md5(src_file_name),
                            debug=f"Do you have file {src_file_name} ?"
                        )
                    else:
                        self._respond_ok(
                            session_id, finished=False,
                            file_name=file_name,
                            file_size=src_file_size, md5=md5(src_file_name)
                        )
                except BaseException as e:
                    if Config.debug:
                        self._respond_exception(
                            session_id, e,
                            debug=f"I cannot open file: {src_file_name}"
                        )
                    else:
                        self._respond_exception(session_id, e)
                    continue

                response = self._recv_response(session_id)
                if not response["success"] or response["data"]["same_file"]:
                    continue

                sent_size = 0
                while sent_size < src_file_size:
                    data = file.read(self.send_buffer)
                    if Config.debug:
                        message = f"Please write {len(data)} bytes data to file {file_name}"
                        self._respond_ok(
                            session_id, data=data,
                            debug=message
                        )
                    else:
                        self._respond_ok(session_id, data=data)
                    sent_size += len(data)
                file.close()

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


def put_folder(self, src_folder_name, dest_folder_name=None, block=True):
    if not os.path.isdir(src_folder_name):
        raise FileNotFoundError(src_folder_name + " is not a folder.")

    session_id = self._get_session_id()

    if dest_folder_name is None:
        dest_folder_name = os.path.basename(src_folder_name)

    self._stop_send = False
    if Config.debug:
        self._request(
            session_id, dest_folder_name=dest_folder_name, block=block,
            debug=f"I will send you folder: {dest_folder_name}"
        )
    else:
        self._request(
            session_id, dest_folder_name=dest_folder_name, block=block
        )

    def session():
        response = self._recv_response(session_id)
        if response["cancel"]:
            return

        if not response["success"]:
            eprint(response["traceback"])
            raise response["exception"]

        i = len(src_folder_name)-1
        while src_folder_name[i] in ['/', '\\']:
            i -= 1

        folders = []
        for root, dirs, files in os.walk(src_folder_name):
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

        for root, dirs, files in os.walk(src_folder_name):
            for name in files:
                src_file_name = os.path.join(root, name)
                src_file_size = file_size(src_file_name)
                file_name = src_file_name[i+2:]

                try:
                    file = open(src_file_name, "rb")
                    if Config.debug:
                        self._respond_ok(
                            session_id, finished=False,
                            file_name=file_name,
                            file_size=src_file_size, md5=md5(src_file_name),
                            debug=f"Do you have file {file_name} ?"
                        )
                    else:
                        self._respond_ok(
                            session_id, finished=False,
                            file_name=file_name,
                            file_size=src_file_size, md5=md5(src_file_name)
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

                sent_size = 0
                while sent_size < src_file_size:
                    if self._stop_send:
                        return
                    data = file.read(self.send_buffer)
                    if Config.debug:
                        message = f"Please write {len(data)} bytes to file {file_name}"
                        self._respond_ok(
                            session_id, data=data,
                            debug=message
                        )
                    else:
                        self._respond_ok(session_id, data=data)

                    sent_size += len(data)
                file.close()

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
        dest_folder_name = request["data"]["dest_folder_name"]
        try:
            if not os.path.isdir(dest_folder_name):
                os.makedirs(dest_folder_name)

            if Config.debug:
                self._respond_ok(session_id,
                                 debug=f"Created folder {dest_folder_name}")
            else:
                self._respond_ok(session_id)

        except BaseException as e:
            if Config.debug:
                self._respond_exception(
                    session_id, e, block=request["block"],
                    debug=f"Cannot create folder {dest_folder_name}"
                )
            else:
                self._respond_exception(session_id, e, block=request["block"])

            self._make_signal(session_id)
            return

        response = self._recv_response(session_id)
        for folder in response["data"]["folders"]:
            folder_path = dest_folder_name + "/" + folder
            if not os.path.isdir(folder_path):
                try:
                    os.makedirs(folder_path)
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

            dest_file_name = dest_folder_name + "/" + data["file_name"]
            same_file = (data["file_size"] == file_size(dest_file_name) and
                         data["md5"] == md5(dest_file_name))

            if same_file:
                if Config.debug:
                    self._respond_ok(
                        session_id, same_file=same_file,
                        debug=f"Already have file {dest_file_name}"
                    )
                else:
                    self._respond_ok(session_id, same_file=same_file)

                continue
            else:
                try:
                    file = open(dest_file_name, "wb")
                    if Config.debug:
                        self._respond_ok(
                            session_id, same_file=same_file,
                            debug="I don't have this file, please send me."
                        )
                    else:
                        self._respond_ok(session_id, same_file=same_file)
                except BaseException as e:
                    if Config.debug:
                        self._respond_exception(session_id, e,
                                                debug="Error")
                    else:
                        self._respond_exception(session_id, e)

                    continue

            recved_size = 0
            full_size = response["data"]["file_size"]
            while recved_size < full_size:
                response = self._recv_response(session_id)
                if response["cancel"]:
                    break
                data = response["data"]["data"]
                file.write(data)
                file.flush()
                recved_size += len(data)
            file.close()

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
