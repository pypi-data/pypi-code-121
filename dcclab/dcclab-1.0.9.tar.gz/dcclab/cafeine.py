from sshtunnel import SSHTunnelForwarder
import time
import keyring
from contextlib import redirect_stderr


class Cafeine:
    def __init__(self, username='dcclab'):
        self.mysqlTunnel = None

    def startMySQLTunnel(self, remote_bind_address="127.0.0.1"):    
        password = keyring.get_password("cafeine2-ssh", "dcclab")

        if password is None:
           print("""
              Run the following command in the terminal to add the dcclab password to your Keychain:
              keyring set cafeine2-ssh dcclab
              (you will be prompted for the password)
              """)
           exit(1)

        import io

        f = io.StringIO()
        with redirect_stderr(f):
            self.mysqlTunnel = SSHTunnelForwarder(
                'cafeine2.crulrg.ulaval.ca',
                allow_agent=False,
                ssh_username="dcclab",
                ssh_password=password,
                remote_bind_address=(remote_bind_address, 3306)
            )
            self.mysqlTunnel.start()
        s = f.getvalue()

        return self.localMySQLPort

    @property
    def localMySQLPort(self):
        return self.mysqlTunnel.local_bind_port

    def stopMySQLTunnel(self):
        self.mysqlTunnel.stop()
        self.mysqlTunnel = None

if __name__ == "__main__":
    tunnel = Cafeine()
    tunnel.startMySQLTunnel()
    print("You can connect to mysql with `mysql -u dcclab -p -h 127.0.0.1 -P {0}`".format(tunnel.localMySQLPort))
    time.sleep(100000)
    tunnel.stopMySQLTunnel()
