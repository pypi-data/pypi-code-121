from pygl_nf import GL
from colorama import Fore as FO
import sys
import time
import os

initing = False
def Init():
    global initing

    for i in range(5): 
        os.system('cls')
        print(FO.CYAN+'Prefabs Initing'+FO.RESET,end='')
        print(FO.CYAN+'.'*(i+1)+FO.RESET)
        time.sleep(0.1)
    os.system('cls')

    if os.path.exists('Prefabs'):
        initing = True
        print(FO.GREEN+'''[ Success ]'''+FO.RESET)
        print(FO.GREEN+'Prefabs Init!'+FO.RESET)
    else:
        print(FO.RED+'''[ Error ]'''+FO.RESET)
        print(FO.RED+'Prefabs Not Init!'+FO.RESET)
        print(FO.YELLOW+'Prefab file not found'+FO.RESET)
        print(FO.CYAN+'Download -- https://github.com/dedisvoin/GRPgraph-versions'+FO.RESET)
    
    
    


class Sound(object):
    def __init__(self):
        global initing
        if initing==False:
            print(FO.RED+'''[ Error ]'''+FO.RESET)
            print(FO.RED+'Prefabs Not Init!'+FO.RESET)
            sys.exit()
            
    class Jamps(object):
        def __init__(self):
            self.jamp1 = 'Prefabs\Sounds\Jamps\Jump1.wav'
            self.jamp2 = 'Prefabs\Sounds\Jamps\Jump2.wav'
            self.jamp3 = 'Prefabs\Sounds\Jamps\Jump3.wav'
            self.jamp4 = 'Prefabs\Sounds\Jamps\Jump4.wav'
            self.jamp5 = 'Prefabs\Sounds\Jamps\Jump5.wav'
            self.jamp6 = 'Prefabs\Sounds\Jamps\Jump6.wav'
            self.jamp7 = 'Prefabs\Sounds\Jamps\Jump7.wav'
            self.jamp8 = 'Prefabs\Sounds\Jamps\Jump8.wav'
            self.jamp9 = 'Prefabs\Sounds\Jamps\Jump9.wav'
            self.jamp10 = 'Prefabs\Sounds\Jamps\Jump10.wav'


            self._Jamp_Sounds = [
                self.jamp1,self.jamp2,self.jamp3,self.jamp4,self.jamp5,
                self.jamp6,self.jamp7,self.jamp8,self.jamp9,self.jamp10
            ]

        def GET_SOUND_FOR_NAME(self,Sound_file):
            sound = GL.Sound_mixer_(Sound_file)
            return sound

        def GET_SOUND_FOR_INDEX(self,Index):
            if Index > len(self._Jamp_Sounds):
                print (FO.RED+"Sound index out of range"+FO.RESET)
                sys.exit()
            sound = GL.Sound_mixer_(self._Jamp_Sounds[Index-1])
            return sound

    class Pickaps_and_Coin(object):
        def __init__(self):
            self.pickup1 = 'Prefabs\Sounds\Pickuping\Pickup_Coin1.wav'
            self.pickup2 = 'Prefabs\Sounds\Pickuping\Pickup_Coin2.wav'
            self.pickup3 = 'Prefabs\Sounds\Pickuping\Pickup_Coin3.wav'
            self.pickup4 = 'Prefabs\Sounds\Pickuping\Pickup_Coin4.wav'
            self.pickup5 = 'Prefabs\Sounds\Pickuping\Pickup_Coin5.wav'
            self.pickup6 = 'Prefabs\Sounds\Pickuping\Pickup_Coin6.wav'
            self.pickup7 = 'Prefabs\Sounds\Pickuping\Pickup_Coin7.wav'
            self.pickup8 = 'Prefabs\Sounds\Pickuping\Pickup_Coin8.wav'
            self.pickup9 = 'Prefabs\Sounds\Pickuping\Pickup_Coin9.wav'
            self.pickup10 = 'Prefabs\Sounds\Pickuping\Pickup_Coin10.wav'


            self._Pickup_Sounds = [
                self.pickup1,self.pickup2,self.pickup3,self.pickup4,self.pickup5,
                self.pickup6,self.pickup7,self.pickup8,self.pickup9,self.pickup10
            ]

        def GET_SOUND_FOR_NAME(self,Sound_file):
            sound = GL.Sound_mixer_(Sound_file)
            return sound

        def GET_SOUND_FOR_INDEX(self,Index):
            if Index > len(self._Pickup_Sounds):
                print (FO.RED+"Sound Index out of range"+FO.RESET)
                sys.exit()
            sound = GL.Sound_mixer_(self._Pickup_Sounds[Index-1])
            return sound


    class Laser_and_Shoot(object):
        def __init__(self):
            self.Laser1 = 'Prefabs\Sounds\Laser\Laser_Shoot1.wav'
            self.Laser2 = 'Prefabs\Sounds\Laser\Laser_Shoot2.wav'
            self.Laser3 = 'Prefabs\Sounds\Laser\Laser_Shoot3.wav'
            self.Laser4 = 'Prefabs\Sounds\Laser\Laser_Shoot3.wav'
            self.Laser5 = 'Prefabs\Sounds\Laser\Laser_Shoot3.wav'
            self.Laser6 = 'Prefabs\Sounds\Laser\Laser_Shoot3.wav'
            self.Laser7 = 'Prefabs\Sounds\Laser\Laser_Shoot3.wav'
            self.Laser8 = 'Prefabs\Sounds\Laser\Laser_Shoot3.wav'
            self.Laser9 = 'Prefabs\Sounds\Laser\Laser_Shoot3.wav'
            self.Laser10 = 'Prefabs\Sounds\Laser\Laser_Shoot3.wav'

            self._Laser_Sounds = [
                self.Laser1,self.Laser2,self.Laser3,self.Laser4,self.Laser5,
                self.Laser6,self.Laser7,self.Laser8,self.Laser9,self.Laser10
            ]

        def GET_SOUND_FOR_NAME(self,Sound_file):
            sound = GL.Sound_mixer_(Sound_file)
            return sound

        def GET_SOUND_FOR_INDEX(self,Index):
            if Index > len(self._Laser_Sounds):
                print(FO.RED+'Sound Index out of range'+FO.RESET)
                sys.exit()
            sound = GL.Sound_mixer_(self._Laser_Sounds[Index-1])
            return sound


    class Explosion(object):
        def __init__(self):
            self.explosion1 = 'Prefabs\Sounds\Explosion\Explosion1.wav'
            self.explosion2 = 'Prefabs\Sounds\Explosion\Explosion2.wav'
            self.explosion3 = 'Prefabs\Sounds\Explosion\Explosion3.wav'
            self.explosion4 = 'Prefabs\Sounds\Explosion\Explosion4.wav'
            self.explosion5 = 'Prefabs\Sounds\Explosion\Explosion5.wav'
            self.explosion6 = 'Prefabs\Sounds\Explosion\Explosion6.wav'
            self.explosion7 = 'Prefabs\Sounds\Explosion\Explosion7.wav'
            self.explosion8 = 'Prefabs\Sounds\Explosion\Explosion8.wav'
            self.explosion9 = 'Prefabs\Sounds\Explosion\Explosion9.wav'
            self.explosion10 = 'Prefabs\Sounds\Explosion\Explosion10.wav'
            self.explosion11 = 'Prefabs\Sounds\Explosion\Explosion11.wav'
            self.explosion12 = 'Prefabs\Sounds\Explosion\Explosion12.wav'
            self.explosion13 = 'Prefabs\Sounds\Explosion\Explosion13.wav'
            self.explosion14 = 'Prefabs\Sounds\Explosion\Explosion14.wav'
            self.explosion15 = 'Prefabs\Sounds\Explosion\Explosion15.wav'

            self._Explosion_Sounds = [
                self.explosion1,self.explosion2,self.explosion3,self.explosion4,self.explosion5,
                self.explosion6,self.explosion7,self.explosion8,self.explosion9,self.explosion10,
                self.explosion11,self.explosion12,self.explosion13,self.explosion14,self.explosion15
            ]
            
        def GET_SOUND_FOR_NAME(self,Sound_file):
            sound = GL.Sound_mixer_(Sound_file)
            return sound

        def GET_SOUND_FOR_INDEX(self,Index):
            if Index > len(self._Explosion_Sounds):
                print(FO.RED+'Sound Index out of range'+FO.RESET)
                sys.exit()
            sound = GL.Sound_mixer_(self._Explosion_Sounds[Index-1])
            return sound

        


        