from curses.ascii import isdigit


def checkgstnum(str):
    # str = "24aaaaa0000a0a0"
    count = 3
    print(str)
    if(len(str) != 15):
        print("not valid gst number")
# print((str[0], str[1], str[7], str[8], str[9], str[10], str[12], str[14]))
    else:
        for i in (str[0], str[1], str[7], str[8], str[9], str[10], str[12], str[14]):
            if not(i.isdigit()):
                # print("not valid gst 2number")
                count = 0
                break
        for i in (str[2], str[3], str[4], str[5], str[6], str[11], str[13]):
            if not(i.isalpha()):
                # print("not valid gst 3number")
                count = 1
                break
        # else:
        #     print("gst number is valid")
        #     continue
    if count == 0:
        print("gst number is not valid")
    elif count == 1:
        print("gst number is not valid")
    elif count == 3:
        print("gst number is valid")
