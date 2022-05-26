"""
Created on Sat Mar 12 14:22:13 2022

@author: Asus
"""
import matplotlib.pyplot as plt
import statistics as st
import numpy as np
from scipy.special import roots_legendre
import warnings

warnings.filterwarnings("ignore")


def productoria(list):
    """Ingresada una lista devuelve el producto de todos sus elementos
        Parametros:
            list:lista con los elementos
        Retorno
            Producto de todos sus elementos"""
    despues = list[0]
    for i in range(1, len(list)):
        despues = despues * list[i]
    return despues


def sumatoria(list):
    """Ingresada una lista devuelve la suma de todos sus elementos
        Parametros:
            list:lista con los elementos
        Retorno
            Suma de todos sus elementos"""
    despues = list[0]
    for i in range(1, len(list)):
        despues = despues + list[i]
    return despues


def interpolacionlagrange(x, X, Y):
    """Ingresada un valor de x, una lista de valores de X y de Y devuelve la interpolacion de lagrange evaluada en x
        Parametros:
            x:valor de x
            X:valores de x
            Y:valores de y
        Retorno
            Interpolacion de lagrange evaluada en x"""

    coeficientes = Y
    polinomios_x = []
    auxiliar = []
    for i in range(0, len(X)):
        for j in range(0, len(X)):
            if i != j:
                auxiliar.append((x - X[j]) / (X[i] - X[j]))
        polinomios_x.append(productoria(auxiliar) * coeficientes[i])
        auxiliar = []
    return sumatoria(polinomios_x)


def derivada_numerica1(x_values, y_values, loc):
    """Ingresados los valores de x(equisdistantes),los valores de y,y la localizacion de un
        punto en x, retorna la derivada numerica en ese punto.
    Parametros: 
        x_values: Valores equisdistantes de x(valores crecientes)
        y_values: Valores de y
        loc: localizacion en la lista del valor de x que queremos evaluar
    Retorno:
        Derivada evaluada numericamente en el punto deseado
    """
    y_values[0]
    if loc != 0 and loc != len(x_values) - 1:
        return (y_values[loc + 1] - y_values[loc - 1]) / (
            2 * (x_values[1] - x_values[0])
        )
    elif loc == 0:
        return (y_values[loc + 1] - y_values[loc]) / ((x_values[1] - x_values[0]))
    elif loc == len(x_values) - 1:
        return (y_values[loc] - y_values[loc - 1]) / ((x_values[1] - x_values[0]))


def derivada_numerica2(x_values, loc, funcion):
    """Ingresados los valores de x,y la localizacion de un punto en x,
        retorna la derivada numerica en ese punto con h=10**-6
        Defina la funcion como funcion(x)
    Parametros: 
        x_values: Valores de x
        loc: localizacion en la lista del valor de x que queremos evaluar
        funcion:funcion deseada
    Retorno:
        Derivada evaluada numericamente en el punto deseado
    """
    h = 10e-6
    return (funcion(x_values[loc] + h) - funcion(x_values[loc] - h)) / (2 * h)


def segunda_derivada_numerica1(x_values, y_values, loc):
    """Ingresados los valores de x(equisdistantes),los valores de y,y la localizacion de un
        punto en x, retorna la segunda derivada numerica en ese punto
    Parametros: 
        x_values: Valores equisdistantes de x(valores crecientes)
        y_values: Valores de y
        loc: localizacion en la lista del valor de x que queremos evaluar
    Retorno:
        Segunda Derivada evaluada nÃºmericamente en el punto deseado. Atencion La funcion evalua en puntos diferentes del inicial y final.
    """
    return (y_values[loc + 1] - 2 * y_values[loc] + y_values[loc - 1]) / (
        (x_values[1] - x_values[0]) ** 2
    )


def segunda_derivada_numerica2(x_values, loc, funcion):
    """Ingresados los valores de x,y la localizacion en el
        punto en x, retorna la segunda derivada numerica en ese punto con h=10**-6
        Defina la funcion como funcion(x)
    Parametros: 
        x_values: Valores de x
        loc: localizacion en la lista del valor de x que queremos evaluar
        funcion: funcion deseada
    Retorno:
        Segunda Derivada evaluada nÃºmericamente en el punto deseado
    """
    h = 10e-6
    funcion(x_values[loc] - h)
    return (
        funcion(x_values[loc] + h)
        - 2 * funcion(x_values[loc])
        + funcion(x_values[loc] - h)
    ) / ((h) ** 2)


def lista_derivada_numerica1(x_values, y_values):
    """Ingresados los valores de x y los valores de y, se retorna las derivadas numericas
    Parametros: 
        x_values: Valores equisdistantes de x(valores crecientes)
        y_values: Valores de y
    Retorno:
        lista con las derivadas numericas
    """

    list = []
    for i in range(0, len(x_values)):
        list.append(derivada_numerica1(x_values, y_values, i))
    return list


