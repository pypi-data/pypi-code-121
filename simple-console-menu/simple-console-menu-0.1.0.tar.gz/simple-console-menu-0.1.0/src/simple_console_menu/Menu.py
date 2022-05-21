import math


def SimpleConsoleMenu(menuName,menuItems,inputQuestion,menuSize = 76,autoAddQuit = False,onlyReturnNumber = True, allowedCharacters = '', acceptedQuitCharacters = ''):
    """
    Makes a menu

    parameters:
        menuName               - Required  : name of the menu (Str)
        menuItems              - Required  : menu items, separated with ';' (Str)
        inputQuestion          - Required  : Question input (Str)
        menuSize               - Optional  : Size of the menu (Int)
        autoAddQuit            - Optional  : automatically add a quit option (Bool)
        onlyReturnNumber       - Optional  : only numbers are allowed to return (Bool)
        allowedCharacters      - Optional  : specifier which character(s) are allowed if onlyReturnNumber is False, separated with ';' (str)
        acceptedQuitCharacters - Optional  : specifier which character is allowed if onlyReturnNumber is False for quit (str)

    """
    chooseLoop = True
    menuItemsList = []
    allowedCharactersList = []
    menuItemsList = str(menuItems).split(';')
    if allowedCharacters != '':
        allowedCharactersList = str(allowedCharacters).split(';')
    if autoAddQuit:
        menuItemsList.append('Quit')
    menuNumber = 1
    chooseAmount = 0
    menuNameLength = len(menuName) + 2
    menuNameLength = menuSize - menuNameLength
    menuNameLength /= 2
    if (menuNameLength % 2) == 0:
        #even
        print(int(menuNameLength)*'-',menuName,int(menuNameLength)*'-')
    else:
        #uneven
        menuNameLength1 = math.ceil(menuNameLength)
        menuNameLength2 = int(math.floor(menuNameLength))
        print(int(menuNameLength1)*'-',menuName,int(menuNameLength2)*'-')
    for x in menuItemsList:
        print(f'{menuNumber}. {x}')
        menuNumber += 1
    print(menuSize*'-')
    while chooseLoop:
        choose = input(inputQuestion)
        if onlyReturnNumber:
            if choose.isdigit():
                chooseLoop = False
        else:
            if acceptedQuitCharacters != '':
                if (choose != '' and choose in allowedCharactersList) or choose.isdigit() or choose == acceptedQuitCharacters:
                    chooseLoop = False
            elif(choose != '' and choose in allowedCharactersList) or choose.isdigit():
                chooseLoop = False

        if chooseAmount >= 20 and chooseLoop:
            menuNumber = 1
            if (menuNameLength % 2) == 0:
                #even
                print(int(menuNameLength)*'-',menuName,int(menuNameLength)*'-')
            else:
                #uneven
                menuNameLength1 = math.ceil(menuNameLength)
                menuNameLength2 = int(math.floor(menuNameLength))
                print(int(menuNameLength1)*'-',menuName,int(menuNameLength2)*'-')
            for x in menuItemsList:
                print(f'{menuNumber}. {x}')
                menuNumber += 1
            print(76*'-')
            chooseAmount = 1
        chooseAmount += 1
    if choose.isdigit():
        if int(choose) == menuNumber-1:
            quit()
    elif choose == acceptedQuitCharacters:
        quit()
    # else:
    if onlyReturnNumber:
        return int(choose)
    else:
        if choose.isdigit():
            return int(choose)
        else:
            return choose


def SimpleConsoleMenuBlock(menuName,menuItems,inputQuestion,menuSize = 76,autoAddQuit = False,onlyReturnNumber = True, allowedCharacters = '', acceptedQuitCharacters = ''):
    """
    Makes a menu with a box arround it

    parameters:
        menuName               - Required  : name of the menu (Str)
        menuItems              - Required  : menu items, separated with ';' (Str)
        inputQuestion          - Required  : Question input (Str)
        menuSize               - Optional  : Size of the menu (Int)
        autoAddQuit            - Optional  : automatically add a quit option (Bool)
        onlyReturnNumber       - Optional  : only numbers are allowed to return (Bool)
        allowedCharacters      - Optional  : specifier which character(s) are allowed if onlyReturnNumber is False, separated with ';' (str)
        acceptedQuitCharacters - Optional  : specifier which character is allowed if onlyReturnNumber is False for quit (str)

    """
    chooseLoop = True
    menuItemsList = []
    allowedCharactersList = []
    menuItemsList = str(menuItems).split(';')
    if allowedCharacters != '':
        allowedCharactersList = str(allowedCharacters).split(';')
    if autoAddQuit:
        menuItemsList.append('Quit')
    menuNumber = 1
    chooseAmount = 0
    menuNameLength = len(menuName) + 2
    menuNameLength = menuSize - menuNameLength
    menuNameLength /= 2
    if (menuNameLength % 2) == 0:
        print('╭'+int(menuNameLength-1)*'─',menuName,int(menuNameLength-1)*'─'+'╮')
    else:
        menuNameLength1 = math.ceil(menuNameLength)
        menuNameLength2 = int(math.floor(menuNameLength))
        print('╭'+int(menuNameLength1-1)*'─',menuName,int(menuNameLength2-1)*'─'+'╮')
    for x in menuItemsList:
        menuItemsWithNumbers = str(menuNumber)+'. '+x
        print(f'│{menuItemsWithNumbers}'+((menuSize-2)-len(menuItemsWithNumbers))*' '+'│')
        menuNumber += 1
    print('╰'+(menuSize-2)*'─'+'╯')
    while chooseLoop:
        choose = input(inputQuestion)
        if onlyReturnNumber:
            if choose.isdigit():
                chooseLoop = False
        else:
            if acceptedQuitCharacters != '':
                if (choose != '' and choose in allowedCharactersList) or choose.isdigit() or choose == acceptedQuitCharacters:
                    chooseLoop = False
            elif(choose != '' and choose in allowedCharactersList) or choose.isdigit():
                chooseLoop = False

        if chooseAmount >= 20 and chooseLoop:
            menuNumber = 1
            if (menuNameLength % 2) == 0:
                print(int(menuNameLength)*'-',menuName,int(menuNameLength)*'-')
            else:
                menuNameLength1 = math.ceil(menuNameLength)
                menuNameLength2 = int(math.floor(menuNameLength))
                print(int(menuNameLength1)*'-',menuName,int(menuNameLength2)*'-')
            for x in menuItemsList:
                print(f'{menuNumber}. {x}')
                menuNumber += 1
            print(76*'-')
            chooseAmount = 1
        chooseAmount += 1
    if choose.isdigit():
        if int(choose) == menuNumber-1:
            quit()
    elif choose == acceptedQuitCharacters:
        quit()
    if onlyReturnNumber:
        return int(choose)
    else:
        if choose.isdigit():
            return int(choose)
        else:
            return choose

# print(SimpleConsoleMenuBlock('menuuuuuuuuuuuuu','item1;item2;item3;item4;item5','Number:',20,True,True))

# ╭─────────────╮
# │    lorem    │
# │    ipsum    │
# │    dolor    │
# ╰─────────────╯
# print(SimpleConsoleMenu('menu','item1;item2','Number:',20,True,False,'a;b','c'))
                    