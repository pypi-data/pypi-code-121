import random
def guessGame_1_10_Easy():
    number = random.randint(1,10)
    ettempt = 0
    Round = 3
    while ettempt != 3 and Round == 3:
        guess = input('请输入你的数字:')
        if number == int(guess):
            print('太棒了，你猜对了!')
            Round = Round - 1
        else:
            print('sorry wrong,please guess again')
            if number < int(guess):
                print('you\'s guess are too big')
            else:
                print('you\'s guess are too small')
            ettempt = ettempt + 1
            if ettempt == 3:
                print('sorry wrong,the collect int is: '+str(number))

        
def guessGame_1_100_Easy():
    number = random.randint(1,100)
    ettempt = 0
    Round = 3
    while ettempt != 3 and Round == 3:
        guess = input('请输入你的数字:')
        if number == int(guess):
            print('太棒了，你猜对了!')
            Round = Round - 1
        else:
            print('sorry wrong,please guess again')
            if number < int(guess):
                print('you\'s guess are too big')
            elif ettempt == 3:
                print('sorry wrong,the collect int is: '+str(number))
            else:
                print('you\'s guess are too small')
            ettempt = ettempt + 1
def guessGame_1_1000_Easy():
    number = random.randint(1,1000)

    guess = input('请输入你的数字:')
    ettempt = 0
    Round = 3
    while ettempt != 3 and Round == 3:
        guess = input('请输入你的数字:')
        if number == int(guess):
            print('太棒了，你猜对了!')
            Round = Round - 1
        elif ettempt == 3:
            print('sorry wrong,the collect int is: '+str(number))
        else:
            print('sorry wrong,please guess again')
            if number < int(guess):
                print('you\'s guess are too big')
            else:
                print('you\'s guess are too small')
            ettempt = ettempt + 1
            if ettempt == 3:
                print('sorry wrong,the collect int is: '+str(number))
def guessGame_1_10000_Easy():
    number = random.randint(1,10000)
    ettempt = 0
    Round = 3
    while ettempt != 3 and Round == 3:
        guess = input('请输入你的数字:')
        if number == int(guess):
            print('太棒了，你猜对了!')
            Round = Round - 1
        else:
            print('sorry wrong,please guess again')
            if number < int(guess):
                print('you\'s guess are too big')
            else:
                print('you\'s guess are too small')
            ettempt = ettempt + 1
            if ettempt == 3:
                print('sorry wrong,the collect int is: '+str(number))
def guessGame_1_100000_Easy():
    number = random.randint(1,100000)
    ettempt = 0
    Round = 3
    while ettempt != 3 and Round == 3:
        guess = input('请输入你的数字:')
        if number == int(guess):
            print('太棒了，你猜对了!')
            Round = Round - 1
        else:
            print('sorry wrong,please guess again')
            if number < int(guess):
                print('you\'s guess are too big')
            elif ettempt == 3:
                print('sorry wrong,the collect int is: '+str(number))
            else:
                print('you\'s guess are too small')
            ettempt = ettempt + 1
            if ettempt == 3:
                print('sorry wrong,the collect int is: '+str(number))
def guessGame_1_1000000_Easy():
    number = random.randint(1,1000000)
    ettempt = 0
    Round = 3
    while ettempt != 3 and Round == 3:
        guess = input('请输入你的数字:')
        if number == int(guess):
            print('太棒了，你猜对了!')
            Round = Round - 1
        else:
            print('sorry wrong,please guess again')
            if number < int(guess):
                print('you\'s guess are too big')
            else:
                print('you\'s guess are too small')
            ettempt = ettempt + 1
            if ettempt == 3:
                print('sorry wrong,the collect int is: '+str(number))
def guessGame_1_10000000_Easy():
    number = random.randint(1,10000000)
    ettempt = 0
    Round = 3
    while ettempt != 3 and Round == 3:
        guess = input('请输入你的数字:')
        if number == int(guess):
            print('太棒了，你猜对了!')
            Round = Round - 1
        else:
            print('sorry wrong,please guess again')
            if number < int(guess):
                print('you\'s guess are too big')
            else:
                print('you\'s guess are too small')
            ettempt = ettempt + 1
            if ettempt == 3:
                print('sorry wrong,the collect int is: '+str(number))
