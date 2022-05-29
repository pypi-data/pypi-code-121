class Dimon:
    """
        คลาส dimon คือ เป็นข้อมูลที่เกียวข้องกับเกี่ยว dimon
        ประกอบด้วยชื่อเพจ
        ชื่อช่องยูทูป

        Example
        #----------------------------------------------
        user = Dimon()
        user.show_name()
        user.show_youtube()
        user.show_page()
        user.about()
        user.show_art()
        #----------------------------------------------
    """
    def __init__(self):
        self.name = 'ดิมจ้า'
        self.page = 'htpps://www.facebook.com/UncleEngineer'

    def show_name(self):
        print('สวัสดีฉันชื่อ {}'.format(self.name))

    def show_youtube(self):
        print('https://www.youtube.com/UncleEngineer')

    def show_page(self):
        print('FB Page: {}'.format(self.page))

    def about(self):
        text = """
        ---------------------------------------------------------------------------------      
            สวัสดีจ้านี่คือ ดิมอน เป็นผู้ดูแลมิติต่าง ๆ ในโลกของอินเตอร์เน็ต
            สามารถติดตามผลงานเราได้เลย ท่านจะได้รับความรู้ต่าง ๆ
        ---------------------------------------------------------------------------------
        """
        print(text)

    def show_art(self):
        text = """
                           __
                ..=====.. |==|
                ||     || |= |
            _   ||     || |^*| _
            |=| o=,===,=o |__||=|
            |_|  _______)~`)  |_|
                [=======]  ()       
        """

        print(text)

if __name__ == '__main__':
    user = Dimon()
    user.show_name()
    user.show_youtube()
    user.show_page()
    user.about()
    user.show_art()