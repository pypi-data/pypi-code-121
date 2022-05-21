import random

def login(username, password, accountsFile):
    loggedIn = False
    for line in open(accountsFile, "r").readlines():
        login_info = line.split()
        if username == login_info[0] and password == login_info[1]:
            loggedIn = True
            return loggedIn
    loggedIn = False
    return loggedIn

def register(username, password, accountsFile):
    file = open(accountsFile, "a")
    file.write(username)
    file.write(" ")
    file.write(password)
    file.write("\n")
    print("Registered!")

def genPassword(length, characters, digits, symbols):
    random.shuffle(characters)
    random.shuffle(digits)
    random.shuffle(symbols)
    if length < 5:
        print("ERROR! Password length must be 5 or higher")
        return
    length -= 2
    password = []
    for i in range(length):
        password.append(random.choice(characters))
    password.append(random.choice(symbols))
    password.append(random.choice(digits))
    random.shuffle(password)
    return password

def viewAccounts(loggedIn, accountsFile):
    if loggedIn == False:
        print("ERROR! Must be logged in to view accounts!")
    else:
        with open(accountsFile) as f:
            contents = f.read()
            return contents
