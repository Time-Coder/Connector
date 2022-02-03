# Connector -- A lightweight network programming tool for Python

## What can Connector do?

**Connector** will greatly simplify Client/Server mode's network programming. **Connector** can help a lot in any situations that need message exchanging. All message communication will become very easy. In detail, it can do following things: 

1. Share/Send variables between different threads/processes/programs/computers.
3. Put/Get files/folders to/from different programs on different computers.
4. RPC (Remote Procedure Call)

Let's see how **Connector** achieve those things.

## Get connected
**Connector** works in Client/Server mode. So if you want to communicate between some computers, you should choose one computers work as a server, other computers work as a clients and should connect with server. So you should use following steps to get all computers connected:

0. You have some computers connected in the one Local Area Network.
1. Choose one computer works as server. Other computers work as clients.
2. On server computer, run code `server = Server(ip, port_number)`. If `port_number` gives nothing, it will use a random avaiable port. If both `ip` and `port_number` give nothing, it will use first avaiable network interface card's ip.
3. On server computer, you can use `print(server.address)` to get address of server. Such that it print `('192.168.199.210', 57680)`. Note it on your notebook.
4. On each client computer, run following code to connect with server:
```python
client = Client()
client.connect('192.168.199.210', 57680) # use the address you note on notebook
```
5. On server computer, you can get each ***client peer*** by this way:
```python
server.clients[0] # to get first connected client
server.clients[('192.168.105.23', 8273)] # to get client whose address is ('192.168.105.23', 8273)
```
***client peer*** means a communication handle on server side that connected with one client.

After that, you got `server` object on server computer and `client` object on each client computer. Let's use **Connector** to communicate with each other!

## Share/Send variables
### via local shared dict
A client and server can use shared variables, just use **local shared dict**. On client side, use `client` just like a normal dict. On server side, use ***client peer*** just like a normal dict. And logically, client side dict and server side dict are one same dict and will always synchronize changes. For example, 
```python
# client side
client["var1"] = 256
```

```python
# server side
print(server.clients[0]["var1"]) # you got 256
server.clients[0]["var1"] = "Hello world!"
```

```python
# client side
print(client["var1"]) # you got "Hello world!"
```
In this example, You can use `client` and `server.clients[0]` just like normal dict. It support all normal dict operations.

### via global shared dict
If a client want to share variables with other clients, just use **global shared dict**. On all client sides, use `client.globals` just like a normal dict. On server side, use `server` just like a normal dict. And logically, `client.globals` on each client computer and `server` are one dict and will always synchronize changes. For example,
```python
# client computer 1
client.globals["test_var"] = [0, "well"]
```

```python
# client computer 2
print(client.globals["test_var"]) # you got [0, "well"]
client.globals["message"] = "Can somebody bring me some milk?"
```

```python
# server computer
print(server["test_var"]) # you got [0, "well"]
print(server["message"]) # you got "Can somebody bring me some milk?"
```

### via local pipes
If you want one client and server just has a conversation, you can use local pipes. On client side, use `client` just like a normal pipe side. On server side, use ***client peer*** just like this pipe's another side. For example,
```python
# client side
client.send("What's you name?")
client.recv() # program will hold on until server side send something.
```

```python
# server side
server.clients[0].recv() # you got "What's you name?"
server.clients[0].send("My name is Bruce.")
# client side's client.recv() statement will get result "My name is Bruce."
```

If you want to use a lot of pipes in some purpose, you can use `pipes` property in `client` object and ***client peer*** on server side. See following code:
```python
# client side
client.pipes["any_name"].send("How old are you?")
client.pipes["any_name"].recv() # program will hold on until server side send something.
```

```python
# server side
server.clients[0].pipes["any_name"].recv() # you got "How old are you?"
server.clients[0].pipes["any_name"].send(25)
# client side's client.pipes["any_name"].recv() statement will get result 25
```

### via local queues
Client and server can also communicate via queues. In this way:
```python
# client side
client.put("Send me a file: test.jpg")
# client.get() # don't call get() here, otherwise it will get the message it put itself.
client.queues["other_queue"].put("Call me in 5 minutes.")
```

```python
# server side
server.clients[0].get() # you got "Send me a file: test.jpg"
server.clients[0].put("No such file!")
server.clients[0].queues["other_queue"].get() # you got "Call me in 5 minutes."
server.clients[0].queues["other_queue"].put("OK")
```

### via global queues
Anybody can `get` and `put` variables in a global shared place: **global queues**. For example:
```python
# client computer 1
client.globals.put({"type": "request"})
client.globals.queues["news"].put({"title": "Super man died", "body": "..."})
```

```python
# client computer 2
client.globals.get() # you got {"type": "request"} that client 1 put
client.globals.put({"type": "respond"})
client.globals.queues["news"].put([0, 1, 2])
```

```python
# server computer
server.get() # you got {"type": "respond"} that client 2 put
server.queues["news"].get() # you got {"title": "Super man died", "body": "..."} that client 1 put
server.queues["news"].get() # you got [0, 1, 2] that client 2 put
```

## Get/Put files/folders
**Connector** can do file exchange in a very easy way. But can only exchange files between server and client. Client and client cannot exchange file directly, but they can do it through server. You can use following functions to get/put files/folders between client and server(where `client` on client side means `client` object and on server side means ***client peer***).

