from server.client import Client


client = Client("localhost", 8000)

client.connect()
# client.send_message(input("Type your message: "))
client.send_message("q")
