# File Transfer

**Connector** can do file exchange in a very easy way. But can only exchange files between server and client. Client and client cannot exchange file directly, but they can do it through server. You can use following functions to get/put files/folders between client and server(where `client` on client side means `client` object and on server side means ***client peer***).

* `client.get_file(src_file_path, dest_file_path = None, block = True)`: Get file from remote computer.
    * `src_file_path`: Remote file path you need to get from remote computer.
    * `dest_file_path`: Local file path you need to put the file at. If it's `None`, it will put file at current working directory.
    * `block`: If it's `True`, it will block the process until file transfer finished. Otherwise this method will immediately return a `Future` object which you can call `done` method on it to check if transfer is finished. To see more usage of a `Future` object, please refer to [User Functions Reference]()
* `client.put_file(src_file_path, dest_file_path = None, block = True)`: Put local file to remote computer.
	* `src_file_path`: Local file path you need to put to remote computer.
	* `dest_file_path`: Remote computer file path which you need to put file at. If it's `None`, it will put file at remote script working directory.
	* `block`: If it's `True`, it will block the process until file transfer finished. Otherwise this method will immediately return a `Future` object which you can call `done` method on it to check if transfer is finished. To see more usage of a `Future` object, please refer to [User Functions Reference]()
* `client.get_folder(src_folder_path, dest_folder_path = None, block = True)`: Get folder from remote computer. The usage is just like `get_file`.
* `client.put_folder(src_folder_path, dest_folder_path = None, block = True)`: Put local folder to remote computer. The usage is just like `put_file`.
* `server.put_file_to_all(src_file_path, dest_file_path)`: Put server computer's file `src_file_path` to all connected clients as path `dest_file_path`.
* `server.put_folder_to_all(src_folder_path, dest_folder_path)`: Put server computer's folder `src_folder_path` to all connected clients as path `dest_folder_path`.
