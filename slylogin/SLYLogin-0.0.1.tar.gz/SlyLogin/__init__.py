def login(username, password, accountsFile):
    loggedIn = False
    for line in open(accountsFile, "r").readlines:
        login_info = line.split()
        if username == login_info[0] and password == login_info[1]:
            loggedIn = True
            return loggedIn
    loggedIn = False
    return loggedIn