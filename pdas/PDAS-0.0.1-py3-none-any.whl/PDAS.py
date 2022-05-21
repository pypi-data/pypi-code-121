import os, time, socket, json

try:
    from colorama import Fore, Back, Style
except ImportError or ModuleNotFoundError:
    os.system("pip install colorama")
try:
    with open(os.path.abspath("PDAS.json"), "r") as jsonfile:
        if os.stat(os.path.abspath("PDAS.json")).st_size == 0:
            pass
        else:
            config = json.load(jsonfile)
except FileNotFoundError:
    with open(os.path.abspath("PDAS.json"), "x+") as jsonfile:
        print("Ignore following error; rerun program.")
        json.dump({"doAudit": True, "doPassword": True, "doIPcollection": True, "maxAttempts": "2", "lockTime": "2",
                   "enableLockdown": False, "systemAdmin": "Building System Adminstrator"}, jsonfile)
        config = json.load(jsonfile)


def LD():
    while config['enableLockdown']:
        print(Fore.RED, f"[-][ ]Program Locked. Contact {config['systemAdmin']}[-][ ]")
        time.sleep(1)
        os.system("clear")
        print(Fore.BLUE, f"[ ][-]Program Locked. Contact {config['systemAdmin']}[ ][-]")
        time.sleep(1)
        os.system("clear")
        with open(os.path.abspath("PDAS.json"), "r") as jsonfile:
            con = json.load(jsonfile)
        if con['enableLockdown'] == False:
            break


def Time():
    from datetime import datetime
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    return current_time


