from tkinter import filedialog, messagebox

def openFileAll():
    return filedialog.askopenfilename()

def selectPath():
    return filedialog.askdirectory()
    
def ShowAlert(titleMsg, contentMsg):
    return messagebox.showwarning(title=titleMsg, message=contentMsg)