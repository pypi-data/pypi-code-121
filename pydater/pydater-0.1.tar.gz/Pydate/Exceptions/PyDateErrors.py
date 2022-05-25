class PathIsEmpty(Exception):
    " Yol Belirtilmediyse Hata Verir "
    def __init__(self,*args: object) -> None:
        super().__init__("Dosya Yolu Bulunamadı")

class LogicError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__("Mantıksal bir hata")