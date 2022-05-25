import sys
import os
from TIME import *
from time import sleep as wait
from traceback import format_exc
from copy import deepcopy
class Editor():
    "CMD Text Editor Program With Pure Native Python"
    if __name__=="__main__": # checks if programed called from CMD
        called=False
    else: #If called from different File
        called=True    
    first_time=True    
    def __init__(self,*args)-> None:
        self.window=properties()
        self.program_name=getForegroundWindowTitle()
        self.window.Length-=1 # grabs line for title
        if self.called:
            sys.argv=["pykernel.py"]
            sys.argv.extend(args)
        #if not self.called: # collect parameters if ran from cmd
        self.args=sys.argv
        self.name:str
        self.word_count=False
        if len(self.args)==1: # No Filename Given
            self.text=""
            self.argument,self.name="Untitled","Untitled"
            self.args.append("Untitled")
            self.named=False
        else: # filename given
            self.named=True
            self.argument=" ".join(self.args[1:]) # removes pykernel.py from arguments and rejoins them
            self.name=self.args[1]
            if os.path.isfile(self.name):
                with open(self.name,"r") as File:
                    self.text=File.read()
            else: # file doesn't exist
                while True:
                    if "n+" in self.args:
                        with open(self.name,"w+") as _:
                            self.text=""
                        break    
                    from glob import glob
                    print("No File Has That Name")
                    choices=[]
                    for remove in range(len(self.name)):
                        choices=glob(self.name+"*")
                        if len(choices)>2:
                            print("Here Are Similar Named Files:")
                            for item in choices:
                                print("-"+item)
                            exit()    
                        self.name=self.name[:-1] 
                    print("There Are No Files with A Similar Name") 
                    exit()             
        self.lines=self.text.split("\n")
        self.para=[] 
        self.a=[]
        t=[]
        for line in self.lines:
            t.append(line.replace("\x00"," "))
        self.lines=t.copy()
        while self.lines[-1].replace(" ","")=="" and len(self.lines)>1: # removes Enter at end of File
            del self.lines[-1]  
        for line in self.lines:
            t=list(line)
            self.para.append(t)
            self.a.append(t) 
        if len(self.para)<self.window.Length:
            self.para.extend([[] for _ in range(self.window.Length-len(self.para))])
        ###start 1
        self.info=self.argument[:self.window.Width-2]
        self.snap_shot_order=["a","para","pointer","postulnar","highlight","highlighting"]
        if self.first_time:
            self.first_time=False
            self.exit,self.number=False,0
            self.postulnar,self.pointer=[0,0],[0,0]
            self.saved=True
            self.saves=("*"," ")
            self.highlighting=False
            self.highlight=[None,None]
            self.saver=False
            self.snap_shot=[]
            self.preffrences(mode="check")
            self.debugging=0
            self.snap_shot_index=-1
            self.snap()# create copy of important variables
            self.snap_shot_index=0
    def loop(self):
        lock()
        while not self.exit:
            self.output=1
            self.string=self.info+self.saves[self.saved]
            self.string+=" "*(self.window.Width-len(self.string))
            self.key=0
            self.remove=""
            self.num=0
            self.i=1
            self.index=[]
            w=self.window.Width
            self.delete_highlight=False
            if self.number: # numbers lines #postulnar[1]+1 becuase list start at 0 and we see that as 1
                l=len(str(self.postulnar[1]+1+self.window.Length)) #Length of biggest number displayed on screen
                w-=l+1 # fake width is subtracted by that length
                self.width_diffrence=l
                n=self.postulnar[1]+1 # set n to be the lowest number displayed on screen  
            for line_index in range(self.postulnar[1],self.postulnar[1]+self.window.Length):
                if self.number:
                    nn=str(n)        
                    self.string+="\u001b[38;5;245m"+"0"*(l-len(nn))+nn+"\u001b[0m"+" "
                    n+=1    
                for char_index in range(self.postulnar[0],self.postulnar[0]+w): # w is width minus buffer for numbers
                    highlighted=False
                    if self.highlighting and self.between(char_index,line_index):
                        self.string+="\u001b[44m"
                        highlighted=True
                    try:
                        ###need to add Highlighting code
                        if self.pointer!=[char_index,line_index]:
                            self.string+=self.para[line_index][char_index]
                        else: # pointer on char postion
                            #self.para[line_index]+=" "
                            #remove=line_index
                            self.string+="\u001b[48;5;239m"+self.para[line_index][char_index]+"\u001b[0m"                                   
                    except IndexError: # no value left to grab on line
                        left=w-char_index+self.postulnar[0]
                        if self.pointer[1]==line_index and self.pointer[0]>char_index-1: # pointer past values on line
                            self.string+=" "*(self.pointer[0]-char_index)+"\u001b[48;5;239m \u001b[0m"+" "*(left-(self.pointer[0]-char_index)-1)
                        else: # normal case
                            self.string+=" "*left
                        if highlighted:
                            self.string+="\u001b[0m"    
                        break   
                    if highlighted:
                        self.string+="\u001b[0m"    
            if self.word_count:
                count=0
                for line in self.para:
                    count+=len(list(filter(None, "".join(line).split(" "))))
                tmp=str(count)
                self.string+="Word Count:"+tmp+" "*(w-len(tmp)-11)     
            self.string+="\u001b[0m"   
            print("\r\x1b[1;1H"+self.string,end="",flush=1)     
            ###start 2
            try:
                key=self.get_key()
            except KeyboardInterrupt:
                key=[0,3]    
            if key[0]: # mouse event
                cmd_cords=list(queryMousePosition())
                if self.number:
                    if cmd_cords[0]>-1: # in cmd
                        cmd_cords[0]-=self.width_diffrence
                        if cmd_cords[0]<0: # mouse on numbers
                            cmd_cords[0]+=2
                cmd_cords[0]-=1
                cmd_cords[1]-=1
                if cmd_cords[0]>-1 and cmd_cords[1]>-1: # if cusor in CMD
                    new_pos=[self.postulnar[0]+cmd_cords[0],self.postulnar[1]+cmd_cords[1]] # don't tuplize
                    #if [self.postulnar[0]+self.pointer[0],self.postulnar[1]+self.pointer[1]]!=new_pos:
                    self.pointer=new_pos.copy()
                if self.highlight==[None,None]:
                    self.highlight=[self.pointer[:],None]
                elif self.highlight[0]!=self.pointer: # pointer in differnt postion
                    self.highlight[1]=self.pointer[:]
                    self.highlighting=True          
            else:
                key=key[1]
                if self.highlighting:
                    self.delete_highlight=True
                #input(key) #debug point
                if key not in [-1, 0, 1, 2, 3, 4, 5, 6, 8, 9, 10, 12, 13, 14, 15, 16, 18, 19, 20, 22, 23, 24, 25, 26, 127, 146, 224]: # keyboard input is a normal key
                    self.saved=False
                    if len(self.para[self.pointer[1]])>=self.pointer[0]:#new character in between values
                        self.para[self.pointer[1]].insert(self.pointer[0],chr(key))
                    else: 
                        self.para[self.pointer[1]].extend([" "]*(self.pointer[0]-len(self.para[self.pointer[1]])))
                        self.para[self.pointer[1]].append(chr(key))
                    self.pointer[0]+=1    
                else:
                    ###start of Key Functions
                    ### start of multi Input Fucntions
                    
                    if not key: # key==0 # ^Alt * which has the funcs help,highlight,shift tab, copy, cut,pate,begining/end of file, word count, find
                        end=event()[1] # gets second key
                        #input(end)
                        while True:
                            self.delete_highlight=False
                            if end == 19: # ^ Alt r run file with command
                                os.system(input("command:"))
                                input("Go Back To Code")
                                break
                            if end == 31: # ^ Alt s toggle auto saver
                                self.saver=not self.saver
                                break
                            if end == 25: # ^ Alt p edit preffrences file
                                self.preffrences(mode="edit")
                                break
                            if end == 49: # ^ Alt n new file
                                self.new()
                                break
                            if end == 45: # ^ Alt x Run
                                self.run()
                                input("\nGo Back To Code")
                                break                              
                            if end == 148: # ^ Shift Tab
                                self.shift_tab()
                                break  
                            if end in (53,35): # ^ Alt h and ^?
                                self.help()
                                break
                            self.delete_highlight=True
                            if end == 46: # ^ Alt c spell check
                                self.word_check()
                                break                            
                            break
                    else:
                        while True:   
                            self.delete_highlight=False
                            if key == 1:# ^ a Highlight all
                                self.highlighting=not self.highlighting
                                if self.highlighting:
                                    index=-1
                                    try:
                                        while self.para[index]==[]:
                                            index-=1
                                    except IndexError:
                                        index+=1    
                                    self.highlight=[[len(self.para[index]),len(self.para)+index],[0,0]]
                                    self.pointer=[0,0]
                                else:
                                    self.delete_highlight=True
                                break
                            if key == 3: # ^ c copy
                                if self.highlighting:
                                    self.highlight_copy()
                                else:
                                    self.quit()    
                                break
                            if key == 22: # ^ v paste
                                self.paste()
                                break
                            if key == 12: # ^ l reload
                                self.__init__()
                                break
                            if key == 15: # ^ o open file
                                self.open()
                                break
                            if key == 4: # ^ d deltes file
                                answer=input("Are You Sure You Want To Delete This File File [y/n]:").lower()
                                if answer in ("y","yes"):
                                    os.remove(self.name)
                                    unlock()
                                    raise SystemExit("Delted File")
                            if key == 23: # ^ w toggles word count
                                self.word_count=not self.word_count
                                self.window.Length+=[1,-1][self.word_count]
                                break
                            if key == 14: # ^ n number
                                self.number=not self.number          
                                break
                            if key == 224: # arrow keys and more
                                self.arrow_keys()
                                break
                            if key == 19: # ^ s save file
                                self.save()
                                break
                            if key == 5: # ^ e exit
                                self.quit()
                            if key == 18: # ^r rename
                                old_name=self.name
                                self.new()
                                os.remove(old_name)
                                break
                            if key == 25: # ^y redo
                                self.redo()
                                break
                            if key == 26: # ^z undo
                                self.undo()
                                break
                            if key == 9: # tab
                                if self.highlighting:
                                    self.highlight_tab()
                                else:    
                                    self.para[self.pointer[1]]=self.para[self.pointer[1]][:self.pointer[0]]+([" "]*3)+self.para[self.pointer[1]][self.pointer[0]:]
                                    self.pointer[0]+=3
                                break 
                            self.delete_highlight=True
                            if key == 6: # ^ f find
                                self.find()
                                break                                
                            if key == 8: # Backspace
                                if self.highlighting:
                                    self.highlight_delete()
                                self.backspace()
                                break
                            if key == 13: # Enter
                                self.enter()
                                break                              
                            if key == 16: # ^p print file
                                self.print()
                                break
                            if key == 21: # ^ u # compiles code before you run it
                                self.run(compile_=True)
                                input("\nGo Back To Code")
                                break   
                            if key == 24: # ^ x cut
                                self.highlight_copy()
                                self.highlight_delete()
                                break       
                            if key == 127: # ^ backspace delete all
                                self.para,self.saved=[[]],False
                                break   
                            if key == 20: # ^t go to line n
                                self.goto()
                                break                                                                         
                            break   
            self.update() 
    def shift_tab(self):
        if self.highlighting:
            try:
                a,b=self.highlight_sort()
            except LookupError:
                return None  
            for line_index in range(a[1],b[1]+1):
                for _ in range(3):
                    try:
                        if self.para[line_index][0]==" ":
                            del self.para[line_index][0]
                        else:
                            break
                    except IndexError:
                        break    
            return None  
        at_end=not self.pointer[0]                              
        for _ in range(3):
            try:
                if self.para[self.pointer[1]][0]==" ":
                    del self.para[self.pointer[1]][0]
            except IndexError:
                if at_end:
                    self.pointer[0]=-1 #update changes it to move up to the next line
                    return None   
            finally:
                self.pointer[0]-=1        
        if self.pointer[0]<0:
            self.pointer[0]=0

    def highlight_tab(self):
        try:
            a,b=self.highlight_sort()
        except LookupError:
            return None  
        self.para[a[1]]=self.para[a[1]][:a[0]]+([" "]*3)+self.para[a[1]][a[0]:]
        if a[1]!=b[1]:
            for index in range(a[1]+1,b[1]+1):
                self.para[index]=([" "]*3)+self.para[index]
        self.pointer[0]+=3
        self.highlight[0][0]+=3
        self.highlight[1][0]+=3
    def highlight_copy(self):
        try:
            a,b=self.highlight_sort()
        except LookupError:
            return None  
        text:str
        if a[1]==b[1]:
            text="".join(self.para[a[1]][a[0]:b[0]+1])
        else:
            text="".join(self.para[a[1]][a[0]:]).rstrip()+"\n"
            text+="\n".join(["".join(line).rstrip() for line in self.para[a[1]+1:b[1]-1]])+"\n"
            try:
                text+="".join(self.para[b[1]][:b[0]+1]).rstrip()
            except IndexError:
                text=text[:-1]    
        paste(text)
    def highlight_sort(self):
        if self.highlighting:
            a,b=self.highlight[0][:],self.highlight[1][:]
            if (a[1]==b[1] and a[0]>b[0]) or a[1]>b[1]: # swaps a and b if a is after b
                c=b[:]
                b=a[:]
                a=c[:]  
            return a,b    
        else:
            unlock()
            raise LookupError("Not In Highlighting Mode")                    
    def highlight_delete(self):
        if self.highlight[0]!=None and self.highlight[1]!=None:
            self.saved=False
            try:
                a,b=self.highlight_sort()
            except LookupError:
                return None  
            if a[1]==b[1]:
                try:
                    del self.para[a[1]][a[0]:b[0]]
                    self.pointer[0]-=b[0]-a[0]
                except IndexError:
                    del self.para[a[1]][a[0]:]
                    self.pointer[0]=a[0]
            else:
                del self.para[a[1]][a[0]:]
                del self.para[a[1]+1:b[1]]
                try:
                    self.para[a[1]].extend(self.para[a[1]+1][b[0]+1:])
                    del self.para[a[1]+1]
                except IndexError:
                    pass    
                
                self.pointer=a[:]
        else:
            self.highlight=[None,None]
        self.highlighting=False    
    def get_key(self)->tuple:
        if self.highlight[0]==None:
            key=event()
            while not self.on_program():
                key=event()   
        else:
            highlighting=True
            while True:
                if self.on_program():
                    if  not mouse_down():
                        highlighting=False
                    key=read_stream()
                    if key[0]:
                        key=key[1:]
                        if (key[0] or self.highlight[1]==None  ) and not highlighting:
                            self.highlighting=False
                            self.highlight=[None,None]
                        break    
        return key
    def between(self,right:int,lower:int)->bool:
        try:
            a,b=self.highlight_sort()
        except LookupError:
            return None  
        if lower>a[1] and lower<b[1]:
            return True    
        if lower==a[1] and right>=a[0] and (a[1]!=b[1] or right<=b[0]):
            return True
        if lower==b[1] and right<=b[0] and (a[1]!=b[1] or right>=a[0]):
            return True             
        return False     

    def preffrences(self,mode:str="edit"):
        if mode=="edit":
            preffrences={"Auto-Save":False,"Number Lines":False,"Word Count":False}          
            print("Type the numbers of the feature automaticalily Ex:1;2;3:")
            n=list(range(1,len(preffrences)+1))
            [print(str(n.pop(0))+"."+preffrence) for preffrence in preffrences]
            response="\n"+"\n"+input("Preffrences:")
            print("What Files do you want these preffrences for seperate files by ; , * indicates for all files, ex. a.txt;b.txt")
            files=input("Files:").split(";")
            top()
            for file_ in files:
                file_=file_.strip()
                response+="\n"+file_
            previous=""
            if os.path.isfile("preffrences.pref"):
                with open("preffrences.pref","r") as file:
                    previous=file.read()
            with open("preffrences.pref","w+") as file:     
              file.write(response+previous)
        if os.path.isfile("preffrences.pref"):
            with open("preffrences.pref","r") as file:
                pref=file.read()
            chunks=pref.split("\n\n")
            for chunk in chunks:
                lines=chunk.split("\n")
                file_included=False
                if lines[-1]=="*": # all files included in the preffrence option
                    file_included=True
                else: # checks if file include for these preffrences
                    for line in lines[1:]:
                        if self.name==line: # check if file in the files for this preffrences
                            file_included=True
                            break            
                if file_included:# file in the preffrence group
                    args=lines[0].split(";") 
                    execute={"1":"self.saver=1","2":"self.number=True","3":"self.word_count=True;self.window.Length-=1"}
                    for arg in args:
                        exec(execute.get(arg,"pass"))  
    def on_program(self)->bool:
        if getForegroundWindowTitle()==self.program_name:
            return True
        return False    
    def goto(self):
        result=input("To Line:")
        if result in ("end","last","inf"):
            self.pointer[1]=len(self.para)
        else:            
            self.pointer[1]=int(result)-1
            self.postulnar[1]=self.pointer[1]                   
    def quit(self):
        if not self.saved:
            answer = input("Work Is Unsaved Do You Want To Save Your Work [y/n]:").lower()         
            if answer in ("y","yes"):
                self.save()      
        unlock()                      
        raise SystemExit("\nUser Exited Program")                    
    def print(self):
        self.save()
        with open(self.name,"r") as file:
            contents=file.read()
        done = False
        change=input("Do You Want To Change The Printing Settings [y/n]:").lower()
        while not done:
            if change in ("y","yes"):
                print("ln:a;b(print lines a throught b auto:1;-1),mc:(auto 0; max amount of chars on line),fmt:(auto:n; options n(normal) 0(none),spc:spacing number,ext:1(to exit from printing);Format input is cascading")
                args=input("Format:").lower()
                commands= args.split(",")
                exit_=False
                for command in commands:
                    while True:
                        func=command.split(":")
                        name=func[0]
                        if name=="ln":
                            values=func[1].split(";")
                            a,b=int(values[0]),int(values[1])
                            if b<0:
                                b+=1 
                            a-=1
                            b-=1    
                            contents="\n".join(contents.split("\n")[a:b])
                            break
                        if name=="mc":
                            max=int(func[1])
                            if max:
                                lines=contents.split("\n")
                                string=""                                    
                                length=0                                  
                                for line in lines:
                                    word=""  
                                    for char in line:
                                        if  length>=max:
                                            string+="\n"
                                            length=0
                                        if char==" " :
                                            string+=word+" "
                                            word=""
                                        else:
                                            word+=char  
                                        length+=1 
                                    else:
                                        string+=word+"\n"

                                contents=string       
                            break
                        if name=="spc":
                            contents=contents.replace("\n","\n"*int(func[1]))
                            break
                        if name=="fmt":
                            name=func[1]
                            if name=='n':
                                a=contents.split(".\n")
                                string=""
                                for chunk in a:
                                    if "\n" in chunk:
                                        string+="\n"+chunk+". "
                                    else:
                                        string+=chunk+". "
                                contents=string
                            break
                        if name=="ext":
                            exit_=True
                            break
                        break
            else:# dont want to change printing settings
                a=contents.split(".\n")
                string=""
                for chunk in a:
                    if "\n" in chunk:
                        string+="\n"+chunk+". "
                    else:
                        string+=chunk+". "
                contents=string[1:]#remove first /n    
            if change=="n":
                exit_=False
            if exit_:  
                break      
            with open("preview.txt","w+") as file:                                        
             file.write(contents)    
            a="start cmd /c python pykernel.py preview.txt" 
            os.system(a) 
            done_=input("Are You Happy With The Format of The File [y/n]:").lower()
            if done_ in ("y","yes"):
                break 
            change="y"  # changes format if you were happy with the pervious formatting of the file
        if not exit_:      
            os.startfile("preview.txt", "print")  
            wait(1)     
    def run(self,compile_=False):
        if self.saver:
            self.save()
        code=""
        for line in self.para:
            code+="".join(line)+"\n"
        code=code[:-1]
        if compile_:
            try:
                code=compile(code,self.name,"exec")
            except (Exception,SystemError,KeyboardInterrupt) as e:
                print(format_exc())        
                return None          
        try:
            exec(code)
        except (Exception,SystemError,KeyboardInterrupt) as e:
            print(format_exc())  
    def grab_snap_shot(self):
        snap_shot=self.snap_shot[self.snap_shot_index]
        for i in range(len(self.snap_shot_order)):
            name=self.snap_shot_order[i]
            self.__setattr__(name,deepcopy(snap_shot[i]))
    def snap(self):
        snap_shot=[]
        for i in range(len(self.snap_shot_order)):
            name=self.snap_shot_order[i]
            value=self.__getattribute__(name)
            snap_shot.append(value)
        snap_shot.append(self.debugging)
        self.debugging+=1    
        self.snap_shot.insert(self.snap_shot_index+1,deepcopy(snap_shot))    
    def undo(self):
        self.snap_shot_index-=1
        if self.snap_shot_index<0:
            self.snap_shot_index=0
        self.grab_snap_shot()
        self.saved=True
    def redo(self):
        self.snap_shot_index+=1
        if self.snap_shot_index>len(self.snap_shot)-1:
           self.snap_shot_index=len(self.snap_shot)-1
        self.grab_snap_shot()
        self.saved=True
    def update(self):
        if len(self.para)<self.window.Length: #document has less lines than view
            self.para.extend([[] for _ in range(self.window.Length-len(self.para))])   
        if self.postulnar[1]>=len(self.para)-self.window.Length:# view past document
            self.postulnar[1]=len(self.para)-self.window.Length
        if self.postulnar[1]>self.pointer[1]-4: # view out of document -4 for better view of document not need 
            #print(-2)
            if self.postulnar[1]>3: # so you cannot get negtive values
                self.postulnar[1]=self.pointer[1]-4
            else:
                self.postulnar[1]=0      
        if self.pointer[1] >= len(self.para)-1: #self.pointer past document
            #print(-1)
            self.pointer[1] = len(self.para)-1 #self.pointer above document
        if self.pointer[0] < 0:
            #print(0)
            self.pointer = [len(self.para[self.pointer[1]-1])-1, self.pointer[1]-1]
        if self.pointer[1] < 0:
            #print("1")
            self.pointer,self.postulnar = [0, 0],[0,0]
        if self.pointer[1] >= len(self.para)-1: # self.pointer past document
            #print("3")
            self.pointer[1] = len(self.para)-1    
        if self.pointer[0] > self.window.Width+self.postulnar[0]-4: # self.pointer out of view
            #print(4)
            self.postulnar[0] +=self.pointer[0]-(self.window.Width+self.postulnar[0]-4)
        if self.pointer[1] > self.window.Length+self.postulnar[1]-4:
            #print(5)
            self.postulnar[1] += self.pointer[1]-(self.window.Length+self.postulnar[1])+4
        if self.postulnar[0] > self.pointer[0]-3:# self.pointer right of view
            #print(6)
            if self.postulnar[0]>3:
                self.postulnar[0] -=self.postulnar[0]-self.pointer[0]+3
            else:
                self.postulnar[0]=0    
    
        if self.postulnar[0] < 0:
            #print(7)
            self.postulnar[0] = 0
            if(len(self.para[self.pointer[1]-1])) < 1:
                self.pointer = [0, self.pointer[1]-1]
        if self.postulnar[1]+self.window.Length>len(self.para): # view encapesale line after the documet
            self.postulnar[1]=len(self.para)-self.window.Length    
        if self.postulnar[1]<0:
            self.postulnar[1]=0            
        if self.highlighting:
            self.highlight[1]=self.pointer[:]     
        elif self.highlight[1]!=None:
            self.highlight=[None,None]  
        if self.delete_highlight:
            self.highlight_delete()  
        if self.saver and not self.saved:
            self.save(auto_call=True)                                 
    def enter(self):
        self.saved=False
        if self.para[self.pointer[1]][self.pointer[0]:] != [" "]*len(self.para[self.pointer[1]][self.pointer[0]:]): # not at end of nonwhitespace in this line
            self.para[self.pointer[1]+1:self.pointer[1]+1]=[self.para[self.pointer[1]][self.pointer[0]:]]  # insert rest of line into next line throught insertation doesn't join the next and old line
        else: # cusor at end of line
            self.para[self.pointer[1]+1:self.pointer[1]+1]=[[]]# insert blank into para
        self.para[self.pointer[1]]=self.para[self.pointer[1]][:self.pointer[0]]
        self.para[self.pointer[1]+1][0:0]=[" "]*(len(self.para[self.pointer[1]])-len("".join(self.para[self.pointer[1]])))    
        index=0
        for char in self.para[self.pointer[1]]:
            if char!=" ":
                break
            index+=1
        self.pointer[1]+=1
        self.pointer[0]=index  
    def backspace(self):
        if self.pointer != [0,0]: # if cusor isn't at the very top right of document
            self.saved=False
            self.pointer[0]-=1
            try:
                if self.pointer[0] == -1: # backspaced last character on that line
                    self.pointer[0]=len(self.para[self.pointer[1]-1])
                    self.para[self.pointer[1]-1].extend(self.para[self.pointer[1]]) # add rest of previous line to new line
                    del self.para[self.pointer[1]]
                    self.pointer[1]-=1
                else: # normal case
                    del self.para[self.pointer[1]][self.pointer[0]]
            except IndexError:
                pass                                            
    def arrow_keys(self):
        end=event()[1]
        #input(end)
        highlight_keys={119: [-1, 0], 134: [0, -1], 118: [0, 1], 117: [1, 0]}
        keys = {75: [-1, 0], 72: [0, -1], 80: [0, 1], 77: [1, 0]} # left up down right
        key_=keys.get(end,[0, 0])
        self.pointer = [self.pointer[i]+key_[i] for i in range(2)] 
        while True:
            if end in [119,134,118,117]:
                if self.highlighting:
                    self.highlight[1]=[self.highlight[1][i]+highlight_keys[end][i] for i in range(2)]
                else:
                    self.highlight=[self.pointer[:],[self.pointer[i]+highlight_keys[end][i] for i in range(2)]]  
                self.pointer=self.highlight[1][:]      
                self.highlighting=True
                break    
            self.highlight=[None,None]
            self.highlighting=False
            if end == 115: # ^ <- to the word before this word or beging of this word
                line=self.para[self.pointer[1]]
                end=self.pointer[0]
                start=end
                for char in reversed(line[:end]): #go to the next nonspace character after space
                    if char==" ":
                        break
                    end-=1
                if start==end: #last character of word
                    if self.pointer[0]>0: # cusor isn't on the first character on the line
                        self.pointer[0]-=1 # makes pointer move on to whites
                        end=self.pointer[0]
                        for char in reversed(line[:end]): # goes to first nonwhite space character of line
                            end-=1
                            if char!=" ": # same logic
                                break
                self.pointer[0]=end
                break
            if end == 116: # ^ -> to next word
                line=self.para[self.pointer[1]]
                end=self.pointer[0]
                start=end
                for char in line[end:]: # moves forward in line till whitespace detected
                    if char==" ":
                        break
                    end+=1
                end-=1      
                if start==end or start==(end+1): # last char on word
                    last_word=len(line)-1 
                    for char in reversed(line): # find last word's index on line
                        if char!=" ":
                            break
                        last_word-=1   
                    if self.pointer[0]>last_word: # cusor not on last word
                        end=last_word
                    elif self.pointer[0]<last_word:
                        end+=1
                        for char in line[end:]:
                            if char!=" ":
                                break
                            end+=1   
                self.pointer[0]=end
                break    
            if end == 79: # Fn -> End Of Line
                line=self.para[self.pointer[1]]
                last_word=len(line)
                for char in reversed(line):
                    if char!=" ":
                        break
                    last_word-=1
                if (last_word==0 or last_word==self.pointer[0]): # already at end of nonwhite space characters
                    last_word=len(self.para[self.pointer[1]])-1
                self.pointer[0]=last_word
            if end == 71: # Fn <- Start of Line
                index=0
                for char in self.para[self.pointer[1]]:
                    if char!=" ":
                        break
                    index+=1
                if index == self.pointer[0]: # if cusor already on last nonwhite character of the line
                    index=0
                self.pointer[0]=index
                break
            if end == 81: # Fn (down arrow) page down
                self.pointer[1]+=self.window.Length
                break
            if end == 73: # Fn (up arrow) page up
                self.pointer[1]-=self.window.Length
                break
            if end == 83: # Delete
               self.pointer[0]+=2
               self.backspace()
               break
            break    
    def open(self):
        file_name=input("File Name:")
        del self.args[1:]
        self.args.extend(file_name.split(" "))
        tmp="start cmd /c python "+" ".join(self.args)
        os.system(tmp)
    def help(self):
        with open("editor_help.txt","r") as help_file:
            with open("help.txt","w+") as tmp_file:
                tmp_file.write(help_file.read())
        os.system("start cmd /c python pykernel.py help.txt")
    def paste(self):
        data=get_clipboard()
        text=data.replace("\r","").split("\n")
        text[-1]+="".join(self.para[self.pointer[1]][self.pointer[0]:])
        del self.para[self.pointer[1]][self.pointer[0]:]
        self.para[self.pointer[1]].extend(list(text[0]))
        for line in text[1:]: 
            self.pointer[0]=0
            self.pointer[1]+=1
            self.para.insert(self.pointer[1],list(line))
        self.pointer[0]+=len(text[-1])
        self.saved=False
    def save(self,auto_call:bool=False):
        self.saved=True
        tmp=""
        para=deepcopy(self.para)
        try:
            while para[-1]==[]:
                del para[-1]
        except IndexError:
            para=[]    
        for line in para:
            tmp+="".join(line)+"\n"
        try:
            with open(self.name,"w+") as file:
                file.write(tmp)
        except PermissionError:
            wait(.1)
            self.save(auto_call)        
        if not auto_call or auto_call:
            self.snap_shot_index+=1
            del self.snap_shot[self.snap_shot_index:]
            self.snap()
            string=""
            for i in self.snap_shot:
                string+=str(i[-1])+" "
    def new(self):
        if not self.saved:
            answer=input("Your Work Has Not Been Saved Do You Want To Save It [y/n]:").lower()
            if answer in ("y","yes"):
                self.save()
        argument=input("New File Name:")
        if os.path.isfile(argument):
            answer=input("File Name Already Exist Do You Want To Replace The File [y/n]:").lower()
            if answer not in ("y","yes"):   
                return None
        self.name=argument
        self.args[1]=argument
        self.argument=argument
        self.info=self.argument[:self.window.Width-2]
        self.save() # writes old file to new file                    
    def find(self):
        find=input("Find:").replace("\\n","\n")
        tmp=[]
        for line in self.para:
            tmp.append("".join(line))
        test="\n".join(tmp)
        replac=input("Replace With:").replace("\\n","\n")
        answer = input("Do You Want To Replace All Occurrences [y/n]:").lower()                       
        if answer in ("y","yes"):
            test=test.replace(find,replac)
        else:
            amount=test.count(find)
            find_=(find+chr(15)) # add invisible flag
            nth={0:"st",1:"nd",2:"rd"}
            for num in range(amount):
                n=str(num+1)
                n+=nth.get(num,"nth")
                answer = input("Do You Want To Replace "+n+" Occurrences [y/n]:").lower()
                if answer in ["y", "yes"]:
                    test=test.replace(find,replac,1)
                else:
                    test=test.replace(find,find_,1) 
            test=test.replace(find_,find)        
        b=[]
        for line in test.split("\n"):
            b.append(list(line))
        self.para=b.copy()
    def word_check(self,rerunning=False):   
        import re
        from difflib import get_close_matches as closest        
        if not os.path.isfile("words.txt"):   
            os.system("curl -OL https://raw.githubusercontent.com/dwyl/english-words/master/words.txt") 
        if not os.path.isfile("words.txt"):               
            return None
        with open("words.txt","r") as file:
            _words=file.read().lower()
        words=_words.split("\n")       
        hash={'':False}
        for word in words:
            hash[word.lower()]=False
        tmp=[]
        for line in self.para:
            tmp.append("".join(line))
        files_text="\n ".join(tmp)
        phrases=re.sub(r"[^a-zA-Z ]",'',files_text)
        phrases=phrases.split(" ")  
        orginal=files_text.replace("\n","").split(" ")
        fake_words={}
        n=0
        for word in phrases:
            word=re.sub("[^0-9a-zA-z]","",word)
            if hash.get(word.lower(),True): # only happens when word not in hash
                fake_words[orginal[n]]=word
            n+=1
        if not rerunning:    
            remove_opitions=input("Do You Want To Remove Opitions From Dictonary [y/n]:").lower()   
            if remove_opitions in ("y","yes"): 
                with open("words.txt","r") as file:
                    new_file=file.read().lower()+"\n"
                while True:
                    remove_word=input("Remove:")
                    remove=re.sub(r"[^a-zA-Z ]",'',remove_word).lower()+"\n"
                    if remove in new_file:
                        new_file=new_file.replace(remove,"")
                        print('"'+remove_word+'" Removed From Dictonary')
                    else:
                        print('There Is No "'+remove_word+'" In Dictonary')
                    remove_another=input("Do You Want To Remove An Another Word [y/n]:").lower()
                    if remove_another not in ("y","yes"):
                        break 
                with open("words.txt","w") as file:
                    file.write(new_file)
                self.word_check(rerunning=True) # rerun program with new dictonary 
        if len(fake_words)==0: # no incorrectily spelt words
            input("No Incorrectily Spelt Words")                      
        for fake in fake_words:
            real_word=fake
            fake=fake_words[fake].lower() # grabs gammar corrected word look at last loop
            sub_words=[]        
            tmp=[]
            add=real_word.split(fake_words[real_word]) # get gammar and non-alphabetical chars before the word same as fake yet doesn't .lower it
            a=add[0]
            if len(add)>1:
                b=add[-1]
            else:
                b=""
            sub_words=[]    
            while len(sub_words)<10:
                tmp=re.findall(r"\b"+fake+"\w+",_words)  
                for opition in tmp:
                    if opition not in sub_words:
                        sub_words.append(opition)
                fake=fake[:-1]  
            try:
                choices=closest(real_word.lower(),sub_words,len(sub_words))
            except ValueError:
                print("Error with spell check for word:",fake,sep="")     
            old={}
            for choice in choices:
                if not old.get(choice,False):
                    old[choice]=True
            choices=list(old.keys())   
            if real_word.isupper():
                for i in range(len(choices)):
                    choices[i]=a+choices[i].upper()+b
            elif real_word[0].islower():
                for i in range(len(choices)):
                    choices[i]=a+choices[i].lower()+b
            if len(choices)>3:
                choices_=choices[:3]
            else: 
                choices_=choices
            done=False # vars for the loop
            view_all=False
            while not done:
                clear()
                top()
                opitons=["Possible Incorrectly Spelled Word:"+real_word,"0. Do Not Change Word"]
                number=1
                a=""
                for change in choices_:
                    if change !=a: # option is new
                        opitons.append(str(number)+". Change "+real_word+" to: "+change)
                        number+=1
                        a=change
                    else:
                        break
                if not view_all:
                    opitons.append(str(number)+". To See Full List")
                else:
                    opitons.append(str(number)+". To See The Best Matches")
                number+=1
                opitons.append(str(number)+". to Input Your Own Word(s)")
                number+=1
                opitons.append(str(number)+". To Add Word(s) To Dictonary ")          
                number+=1            
                opitons.append(str(number)+". To Exit Spell Checking Menu")
                while True:
                    for line in opitons:
                        print(line)
                    try:
                        descion=int(input("Choice:"))
                        if descion>-1 and descion<=number:
                            break
                        else:
                            print("Please Type In Integer From 0 To",number)
                    except ValueError:
                        print("Please Type In Integer")    
                while True:
                    if descion==0: # don't change word
                        done=True
                        break
                    if descion<=number-4:
                        files_text=files_text.replace(real_word,choices[descion-1])      
                        done=True
                        break
                    if descion==number-3:#See best or all of the word list
                        if not view_all:
                            choices_=sorted(choices)  
                            view_all=True
                        else:
                            choices_=choices[:3]
                        break       
                    if descion==number-2:
                        files_text=files_text.replace(real_word,input("Replaced Incorrectly Spelled Word With:"))
                        done=True
                        break
                    if descion==number-1: # add word to dictonary
                        with open("words.txt","a") as file:
                            file.write("\n"+fake_words[real_word].lower())     
                        hash[fake_words[real_word].lower()]=False
                        done=True                                       
                        break
                    if descion==number:
                        return None 
        tmp=files_text.split("\n ")
        char=[]
        for line in tmp:
            char.append(list(line))
        self.para=char.copy()                                        
if __name__=="__main__":
    program=Editor() 
    try:
        program.loop()
    except KeyboardInterrupt:
        program.quit()