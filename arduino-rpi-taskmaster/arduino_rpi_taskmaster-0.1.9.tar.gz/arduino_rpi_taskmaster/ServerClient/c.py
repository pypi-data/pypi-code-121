import Client

if __name__ == "__main__":
    c = Client.Client(999)
    c.send_data("localhost","amal")
    c.send_data("localhost","Hello World")
