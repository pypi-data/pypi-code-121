from TeraApp.TeraApp.AppScreen.AppScreen import *

app = TeraApp('TeraApp', 700, 700, 'darkslategray') #500 = x,500(2) = y
app.inputr(210, 300, 'blue', 100, 100)
app.appbar('red',100)
app.txtc('Titledddddddddddddddddddddddd', 240,70, 15, 'blue') #(x = 240), (y = 2), (15 = txt size)
app.txt('df',40,120,30)
app.imgl('https://cdn.discordapp.com/attachments/872450263171100692/976347389340307466/f.png',0,400,250,250)

def fds():
    print("gg")


app.buttonf('save', 210,50, 'green', fds)
app.buttonfri(20,20,'oren.png',fds,80,80, 22)
app.app.exec()
