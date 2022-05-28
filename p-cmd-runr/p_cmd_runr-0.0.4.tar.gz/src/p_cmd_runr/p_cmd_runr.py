
import sys, os, signal
from time import sleep, time, strftime, localtime
import getpass
#import argparse as ap
import functools
import paramiko



def get_nodes(jumpboxes):
    """
    Description:
        Returns the list of nodes (with the same login credentials) contained in jumpboxes.
    Parameters:
        - jumpboxes a ConfigGrabber object.
    Returns:
        A list of nodes.
    """
    nodes = []
    for e in jumpboxes:
        if e.get("nodes"):
            nodes = e["nodes"]
            break

    return nodes



def get_all_nodes(jumpboxes):
    """
    Description:
        Returns the list of all nodes contained in jumpboxes.
    Parameters:
        - jumpboxes a ConfigGrabber object.
    Returns:
        A list of nodes.
    """
    nodes = []
    snodes = []
    for e in jumpboxes:
        if e.get("node"):
            if e.get("log_file"):
                snodes.append(e["log_file"])
            else:
                snodes.append(e["node"])
        elif e.get("nodes"):
            nodes = e["nodes"]
    snodes.extend(nodes)
    return snodes



def move_to_tmp(nodes, func=None):
    """
    Description:
        Manipulates the output file(s) from the commands run on the nodes according to func, and then attempts to move the output file(s) to a tmp folder, if it exists.
    Parameters:
        - nodes list of nodes.
        - func a function used to manipulate a text file. default value is None.
    """
    tomove = []
    for node in nodes:
        with os.scandir() as entries:
            for entry in entries:
                if (entry.name.startswith(node) or (node in entry.name)) and not entry.is_dir(follow_symlinks=False):
                    tomove.append(entry.name)
        entries.close()
    if tomove and func:
        print("File manipulation in progress...")
    for entryname in tomove:
        try:
            if func:
                func(entryname)
            os.replace(f"./{entryname}", f"./tmp/{entryname}")  # move the output file in tmp folder
        except:
            pass



def main(jumpboxes, channelstack=None, print_output=False, blocking=True):
    """
    Description:
        Executes commands on the list of nodes, accessed jumpbox-style, and outputs the results in log file(s).
    Parameters:
        - jumpboxes list containing a nodes list, a cmd_files list, and a jumpbox object.
        - channelstack optional channel created by the previous node (if there was a previous node).
        - print_output determines whether or not to print command output on the screen.
        - blocking determines whether to block and wait for a command to finish executing.
    """
    pl = []
    nodes = retreive_dict_by_key(jumpboxes, "nodes")
    command_files = retreive_dict_by_key(jumpboxes, "cmd_files")
    if nodes:
        if len(nodes["nodes"]) > 1:
            for i, node in enumerate(nodes["nodes"], start=0):
                timestr = strftime("%d-%m-%Y_%H%M%S", localtime())
                cmdlogf = "_".join([node, timestr + ".txt"])
                if (len(command_files["cmd_files"]) == len(nodes["nodes"])) or (i < len(command_files["cmd_files"])): 
                    cmd = CmdRunner(jumpboxes[0], node=node, cmd_file=command_files["cmd_files"][i], log_file=cmdlogf, blocking=blocking) 
                elif len(command_files["cmd_files"]) < len(nodes["nodes"]):
                    cmd = CmdRunner(jumpboxes[0], node=node, cmd_file=command_files["cmd_files"][-1], log_file=cmdlogf, blocking=blocking) 
                else:
                    cmd = CmdRunner(jumpboxes[0], node=node, cmd_file=command_files["cmd_files"][len(nodes["nodes"]) - 1], log_file=cmdlogf, blocking=blocking) 

                pl.append(cmd)
        else:
            node = nodes["nodes"][0]
            timestr = strftime("%d-%m-%Y_%H%M%S", localtime())
            cmdlogf = "_".join([node, timestr + ".txt"])
            cmd = CmdRunner(jumpboxes[0], node=node, cmd_file=command_files["cmd_files"][0], log_file=cmdlogf, blocking=blocking) 
            pl.append(cmd)

        for p in pl:
            if channelstack:
                transport = channelstack.get_transport()
                channel = transport.open_session()
                channel.get_pty()
                channel.invoke_shell()
                p.jump(channel)
            else:
                p.jump(channelstack)
            p.execute(print_output)
        print("main has finished.")

	

