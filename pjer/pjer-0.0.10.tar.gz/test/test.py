import pjer
import handydandy

model=[
    1,1,1,0,
    0,0,1,1,
    1,1,1,1,
    1,0,1,0,
]

pjer.sprite(model,10).draw(0,0,10)
handydandy.userinput.quitpause('not end')