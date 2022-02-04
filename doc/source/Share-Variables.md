# Share/Send variables

## via local shared dict

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

## via global shared dict

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

## via local pipes

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

## via local queues

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

## via global queues

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
