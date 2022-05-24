# Created by Yagiz Iskirik ® 2022
import sys
from time import sleep
import string

args = ""
sleepInMS = 40

alphabet = " " + string.ascii_lowercase + string.punctuation

def bruteText(arguments, sleepTime):
    """
    Usage: bruteText("Your text to appear", x) -> x is the time to sleep in milliseconds
    """
    outputText= ""
    for char in arguments:
        outputText += "a"
        for defChar in alphabet:
            outputText = outputText[:-1] + defChar
            if char.lower() == defChar:
                outputText = outputText[:-1] + char
                print(outputText, end='\r')
                break
            print(outputText, end='\r')
            sleep(sleepTime / 1000)
    print("")

if __name__ == "__main__":
    if sys.argv[1] == "-h":
        print("Usage: brutetext -h -> To show this screen")
        print("brutetext This is a test -> Type 'This is a text' in brute force way")
        print(f"brutetext -t x This is a test -> specify x (milliseconds) to sleep between inputs (Default {sleepInMS}ms)")
    elif sys.argv[1] == "-t":
        sleepInMS = int(sys.argv[2])
        for i in range(3, len(sys.argv)):
            args += sys.argv[i] + " "
        args = args[:-1]
        bruteText(args, sleepInMS)
    else:
        for i in range(1, len(sys.argv)):
            args += sys.argv[i] + " "
        args = args[:-1]
        bruteText(args, sleepInMS)
