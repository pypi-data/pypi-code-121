import random

def start_game():
    credit = input('Please insert amount: ')
    risk = input('Please insert risk: ')

    if credit.isnumeric() == True and risk.isnumeric() == True:
        credit = float(credit)
        risk = int(risk)
        is_valid = True
    else:
        print('Not valid input!')
        is_valid = False

    if is_valid == True:
        choosed_number = random.randint(1, risk)
        user_number = int(input('Please insert number to guess: '))

        if choosed_number == user_number:
            print('You Win!!!')
            credit = credit * risk
            print(f'Your credit is: {credit}$')
        else:
            print('You Lose!!!')
            credit = credit - (1 / risk) * credit
            print(f'Your credit is: {round(credit, 2)}$')
        
        print(f'The number was: {choosed_number}')
