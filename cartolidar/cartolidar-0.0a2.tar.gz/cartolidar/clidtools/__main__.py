'''
Created on 9 may 2022

@author: benmarjo
'''
# Se ejecuta cuando se llama al paquete en linea de comandos con \>python -m clidtools

if __name__ == '__main__':
    print('clidtools-> Menu de herramientas de cartolidar')
    print('\t1. clidtwins')
    print('\t2. clidmerge')
    selec = input('Elije opcion (0): ')
    try:
        nOpcionElegida = int(selec)
    except:
        nOpcionElegida = 0
    if nOpcionElegida == 1:
        print('\nSe ha elegido ejecutar clidtwuins de forma interactiva')
        # import clidtwins
        from clidtools.clidtwins import DasoLidarSource
        print('Metodos de DasoLidarSource: {}'.format(dir(DasoLidarSource)))
    print('Fin de clidtools')