def lista_derivada_numerica2(x_values, funcion):
    """Ingresados los valores de x y la funcion deseada, se retorna las derivadas numericas
    Parametros: 
        x_values: Valores equisdistantes de x(valores crecientes)
        funcion: funcion deseada
    Retorno:
        lista con las derivadas numericas
    """

    list = []
    for i in range(0, len(x_values)):
        list.append(derivada_numerica2(x_values, i, funcion))
    return list


def lista_segunda_derivada_numerica1(x_values, y_values):
    """Ingresados los valores de x y los valores de y, se retorna las segundas derivadas numericas
    Parametros: 
        x_values: Valores equisdistantes de x(valores crecientes)
        y_values: Valores de y
    Retorno:
        lista con las segundas derivadas numericas
    """
    list = []
    for i in range(1, len(x_values) - 1):
        list.append(segunda_derivada_numerica1(x_values, y_values, i))
    return list


def lista_segunda_derivada_numerica2(x_values, funcion):
    """Ingresados los valores de x y la función, retorna lista de las segundas derivadas numericas
    Parametros: 
        x_values: Valores equisdistantes de x(valores crecientes)
        funcion: funcion deseada
    Retorno:
        lista con las segundas derivadas numericas
    """
    list = []
    for i in range(0, len(x_values)):
        list.append(segunda_derivada_numerica2(x_values, i, funcion))
    return list


def newton_raphson_derivada_conocida(x0, funcion, derivada):
    """Ingresados los valores de x0, la funcion y la derivada
        retorna la solucion numerica, porfavor verifique que la funcion no cambie de
        concavidad y la derivada sea diferente de 0 en el intervalo de convergencia, y asegure un intervalo de convergencia; 
        de lo contrario el programa puede no funcionar(Puede asegurar el intervalo gráficamente).
        Defina la funcion como f(x).
    Parametros: 
        x0: valor inicial
        función: función
        derivada: derivada
    Retorno:
        Solucion numerica newton-raphson

    """
    xantes = x0
    xdespues = xantes - (funcion(xantes) / derivada(xantes))
    while (xdespues - xantes) / xantes > 10e-6:
        xantes = xdespues
        xdespues = xantes - (funcion(xantes) / derivada(xantes))
    return xdespues


def newton_raphson_derivada_desconocida(x0, funcion):
    """Ingresados los valores de x y y
        retorna la solucion numerica(En caso que la derivada sea complicada), porfavor verifique que la funcion no cambie de
        concavidad y la derivada sea diferente de 0 en el intervalo de convergencia, y asegure un intervalo de convergencia; de lo contrario el programa puede no funcionar(Puede asegurar el intervalo gráficamente).
        Defina la funcion como f(x).
    Parametros: 
        x0: valor inicial
        funcion: función conocida.
    Retorno:
        Solucion numerica newton-raphson
    """
    xantes = x0
    xdespues = x0 - (funcion(xantes) /
                     derivada_numerica2([xantes], 0, funcion))
    while (xdespues - xantes) / xantes < 10e-6:
        xantes = xdespues
        xdespues = xantes - (funcion(xantes) /
                             derivada_numerica2([xantes], 0, funcion))
    return xdespues


def integral_riemann(f, a, b):
    """Ingresada la funcion, los limites de integracion(1000 particiones) devuelve la integral numerica(riemann) aproximada
        Parametros:
            f:funcion
            a: intervalo inferior
            b: intervalo superior
            n: numero de intervalos
       Retorno
           Devuelve la integral numerica(riemann)"""
    Δx = (b - a) / 1000
    I = 0
    for i in range(0, 1000):
        xi = a + i * Δx
        I += f(xi) * Δx
    return I


def integral_trapecio(f, a, b):
    """Ingresada la funcion, los limites de integracion(1000 particiones) devuelve la integral numerica(trapecio) aproximada
        Parametros:
            f:funcion
            a: intervalo inferior
            b: intervalo superior
            n: numero de intervalos
       Retorno
           Devuelve la integral numerica(trapecio)"""
    Δx = (b - a) / 1000
    yi = f(a)
    yf = f(b)
    sigmaf = 0
    xi = 0
    for i in range(1, 1000):
        xi = a + i * Δx
        sigmaf += f(xi)

    I = Δx * ((yi / 2) + sigmaf + (yf / 2))
    return I


def intregral_gauss_legendre(funcion, a, b):
    """Ingresada la funcion, los limites de integracion(1000 particiones) devuelve la integral numerica(gauss legendre) aproximada
        Parametros:
            f:funcion
            a: intervalo inferior
            b: intervalo superior
            n: numero de intervalos
       Retorno
           Devuelve la integral numerica(gauss legendre)"""

    x, integral = 0, 0
    raices, pesos = roots_legendre(1000)
    for i in range(0, 1000):
        x = (1 / 2) * (raices[i] * (b - a) + a + b)
        integral += funcion(x) * pesos[i]
    integral = (1 / 2) * (b - a) * integral
    return integral


