from Connector import Server, Client, Config
Config.debug = True

server = Server()
client = Client()
client.connect(server.address)