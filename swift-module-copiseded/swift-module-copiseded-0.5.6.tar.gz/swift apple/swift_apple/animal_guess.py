person=input('What\'s you name?:\n')
print('hello, '+person)

def check_guess(guess,English_answer,Chinese_answer):
    global score
    still_guessing=True
    attempt=0
    while still_guessing and attempt<3:
        if guess.lower()==Chinese_answer.lower() or guess.lower()==English_answer.lower():
            print('Correct answer!')
            score=score+1
            still_guessing = False
        else:
            if attempt<2:
                guess = input('Sorry wrong answer,Try again.')
            attempt = attempt + 1
            
    if attempt == 3:
        print('The correct answer is '+ answer)
        
score=0
print('Guess the animals')
guess1=input('Which animal lives at the north pole?:\n')
check_guess(guess1,'polar bear','北极熊')
guess2=input('Which is the fastest land animal?:\n')
check_guess(guess2,'cheetah','猎豹')
guess3=input('Which is the largest animal?:\n')
check_guess(guess3,'blue whale','蓝鲸')

print('your score is %s .'% (score))