def integral_riemann_funciondes(X, Y, loc1, loc2):
    """Ingresada una serie de datos, los limites de integracion(1000 particiones) devuelve la integral numerica(riemann) aproximada(No elija como intervalo superior el ultimo datos en X)
        Parametros:
            X:valores de x 
            Y: valores de y
            loc1: intervalo inferior
            loc2: intervalo superior
       Retorno
           Devuelve la integral numerica(riemann)"""
    Δx = None
    I = 0
    for i in range(loc1, loc2):
        Δx = X[i + 1] - X[i]
        I += Y[i] * Δx
    return I


def integral_trapecio_funciondes(X, Y, loc1, loc2):
    """Ingresada una serie de datos, los limites de integracion(1000 particiones) devuelve la integral numerica(trapecio) aproximada(No elija como intervalo superior el ultimo datos en X)
        Parametros:
            X:valores de x 
            Y: valores de y
            loc1: intervalo inferior
            loc2: intervalo superior
       Retorno
           Devuelve la integral numerica(trapecio)"""
    Δx = None
    I = 0
    aux = 0
    for i in range(loc1, loc2):
        Δx = X[i + 1] - X[i]
        aux = (Y[i] + Y[i + 1]) / 2
        I += aux * Δx
    return I


def matriz_vacia(n, m):
    """Ingresados los valores deseados de columnas y filas
        retorna una matriz vacía de nxm
    Parametros: 
        n: numero de filas
        m: numero de columnas
    Retorno:
        Matriz vacia de nxm
    """
    vacia = []
    for i in range(0, n):
        vacia.append([])
    for j in vacia:
        for k in range(0, m):
            j.append(0)
    return vacia


def vector_vacio(n):
    """Dado un numero n, devuelve con un vector de dimension n con todas las entradas iguales a 0
        Parametros:
            n: numero de entradas
        Retorno:
           Vector: con n entradas y entradas iguales a 0"""
    aux = []
    for i in range(n):
        aux.append(0)
    return [aux]


def print_matriz(matriz):
    """Imprime la matriz de manera organizada
    """
    aux = matriz_vacia(len(matriz), len(matriz[0]))
    for i in range(len(matriz)):
        for j in range(len(matriz[0])):
            aux[i][j] = round(matriz[i][j], 6)

    for i in range(0, len(matriz)):
        print(aux[i])
    return " "


def columnaj(matriz, j):
    """Ingresados la columna deseada
        retorna esta columna
    Parametros: 
        matriz: matriz deseada
        m: columna deseada(la primera columna es 0)
    Retorno:
        columna deseada
    """
    columna = []
    for i in range(0, len(matriz)):
        columna.append(matriz[i][j])
    return [columna]


def auxproducto(vector1, vector2):
    """Ingresados 2 vectores
        retorna su producto punto
    Parametros: 
        vector1: vector 2
        vector2: vector 1
    Retorno:
        producto punto
    """
    productopunto = 0
    for k in range(0, len(vector1)):
        productopunto += vector1[k] * vector2[k]
    return productopunto


def suma(matriz1, matriz2):
    """Ingresados 2 Matrices
        retorna su suma
    Parametros: 
        matriz1: Matriz 2
        matriz2: Matriz 1
    Retorno:
        Retorna su suma
    """
    suma = matriz_vacia(len(matriz1), len(matriz1[0]))
    for i in range(0, len(matriz1)):
        for j in range(0, len(matriz1[0])):
            suma[i][j] = matriz1[i][j] + matriz2[i][j]
    return suma


def escalarmatriz(matriz, c):
    """Ingresados 1 Matriz y un escalar
        retorna el producto
    Parametros: 
        matriz1: Matriz 
        c: Escalar
    Retorno:
        Retorna c*Matriz 1
    """
    new = matriz_vacia(len(matriz), len(matriz[0]))
    for i in range(0, len(matriz)):
        for j in range(0, len(matriz[0])):
            new[i][j] = (matriz[i][j]) * c
    return new


def resta(matriz1, matriz2):
    """Ingresados 2 Matrices
        retorna su resta
    Parametros: 
        matriz1: Matriz 1
        matriz2: Matriz 2
    Retorno:
        Retorna Matriz 1 - Matriz 2
    """
    return suma(matriz1, escalarmatriz(matriz2, -1))