class PDAS:
    """Main Class of PDAS. """
    pass
    audit = open("Audit.txt", "a")
    audit.write(f'\n ------NEW RUN @ {Time()} ---- \n ')
    audit.write(
        f"Current Configuration Values: \n > Password Enabled?: {config['doPassword']} \n > IP Collection?: {config['doIPcollection']} \n > Audit Enabled?: {config['doAudit']} \n END CCV \n")
    if config['enableLockdown'] == True:
        audit.write(f"Program Entered LOCKDOWN @ {Time()}.")
        audit.close()
        LD()

    audit.close()

    def __init__(self):

        pass

    class System:
        """Subclass for Security, Logging, Console, Login_Monitoring. """
        pass

        def __init__(self):

            print("Directory: " + str(PDAS.System))

        class Security:
            """Security Class. Handles Passwords and logging."""
            pass

            def timeout(TIMEDELAY=config["lockTime"]):
                """Priority 3 Notifcation: Info -> Okay -> Warning -> Fatal"""
                pass
                try:
                    Warn(f"Security Lock for {int(TIMEDELAY)} Minutes")
                    time.sleep(int(TIMEDELAY) * 60)
                    PDAS.System.Security.Lock()
                except KeyboardInterrupt:
                    pass
                    print("\n")
                    Warn("You cannot do that! Time Restarted.")
                    TimeOUT()

            def Lock(self):
                """Password Protection. Takes password from OS.env under the name "PASSWORD" """
                pass
                try:
                    Password = os.environ["PASSWORD"]
                except:
                    Warn("PASSWORD ENV NOT DECLARED! ABORTING")
                if config['doPassword'] == False or os.getenv('PASSWORD') is None:
                    Info("Password Login Aborted.")
                    return 1
                else:
                    attempts = int(config['maxAttempts'])
                    if attempts < 0:
                        attempts = attempts * -1
                    os.system("clear")
                    Info(f"PASSWORD PROTECTED! \n You have {attempts} attempts to enter a password match.")
                    while attempts != 0:
                        submitted_pass = input("Enter Password: ")
                        if submitted_pass != Password:
                            attempts = attempts - 1
                            Warn(f"Incorrect! You have {attempts} Remaining Attempt(s)")
                        if submitted_pass == Password:
                            os.system("clear")
                            Okay("Access Granted!")
                            break
                    if attempts == 0:
                        PDAS.System.Security.timeout()
                    if attempts > 0:
                        return 1
                        pass

            class Login_Monitoring:
                """Handles Audit for Logins."""
                pass

                def __init__(self):
                    print("Handles Logging \n PDAS.System.Console.Log")

                def collectIP(self):
                    hostname = socket.gethostname()
                    ip_address = socket.gethostbyname(hostname)
                    if config["doIPcollection"] == True:
                        Warn(
                            f"Host with directory: {hostname} has logged on with IP_Address {ip_address} at {Time()}. {hostname} has been sent to password verification. Secure devices now.")
                        condition = Lock()
                        if condition == 1:
                            Okay(f"Device {ip_address} : {hostname} Verified @ {Time()}")
                        else:
                            Info(
                                f"Host with directory: {hostname} has logged on with IP_Address {ip_address} at {Time()}")
                            pass
                    else:
                        Warn(
                            f"Host with directory: {hostname} has logged on with IP_Address {ip_address} at {Time()}. {hostname}")
                        pass

        class Console:
            """Subclass containing the subclass(s): Log."""
            pass

            class Log:
                """Subclass containing logging utility such as Audit and terminal error return functionality. """
                pass

                def __init__(self):
                    print("Handles Logging \n PDAS.System.Console.Log")

                def Warn(arg):
                    """Priority 2 Notifcation: Info -> Okay -> Warning -> Fatal"""
                    pass
                    audit = open("Audit.txt", "a+")
                    print(Fore.RED + f'WARN: {arg}')
                    audit.write(f'WARNING @ {Time()} : {arg} \n')
                    print(Style.RESET_ALL)
                    audit.close()

                def Info(arg):
                    """Priority 4 Notifcation: Info -> Okay -> Warning -> Fatal"""
                    pass
                    audit = open("Audit.txt", "a+")
                    print(Fore.BLUE + f'INFO: {arg}')
                    audit.write(f'INFO @ {Time()} : {arg} \n')
                    print(Style.RESET_ALL)
                    audit.close()

                def OK(arg):
                    """Priority 3 Notifcation: Info -> Okay -> Warning -> Fatal"""
                    pass
                    audit = open("Audit.txt", "a+")
                    print(Fore.GREEN + f'OKAY: {arg}')
                    audit.write(f'OKAY @ {Time()} : {arg} \n')
                    print(Style.RESET_ALL)
                    audit.close()

                def Fatal(arg, boolraise=False):
                    """Priority 1 Notifcation: Info -> Okay -> Warning -> Fatal. \n Allows you to choose to stop the program and log or log and pass."""
                    pass
                    audit = open("Audit.txt", "a+")
                    print(Fore.WHITE + Back.RED + f'FATAL: {arg}')
                    audit.write(f'FATAL ERROR: @ {Time()} : {arg} \n')
                    print(Style.RESET_ALL)
                    if boolraise:
                        audit.write(f'\n Fatal Error Raised')
                        audit.close()
                    else:
                        pass

                def Recall(amount=all):
                    """Returns all the logs in Audit.txt. Amount is currently unused."""
                    pass
                    try:
                        y = open("Audit.txt", "r")
                        Lines = y.readlines()
                        for x in Lines:
                            if "WARNING" in x:
                                print(Fore.RED + Back.WHITE + x.strip())
                            if "FATAL" in x:
                                print(Fore.WHITE + Back.RED + x.strip())
                            if "INFO" in x:
                                print(Fore.BLUE + Back.WHITE + x.strip())
                            if "OKAY" in x:
                                print(Fore.GREEN + Back.WHITE + x.strip())
                        print(Style.RESET_ALL)
                        print(f'There was {len(Lines)} Logs in Audit.')
                        print(Style.RESET_ALL)
                        y.close()
                    except:

                        print("Error")

                def Purge(Force=False):
                    """Purges Audit.txt. Boolean Force allows you to determine if the function asks before purging; or purge without asking. Static and set to false by default."""
                    pass
                    try:
                        if Force != False and Force != True:
                            Warn("Only Accepts True False. Aborting Purge of Audit.")

                        else:
                            if Force:
                                try:
                                    aud = open("Audit.txt", "w+")
                                    aud.write(" ")
                                    aud.close()
                                    Info("Complete")
                                except BaseException as error:
                                    Warn(f"{str(error)}")
                            else:
                                action = input("Are you sure you wish to purge audit? Y/N")
                                if action == "Y":
                                    try:
                                        aud = open("Audit.txt", "w+")
                                        aud.write(" ")
                                        aud.close()
                                        Info("Complete. Reason: User Requested Purge.")
                                    except BaseException as error:
                                        Info("USER TRIED PURGE")
                                        Warn(str(error))
                                if action == "N":
                                    Info("Skipping Audit Purge")
                                if action != "Y" and action != "N":
                                    Warn("Must be Y or N.")


                    except BaseException as error:
                        Warn({str(error)})


## Pre-Declares Shortened
pdas = PDAS.System.Console.Log
Warn = PDAS.System.Console.Log.Warn
Info = PDAS.System.Console.Log.Info
Okay = PDAS.System.Console.Log.OK
Fatal = PDAS.System.Console.Log.Fatal
Recall = PDAS.System.Console.Log.Recall
Purge = PDAS.System.Console.Log.Purge
Lock = PDAS.System.Security.Lock
TimeOUT = PDAS.System.Security.timeout
CollectIP = PDAS.System.Security.Login_Monitoring.collectIP
Lockdown = LD()