def remove_comment(line, comment="#"):
    """
    Description:    
        Return line without the comment portion.
        It is assumed that a comment, if present, extends to the end of the line.
        Returns an empty string if line is a comment.
    Parameters:
        - line line of text from which the comment is to be removed.
        - comment character used to specify the start of a comment.
    Returns:
        The line string without the comments.
    """
    index = line.find(comment)
    if index < 0:
        return line
    if line.strip().lower().startswith("password"):
        return line
    if line.strip().lower().startswith("prompts"):
        p1 = line[:index+1].strip()
        p2 = line[index+1:].strip()
        p3 = remove_comment(p2, comment)
        return p1 + p3
    return line[:index].strip()



def my_strip(n):
    return n.strip()
    


class ConfigGrabber:
    def __init__(self, filename="config.txt", separator="=", comment="#", mvs=",", delay="0", cmd_timeout="0.5", prompts="$#?<>"):
        """
        Description:
            Initializer of a ConfigGrabber object.
            Reads a configuration file and makes available a dictionary of key value-pairs taken from that configuration file.
        Parameters:
            - Filename specifies the name of the configuration file to process.
            - separator defines the char or string used as separator between key value pairs.
            - comment defines the char or string used for line comments.
            - mvs or multi-value seperator: defines the char or string that seperates multiple values.
            - delay pause time (in seconds) before running the next command.
            - cmd_timeout maximum time (in seconds) to wait for a command to finish executing.
            - prompts string of characters representing command line prompts.
        Returns:
            ConfigGrabber object (also known as jumpboxes).
        """
        self.filename = filename
        self.sep = separator
        self.com = comment
        self.mvs = mvs
        self.prompts = prompts
        self.jumpbox_list = []
        self.delay = delay
        self.cmd_timeout = cmd_timeout
        config_dict = {}
        with open(self.filename, mode="rt", encoding="utf-8") as fpo:
            for line in fpo.readlines():
                line = remove_comment(line, comment)
                if not line:
                    continue
                key, _, value = line.partition(self.sep)
                key = key.lower().strip()
                if key == "end":
                    if not config_dict.get("delay"):
                        config_dict["delay"] = self.delay
                    if not config_dict.get("cmd_timeout"):
                        config_dict["cmd_timeout"] = self.cmd_timeout
                    if not config_dict.get("prompts"):
                        config_dict["prompts"] = self.prompts
                    self.jumpbox_list.append(config_dict)
                    config_dict = {}
                    continue
                if not _:
                    continue
                if (self.mvs in value) and (key != "password" and key != "prompts"):
                    value = list(map(my_strip, value.split(self.mvs)))
                if key == "jump_cmd" or key == "nodes" or key == "cmd_files":
                    if key == "nodes" or key == "cmd_files":
                        config_dict[key] = value if type(value) is list else [value.strip()]
                        self.jumpbox_list.append(config_dict)
                        config_dict = {}
                    else:
                        config_dict[key] = value.strip()
                else:
                    config_dict[key] = value.strip()


    def __getitem__(self, i):
        return self.jumpbox_list[i]
   

    def __iter__(self):
        return iter(self.jumpbox_list[:])


    def __delitem__(self, i):
        del self.jumpbox_list[i]


    def __repr__(self):
        return str(self.jumpbox_list)


    def __str__(self):
        ret = ""
        for d in self.jumpbox_list:
            for k, v in d.items():
                if isinstance(v, list):
                    ret += ":\t".join([k, str(v)]) + "\n"
                else:
                    ret += ":\t".join([k, v]) + "\n"
            ret += "\n"
        return ret


    def __len__(self):
        return len(self.jumpbox_list)


    def pop(self, i=0):
        r = self.jumpbox_list[i]
        del self.jumpbox_list[i]
        return r