def producto(matriz1, matriz2):
    """Ingresados 2 Matrices
        retorna su producto
    Parametros: 
        matriz1: Matriz 1
        matriz2: Matriz 2
    Retorno:
        Retorna Matriz 1*Matriz 2
    """
    if len(matriz1) == 1 and len(matriz1[0]) != 1 and len(matriz2) == 1:
        aux1 = matriz1[0]
        aux2 = matriz2[0]
        return auxproducto(aux1, aux2)

    if (
        len(matriz1) != 1 and len(matriz2) == 1
    ):  # El número de columnas de la primera matriz debe coincidir con el número de filas de la segunda matriz.
        sumatoria = vector_vacio(len(matriz1))
        for i in range(len(matriz1)):
            sumatoria[0][i] = auxproducto(matriz1[i], matriz2[0])
        return sumatoria
    if len(matriz1) == 1 and len(matriz2) != 1:
        sumatoria = vector_vacio(len(matriz2[0]))
        for i in range(len(matriz2[0])):
            sumatoria[0][i] = auxproducto(matriz1[0], columnaj(matriz2, i)[0])
        return sumatoria
    if len(matriz1) == 1 and len(matriz1[0]) == 1 and len(matriz2) == 1:
        return escalarmatriz(matriz2, matriz1[0][0])
    else:
        producto = matriz_vacia(len(matriz1), len(matriz2[0]))
        for i in range(0, len(matriz1)):
            for j in range(0, len(matriz2[0])):
                producto[i][j] = auxproducto(
                    matriz1[i], columnaj(matriz2, j)[0])
        return producto


def eliminarfilai(matriz, i):
    """Ingresados 1 Matriz y una fila 
        retorna la matriz sin la fila
    Parametros: 
        matriz1: Matriz 1
        i: Fila deseada(la primera fila es 0)
    Retorno:
        Matriz sin la fila i
    """
    del matriz[i]
    return matriz


def eliminarcolumnaj(matriz, j):
    """Ingresados 1 Matriz y una columna
        retorna la matriz sin la columna
    Parametros: 
        matriz1: Matriz 1
        j: Columna deseada(la primera columna es 0)
    Retorno:
        Matriz sin la Columna j
    """
    for i in range(0, len(matriz)):
        for k in range(0, len(matriz[0])):
            if k == j:
                del matriz[i][k]
    return matriz


def eliminar_filai_columnaj(matriz, i, j):
    """Ingresados 1 Matriz,una fila y una columna
        retorna la matriz sin la fila y la columna
    Parametros: 
        matriz1: Matriz 1
        i: Fila deseada (la primera fila es 0)
        j: Columna deseada (la primera columna es 0)
    Retorno:
        Matriz sin la fila i y la columna j
    """
    new = eliminarfilai(matriz, i)
    new = eliminarcolumnaj(new, j)
    return new


def transpuesta(A):
    """Ingresada una matriz,devuelve su transpuesta
        Parametros:
            A: Matriz
        Retorno
            Matriz transpuesta"""
    B = matriz_vacia(len(A[0]), len(A))
    for i in range(len(A)):
        for j in range(len(A[0])):
            B[j][i] = A[i][j]
    return B


def magnitud_vector(vector):
    """Dado un vector retorna su norma
        Parametros:
            vector: vector
        Retorno
            Norma del vector"""
    vector = vector[0]
    norma = 0
    for i in vector:
        norma += i ** 2
    return (norma) ** (1 / 2)


def angulo_vectores(vector1, vector2):
    """Dado 2 vectores, devuelve el angulo entre ellos
        Parametros:
            vector1: vector
            vector 2: vector
        Retorno:
            Angulo entre ellos(grados)"""
    costetha = (producto(vector1, vector2)) / (
        magnitud_vector(vector1) * magnitud_vector(vector2)
    )
    tetha = np.arccos(costetha)
    return np.degrees(tetha)


def indmaxarg(vector):
    """Dado un vector retorna el indice con mayor valor
        Parametros:
            vector: vector
        Retorno
            Indice con mayor valor(el primer indice es 0)"""
    maxi = max(vector[0])
    for i in range(len(vector[0])):
        if vector[0][i] == maxi:
            return i


def aux_triangular(A):
    B = A
    rows = len(B)
    aux = None
    d = 0
    for i in range(rows - 1):
        aux = [columnaj(B, i)[0][i:-1]]
        indi_max = indmaxarg(aux)
        if indi_max > 0:
            C = B[i]
            B[i] = B[i + indi_max]
            B[i + indi_max] = C
            d += 1
    return B, d


def triangular_superior(A):
    """Dada una matriz A(cuadrada), la transforma mediante o.e.f a una matriz triangular superior, no debe haber 0's en la diagonal
        Parametros:
            A:matriz
        Retorno:
            Matriz en forma triangular superior"""
    B, d = aux_triangular(A)
    rows = len(A)
    aux = None
    for i in range(rows):
        for j in range(i + 1, rows):
            aux = escalarmatriz([B[i]], (B[j][i] / B[i][i]))
            B[j] = resta([B[j]], aux)[0]
    return B, d


def triangular_inferior(A):
    """Dada una matriz A(cuadrada), la transforma mediante o.e.f a una matriz triangular inferior
        Parametros:
            A:matriz
        Retorno:
            Matriz en forma triangular inferior"""
    B, d = aux_triangular(A)
    n = len(A)
    for i in range(n - 1, -1, -1):
        for j in range(i - 1, -1, -1):
            aux = escalarmatriz([B[i]], (B[j][i] / B[i][i]))
            B[j] = resta([B[j]], aux)[0]
        # B[i]=escalarmatriz([B[i]],1/(B[i][i]))[0]

    return B, d