* `client.get_file(src_file_path, dest_file_path = None, block = True)`: Get file from remote computer.
    * `src_file_path`: Remote file path you need to get from remote computer.
    * `dest_file_path`: Local file path you need to put the file at. If it's `None`, it will put file at current working directory.
    * `block`: If it's `True`, it will block the process until file transfer finished. Otherwise this method will immediately return a `Future` object which you can call `done` method on it to check if transfer is finished. To see more usage of a `Future` object, please refer to section **User Functions Reference**
* `client.put_file(src_file_path, dest_file_path = None, block = True)`: Put local file to remote computer.
	* `src_file_path`: Local file path you need to put to remote computer.
	* `dest_file_path`: Remote computer file path which you need to put file at. If it's `None`, it will put file at remote script working directory.
	* `block`: If it's `True`, it will block the process until file transfer finished. Otherwise this method will immediately return a `Future` object which you can call `done` method on it to check if transfer is finished. To see more usage of a `Future` object, please refer to section **User Functions Reference**
* `client.get_folder(src_folder_path, dest_folder_path = None, block = True)`: Get folder from remote computer. The usage is just like `get_file`.
* `client.put_folder(src_folder_path, dest_folder_path = None, block = True)`: Put local folder to remote computer. The usage is just like `put_file`.
* `server.put_file_to_all(src_file_path, dest_file_path)`: Put server computer's file `src_file_path` to all connected clients as path `dest_file_path`.
* `server.put_folder_to_all(src_folder_path, dest_folder_path)`: Put server computer's folder `src_folder_path` to all connected clients as path `dest_folder_path`.

## RPC (Remote Procedure Call)
**Connector** can do RPC in a easy way. It can call functions, call system commands and run scripts on remote computer. In following description, `client` means `client` object on client side, means ***client peer*** on server side.

* `client.eval(statement, block = True)`: Let remote computer call python `eval` and get return value.
	* `statement`: The string of Python code.
	* `block`: If `block` is `True`, it will block process until remote `eval` returns. Otherwise it will immediately return a `Future` object which you can call `result()` on it to get real return value.
* `client.exec(code, block = True)`: Let remote computer call python `exec` and get return value. Usage just like `client.eval`.
* `client.execfile(local_script_path, block=True)`: Let remote computer run a local python script.
	* `local_script_path`: Script file path on local computer.
	* `block`: If `block` is `True`, it will block process until remote computer run script finished. Otherwise, it will immediately return a `Future` object which you can call `result()` on to wait it finished.
* `client.exec_remote_file(remote_script_path, block=True)`: Let remote computer run a remote python script. The usage is just like `client.run`.
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

## Examples

Let's see some exciting examples that **Connector** can do.

### Chat room
If you want to do make a chat room, **Connector** can help a lot. Run following code on server computer:
```python
# server side
from Connector import *

def on_connect(client):
    print(client.address, "is in.")
    while not client.is_closed:
        content = client.recv()
        for address in client.server.clients:
            try:
                if address != client.address:
                    client.server.clients[address].send({"address": client.address, "content": content})
            except:
                pass

def on_disconnect(address):
    print(address, "is out.")

server = Server("192.168.199.210", 1900) # Please input your server computer's real ip
server.set_connect_callback(on_connect)
server.set_disconnect_callback(on_disconnect)
server.hold_on()
```

Run following code on each client computer:
```python
# client side
from Connector import *
from inputer import * # you need call 'pip install inputer'
import threading

client = Client()
client.connect("192.168.199.210", 1900) # Please input server computer's real ip
inputer = Inputer()

def recving(client, inputer):
    while True:
        try:
            message = client.recv()
        except:
            break
            
        inputer.print_before(message["address"], ": ", message["content"], sep="")

recving_thread = threading.Thread(target=recving, args=(client, inputer), daemon=True)
recving_thread.start()

while True:
    content = inputer.input("Myself: ")
    if content == "exit":
        break
    client.send(content)

client.close()
```

### Time consuming integral
If you want to get the integral value of a function on an inteval, in a simple way, you can use following code:
```python
import math
def integral(func, inteval):
    result = 0
    n = 1000
    L = inteval[1] - inteval[0]
    dx = L / n
    for i in range(n):
        x = inteval[0] + i/n*L
        result += dx * func(x)
    return result

def f(x):
    return math.sin(x)

if __name__ == '__main__':
    print(integral(f, [0, math.pi]))
```

But in above code, `f` is a simple function. But if `f` is a very time consuming function, the time consuming will be multiplied by 1000 for total integral time. We can do it in distributed computing way:
```python
# server side
import math
from Connector import *

def integral(func, inteval):
    result = 0
    n = 1000
    L = inteval[1] - inteval[0]
    dx = L / n

    server = Server("192.168.199.210", 1900)
    server["func"] = func
    for i in range(n):
        x = inteval[0] + i/n*L
        server.queues["task"].put(x)

    while n > 0:
        result += dx * server.queues["result"].get()
        n -= 1

    server.close()

    return result

def f(x):
    return math.sin(x)

if __name__ == '__main__':
    print(integral(f, [0, math.pi]))
```

```python
# client side
from Connector import *

client = Client()
client.connect("192.168.199.210", 1900)

f = client.globals["func"]
while True:
    try:
        x = client.globals.queues["task"].get()
        value = f(x)
        client.globals.queues["result"].put(value)
    except:
        break
```