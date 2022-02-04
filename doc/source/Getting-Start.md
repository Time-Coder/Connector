# Getting Start

## Installation

Just use pip command to install **Connector** to your local Python environment:
```batch
pip install tcp-connector
```
And in Python environment, if following import won't throw exception, that means your installation is succeeded.
```python
>>> import connector
```

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