def diagonal(A):
    B, d = triangular_superior(A)
    n = len(A)
    for i in range(n - 1, -1, -1):
        for j in range(i - 1, -1, -1):
            aux = escalarmatriz([B[i]], (B[j][i] / B[i][i]))
            B[j] = resta([B[j]], aux)[0]
        # B[i]=escalarmatriz([B[i]],1/(B[i][i]))[0]

    return B, d


def red_gauss(A):
    """Dada una matriz A que representa un sistema de ecuaciones lineales,aplica el algoritmo de reduccion de gauss
        primero la convierte en una matriz triangular superior y despues en una matriz diagonal donde las soluciones son explicitas
        (La matriz debe tener tamano nx(n+1))
        Parametros:
            A:matriz
        Retorno:
            Solucion sistemas de ecuaciones lineales"""
    B, d = diagonal(A)
    for i in range(len(B)):
        B[i] = escalarmatriz([B[i]], 1 / (B[i][i]))[0]
    return B, d


def matriz_aum_id(A):
    """Dada una matriz cuadrada a, retorna una matriz aumentada con la identidad
    Parametros:
        A:matriz
    Retorno
        Matriz aumentada con la identidad"""
    new = matriz_vacia(len(A), 2 * len(A))
    for i in range(len(A)):
        for j in range(len(A)):
            new[i][j] = A[i][j]
    for i in range(len(A)):
        for j in range(len(A), 2 * len(A)):
            if j - len(A) == i:
                new[i][j] = 1
    return new


def inversa(A):
    """Dada una matriz cuadrada A, retorna su inversa
      Parametros:
          A: matriz
      Retorno:
          matriz inversa"""
    if len(A) == 1 and len(A[0]) == 1:
        return [[1 / A[0][0]]]
    B = matriz_aum_id(A)
    B = red_gauss(B)[0]
    for i in range(len(A)):
        eliminarcolumnaj(B, 0)
    return B


def diagonales(A):
    n = vector_vacio(len(A))
    for i in range(len(A)):
        n[0][i] = A[i][i]
    return n


def determinante(matriz):
    """Dada una matriz cuadrada A,retorna su determinante
        Parametros:
            A: matriz
        Retorno
            determinante de A"""
    A, d = diagonal(matriz)
    aux = diagonales(A)
    return round(productoria(aux[0]) * ((-1) ** d), 6)


def remplazarcolumnaj(matriz, j, vector):
    """Dada una matriz, su columna y un vector, remplaza la columna por el vector dado
        Parametros:
            matriz: matriz
            j: columna(primera columna 0)
            vector: vector que se desea remplazar
        Retorno:
            matriz con el elemento remplazado"""
    for i in range(len(matriz)):
        matriz[i][j] = vector[0][i]
    return matriz


def remplazar_posicion(matriz, i, j, c):
    """Dada una matriz,y la posición i,j ; remplaza la columna por el vector dado
        Parametros:
            matriz: matriz
            j: columna(primera columna 0)
            i: fila(primera fila 0)
            c:valor a remplazar
        Retorno:
            matriz con el elemento remplazado"""
    for k in range(len(matriz)):
        for m in range(len(matriz[0])):
            if k == i and m == j:
                matriz[k][m] = c
    return matriz


def proyeccion(vector1, vector2):
    """Proyección de v1 sobre v2"""
    aux1 = producto(vector1, vector2)
    aux2 = magnitud_vector(vector2)
    aux3 = aux1 / aux2
    return escalarmatriz(vector2, aux3)


def normalizar(vector1):
    return escalarmatriz(vector1, (1 / magnitud_vector(vector1)))


def calcula_qj(Q, aj, j, n):
    """Funcion auxiliar que calcula el vector ortonormal qj, no es de utilidad solo es una funcion auxiliar de gram_schmidt
  Q=matriz
  aj=vectorj
  n=columnasQ(desde0)
 """
    sigma = vector_vacio(n)
    for i in range(j):
        sigma = suma(sigma, proyeccion(aj, columnaj(Q, i)))
    return normalizar(resta(aj, sigma))


def gram_schmidt(A):
    """ Dada una matriz cuadrada, cuyas columnas son bases para R**n, devuelve una matriz ortogonal a traves del proceso de ortonormalizacion de gram-schmidt
      Parametros:
          A: matriz
      Retorno:
          matriz ortogonal"""
    columns = len(A[0])
    Q = matriz_vacia(len(A), len(A[0]))
    Q = remplazarcolumnaj(Q, 0, calcula_qj(Q, columnaj(A, 0), 0, columns))
    for j in range(columns):
        Q = remplazarcolumnaj(Q, j, calcula_qj(Q, columnaj(A, j), j, columns))
    return Q


def factorizacionQR(A):
    Q = gram_schmidt(A)
    R = producto(transpuesta(Q), A)
    print("Q=")
    print(print_matriz(Q))
    print("R=")
    print(print_matriz(R))
    return ""