def send_receive_cmd_blocking(channel, cmd, prompts="$#?<>", print_output=False):
    """
    Description:
        Blocking version of send_receive_cmd.
    Paramaters:
        - channel a Paramiko channel.
        - cmd text to send.
        - print_output determines whether or not to print command output on the screen.
        - prompts string of characters representing command line prompts. the function will not return unless it detects one of the prompt characters in the end of the command output.
    Returns:
        Received text as a result of sent cmd.
    """
    rcv = output = ""
    wait_time = 0.1
    channel.send(cmd + "\n")

    while not channel.exit_status_ready():
        sleep(wait_time)
        if channel.recv_ready():
            output  = channel.recv(10000000).decode(encoding="utf-8")
            if print_output:
                print(output)
            rcv += output
            while output:
                sleep(wait_time)
                if channel.recv_ready():
                    output  = channel.recv(10000000).decode(encoding="utf-8")
                    if print_output:
                        print(output)
                    rcv += output
                output = output.strip()
                if len(output) == 0 or output[-1] in prompts:
                    break
        elif output and output[-1] in prompts:
            break
        
    return rcv



def send_receive_cmd(channel, cmd, cmd_timeout=0.5, print_output=False):
    """
    Description:
        Send and receive through a channel.
    Paramaters:
        - channel a Paramiko channel.
        - cmd text to send.
        - cmd_timeout maximum time to wait (in seconds) for command to return output.
        - print_output determines whether or not to print command output on the screen.
    Returns:
        Received text as a result of sent cmd.
    """
    rcv = ""
    channel.send(cmd + "\n")
    wait_time = 0.1
    elapsed = 0.0
    while True:
        if channel.recv_ready():
            output = channel.recv(10000000).decode(encoding="utf-8")
            if print_output:
                print(output)
            rcv += output
            if len(output):
                elapsed = 0.0
        elif elapsed <= cmd_timeout:
            sleep(wait_time)
            elapsed += wait_time
        else:
            break
    return rcv



def retreive_dict_by_key(jumpboxes, key_name):
    """
    Description:
        Removes and returns the dictionary element having key_name from jumpboxes, else returns None if not found.
    Parameters:
        - jumpboxes list containing a nodes list, a cmd_files list, and a jumpbox object.
        - key_name name of dictionary key.
    Returns:
        returns the dictionary element having key_name from jumpboxes.
        (jumpboxes no longer contains that dictionary element.)
    """
    rmi = -1
    rte = None
    for i, e in enumerate(jumpboxes, start=0):
        if e.get(key_name):
            rmi = i
            rte = e
            break
    if rmi >= 0:
        del jumpboxes[rmi]
    return rte



