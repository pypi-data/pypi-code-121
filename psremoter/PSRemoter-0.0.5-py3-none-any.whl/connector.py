import subprocess
from uuid import uuid4
import platform

class Execute(subprocess.Popen):
    _script_file: str = None
    output: str = ...
    return_code: int = ...
    status: bool = ...

    def __new__(cls, *args, **kwargs):
        system= str(platform.system()).lower()
        if system != "windows":
            raise Exception(f"Current system ({system}) is not valid please execute this module from [Windows] platform.")
        return super(Execute, cls).__new__(cls)

    def __init__(self, hostname:str, command:str,username=None, password=None, powershell=False, domain=None):
        if domain:
            self.domain = domain + "\\"
        else:
            self.domain = ".\\"

        self.hostname = hostname
        self.username = username
        self.password = password
        self.command = command.strip()
        self.powershell = powershell

    def delete_file(self) -> None:
        if self._script_file:
            super().__init__(f"del /f {self._script_file}", shell=True)

    def build_powershell_command(self) -> None:
        if not self.powershell:
            return
        self._script_file= script = str(uuid4())+ ".ps1"

        with open(script, 'a') as script_file:
            script_file.write("try{" + "\n")
            for line in self.command.splitlines():
                script_file.write(line + "\n")
            script_file.write("}catch{echo $_.exception.message; exit -1}")
            script_file.close()

    def local_execution(self):
        if self.powershell:
            self.build_powershell_command()
            self.command = f"%SystemRoot%\\sysnative\\WindowsPowerShell\\v1.0\\powershell.exe -ExecutionPolicy Bypass -File {self._script_file}"

        super().__init__(self.command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        self.output= self.communicate()[0].decode('utf-8')
        self.return_code = self.returncode

        if self.return_code == 0:
            self.status= True
        else:
            self.status= False

        if self.powershell:
            self.delete_file()

        return self

    def remote_execution(self):
        if not self.powershell:
            raise Exception('remote_execution method working only as PowerShell script...\nPlease change your script to a PowerShell one.')
        elif not self.username:
            raise Exception(
                f'Please add remote host ({self.hostname}) username.')
        elif not self.password:
            raise Exception(
                f'Please add remote host ({self.hostname}) password.')

        self.command= """
            $User = "{}{}"
            $PWord = ConvertTo-SecureString -String "{}" -AsPlainText -Force
            $Credential = New-Object -TypeName System.Management.Automation.PSCredential -ArgumentList $User, $PWord
            Invoke-Command -ComputerName {} -ScriptBlock {} -Credential $Credential -ErrorAction Stop
        """.format(
            self.domain,
            self.username,
            self.password,
            self.hostname,
            "{" + self.command + "}"
        )
        return self.local_execution()

    def __str__(self):
        return f"Result ({self.status=}), Return Code ({self.return_code=}), Output ({self.output[:30]=})"