def valores_propios_algoritmo_QR(A):
    """Dada una matriz cuadrada,se itera 100 veces, el algoritmo devuelve los valores propios a traves del algoritmo qr
      Parametros:
          A:matriz
          iteraciones: iteraciones del algoritmo
      Retorno:
          valores propios(reales) aproximados"""
    Ak = A
    for k in range(1000):
        Qk = gram_schmidt(Ak)
        Ak = producto(producto(transpuesta(Qk), Ak), Qk)
    return diagonales(Ak)


def metodo_de_potencias(A):
    """Dada una matriz cuadrada,se calcula el autovector de mayor autovalor
      Parametros:
          A:matriz
      Retorno:
          autovector con mayor autovalor"""
    x = vector_vacio(len(A[0]))
    x2 = None
    for i in range(len(x[0])):
        x[0][i] = 1
    for i in range(1000):
        x2 = escalarmatriz(producto(A, x), 1 / magnitud_vector(producto(A, x)))
        x = x2
    return x


def apro_mayor_valor_propio(A, v_prop):
    """Dado una aproximacion al autovector de mayor valor propio o un valor exacto, la funcion
    retorna una aproximacion al autovalor correspondiente
    Parametros:
        A:matriz
        v_prop: vector propio(fila)
    Retorno:
        Autovalor dominante"""

    return (producto(v_prop, (producto(A, v_prop)))) / (magnitud_vector(v_prop) ** 2)


def E_fila_c(n, k, c):
    """Dado una dimensión, retorna la matriz elemental E de nxn asociada a multiplicar un 
    escalar  c por la fila k de una matriz A de nxm
    Parametros:
        n:dimensión matriz elemental
        k:fila por la que se multiplica el escalar(empieza por la fila 0)
        c:escalar
    Retorno:
        matriz elemental E de nxn asociada a multiplicar un 
        escalar c por la fila k de una matriz A de nxm"""
    A = matriz_vacia(n, n)
    for i in range(n):
        for j in range(n):
            A[i][i] = 1
    A[k][k] = c
    return A


# http://www1.monografias.com/docs115/regresion-lineal-multiple/regresion-lineal-multiple2.shtml

def regresion1(x, y, grado, tupla):
    columnas = 0
    aux = []
    for i in range(len(tupla)):
        if tupla[i] == 1:
            columnas += 1
            aux.append(i)
    rows = len(x)
    A = matriz_vacia(rows, columnas)
    for i in range(len(aux)):
        A = remplazarcolumnaj(A, i, [(np.array(x) ** (aux[i])).tolist()])
    A = transpuesta(A)
    v = [[1 / producto(A, A)]]
    v = producto(v, A)
    v = [producto(v, [y])]
    aux1 = producto([v], A)
    aux1 = resta([y], aux1)
    aux3 = (magnitud_vector(aux1)) ** 2
    aux1 = aux3
    aux2 = len(A[0]) - 2
    sigma_2 = aux1 / aux2
    cov = [sigma_2 / producto(A, A)]
    incer = [cov[0] ** (1 / 2)]
    media = st.mean(y)
    VT = sumatoria(((np.array(y) - media) ** 2).tolist())
    R_2 = 1 - (aux3 / VT) * ((len(A[0]) - 1) / (len(A[0]) - 2))
    R = R_2 ** (1 / 2)
    return v, incer, R


def regresion(x, y, grado, tupla):
    """Ingresados valores de x,y y el grado del polinomio para la regresión,retorna los parámetros de la regresión
    Parametros
        x: valores de x
        y: valores de y
        grado: grado del polinomio a ajustar
       tupla: tupla que indica que coeficientes queremos diferentes de cero, ajuste(x**2+1)-> tupla=(1,0,1)(ascendente)
    Retorno
        Retorna los coeficientes de mayor a menor, la incertidumbre y el coeficiente de correlacion
        """
    columnas = 0
    aux = []
    for i in range(len(tupla)):
        if tupla[i] == 1:
            columnas += 1
            aux.append(i)
    rows = len(x)
    A = matriz_vacia(rows, columnas)
    for i in range(len(aux)):
        A = remplazarcolumnaj(A, i, [(np.array(x) ** (aux[i])).tolist()])
    if len(transpuesta(A)) == 1:
        return regresion1(x, y, grado, tupla)
    v = inversa(producto(transpuesta(A), A))
    v = producto(v, transpuesta(A))
    v = producto(v, [y])
    aux1 = resta(producto(A, v), [y])
    aux1 = (magnitud_vector(aux1)) ** 2
    if len(A) - len(A[0]) - 1 != 0:
        aux2 = len(A) - len(A[0]) - 1
    elif len(A) - len(A[0]) - 1 == 0:
        aux2 = len(A) - len(A[0])
    sigma_2 = aux1 / aux2
    cov = inversa(producto(transpuesta(A), A))
    cov = escalarmatriz(cov, sigma_2)
    incer = []
    media = st.mean(y)
    VT = sumatoria(((np.array(y) - media) ** 2).tolist())
    R_2 = 1 - (sigma_2 * (len(A) - 1) / VT)
    R = (R_2) ** (1 / 2)
    for i in range(len(cov)):
        incer.append((abs(cov[i][i])) ** (1 / 2))
    return v[0][::-1], incer[::-1], R


