import os
import ctypes
import msvcrt
from typing import Optional
from ctypes import wintypes, windll, create_unicode_buffer
def getForegroundWindowTitle() -> Optional[str]:
    hWnd = windll.user32.GetForegroundWindow()
    length = windll.user32.GetWindowTextLengthW(hWnd)
    buf = create_unicode_buffer(length + 1)
    windll.user32.GetWindowTextW(hWnd, buf, length + 1)
    
    # 1-liner alternative: return buf.value if buf.value else None
    if buf.value:
        return buf.value
    else:
        return None
kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
device = r'\\.\CONIN$'
def lock():
    with open(device, 'r') as con:
        hCon = msvcrt.get_osfhandle(con.fileno())
        kernel32.SetConsoleMode(hCon, 0x0080) 
def unlock():   
    with open(device, 'r') as con:
        hCon = msvcrt.get_osfhandle(con.fileno())
        kernel32.SetConsoleMode(hCon, 0x0040) 
PRINT=print
EXIT=exit
def exit():
    unlock()
    EXIT()
def print(*w,**k)-> None:
    if msvcrt.kbhit():
        if msvcrt.getch() ==b"\x03": #exits program if ^C was entered
            raise KeyboardInterrupt
    "Display text in Termnial lines=0 tells how far up or down to print message"
    line_value=0
    file=False
    if "file" in k:
        filename=k["file"]
        file=True
        del k["file"]
    if "lines" in k:
        line_value=int(k["lines"])
        del k["lines"]
    if line_value==0:
        PRINT(*w,**k) 
        return None
    if line_value>0:
        PRINT("\r\x1b["+str(line_value)+"A"+" "*(__info__.Width*line_value),end="")  
        String=""
        for item in w:
            String+=str(item)+" "  
        PRINT("\r\x1b["+str(line_value-1)+"A"+String,**k) 
    if line_value<0:
        PRINT("\r\x1b["+str(line_value)+"B"+" "*(__info__.Width*line_value),end="")  
        String=""
        for item in w:
            String+=str(item)+" "  
        PRINT("\r\x1b["+str(line_value-1)+"B"+String,**k)    
    if file:
        with open(filename,"w+") as file:
            file.write(String)              
os.system("color") # sets up class and stuff don't mess with
user32 = ctypes.windll.user32
handle=user32.GetForegroundWindow()
rect = wintypes.RECT()
class WINDOWINFO(ctypes.Structure):
    """ctype Structure for WINDOWINFO"""
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("rcWindow", wintypes.RECT),
        ("rcClient", wintypes.RECT),
        ("dwStyle", wintypes.DWORD),
        ("dwExStyle", wintypes.DWORD),
        ("dwWindowStatus", wintypes.DWORD),
        ("cxWindowBorders", wintypes.UINT),
        ("cyWindowBorders", wintypes.UINT),
        ("atomWindowType", wintypes.ATOM),
        ("wCreatorVersion", wintypes.DWORD),
    ]
class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
class properties:
    def __init__(self) -> None:
        user32 = ctypes.WinDLL('user32')
        self.info=WINDOWINFO()
        self.Length = os.get_terminal_size().lines
        self.Width = os.get_terminal_size().columns
        ctypes.windll.user32.GetWindowInfo(handle, ctypes.pointer(self.info)) 
        self.CmdLeft,self.CmdTop,self.CmdRight,self.CmdBottom=self.info.rcClient.left,self.info.rcClient.top,self.info.rcClient.right,self.info.rcClient.bottom
        self.CmdLength=self.CmdRight-self.CmdLeft
        self.CmdHeight=self.CmdBottom-self.CmdTop
        self.FontHeight=self.CmdHeight/self.Length
        self.FontWidth=self.CmdLength/self.Width
        self.pt=POINT()
