def DiccionarioPredeter(Diccionario):
    '''DiccionarioPredeter("01")
    
    Devuelve un array con el diccionario predeterminado correspondiente. En caso de entregar algo no especificado lo devolverá tal cual.

    Opciones: "01", "09", "AZ", "AñZ", "az", "añz", "AZaz", "AñZañz", "0Z", "0ñZ", "0z", "0ñz", "A0", "Añ0", "a0", "añ0"
    '''

    # Binario
    if Diccionario == "01": Diccionario = ["0", "1"]
    # Numeral
    elif Diccionario == "09": Diccionario = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    # Alfabético mayúsculas
    elif Diccionario == "AZ": Diccionario = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
    elif Diccionario == "AñZ": Diccionario = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "Ñ", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
    # Alfabético minúsculas
    elif Diccionario == "az": Diccionario = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
    elif Diccionario == "añz": Diccionario = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "ñ", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
    # Alfabético mayúsculas y minúsculas
    elif Diccionario == "AZaz": Diccionario = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
    elif Diccionario == "AñZañz": Diccionario = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "Ñ", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "ñ", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
    # Alfabético minúsculas y mayúsculas
    elif Diccionario == "azAZ": Diccionario = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
    elif Diccionario == "añzAñZ": Diccionario = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "ñ", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "Ñ", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
    # Numeral alfabético mayúsculas
    elif Diccionario == "0Z": Diccionario = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
    elif Diccionario == "0ñZ": Diccionario = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "Ñ", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
    # Numeral alfabético minúsculas
    elif Diccionario == "0z": Diccionario = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
    elif Diccionario == "0ñz": Diccionario = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "ñ", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
    # Alfabético mayúsculas numeral
    elif Diccionario == "A0": Diccionario = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    elif Diccionario == "Añ0": Diccionario = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "Ñ", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    # Alfabético minúsculas numeral
    elif Diccionario == "a0": Diccionario = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    elif Diccionario == "añ0": Diccionario = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "ñ", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

    return Diccionario





def NumDiccionario(Diccionario, Devolver, *Grupo):
    '''NumDiccionario(Diccionario, Devolver, Grupo)

    Diccionario: Nuevo diccionario en array o predeterminado - ["A", "B", "C"] - "AZ"

    Devolver: Rango que devolver - [0] = [A] - [0,4] = [AA, AB, AC, BA]

    Grupo: Mínimo de caracteres - Manual 3 = ABA - Automática (No declarándola) BA
    '''
    
    Diccionario=DiccionarioPredeter(Diccionario) # Diccionario predeterminado
    LenDiccionario = len(Diccionario) # Largo del diccionario
    LenDevolver = len(Devolver) # Largo del devolver
    Salida = [] # Array de salida


    # Declarar cuando empieza y termina
    if LenDevolver == 1: Desde=Devolver[0]; Hasta=Devolver[0]
    elif LenDevolver == 2: Desde=Devolver[0]; Hasta=Devolver[1]


    # Contar cantidad de caracteres que habrá al final
    UnCaracter = 1
    NumCaracteres = 1
    # Equivalente de cálculo logarítmico
    while True:
        UnCaracter = LenDiccionario * UnCaracter # Calcular número de lista combinada si son 4 caracteres hay que calcular una lista de AAA, ... ZZZ
        if (Hasta / UnCaracter) <= 1: break # Terminar bucle cuando el resultado sea -1
        else: NumCaracteres+=1 # Contar veces que se ejecuta el bucle
    # Comprobar que a Grupo se le haya asignado un valor
    if len(Grupo)!=0:
        # Si NumCaracteres es menor que el definido en Grupo
        if NumCaracteres < Grupo[0]: NumCaracteres=Grupo[0]


    # Bucle que recoja todos los valores que se quiere sacar. Mientras que Desde sea mayor o igual que Hasta
    while Desde <= Hasta:
        # Devolver valor correspondiente del array
        Resultado="" # En valor de array
        Actual=Desde # Guardar valor actual

        # Condicional para calcular letra dependiendo de si es una sola o varias
        if LenDiccionario <= Actual:
            # Bucle mientras Desde sea mayor que la lista
            while LenDiccionario <= Actual:
                # Guardar resto de la división
                Resultado=Diccionario[Actual%LenDiccionario]+Resultado # En valor de array
                # Si el resultado de la división es menor a la cantidad de la lista
                if Actual//LenDiccionario < LenDiccionario:
                    # Guardar último valor el resultado de la última división
                    Resultado=Diccionario[Actual//LenDiccionario]+Resultado # En valor de array
                # Calcula el resultado entero de la división
                Actual=Actual//LenDiccionario
        # En caso de que solo sea una letra
        else: Resultado=Diccionario[Desde]
        # Pasar al siguiente elemento
        Desde+=1

        # Mientras que tenga una longitud inferior
        while len(Resultado) < NumCaracteres:
            Resultado = Diccionario[0]+Resultado

        # Añadir resultado en array
        Salida.append(Resultado)


    return Salida # Extraer array





def DiccionarioNum(Diccionario, Resolver):
    '''DiccionarioNum(Diccionario, Resolver)

    Diccionario: Nuevo diccionario en array o predeterminado - ["A", "B", "C"] - "AZ"

    Elementos para resolver - ['AAAAA', 'AAAAC', 'AACAB'] = [0, 2, 19]
    '''
    
    Diccionario=DiccionarioPredeter(Diccionario) # Diccionario predeterminado
    LenDiccionario = len(Diccionario) # Largo del diccionario
    Salida = [] # Array de salida
    

    # Recorrer lista
    for Elemento in Resolver:
        Multiplo=1 # Variable que multiplicara por la posición de la lista
        Valor=0 # Variable que almacena el valor del elemento de la lista

        # Recorrer cada letra
        for Caracter in reversed(Elemento):
            # Encontrar posición y multiplicar por múltiplo
            Valor+=Diccionario.index(Caracter) * Multiplo

            # Multiplicar por largo de diccionario
            Multiplo*=LenDiccionario

        # Añadir resultado en array
        Salida.append(Valor)


    return Salida # Extraer array
