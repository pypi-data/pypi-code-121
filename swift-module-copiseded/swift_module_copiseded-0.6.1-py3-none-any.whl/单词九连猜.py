import random
from tkinter import Button,HIDDEN,NORMAL,DISABLED,Tk,messagebox
words = ['pizza','fairy','teeth','shirt','otter','plane','sleepy','slow',
         'smelly','wet','fat','red','orange','yellow','green','blue','purple','fluffy',
         'white','pround','brave','apple','dinosaur','ball','toaster','goat','dragon','hammer','duck'
         'panda']
attempt = 0
secret_word = random.choice(words)
wordsf = list(secret_word)
clue = list(len(wordsf) * '?')
present = list('????????????0')
heart_symbol = u'\u2764'
presents = 0
guessed_word_correctly = False
def update_clue(guessed_leter,secret_word,clue):
    index = 0
    while index < len(secret_word):
        if guessed_leter == secret_word[index]:
            clue[index] = guessed_leter
        index = index + 1
def 金币系统(number_1,number_2):
    金币数量 = str(number_1 + number_2)
    金币数列表 = list(金币数)
    return 金币数列表[0]
level = input('please choose game difficulty: \na:easy \nb:normal \nc:hard\n:')
if level == 'a' or level == 'easy':
    lives = 12
elif level == 'b' or level == 'normal':
    lives = 9
else:
    lives = 6
while lives > 0:
    print(clue)
    print('金币数量:',present)
    print('Lives Left:'+ heart_symbol * lives)
    guess = input('Guess a leter or a whole word: ')
    if guess == secret_word:
        guessed_word_correctly = True
        break
    if guess in secret_word:
        update_clue(guess,secret_word,clue)
    else:
        print('Incorrect, you lose a life')
        lives -= 1
    attempt = attempt + 1
if guessed_word_correctly:
	print('you win!')
	if attempt <= 8:
		print('获得金币数：'+ str(attempt * 2 * 10000000))
		print('金币数量:',list(str(attempt * 2 * 10000000)))
	elif attempt > 8:
		print('获得金币数：'+ str(attempt * 4 * 1000000))
		print('金币数量:',list(str(attempt * 4 * 1000000)))
	else:
		print('获得金币数：'+ str(attempt * 8 * 100))
		print('金币数量:',list(str(attempt * 8 * 100)))
else:
    print('you lost')
print('The secret word was',secret_word)
se = input('你要不要用金币试玩更多好玩的作品? no or yes')
if se.lower() == 'yes':
    print('                        金币悬赏\n')
    print('!!!!!!!!!!!!!!!!!!!!!!!!!New!!!!!!!!!!!!!!!!!!!!!!!!!!')
    print('玩玩下面作品吧！')
    print('alien침입하다之4つの言語の会話')
    print('1982년에 당신은 외계인으로서 지구를 침입했지만 지구인들은 당신에게 우호를 표시했습니다.')
    print('\'>>>\'地球人の言うことを表す')
    welcome=input('>>>welcome,Ally Alien,what\'s your name?Can you tell me?I\'m kind!')
    print('>>>Say it again(\"あなたの気持ちが変わったかどうかを再確認するために\")')
    answer=input('>>>What\'s your name?')
    print('>>>Welcome ,'+answer+'， I\'m kind')
    play_answer=input('>>>Can you play with me?Yes or No')
    if play_answer.lower()=='no':
        print('I\'m disappointed')
    elif play_answer.lower()=='yes':
        print('We can get to the supermarket!')
        print('At the supermarket')
    else:
        print('At the supermarket')
        love_age=input('>>>what\'s your age?')
        print('>>>That\'s wonderful, how a great age! '+love_age)
        print('Thank you very much!')
        print('>>>You\'re welcome!')
    answer=input('what are you doing?get along well?time to attack?orスキップしない')
    if answer.lower()=='get along well':
        print('>>>私たちは日本に行って、中国に行って、イギリスに行って......')
    elif answer.lower()=='time to attack':
        print('Boon!数秒後、地球人は悲鳴をあげ、あなたも警察署に送られました(narration)')
    else:
        place=input(['go to the cinema?','go to the beach?','go to the bus stop,go to the garden,see the beautiful lake?'])
        if place.lower()=='go to tne cinema':
            print('>>>go!')
            print('At the cinema')
            print('Look,It\'s a tiger,It\'s jumping at me Ahhhhhhhhhhhh!')
            print('>>>Don\'t be afraid')
        else:
            print('>>>No,I can\'t catch the car')
            Refuse=('see you again')
            for char in Refuse:
                print(Refuse)
                break
else:
    Refuse=('OK,Bye',u'\u2764')
    for char in Refuse:
        print(Refuse)
        break
