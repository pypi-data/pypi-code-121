def fibonacci_numbers(number):
    if number <= 1:
        return number
    else:
        return fibonacci_numbers(number - 1) + fibonacci_numbers(number - 2)


user_number = int(input("შემოიტანეთ მთელი რიცხვი: "))

if user_number < 0:
    print("შემოიტანეთ დადებითი რიცხვი")
else:
    print("ფიბონაჩის მიმდებრობა: ")
    for i in range(user_number):
        print(fibonacci_numbers(i))