def aux_regresion(x, y, grado, tupla):
    """Ingresados valores de x,y y el grado del polinomio para la regresión,retorna los datos de y ajustados a x
    Parametros
        x: valores de x
        y: valores de y
        grado: grado del polinomio a ajustar
       tupla: tupla que indica que coeficientes queremos diferentes de cero, ajuste(x**2+1)-> tupla=(1,0,1)(ascendente)
    Retorno
        Retorna los datos de y ajustados a x
        """
    ajuste = regresion(x, y, grado, tupla)
    parametros = ajuste[0][::-1]
    x = np.array((np.linspace(min(x), max(x)), 1000))[0]
    grados = []
    yajus1 = []
    aux = None
    result = None
    for i in range(len(tupla)):
        if tupla[i] == 1:
            grados.append(i)
    for i in range(len(parametros)):
        yajus1.append((parametros[i] * (x ** (grados[i]))))
    result = yajus1[0]
    for i in range(1, len(yajus1)):
        aux = yajus1[i]
        result = aux + result
    return result


def dibujo_reg(x, y, grado, tupla, fila, columna, nombre, nombrex, nombrey, label, ax, aux, aux2):
    """Ingresados valores de x,y y el grado del polinomio para la regresión,retorna los datos ploteados en 2 dimensiones
    se compara experimento con ajuste, ( se debe antes crear el plano)
    si no cola subplot fila=columna=0, importe matplotlib
    --------------------------
    Colocar antes fig,ax = plt.subplots(filas(desde 0),columnas(desde 0),figsize=(eje x,ejey))
    ---------------------------
    Parametros
        x: valores de x
        y: valores de y
        grado: grado del polinomio a ajustar
       tupla: tupla que indica que coeficientes queremos diferentes de cero, ajuste(x**2+1)-> tupla=(1,0,1)(ascendente)
       fila: columna en el subplot empieza desde 0
       columna: columna en el subplot empieza desde 0
       nombre: Nombre gráfica
       nombrex: Nombre en x
       nombrey: Nombre en y
       label: Nombre de la linea
       aux: True if ax has atribuite plt.subplots()
       aux2 : True if ax has atribuite plt.subplots(a,b)

    Retorno
        Retorna los datos ploteados en una (figura ya hecha) en 2 dimensiones se compara experimento con ajuste"""

    if columna == 0 and fila == 0 and aux == True:

        ax.scatter(x, y, label="datos " + label)
        ax.plot(
            np.array((np.linspace(min(x), max(x)), 1000))[0],
            aux_regresion(x, y, grado, tupla),
            label="ajuste " + label,
        )
        ax.set_xlabel(nombrex)
        ax.set_ylabel(nombrey)
        ax.set_title(nombre)
        ax.legend()
    elif aux2 == True:
        ax[fila][columna].scatter(x, y, label="datos " + label)
        ax[fila][columna].plot(
            np.array((np.linspace(min(x), max(x)), 1000))[0],
            aux_regresion(x, y, grado, tupla),
            label="ajuste " + label,
        )
        ax[fila][columna].set_xlabel(nombrex)
        ax[fila][columna].set_ylabel(nombrey)
        ax[fila][columna].set_title(nombre)
        ax[fila][columna].legend()
    elif columna == 0:

        ax[fila].scatter(x, y, label="datos " + label)
        ax[fila].plot(
            np.array((np.linspace(min(x), max(x)), 1000))[0],
            aux_regresion(x, y, grado, tupla),
            label="ajuste " + label,
        )
        ax[fila].set_xlabel(nombrex)
        ax[fila].set_ylabel(nombrey)
        ax[fila].set_title(nombre)
        ax[fila].legend()

    elif fila == 0:
        ax[columna].scatter(x, y, label="datos " + label)
        ax[columna].plot(
            np.array((np.linspace(min(x), max(x)), 1000))[0],
            aux_regresion(x, y, grado, tupla),
            label="ajuste " + label,
        )
        ax[columna].set_xlabel(nombrex)
        ax[columna].set_ylabel(nombrey)
        ax[columna].set_title(nombre)
        ax[columna].legend()


