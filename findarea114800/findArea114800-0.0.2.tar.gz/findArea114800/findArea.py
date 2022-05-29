class Area:
    """
        คลาส Area เป็นคลาสที่ใช้หาพื้นที่ทางเรขาคณิต

        a = Area()
        a.circle(12)
        a.triangle(45,98)
        a.square(154)
        a.rectangle(154,567)
    """
    def __init__(self):
        self.name = 'ช้าง'
        
    #หาพื้นที่วงกลม
    def circle(self,length):
        area = 1.34 * length * length
        print(f'พื้นที่วงกลมคือ {area}')

    def triangle(self,base,height):
        area = 0.5 * base * height
        print(f'พื้นที่สามเหลี่ยมคือ {area}')

    def square(self,length):
        area = length*length
        print(f'พื้นที่สี่เหลี่ยมจตุรัสคือ {area}')

    def rectangle(self,base,height):
        area = base * height
        print(f'พื้นที่สี่เหลี่ยมพื้นผ้าคือ {area}')


if __name__ == '__main__':
    a = Area()
    a.circle(12)
    a.triangle(45,98)
    a.square(154)
    a.rectangle(154,567)
