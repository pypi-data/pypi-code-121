from os import system
def vgratient(text,start,end):
    system(""); rgb = ""
    red = start[0]
    green = start[1]
    blue = start[2]
    redLast=end[0]
    greenLast=end[1]
    blueLast=end[2]
    lines=len(text.splitlines())
    redD=int((redLast-red)/lines)
    greenD=int((greenLast-green)/lines)
    blueD=int((blueLast-blue)/lines)
    for line in text.splitlines():
        rgb += (f"\033[38;2;{red};{green};{blue}m{line}\033[0m"+'\n')
        red = red + redD
        green=green+greenD
        blue=blue+blueD
    return rgb