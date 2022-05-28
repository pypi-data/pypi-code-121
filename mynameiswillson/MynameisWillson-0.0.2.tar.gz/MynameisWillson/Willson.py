from cgitb import text
from time import sleep


class Willson:
    """
    คลาส sogood คือ
    ข้อมูลที่เกียวข้องกับ Willson

    Example
    #---------------
    so.show_name
    so.about
    so.art
    #---------------
    """
    def __init__(self):
        self.name = 'Willson Good'
        self.Youtube = 'https://www.youtube.com/channel/UCw0DXnAX7kh5j1c3We5ykzg/videos'

    def show_name(self):
        print('Hi my name is {}'.format(self.name))

    def about(self):
        text = """
        -------------------------------------
        Hi i am Willson Good
        My Youtube is "https://www.youtube.com/channel/UCw0DXnAX7kh5j1c3We5ykzg/videos"
        -------------------------------------"""
        print(text)

    def art(self):
        text = """
                    ,---------------------------,
                    |  /---------------------\  |
                    | |                       | |
                    | |     Computer          | |
                    | |      Services         | |
                    | |       Company         | |
                    | |                       | |
                    |  \_____________________/  |
                    |___________________________|
                    ,---\_____     []     _______/------,
                /         /______________\           /|
                /___________________________________ /  | ___
                |                                   |   |    )
                |  _ _ _                 [-------]  |   |   (
                |  o o o                 [-------]  |  /    _)_
                |__________________________________ |/     /  /
            /-------------------------------------/|      ( )/
        /-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/ /
        /-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/ /
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """
        print(text)

if __name__ == '__main__':
    so = Willson()
    so.show_name()
    so.about()
    so.art()
