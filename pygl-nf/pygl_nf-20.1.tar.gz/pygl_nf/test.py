import GL
from pygl_nf.GL import Text_

win = GL.Display_init_([1000,750])


particle_1 = GL.Particles.Point(win,[400,400],[0,-0.6],['c','yellow',15],1,2,10,1,True,0.6,400)
particle_2 = GL.Particles.Point(win,[400,400],[0,-0.3],['c','orange',12],1,1,10,5,True,0.4,200)
particle_3 = GL.Particles.Point(win,[400,400],[0,-0.3],['c','red',7],1,1,10,5,True,0.3,200)

def p_1():
    particle_1.Set_position(GL.Open_mouse.GET_POSITION())
    particle_1.Emiter()
    particle_1.Focus()
    particle_1.Lifeter()
    particle_1.PCount([5,5])
    particle_1.Render()
    particle_1.Xclean()

def p_2():
    particle_2.Set_position(GL.Open_mouse.GET_POSITION())
    particle_2.Emiter()
    particle_2.Focus()
    particle_2.Lifeter()
    particle_2.PCount([5,20])
    particle_2.Render()
    particle_2.Xclean()

def p_3():
    particle_3.Set_position(GL.Open_mouse.GET_POSITION())
    particle_3.Emiter()
    particle_3.Focus()
    particle_3.Lifeter()
    particle_3.PCount([5,35])
    particle_3.Render()
    particle_3.Xclean()


while win.CEUF(FPS=60):
    GL.Text_(str(win.GET_FPS()),True,'black','arial',20,[5,50],SURF=win.screen).RENDER()
    p_1()
    p_2()
    p_3()
