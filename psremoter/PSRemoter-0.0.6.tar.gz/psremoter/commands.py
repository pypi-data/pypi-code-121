from connector import Execute

class Scheduler(Execute):
    def __init__(
            self,
            hostname: str,
            username: str,
            password: str,
            domain=None
        ):
        self.hostname= hostname
        self.username= username
        self.password= password
        self.domain= domain

    def init(self, command):
        super().__init__(
            hostname=self.hostname,
            command=command,
            username=self.username,
            password=self.password,
            domain=self.domain,
            powershell=True
        )
        return super().remote_execution()

    def new(self, command):
        pass

    def get_all(self):
        command= """
           Get-ScheduledTask | ConvertTo-Json
        """
        return self.init(command=command)

    def get_by_name(self, name):
        command= "get-ScheduledTask | where {$_.taskName -like '*"
        command+=name
        command+= """*'} | ConvertTo-Json"""
        print(command)
        return self.init(command=command)