class CmdRunner:
    """
    Description:
        Logs into node jumpbox-style and runs commands taken from cmd_file. Output results in log_file.
    """
    def __init__(self, jumpbox, node, cmd_file, log_file, blocking):
        """
        Description:
            Initializer of CmdRunner object.
        Parameters:
            - jumpbox defines parameters needed to login to node.
            - node host name or IP address of the node.
            - cmd_file file containing the commands to execute on node.
            - log_file name of file in which activity is logged. If log_file is not given, a log file will be created.
            - blocking determines whether to block and wait for a command to finish executing.
        Returns:
            CmdRunner object.
        """
        self.jumpbox = jumpbox
        self.node = node
        self.blocking = blocking
        self.commands = []
        self.log_fp = None
        self.ssh = None
        self.channel = None
        self.transport = None
        try:
            self.delay = float(self.jumpbox["delay"])
        except ValueError:
            print("Invalid delay value:", self.jumpbox["delay"])
            print("Using 0 seconds instead")
            self.delay = 0
        try:
            self.cmd_timeout = float(self.jumpbox["cmd_timeout"])
        except ValueError:
            print("Invalid cmd_timeout value:", self.jumpbox["cmd_timeout"])
            print("Using 0.5 seconds instead")
            self.cmd_timeout = 0.5
        except:
            print("Empty jumpbox")
            sys.exit(1)
        if cmd_file:
            with open(cmd_file, mode="rt", encoding="utf-8") as fp:
                for line in fp.readlines():
                    line = remove_comment(line).strip()
                    if line:
                        self.commands.append(line)
            try:
                self.log_fp = open(log_file, mode="wt", encoding="utf-8")
            except OSError as e:
                print("Unable to open log file", log_file)
                print(e)
                sys.exit(1)


    def jump(self, channelstack=None):
        """
        Description:
            Jumps to a node by creating a new channel or from the channelstack if specified.
        Parameters:
            - channelstack optional channel from the previous node.
        """
        try:
            rcv = None
            port = 22
            if self.jumpbox.get("port"):
                port = int(self.jumpbox["port"])
            if channelstack == None:
                if self.jumpbox["jump_cmd"].lower() == "ssh":
                    self.ssh = paramiko.SSHClient()
                    self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    self.ssh.connect(hostname=self.node, port=port, username=self.jumpbox["username"], password=self.jumpbox["password"])
                    self.transport = self.ssh.get_transport()  # store this new transport
                    self.channel = self.transport.open_session()
                    self.channel.get_pty()
                    self.channel.invoke_shell()
                else:
                    raise Exception("Need to jump to at least a different node in order to access Amos/Moshell")
            elif channelstack:
                if self.jumpbox["jump_cmd"].lower() == "ssh":
                    channelstack.send(f"ssh -o 'StrictHostKeyChecking no' {self.jumpbox['username']}@{self.node} -p {port}" + "\n")

                    rcv = ""
                    while not rcv.endswith("assword: "):
                        output = channelstack.recv(10000000).decode(encoding="utf-8")
                        rcv += output
                    send_receive_cmd(channelstack, self.jumpbox["password"] + "\n", self.cmd_timeout)
                elif "mos" in self.jumpbox["jump_cmd"].lower():
                    channelstack.send(f"{self.jumpbox['jump_cmd']} {self.node}" + "\n")
                    sleep(10)
                    while not channelstack.recv_ready() and not channelstack.closed:
                        sleep(2)
                    rcv = channelstack.recv(10000000).decode(encoding="utf-8")
                else:
                    raise Exception(f"{self.jumpbox['jump_cmd']} not supported")

                self.channel = channelstack
                self.transport = self.channel.get_transport()  # store this new transport
                
            else:
                raise Exception("channelstack is not supposed to be null")

        except (paramiko.SSHException, Exception) as e:
            print(e)
            print(f"Failed to connect to {self.node}")
            if self.ssh:
                self.ssh.close()
                
            sys.exit(f"{self.node} connection failed")
        

    def execute(self, print_output=False):
        """
        Description:
            Executes the commands sequentially, while waiting delay seconds between commands.
            commands are taken from file(s) specified in either cmd_file or cmd_files in the configuration file config.txt.
            delay is defined in the configuration file config.txt (for each node), and defaults to 0 if not defined.
        Paramaters:
            - print_output determines whether or not to print command output on the screen. the default is not to print.
        """
        for cmd in self.commands:
            rcv = None
            if self.blocking:
                rcv = send_receive_cmd_blocking(self.channel, cmd, prompts=self.jumpbox["prompts"], print_output=print_output)
            else:
                rcv = send_receive_cmd(self.channel, cmd, self.cmd_timeout, print_output=print_output)
            self.log_fp.write(rcv)
            sleep(self.delay)
                
        self.log_fp.close()


    def get_channel(self):
        """
        Description:
            Returns the node's channel
        Returns:
            channel
        """
        return self.channel


    def reset_channel(self):
        """
        Description:
            Reset the channel (which might be the same as channelstack) using the stored transport.
        """
        self.channel = self.transport.open_session()
        self.channel.get_pty()
        self.channel.invoke_shell()
        


