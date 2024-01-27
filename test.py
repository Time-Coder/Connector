from Connector import Client, Server

server = Server()
client = Client()
client.connect(server.address)
client["test"] = 5
print(server.clients[0]["test"])