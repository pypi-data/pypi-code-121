i = int(input("რამდენი რიცხვი დავბეჭდოთ?: "))

n1 = 0
n2 = 1
count = 0

if i <= 0:
    print("შეიყვანეთ დადებითი მთელი რიცხვი")
elif i == 1:
    print('ფიბონაჩის მიმდევრობამდე',i,':')
    print(n1)
else:
    print("ფიბონაჩის თანმიმდევრობა")
    while count < i:
        print(n1)
        jami = n1 + n2

        n1 = n2
        n2 = jami
        count += 1