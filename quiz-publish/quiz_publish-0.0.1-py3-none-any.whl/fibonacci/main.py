while True:
    try:
        n = int(input("Enter the range:"))
        i = 0
        a = 0
        b = 1
    except ValueError:
        print("Enter Number")
    else:
        while (i < n):
            if (i <= 1):
                c = i
            else:
                c = a + b
                a = b
                b = c
            print(c)
            i = i + 1