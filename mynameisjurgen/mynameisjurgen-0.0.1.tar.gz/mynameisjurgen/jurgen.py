class Jurgen:
    """
    คลาส Jurgen คือ
    ข้อมูลที่เกี่ยวข้องกับ Jurgen Klopp
    ประกอบด้วยประวัติ
    ชื่อช่อง Youtube
    """

    def __init__(self):
        self.name = 'Jurgen Klopp'
        self.page = 'https://en.wikipedia.org/wiki/Jürgen_Klopp'

    def my_name_is(self):
        print(f'Hello my name is {self.name}')

    def show_youtube(self):
        print('https://www.youtube.com/watch?v=_26-ypaNOc4')

    def about(self):
        text = """
        Jürgen Norbert Klopp ( born 16 June 1967) is a German professional football manager 
        and former player who is the manager of Premier League club Liverpool. 
        He is widely regarded as one of the best managers in the world."""
        print(text)

    def show_page(self):
        print(f'This is my {self.page}')

    def show_art(self):
        text = """
                Football (Soccer)
                _...----.._
            ,:':::::.     `>.
        ,' |:::::;'     |:::.
        /    `'::'       :::::\
        /         _____     `::;\
        :         /:::::\      `  :
        | ,.     /::SSt::\        |
        |;:::.   `::::::;'        |
        ::::::     `::;'      ,.  ;
        \:::'              ,::::/
        \                 \:::/
        `.     ,:.        :;'
            `-.::::::..  _.''
                ```----'''
        """
        print(text)
    

if __name__ == '__main__':
    kloop = Jurgen()
    kloop.my_name_is()
    kloop.show_youtube()   
    kloop.about()
    kloop.show_art()