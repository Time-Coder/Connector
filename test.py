from Connector import Server, Client, Config
Config.debug = True

server = Server()
print(server.address)
server.hold_on()