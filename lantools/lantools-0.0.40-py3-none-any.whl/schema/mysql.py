from pydantic import BaseModel

class Mysql(BaseModel):
    host: str
    port: int
    name: str
    user: str
    password: str

    def get_dsn(self):
        return "mysql+mysqlconnector://{}:{}@{}:{}/{}".format(
            self.user,
            self.password,
            self.host,
            self.port,
            self.name
        )