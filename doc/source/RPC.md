# Remote Procedure Call

**Connector** can do RPC in a easy way. It can call functions, call system commands and run scripts on remote computer. In following description, `client` means `client` object on client side, means ***client peer*** on server side.

* `client.eval(statement, block = True)`: Let remote computer call python `eval` and get return value.
	* `statement`: The string of Python code.
	* `block`: If `block` is `True`, it will block process until remote `eval` returns. Otherwise it will immediately return a `Future` object which you can call `result()` on it to get real return value.
* `client.exec(code, block = True)`: Let remote computer call python `exec` and get return value. Usage just like `client.eval`.
* `client.execfile(local_script_path, block=True)`: Let remote computer run a local python script.
	* `local_script_path`: Script file path on local computer.
	* `block`: If `block` is `True`, it will block process until remote computer run script finished. Otherwise, it will immediately return a `Future` object which you can call `result()` on to wait it finished.
* `client.exec_remote_file(remote_script_path, block=True)`: Let remote computer run a remote python script. The usage is just like `client.execfile`.
* `client.system(cmd, quiet=False, remote_quiet=False, once_all=False, block=True)`: Let remote computer run system command.
	* `cmd`: System command string need to be call.
	* `quiet`: If `quiet` is `True`, local side won't print anything of standard output and standard error.
	* `remote_quiet`: If it's `True`, remote side won't print anything of standard output and standard error.
	* `once_all`: Local and remote side won't print anything during system call processing and will print message after system finished.
	* `block`: If `block` is `True`, it will block process until system call finished and return system call's return value. Otherwise, it will immediately return a `Future` object which you can call `result()` on it to get system call's return value.
* `client.call(function, args=(), kwargs={}, block=True)`: Let remote computer call a local function.
	* `function`: A local callable python object, for example `print` is OK.
	* `args`: Function's positional arguments need to be passed.
	* `kwargs`: Function's key words arguments need to be passed.
	* `block`: If `block` is `True`, it will block process until remote computer call this function finished and return this function calling return value. Otherwise, it will immediately return a `Future` object which you can call `result()` on it to get function calling return value.
* `client.call_remote(function_name, args=(), kwargs={}, block=True)`: Let remote computer call a remote function.
	* `function_name`: A remote function name string, for example `"print"` is OK.
	* `args`: Function's positional arguments need to be passed.
	* `kwargs`: Function's key words arguments need to be passed.
	* `block`: If `block` is `True`, it will block process until remote computer call this function finished and return this function calling return value. Otherwise, it will immediately return a `Future` object which you can call `result()` on it to get function calling return value.
