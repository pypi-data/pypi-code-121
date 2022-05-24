def join_path(str1, str2):
    if str1[-1] == '/':
        if str2[0] == '/':
            return str1 + str2[1:]
        else:
            return str1 + str2
    else:
        if str2[0] == '/':
            return str1 + str2
        else:
            return str1 + '/' + str2