def guessGame_1_100000000_Easy():
    number = random.randint(1,100000000)
    ettempt = 0
    Round = 3
    while ettempt != 3 and Round == 3:
        guess = input('请输入你的数字:')
        if number == int(guess):
            print('太棒了，你猜对了!')
            Round = Round - 1
        else:
            print('sorry wrong,please guess again')
            if number < int(guess):
                print('you\'s guess are too big')
            else:
                print('you\'s guess are too small')
            ettempt = ettempt + 1
            if ettempt == 3:
                print('sorry wrong,the collect int is: '+str(number))
def guessGame_1_1000000000_Easy():
    number = random.randint(1,10000000000)
    ettempt = 0
    Round = 3
    while ettempt != 3 and Round == 3:
        guess = input('请输入你的数字:')
        if number == int(guess):
            print('太棒了，你猜对了!')
            Round = Round - 1
        else:
            print('sorry wrong,please guess again')
            if number < int(guess):
                print('you\'s guess are too big')
            else:
                print('you\'s guess are too small')
            ettempt = ettempt + 1
            if ettempt == 3:
                print('sorry wrong,the collect int is: '+str(number))

def guessGame_1_10000000000_Easy():
    number = random.randint(1,10000000000)
    ettempt = 0
    Round = 3
    while ettempt != 3 and Round == 3:
        guess = input('请输入你的数字:')
        if number == int(guess):
            print('太棒了，你猜对了!')
            Round = Round - 1
        else:
            print('sorry wrong,please guess again')
            if number < int(guess):
                print('you\'s guess are too big')
            else:
                print('you\'s guess are too small')
            ettempt = ettempt + 1
            if ettempt == 3:
                print('sorry wrong,the collect int is: '+str(number))

def guessGame_1_100000000000_Easy():
    number = random.randint(1,100000000000)
    ettempt = 0
    Round = 3
    while ettempt != 3 and Round == 3:
        guess = input('请输入你的数字:')
        if number == int(guess):
            print('太棒了，你猜对了!')
            Round = Round - 1
        else:
            print('sorry wrong,please guess again')
            if number < int(guess):
                print('you\'s guess are too big')
            else:
                print('you\'s guess are too small')
            ettempt = ettempt + 1
            if ettempt == 3:
                print('sorry wrong,the collect int is: '+str(number))


def guessGame_1_999999999999_Easy():
    number = random.randint(1,999999999999)
    ettempt = 0
    Round = 3
    while ettempt != 3 and Round == 3:
        guess = input('请输入你的数字:')
        if number == int(guess):
            print('太棒了，你猜对了!')
            Round = Round - 1
        else:
            print('sorry wrong,please guess again')
            if number < int(guess):
                print('you\'s guess are too big')
            else:
                print('you\'s guess are too small')
            ettempt = ettempt + 1
            if ettempt == 3:
                print('sorry wrong,the collect int is: '+str(number))


def guessGame_1_9_Easy():
    number = random.randint(1,9)
    ettempt = 0
    Round = 3
    while ettempt != 3 and Round == 3:
        guess = input('请输入你的数字:')
        if number == int(guess):
            print('太棒了，你猜对了!')
            Round = Round - 1
        else:
            print('sorry wrong,please guess again')
            if number < int(guess):
                print('you\'s guess are too big')
            else:
                print('you\'s guess are too small')
            ettempt = ettempt + 1
            if ettempt == 3:
                print('sorry wrong,the collect int is: '+str(number))


def guessGame_1_99_Easy():
    number = random.randint(1,99)
    ettempt = 0
    Round = 3
    while ettempt != 3 and Round == 3:
        guess = input('请输入你的数字:')
        if number == int(guess):
            print('太棒了，你猜对了!')
            Round = Round - 1
        else:
            print('sorry wrong,please guess again')
            if number < int(guess):
                print('you\'s guess are too big')
            else:
                print('you\'s guess are too small')
            ettempt = ettempt + 1
            if ettempt == 3:
                print('sorry wrong,the collect int is: '+str(number))


def guessGame_1_999_Easy():
    number = random.randint(1,999)
    ettempt = 0
    Round = 3
    while ettempt != 3 and Round == 3:
        guess = input('请输入你的数字:')
        if number == int(guess):
            print('太棒了，你猜对了!')
            Round = Round - 1
        else:
            print('sorry wrong,please guess again')
            if number < int(guess):
                print('you\'s guess are too big')
            else:
                print('you\'s guess are too small')
            ettempt = ettempt + 1
            if ettempt == 3:
                print('sorry wrong,the collect int is: '+str(number))


