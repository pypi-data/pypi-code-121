from cgitb import text


class kninfo:
    """class kninfo is my personal information
        -facebook page
    Example
    #----------

    #----------
    """


    def __init__(self):
     self.name = 'kongdach np'
     self.page ='https://www.disignage.tech'
     self.mywork = 'I am IT'

    def show_name(self):
     print('Hello my name is {}'.format(self.name))

    def about(self):
        text = """
        -----------------------------------------
        สวัสดีครับ ยินดีที่ได้รู้จักผมทำงานด้าน IT ครับ มีความสนใจภาษา python และ IOT 
        จึงได้เรียนกับลุงวิศวกร สอนสนุกและเข้าใจดีครับ
        -----------------------------------------"""
        print(text)

    def show_art(self):
        text =""""
                                                            _            
                                                     (_)           
  _ __ ___  _   _   _ __   __ _ _ __ ___   ___   _ ___        
 | '_ ` _ \| | | | | '_ \ / _` | '_ ` _ \ / _ \ | / __|       
 | | | | | | |_| | | | | | (_| | | | | | |  __/ | \__ \       
 |_| |_| |_|\__, | |_| |_|\__,_|_| |_| |_|\___| |_|___/       
   _         __/ |           _            _                   
  | |       |___/           | |          | |                  
  | | _____  _ __   __ _  __| | __ _  ___| |__    _ __  _ __  
  | |/ / _ \| '_ \ / _` |/ _` |/ _` |/ __| '_ \  | '_ \| '_ \ 
  |   < (_) | | | | (_| | (_| | (_| | (__| | | | | | | | |_) |
  |_|\_\___/|_| |_|\__, |\__,_|\__,_|\___|_| |_| |_| |_| .__/ 
                    __/ |                              | |    
                   |___/                               |_|    
             """
        print(text)

if __name__ == '__main__':
    name = kninfo()
    name.show_name()
    name.about()
    name.show_art()