OpenClipboard = user32.OpenClipboard
OpenClipboard.argtypes = wintypes.HWND,
OpenClipboard.restype = wintypes.BOOL
CloseClipboard = user32.CloseClipboard
CloseClipboard.restype = wintypes.BOOL
EmptyClipboard = user32.EmptyClipboard
EmptyClipboard.restype = wintypes.BOOL
GetClipboardData = user32.GetClipboardData
GetClipboardData.argtypes = wintypes.UINT,
GetClipboardData.restype = wintypes.HANDLE
SetClipboardData = user32.SetClipboardData
SetClipboardData.argtypes = (wintypes.UINT, wintypes.HANDLE)
SetClipboardData.restype = wintypes.HANDLE
GlobalLock = kernel32.GlobalLock
GlobalLock.argtypes = wintypes.HGLOBAL,
GlobalLock.restype = wintypes.LPVOID
GlobalUnlock = kernel32.GlobalUnlock
GlobalUnlock.argtypes = wintypes.HGLOBAL,
GlobalUnlock.restype = wintypes.BOOL
GlobalAlloc = kernel32.GlobalAlloc
GlobalAlloc.argtypes = (wintypes.UINT, ctypes.c_size_t)
GlobalAlloc.restype = wintypes.HGLOBAL
GlobalSize = kernel32.GlobalSize
GlobalSize.argtypes = wintypes.HGLOBAL,
GlobalSize.restype = ctypes.c_size_t
CF_UNICODETEXT=13
GMEM_MOVEABLE = 0x0002
GMEM_ZEROINIT = 0x0040
__info__=properties()  
def cusor_pos()->tuple[int,int]:
    "returns (x,y) of terminal's cusor postistion"
    print("\x1b[6n",end="",flush=True) # move up then gets the postion which fills the keyboard input buffer 
    pos=""
    while msvcrt.kbhit():
        pos+=chr(ord(msvcrt.getch()))
    pos=pos.replace("\x1b[","").replace("R","").split(";")  
    return int(pos[0]), int(pos[1])     
def clear() -> None:
    "flushes terminal to be clear"
    os.system("cls")
def queryMousePosition(terminal_mode:bool=True)-> tuple:
    "get mouse postition if terminal_mode is true returns in Terminal pixels if it returns (-1,-1) this means the click was out of the cmd window  else returns in acutal pixels"
    ctypes.windll.user32.GetCursorPos(ctypes.byref(__info__.pt))
    x,y=__info__.pt.x,__info__.pt.y
    if not terminal_mode:
        return (x,y)
    y-=__info__.CmdTop
    y/=round(__info__.FontHeight-.5)
    y=round(y)
    x=round((x-__info__.CmdLeft)/__info__.FontWidth)
    if x<0 or y<0 or x>=__info__.Width or y>=__info__.Length:
        x,y=-1,-1   
    return(x,y)        
def event(display_raw:bool=False) -> tuple:
    "returns a tuple->(mouse clicked:bool=0,key clicked:int=0)"
    while 1:
        if ctypes.windll.user32.GetKeyState(0x01)>1: #checks if mouse is down
            return (1,0) 
        if msvcrt.kbhit(): #checks if key is down 
            getch=msvcrt.getch()
            if display_raw:
                print(getch)  
            if getch==b'\x03':
                raise KeyboardInterrupt    
            return (0,ord(getch))     
def paste(s):
    data = s.encode('utf-16le')
    OpenClipboard(None)
    EmptyClipboard()
    handle = GlobalAlloc(GMEM_MOVEABLE | GMEM_ZEROINIT, len(data) + 2)
    pcontents = GlobalLock(handle)
    ctypes.memmove(pcontents, data, len(data))
    GlobalUnlock(handle)
    #print(CF_UNICODETEXT)
    SetClipboardData(CF_UNICODETEXT, handle)
    CloseClipboard() 
def read_stream():
    if ctypes.windll.user32.GetKeyState(0x01)>1: #checks if mouse is down
        return (1,1,0) 
    if msvcrt.kbhit(): #checks if key is down 
        getch=msvcrt.getch()
        if getch==b'\x03':
            raise KeyboardInterrupt    
        return (1,0,ord(getch))     
    return (0,0,0)                               
