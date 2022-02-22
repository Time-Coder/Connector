# Examples

In this section, we will write 2 excition examples with **Connector** to see how it make complex things easy.

## Chat room

If you want to do make a chat room program, **Connector** can help a lot. Run following code on server computer:
```python
# server side
from Connector import *

def on_connect(client):
    print(client.address, "is in.")

def on_disconnect(address):
    print(address, "is out.")

server = Server("192.168.199.210", 1900) # Please input your server computer's real ip
server.set_connect_callback(on_connect)
server.set_disconnect_callback(on_disconnect)
while True:
    message = server.get()
    for client in server.clients:
        if client.address != message["address"]:
            client.send(message)
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
    client.globals.put({"address": client.address, "content": content})

client.close()
```

Then you can get this effect:
![chat room effect](https://github.com/Time-Coder/Connector/blob/master/doc/source/chat_room.gif)

## Time consuming integral

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

In above code, `f` is a simple function. But if `f` is a very time consuming function, the time consuming will be multiplied by 1000 for total integral. Naturally, we want multiple computers to calculate function value at the same time. Then we can use **Connector** to get multiple computer work together and do task scheduling easily. Just use following code:
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

If you just copy this example and test, you will find that use distributed computing way is even slower then before. Because in this example, network communication time delay is larger then calculating `sin(x)`. Only to use distributed computing way when your function is complicated enough.
