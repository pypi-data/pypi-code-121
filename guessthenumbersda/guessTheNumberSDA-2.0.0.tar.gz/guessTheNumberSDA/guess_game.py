import random
from guessTheNumberSDA.data_validations import validate_input

def start_game(credit, risk, user_number):

    choosed_number = random.randint(1, risk)

    if choosed_number == user_number:
        print('You Win!!!')
        credit = credit * risk
        print(f'Your credit is: {credit}$')
    else:
        print('You Lose!!!')
        credit = credit - (1 / risk) * credit
        print(f'Your credit is: {round(credit, 2)}$')
    
    print(f'The number was: {choosed_number}')
    print('---------------------------------------------------------------')
    return credit

# start_game()