def ask(message="",end_key:str='\r',end:str="\n") -> str:
    "display the message in the terminal and records keys pressed until end_key is pressed then returns response"
    message=str(message)   
    last_bit=message.split("\n")[-1]
    query=len(last_bit)%__info__.Width
    last_bit=last_bit[-1*query:]
    print(str(message),end="",flush=True)
    end_code=ord(end_key) #converts End_key str to ascii char value
    response=""
    remove=0 #bool
    while 1:
        key=event()
        if not key[0]: # only executes if not a mouse event AKA if a key was pressed
            key=key[1] # sets key to be the ascii char value that was pressed
            if end_code==key:
                break
            char=chr(key)
            if key in (8,224):
                while 1:
                    remove=0
                    if key==8:
                        response=response[:-1]
                        remove=1
                        break
                    if key==224:
                        special=event()
                        break
                    break
            else:        
                response+=char
                remove=0   
            if remove:
                __info__.Width-=1 
                output=last_bit+response
                print("\r"+output[-1*__info__.Width:]+" ",end="")  
                __info__.Width+=1 
            output=last_bit+response
            print("\r"+output[-1*__info__.Width:],end="")      
    print(end=end)        
    return response    
input=ask
def dimensions(string:str,return_parts:bool=False,flag_char:str="")-> int:
    "returns how many lines string will take on console"
    Leng=__info__.Width
    parts=string.split("\n")
    Length=len(parts)
    Parts=[]
    for part in parts:
        count=0
        Parts.append("")
        for char in part:
            if count>Leng:
                Parts.append("")
                count=0
            Parts[-1]+=char
            if char!=flag_char:
                count+=1           
        Length+=len(part.replace(flag_char,""))//Leng
  
    if return_parts:
        return Length,Parts  
    return Length  
def mouse_down()->bool:
    "return bool of if mouse is down or not"
    if ctypes.windll.user32.GetKeyState(0x01)>1: 
        return True
    return False  
def top():
    "Put cusor to the top"
    print("\x1b[1;1H",end="",flush=True)    
def mode(*options,sep:str="\n") ->tuple:
    "Return a tuple (choice's index,choice) after user clicks on it "
    cusor_line=cusor_pos()[0]
    cords=(-2,-2)
    sep+="\x00"
    String=sep.join(options) # to flush terminal and make mouse easier
    Lines,Parts=dimensions(String,True,"\x00")
    Display=""
    for part in Parts:
        Display+=part+" "*(__info__.Width-len(part.replace("\x00",""))%__info__.Width)    
    print(Display,end="",flush=True)
    Length=__info__.Length
    if (cusor_line+Lines)>Length:
        cusor_line=Length-Lines+1  
    go_back=0
    if "\n"  not in sep or len(options)==1:
        go_back=2  
    while 1:
        if msvcrt.kbhit():
            if msvcrt.getch() ==b"\x03": #exits program if ^C was entered
                raise KeyboardInterrupt 
        mouse_off=True     
        if cords!=(-1,-1) and ( (cords[1]<cusor_line+2-go_back) and (cords[1]>(cusor_line+1-Lines-go_back)) ):
            #print(vars())
            if go_back==2:
                current_line=0
            else:    
                current_line=Lines-(cusor_line-cords[1]+2)
            if cords[0]<=len(Parts[current_line].replace("\x00","")):
                text=""
                count=0
                index=0
                line=Parts[current_line]
                section=0
                if current_line: # only happens if cusor on second+ line
                    section=len("".join(Parts[:current_line]).split("\x00"))-1
                while count<cords[0]:
                    char=line[index]
                    text+=char
                    index+=1
                    if char!="\x00":
                        count+=1
                    else:
                        section+=1    
                mouse_off=True           
                print("\r"+"\x1b["+str(Lines-1)+"A"+Display.replace(options[section],"\u001b[48;5;239m"+options[section]+"\u001b[0m"),end="",flush=True)        
                if mouse_down():
                    while mouse_down():
                        pass#print("foo berry",flush=True)              
                    return(section,options[section])
            elif mouse_off:
                mouse_off=0
                print("\r"+"\x1b["+str(Lines-1)+"A"+Display,end="",flush=True)       
        elif mouse_off:      
            mouse_off=0
            print("\r"+"\x1b["+str(Lines-1)+"A"+Display,end="",flush=True)                                    
def get_clipboard():         
    OpenClipboard(None)
    
    handle = GetClipboardData(CF_UNICODETEXT)
    pcontents = GlobalLock(handle)
    size = GlobalSize(handle)
    if pcontents and size:
        raw_data = ctypes.create_string_buffer(size)
        ctypes.memmove(raw_data, pcontents, size)
        text = raw_data.raw.decode('utf-16le')#.rstrip(u'\0')
    else:
        text = None

    GlobalUnlock(handle)
    CloseClipboard()
    return text            