def regresionlineal(x, y):
    mediay = st.mean(y)
    mediax = st.mean(x)
    sigma1 = 0
    sigma2 = 0
    sigma4 = 0
    sigma5 = 0
    sigma6 = 0
    sigma7 = 0
    sigma8 = 0
    for i in range(len(x)):
        sigma1 += x[i] * (y[i] - mediay)
        sigma2 += x[i] * (x[i] - mediax)
    m = sigma1 / sigma2
    b = mediay - m * mediax
    coeficientes = [m, b]
    for i in range(len(x)):
        sigma4 += (y[i] - b - m * x[i]) ** 2
    varianza = (sigma4 / (len(x) - 2)) ** (1 / 2)
    error_m = varianza * ((len(x) / sigma2) ** (1 / 2))
    for i in range(len(x)):
        sigma5 += x[i] ** 2
    error_b = varianza * ((sigma5 / sigma2) ** (1 / 2))
    errores = [error_m, error_b]
    for i in range(len(x)):
        sigma6 += (x[i] - mediax) * (y[i] - mediay)
        sigma7 += (x[i] - mediax) ** 2
        sigma8 += (y[i] - mediay) ** 2
    r = sigma6 / (np.sqrt(sigma7 * sigma8))
    return coeficientes, errores, abs(r)


# https://glosarios.servidor-alicante.com/terminos-estadistica/coeficiente-de-correlacion-lineal-de-pearson
# print(regresionlineal([1,2,3],[1,4,6]))


def aux_regresionlin(x, y):
    """Ingresados valores de x,y y el grado del polinomio para la regresión,retorna los datos de y ajustados a x
    Parametros
        x: valores de x
        y: valores de y
        grado: grado del polinomio a ajustar
       tupla: tupla que indica que coeficientes queremos diferentes de cero, ajuste(x**2+1)-> tupla=(1,0,1)(ascendente)
    Retorno
        Retorna los datos de y ajustados a x
        """
    ajuste = regresionlineal(x, y)
    parametros = ajuste[0][::-1]
    x = np.array((np.linspace(min(x), max(x)), 1000))[0]
    grados = (0, 1)
    yajus1 = []
    aux = None
    result = None
    for i in range(len(parametros)):
        yajus1.append((parametros[i] * (x ** (grados[i]))))
    result = yajus1[0]
    for i in range(1, len(yajus1)):
        aux = yajus1[i]
        result = aux + result
    return result


def dibujo_reglineal(x, y, fila, columna, nombre, nombrex, nombrey, ax, label, aux, aux2):
    """Ingresados valores de x,y y el grado del polinomio para la regresión,retorna los datos ploteados en 2 dimensiones
    se compara experimento con ajuste, ( se debe antes crear el plano)
    si no cola subplot fila=columna=0, importe matplotlib
    --------------------------
    Colocar antes fig,ax = plt.subplots(filas(desde 0),columnas(desde 0),figsize=(eje x,ejey))
    ---------------------------
    Parametros
        x: valores de x
        y: valores de y
        grado: grado del polinomio a ajustar
       tupla: tupla que indica que coeficientes queremos diferentes de cero, ajuste(x**2+1)-> tupla=(1,0,1)(ascendente)
       fila: columna en el subplot empieza desde 0
       columna: columna en el subplot empieza desde 0
       nombre: Nombre gráfica
       nombrex: Nombre en x
       nombrey: Nombre en y
       label: Nombre de la linea
       aux: True if ax has atribuite plt.subplots()
       aux2 : True if ax has atribuite plt.subplots(a,b)
    Retorno
        Retorna los datos ploteados en una (figura ya hecha) en 2 dimensiones se compara experimento con ajuste"""

    if columna == 0 and fila == 0 and aux == True:
        ax.scatter(x, y, label="datos " + label)
        ax.plot(
            np.array((np.linspace(min(x), max(x)), 1000))[0],
            aux_regresionlin(x, y),
            label="ajuste " + label,
        )
        ax.set_xlabel(nombrex)
        ax.set_ylabel(nombrey)
        ax.set_title(nombre)
        ax.legend()
    elif aux2 == True:
        ax[fila][columna].scatter(x, y, label="datos " + label)
        ax[fila][columna].plot(
            np.array((np.linspace(min(x), max(x)), 1000))[0],
            aux_regresionlin(x, y),
            label="ajuste " + label,
        )
        ax[fila][columna].set_xlabel(nombrex)
        ax[fila][columna].set_ylabel(nombrey)
        ax[fila][columna].set_title(nombre)
        ax[fila][columna].legend()
    elif columna == 0:
        ax[fila].scatter(x, y, label="datos " + label)
        ax[fila].plot(
            np.array((np.linspace(min(x), max(x)), 1000))[0],
            aux_regresionlin(x, y),
            label="ajuste " + label,
        )
        ax[fila].set_xlabel(nombrex)
        ax[fila].set_ylabel(nombrey)
        ax[fila].set_title(nombre)
        ax[fila].legend()
    elif fila == 0:
        ax[columna].scatter(x, y, label="datos " + label)
        ax[columna].plot(
            np.array((np.linspace(min(x), max(x)), 1000))[0],
            aux_regresionlin(x, y),
            label="ajuste " + label,
        )
        ax[columna].set_xlabel(nombrex)
        ax[columna].set_ylabel(nombrey)
        ax[columna].set_title(nombre)
        ax[columna].legend()