def guessGame_1_9999_Easy():
    number = random.randint(1,9999)
    ettempt = 0
    Round = 3
    while ettempt != 3 and Round == 3:
        guess = input('请输入你的数字:')
        if number == int(guess):
            print('太棒了，你猜对了!')
            Round = Round - 1
        else:
            print('sorry wrong,please guess again')
            if number < int(guess):
                print('you\'s guess are too big')
            else:
                print('you\'s guess are too small')
            ettempt = ettempt + 1
            if ettempt == 3:
                print('sorry wrong,the collect int is: '+str(number))

def guessGame_1_99999_Easy():
    number = random.randint(1,99999)
    ettempt = 0
    Round = 3
    while ettempt != 3 and Round == 3:
        guess = input('请输入你的数字:')
        if number == int(guess):
            print('太棒了，你猜对了!')
            Round = Round - 1
        else:
            print('sorry wrong,please guess again')
            if number < int(guess):
                print('you\'s guess are too big')
            elif ettempt == 3:
                print('sorry wrong,the collect int is: '+str(number))
            else:
                print('you\'s guess are too small')
            ettempt = ettempt + 1
            if ettempt == 3:
                print('sorry wrong,the collect int is: '+str(number))

def guessGame_1_999999_Easy():
    number = random.randint(1,999999)
    ettempt = 0
    Round = 3
    while ettempt != 3 and Round == 3:
        guess = input('请输入你的数字:')
        if number == int(guess):
            print('太棒了，你猜对了!')
            Round = Round - 1
        else:
            print('sorry wrong,please guess again')
            if number < int(guess):
                print('you\'s guess are too big')
            elif ettempt == 3:
                print('sorry wrong,the collect int is: '+str(number))
            else:
                print('you\'s guess are too small')
            ettempt = ettempt + 1
            if ettempt == 3:
                print('sorry wrong,the collect int is: '+str(number))

def guessGame_1_9999999_Easy():
    number = random.randint(1,9999999)
    ettempt = 0
    Round = 3
    while ettempt != 3 and Round == 3:
        guess = input('请输入你的数字:')
        if number == int(guess):
            print('太棒了，你猜对了!')
            Round = Round - 1
        else:
            print('sorry wrong,please guess again')
            if number < int(guess):
                print('you\'s guess are too big')
            else:
                print('you\'s guess are too small')
            ettempt = ettempt + 1
            if ettempt == 3:
                print('sorry wrong,the collect int is: '+str(number))

def guessGame_1_99999999_Easy():
    number = random.randint(1,99999999)
    ettempt = 0
    Round = 3
    while ettempt != 3 and Round == 3:
        guess = input('请输入你的数字:')
        if number == int(guess):
            print('太棒了，你猜对了!')
            Round = Round - 1
        else:
            print('sorry wrong,please guess again')
            if number < int(guess):
                print('you\'s guess are too big')
            else:
                print('you\'s guess are too small')
            ettempt = ettempt + 1
            if ettempt == 3:
                print('sorry wrong,the collect int is: '+str(number))

def guessGame_1_999999999_Easy():
    number = random.randint(1,999999999)
    ettempt = 0
    Round = 3
    while ettempt != 3 and Round == 3:
        guess = input('请输入你的数字:')
        if number == int(guess):
            print('太棒了，你猜对了!')
            Round = Round - 1
        else:
            print('sorry wrong,please guess again')
            if number < int(guess):
                print('you\'s guess are too big')
            else:
                print('you\'s guess are too small')
            if ettempt == 3:
                print('sorry wrong,the collect int is: '+str(number))


def guessGame_1_9999999999_Easy():
    number = random.randint(1,9999999999)
    ettempt = 0
    Round = 3
    while ettempt != 3 and Round == 3:
        guess = input('请输入你的数字:')
        if number == int(guess):
            print('太棒了，你猜对了!')
            Round = Round - 1
        else:
            print('sorry wrong,please guess again')
            if number < int(guess):
                print('you\'s guess are too big')
            else:
                print('you\'s guess are too small')
            ettempt = ettempt + 1
            if ettempt == 3:
                print('sorry wrong,the collect int is: '+str(number))

def guessGame_1_99999999999_Easy():
    number = random.randint(1,99999999999)
    ettempt = 0
    Round = 3
    while ettempt != 3 and Round == 3:
        guess = input('请输入你的数字:')
        if number == int(guess):
            print('太棒了，你猜对了!')
            Round = Round - 1
        else:
            print('sorry wrong,please guess again')
            if number < int(guess):
                print('you\'s guess are too big')
            else:
                print('you\'s guess are too small')
            ettempt = ettempt + 1
            if ettempt == 3:
                print('sorry wrong,the collect int is: '+str(number))
