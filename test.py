from Connector import Server, Config
Config.debug = True

server = Server()
print(server.address)
server.hold_on()