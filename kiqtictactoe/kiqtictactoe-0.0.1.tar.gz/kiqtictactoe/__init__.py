from random import randrange
import os
board = [[1,2,3],[4,"X",6],[7,8,9]]

def MakeListOfFreeFields(board):
    # La función examina el tablero y construye una lista de todos los cuadros vacíos.
    # La lista esta compuesta por tuplas, cada tupla es un par de números que indican la fila y columna.
    lst = []
    for i in range(3):
        for j in range(3):
            if type(board[i][j]) == int:
                lst.append((i,j))
    
    return lst

def DisplayBoard(board):
    # La función acepta un parámetro el cual contiene el estado actual del tablero
    # y lo muestra en la consola.
    os.system('cls')
    print("+-------+-------+-------+")
    print("|       |       |       |")
    print(f"|    {board[0][0]}  |   {board[0][1]}   |   {board[0][2]}   |")
    print("|       |       |       |")
    print("+-------+-------+-------+")
    print("|       |       |       |")
    print(f"|    {board[1][0]}  |   {board[1][1]}   |   {board[1][2]}   |")
    print("|       |       |       |")
    print("+-------+-------+-------+")
    print("|       |       |       |")
    print(f"|    {board[2][0]}  |   {board[2][1]}   |   {board[2][2]}   |")
    print("|       |       |       |")
    print("+-------+-------+-------+")

def EnterMove(board):
    # La función acepta el estado actual del tablero y pregunta al usuario acerca de su movimiento, 
    # verifica la entrada y actualiza el tablero acorde a la decisión del usuario.
    a = True
    while a:
        try:
            mov_user = int(input("Ingresa tu movimiento: "))
            for i in range(3):
                for j in range(3):
                    if mov_user == board[i][j]:
                        board[i][j] = "O"
                        a = False
        except TypeError:
            print("Por favor, insertar un entero entre 1 y 9 que además esté disponible en el tablero.")
        except KeyboardInterrupt:
            break
        except:
            print("No sé que hacer con este valor.")
        
def VictoryFor(board, sign):
    # La función analiza el estatus del tablero para verificar si
    # el jugador que utiliza las 'O's o las 'X's ha ganado el juego.
    buscar = [sign, sign, sign]
    exito = [board[0],board[1],board[2],
            [board[0][0],board[1][0],board[2][0]],
            [board[0][1],board[1][1],board[2][1]],
            [board[0][2],board[1][2],board[2][2]],
            [board[0][0],board[1][1],board[2][2]],
            [board[2][2],board[1][1],board[0][0]]
            ]
    if buscar in exito:
        print(f"EL ganador es: {sign}")
        return sign
    else:
        pass

def DrawMove(board):
    # La función dibuja el movimiento de la máquina y actualiza el tablero.
    restante = MakeListOfFreeFields(board)
    mov = randrange(len(restante))
    sel = restante[mov]
    board[sel[0]][sel[1]] = "X"

DisplayBoard(board)

signes = ["O","X"]

cond = True
while cond: 
    for signe in signes:
        print(f"Le toca a {signe}")
        if signe == "O":
            EnterMove(board)
        elif signe == "X":
            DrawMove(board)
        else:
            continue
        DisplayBoard(board)
        print(MakeListOfFreeFields(board))
        
        if VictoryFor(board,signe) != None: 
            cond = False
            break
        
        if len(MakeListOfFreeFields(board)) <= 0:
            print("Juego empatado")
            cond = False
            break