def boxjumper(jumpboxes, count, fp=None, channelstack=None, print_output=False, blocking=True):
    """
    Description:
        boxjumper recursively logs into the boxes/nodes defined in jumpboxes.
        And optionally executes the commands for the current node if it's defined.
    Parameters:
        - jumpboxes list of jumpbox objects.
        - count number of jumpboxes.
        - fp boxjumper's log file pointer.
        - channelstack optional channel created by the previous node (if there was a previous node).
        - print_output determines whether or not to print command output on the screen.
        - blocking determines whether to block and wait for a command to finish executing.
    Returns:
        fp boxjumper's log file pointer. (the file itself is named boxjumper.log)
    """
    if len(jumpboxes):
        cmdlogf = None
        cmd = None
        currentnode = None
        if jumpboxes[0].get("node"):
            if fp == None:
                fp = open("boxjumper.log", mode="w", encoding="utf-8")
            if jumpboxes[0].get("cmd_file"):
                if not jumpboxes[0].get("log_file"):
                    timestr = strftime("%d-%m-%Y_%H%M%S", localtime())
                    cmdlogf = "_".join([jumpboxes[0].get("node"), timestr + ".txt"])
                else:
                    cmdlogf = jumpboxes[0].get("log_file")
            if jumpboxes[0].get("jump_cmd").lower() == "ssh":
                if not jumpboxes[0].get("username"):
                    jumpboxes[0]["username"] = input(f"Enter username for {jumpboxes[0]['node']}: ")
                if not jumpboxes[0].get("password"):
                    jumpboxes[0]["password"] = getpass.getpass(f"Enter password for {jumpboxes[0]['node']}: ")
            
            currentnode = jumpboxes[0]["node"]
            fp.write(f"Accessing {currentnode}\n")
            cmd = CmdRunner(jumpboxes[0], node=currentnode, cmd_file=jumpboxes[0].get("cmd_file"), log_file=cmdlogf, blocking=blocking)
            cmd.jump(channelstack)
            
            jumpboxes.pop()

            fp = boxjumper(jumpboxes, len(jumpboxes), fp=fp, channelstack=cmd.get_channel(), print_output=print_output, blocking=blocking)
        else:
            main(jumpboxes, channelstack, print_output=print_output, blocking=blocking)

        if cmdlogf:
            fp.write(f"Executing commands on {currentnode}\n")
            if count > 1:
                cmd.reset_channel()
            cmd.execute(print_output)

        if cmd and cmd.ssh:
            cmd.ssh.close()

        if currentnode:
            fp.write(f"Leaving {currentnode}\n")

    return fp



##if __name__ == "__main__":
##    parser = ap.ArgumentParser(prog="p_cmd_runr.py", description="general purpose command runner", \
##                               epilog="""*** NO RESPONSIBILITY OR LIABILITY DISCLAIMER ***
##IN NO EVENT SHALL THE AUTHOR BE LIABLE TO YOU OR ANY THIRD PARTIES FOR ANY SPECIAL, 
##PUNITIVE, INCIDENTAL, INDIRECT OR CONSEQUENTIAL DAMAGES OF ANY KIND, 
##OR ANY DAMAGES WHATSOEVER, INCLUDING, WITHOUT LIMITATION, 
##THOSE RESULTING FROM LOSS OF USE, LOST DATA OR PROFITS, OR ANY LIABILITY, 
##ARISING OUT OF OR IN CONNECTION WITH THE USE OF THIS SCRIPT.""")
##    parser.add_argument("-d", "--dry_run", help="display loaded configuration, but do not execute", action="store_true")
##    parser.add_argument("-t", "--timeout", help="sets command execution to non-blocking. default is blocking", action="store_true")
##    parser.add_argument("-p", "--print_output", action="store_true", help="flag to print command output to the screen. default is not to print")
##    parser.add_argument("-c", "--config", help="configuration file. default is config.txt")
##    args = parser.parse_args()
##    if args.config:
##        print(f"\nusing configuration file {args.config}")
##        cgo = ConfigGrabber(args.config)
##    else:
##        cgo = ConfigGrabber()        
##    
##    if not args.dry_run:
##        fp = boxjumper(cgo, len(cgo), print_output=args.print_output, blocking= not args.timeout)
##        if fp:
##            fp.close()
##    else:
##        print(f"print output is {args.print_output}")
##        print(f"blocking is {not args.timeout}\n")
##        print(cgo)
