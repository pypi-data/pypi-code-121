from threading import current_thread
import paramiko, encodings, scp, re, datetime, os
from typing import Dict, List

from ..models.main import AlphaFile
from .string_lib import universal_decode
from . import io_lib

WINDOWS_LINE_ENDING = "\r\n"
UNIX_LINE_ENDING = "\n"


def standardize_content(content: str):
    if type(content) != str:
        content = content.decode('utf-8')
    return content.replace("\\r\\n", "\n").replace("\\r\n", "\n").replace("\\t", "\t")


def process_content(content: str, parameters:Dict[str,object]=None):
    if content.startswith("file:"):
        path = content.replace("file:", "")
        if not os.path.exists(path):
            path = os.getcwd() + os.sep + path
        with open(path, "r") as f:
            content = f.read()
    if parameters is not None:
        for key, value in parameters.items():
            content = content.replace("{{%s}}"%key, value)
    return content


class AlphaSsh:
    host = None
    user = None
    password = None
    ssh = None

    def __init__(self, host, user, password=None, log=None, keys=True):
        self.host = host
        self.user = user
        self.password = password
        self.log = log
        self.keys = keys

        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        self.history = {}

    def connect(self):
        if self.keys:
            self.ssh.connect(self.host, username=self.user, password=self.password)
        else:
            self.ssh.connect(
                self.host,
                username=self.user,
                password=self.password,
                look_for_keys=False,
            )
        connected = self.test()
        if connected:
            self.scp = scp.SCPClient(self.ssh.get_transport())
        return connected

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.disconnect()

        if exc_type:
            print(f"exc_type: {exc_type}")
            print(f"exc_value: {exc_value}")
            print(f"exc_traceback: {exc_traceback}")

    def disconnect(self):
        """Close ssh connection."""
        if self.test():
            self.ssh.close()
        self.scp.close()  # Coming later

    def test(self):
        return (
            self.ssh.get_transport() is not None
            and self.ssh.get_transport().is_active()
        )

    def wait(self):
        ssh_stdin, ssh_stdout, ssh_stderr = self.ssh.exec_command("")
        while not ssh_stdout.channel.exit_status_ready():
            pass

    def list_files(self, directory: str) -> List[AlphaFile]:
        """[summary]

        Args:
            directory (str): [description]

        Returns:
            List[AlphaFile]: [description]
        """
        output = self.execute_cmd(f"ls -l {directory}")
        files = io_lib.get_list_file(output)
        return files

    def list_files_names(
        self, directory: str, pattern: str = None, hidden: bool = False
    ) -> List[str]:
        cmd = "ls -l -f %s" % directory
        output = self.execute_cmd(cmd)
        lines = str(output).split()
        if pattern is not None:
            """filtered = []
            for line in lines:
                matchs = re.findall(pattern,line)
                if matchs:
                    filtered.append(line)
            lines = filtered"""
            lines = [x for x in lines if len(re.findall(pattern, x)) != 0]
        if hidden:
            return [
                x
                for x in lines
                if x.replace(".", "") != "" and (not "." in x or x.startswith("."))
            ]
        else:
            return [x for x in lines if x.replace(".", "") != "" and not "." in x]

    def list_directories(self, directory: str) -> List[AlphaFile]:
        """[summary]

        Args:
            directory (str): [description]

        Returns:
            List[AlphaFile]: [description]
        """
        output = self.execute_cmd("ls -l %s" % directory)
        directories = io_lib.get_list_file(output)
        return directories

    def list_directories_names(self, directory: str, hidden: bool = False) -> List[str]:
        output = self.execute_cmd("ls -l -f %s" % directory)
        lines = str(output).split()
        if hidden:
            return [
                x
                for x in lines
                if x.replace(".", "") != "" and (not "." in x or x.startswith("."))
            ]
        else:
            return [x for x in lines if x.replace(".", "") != "" and not "." in x]

    def get_file_content(
        self, filepath: str, decode=False, escape_replace: bool = True
    ):
        output = self.execute_cmd(f"cat {filepath}", decode=decode)
        return standardize_content(output) if escape_replace else output

    def is_file(self, filename: str):
        output = self.execute_cmd("test -f %s && echo 'y'" % filename)
        return "y" in output

    def is_dir(self, path: str, group: str = None, user: str = None, mode=None):
        output = self.execute_cmd("test -d %s && echo 'y'" % path)
        if group is not None and not self.is_group(group, path):
            self.change_group(group, path)
        if user is not None and not self.is_user(user, path):
            self.change_user(user, path)
        if mode is not None and not self.is_mode(mode, path):
            self.change_mode(mode, path)
        return "y" in output

    def make_directory(
        self,
        path: str,
        group: str = None,
        user: str = None,
        mode=None,
        ensure_path: bool = True,
    ):
        options = ""
        if ensure_path:
            options = "-p"
        if not self.is_dir(path):
            self.execute_cmd("mkdir %s %s" % (options, path))
        if not self.is_dir(path):
            return False
        if group is not None:
            self.change_group(group, path)
        if user is not None:
            self.change_user(user, path)
        if mode is not None:
            self.change_mode(mode, path)
        return True

    def get_mode(self, path: str):
        out = self.execute_cmd("stat -c %a " + path)
        mode = re.findall(r"[0-9]+", out)
        return mode[0] if len(mode) != 0 else None

    def is_mode(self, mode: str, path: str):
        mode = str(self.get_mode(path))
        return mode == str(mode)

    def change_mode(self, mode: int, path: str, recursively: bool = False):
        mode_c = ""
        if recursively:
            mode_c = "-R"
        self.execute_cmd("chmod %s %s %s" % (mode_c, mode, path))
        return str(mode) == self.get_mode(path)

    def change_group(self, group: int, path: str, recursively: bool = False):
        mode = ""
        if recursively:
            mode = "-R"
        self.execute_cmd("chgrp %s %s %s" % (mode, group, path))

    def get_group(self, path: str):
        return self.execute_cmd("stat -c %G " + path)

    def is_group(self, group: str, path: str):
        current_group = self.get_group(path)
        current_group = current_group.split()[0]
        return current_group == group

    def change_user(self, user: str, path: str, recursively: bool = False):
        mode = ""
        if recursively:
            mode = "-R"
        self.execute_cmd("chown %s %s %s" % (mode, user, path))

    def add_group_to_user(self, user: str, group: str):
        self.execute_cmd("usermod -a -G %s %s" % (group, user))

    def get_user(self, path: str):
        return self.execute_cmd("stat -c %U " + path).replace("\\r\\n", "")

    def is_user(self, user: str, path: str):
        current_user = self.get_user(path)
        return current_user == user

    def append_to_file(self, content: str, path: str):
        content = process_content(content)
        original_content = self.get_file_content(path, decode=True)
        self.execute_cmd("echo '%s' >> %s" % (content, path))
        new_content = self.get_file_content(path, decode=True)
        if not "No such file or directory" in original_content:
            return new_content == original_content + content + "\n"
        return new_content == content + "\n"

    def is_in_file(self, content: str, path: str):
        content = process_content(content)
        original_content = self.get_file_content(path, decode=True)
        return content in original_content

    def restart_service(self, service: str):
        self.execute_cmd("sudo systemctl restart %s" % service)

    def is_equal_to_file(self, content: str, path: str, mode: int = None):
        if not self.is_file(path):
            return False

        if mode is not None:
            self.change_mode(mode, path)

        content = process_content(content)
        double_backslash = "\\n" in content
        original_content = self.get_file_content(path, decode=True)

        content = content.replace(WINDOWS_LINE_ENDING, UNIX_LINE_ENDING)
        original_content = original_content.replace(
            WINDOWS_LINE_ENDING, UNIX_LINE_ENDING
        )
        original_content_u = "\\n" in original_content
        """if double_backslash and not original_content_u:
            original_content = original_content.replace('\\','\\\\')"""
        original_content = original_content.replace("\\'", "'").replace("\\\\", "\\")

        content = content.replace(WINDOWS_LINE_ENDING, UNIX_LINE_ENDING)
        original_content = original_content.replace(
            WINDOWS_LINE_ENDING, UNIX_LINE_ENDING
        )

        equal = content == original_content or (
            content == original_content[:-1] and original_content[-1:] == "\n"
        )

        """if not equal:
            lines1, lines2 = content.split('\n'), original_content.split('\n')
            for i, e in enumerate(lines1):
                if lines1[i] != lines2[i]:
                    a, b = lines1[i],lines2[i]
                    c, d = a, b.replace('\\\'','\'')
                    print(lines1[i],'\n',lines2[i])"""

        return equal

    def create_file(self, path: str):
        self.execute_cmd(f"touch {path}")
        return self.is_file(path)

    def write_to_file(self, content: str, path: str, ensure_path: bool = True, parameters:Dict[str, object]=None) -> bool:
        if ensure_path:
            self.make_directory(os.path.dirname(path))

        if content.startswith("file:"): #TODO: remove
            content_path = content.replace("file:", "")
            self.scp.put(content_path, path)
            return True
        else:
            if not self.is_file(path):
                self.create_file(path)
            content = process_content(content, parameters)

            content = content.replace(WINDOWS_LINE_ENDING, UNIX_LINE_ENDING)
            self.execute_cmd(f"echo -e '{content}' > {path}")
            new_content = self.get_file_content(path, decode=True).replace(
                WINDOWS_LINE_ENDING, UNIX_LINE_ENDING
            )
            return new_content == content + "\n"

    def is_sudoers(self, user: str, cmd: str):
        sudo_line = "%s ALL = (ALL) NOPASSWD: %s" % (user, cmd)
        sudoers_content = self.get_file_content("/etc/sudoers", decode=True)
        return sudo_line in sudoers_content

    def is_user_exist(self, user: str):
        users_content = self.get_file_content("/etc/passwd", decode=True)
        return user + ":" in users_content

    def check_python_version(self, version: str):
        output = self.execute_cmd("python --version")
        current_version = re.findall(r"\s([0-9]+.[0-9]+.?[0-9]*)\b", output)[0]
        version_nb = re.findall(r"([0-9\.]+)", version)
        version = version.replace(version_nb[0], "'%s'" % version_nb[0])

        cmd = "'%s' %s" % (str(current_version), str(version))
        valid_version = eval(cmd)
        return valid_version

    def is_output(self, cmd: str):
        output = self.execute_cmd(cmd)
        return len(output.replace("\\n", "").replace("\\r", "").strip()) != 0

    def is_found(self, cmd: str, greps: List[str] = []):
        if type(greps) == str:
            greps = [greps]
        cmd = cmd + " | " + " | ".join(['grep "%s"' % x for x in greps])
        output = self.execute_cmd(cmd, lines=True)
        if "illegal" in output[0]:
            return False
        if len(output) == 1 and output[0].strip() == "":
            return False
        return len(output) != 0

    def get_pid(self, greps: List[str] = []):
        if type(greps) == str:
            greps = [greps]
        cmd = "ps aux -P | " + " | ".join(['grep "%s"' % x for x in greps])
        output = self.execute_cmd(cmd, lines=True)
        if len(output) == 0:
            return None
        if len(output) == 1:
            return re.findall(r"[0-9]+", output)[0]
        return [
            re.findall(r"[0-9]+", x)[0]
            for x in output
            if len(re.findall(r"[0-9]+", x)) != 0
        ]

    def is_pid(self, greps=[]):
        return self.get_pid(greps=greps) is not None

    def service_restart(self, service: str):
        cmd = f"sudo systemctl restart {service}"
        return self.execute_cmd(cmd)

    def service_start(self, service: str, start: bool = True):
        action = "restart" if start else "stop"
        cmd = f"sudo systemctl {action} {service}"
        return self.execute_cmd(cmd)

    def service_enable(self, service: str, enable=True):
        action = "enable" if enable else "disable"
        cmd = f"sudo systemctl {action} {service}"
        return self.execute_cmd(cmd)

    def reload_systemctl(self):
        cmd = "systemctl daemon-reload"
        return self.execute_cmd(cmd)

    def package_installed(self, package: str):
        cmd = "sudo yum list installed | grep " + package
        output = self.execute_cmd(cmd)
        return output.startswith(package)

    def install_package(self, package: str):
        cmd = "yum install -y " + package
        output = self.execute_cmd(cmd)
        return output.startswith(package)

    def is_python_module(self, module: str):
        cmd = "which python"
        output = self.execute_cmd(cmd)
        cmd = "python -c 'import %s'" % module
        output = self.execute_cmd(cmd)
        valid = not ("No module named " in output and module in output)
        return valid

    def install_python_module(self, module: str, version: str = None):
        cmd = "which pip"
        output = self.execute_cmd(cmd)
        cmd = f"yes | pip install {module}{version}"
        output = self.execute_cmd(cmd)
        return not "error" in output

    def add_user(
        self,
        user: str,
        description: str = None,
        group: str = None,
        password: str = None,
    ):
        options = ""
        if description is not None:
            options += ' -c "%s"' % description
        cmd = "sudo useradd %s %s" % (options, user)
        self.execute_cmd(cmd)

        if group is not None:
            self.add_group_to_user(user, group)

        if password is not None:
            cmd = 'echo "%s" | sudo passwd --stdin %s' % (password, user)
            self.execute_cmd(cmd)

    def execute_cmd(self, cmd, decode=True, lines=False, timeout: int = 600):
        inputs, output, err = "", "", ""
        if self.log:
            self.log.info(f"EXEC: {cmd}")
        ssh_stdin, ssh_stdout, ssh_stderr = self.ssh.exec_command(
            cmd, get_pty=True, timeout=timeout
        )
        output = ssh_stdout.read()
        if lines:
            decode = True
        if decode:
            try:
                output = output.decode("utf-8")
                if self.log:
                    self.log.info(f"OUTPUT: {output[:100]} ...")
                # output = output.decode('utf-8').encode('ascii')
            except Exception as ex:
                if self.log:
                    self.log.error(f"", ex=ex)
                pass
            output = str(output)
            if output[:2] == "b'":
                output = output[2:-1]

        output = standardize_content(output)
        if lines:
            output = output.split("\n")

        self.history[datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S.%f")] = [
            cmd,
            output,
        ]
        return output

    def execute_cmd_interactive(self, cmd, decode=True):
        inputs, output, err = "", "", ""
        ssh_stdin, ssh_stdout, ssh_stderr = self.ssh.exec_command(cmd)

        i, limit = 0, 100
        while not ssh_stdout.channel.exit_status_ready() and i < limit:
            # Print data whena available
            if ssh_stdout.channel.recv_ready():
                alldata = ssh_stdout.channel.recv(1024)
                prevdata = b"1"
                while prevdata:
                    prevdata = ssh_stdout.channel.recv(1024)
                    alldata += prevdata
                output += str(alldata)
            i += 1

        if decode:
            inputs, output, err = (
                universal_decode(inputs),
                universal_decode(output),
                universal_decode(err),
            )
            if inputs != "" and self.log:
                self.log.info("inputs:", inputs)
            if err != "" and self.log:
                self.log.error("err:", err)
        return output
