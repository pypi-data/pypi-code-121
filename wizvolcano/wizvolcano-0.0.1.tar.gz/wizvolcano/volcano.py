class Wizvolcano:
    ''' 
    คลาส Wizvolcano คือ
    ข้อมูลที่เกี่ยวข้องกับ VC

    Example
    # ----------------
    vc = Wizvolcano()
    vc.show_name()
    vc.about()
    vc.show_art()
    # ----------------
    '''
    def __init__(self):
        self.name = 'Wizvolcano'
        self.Github = 'https://github.com/Wizvolcano/'

    def show_name(self):
        print('สวัสดีฉันชื่อ {}'.format(self.name))

    def about(self):
        text = ''' 
        ----------------------------
        Test Wizvolcano oVolcAnOo VC
        ----------------------------
        '''
        print(text)

    def show_art(self):
        text = '''
                      ___..............._
             __.. ' _'.""""""\\""""""""- .`-._
 ______.-'         (_) |      \\           ` \\`-. _
/_       --------------'-------\\---....______\\__`.`  -..___
| T      _.----._           Xxx|x...           |          _.._`--. _
| |    .' ..--.. `.         XXX|XXXXXXXXXxx==  |       .'.---..`.     -._
\_j   /  /  __  \  \        XXX|XXXXXXXXXXX==  |      / /  __  \ \        `-.
 _|  |  |  /  \  |  |       XXX|""'            |     / |  /  \  | |          |
|__\_j  |  \__/  |  L__________|_______________|_____j |  \__/  | L__________J
     `'\ \      / ./__________________________________\ \      / /___________\
        `.`----'.'   dp                                `.`----'.'
          `""""'                                         `""""'
        
        '''
        print(text)

if __name__ == '__main__':
    vc = Wizvolcano()
    vc.show_name()
    vc.about()
    vc.show_art()
        