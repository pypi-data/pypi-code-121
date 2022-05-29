import requests
import pyquery
import sys
import webbrowser
def help():
    print("""
    Usage: zzzing [COMMAND]
    
    Options:
        help, -h: show this help message and exit
        open, -o: open zzzing.cn in browser (default)
        dyn, -d: show dynamics in zzzing.cn
    """)
def open_zzzing():
    webbrowser.open("https://zzzing.cn")

def dyn():
    r = requests.get("https://zzzing.cn/dynamic")
    pq = pyquery.PyQuery(r.text)
    print(pq(".dynamic-content").text())

def main():
    print("zzzing CLI by xuanzhi33")
    print("Type 'zzzing help' for more information.")
    argv = sys.argv
    if len(argv) == 1:
        open_zzzing()
    elif argv[1] == "-h" or argv[1] == "--help":
        help()
    elif argv[1] == "-o" or argv[1] == "--open":
        print("Opening zzzing.cn in your browser...")
        open_zzzing()
    elif argv[1] == "-d" or argv[1] == "--dyn":
        dyn()
    else:
        print("Unknown command:", argv[1])
        help()