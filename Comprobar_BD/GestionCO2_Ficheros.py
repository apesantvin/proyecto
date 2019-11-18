import sqlite3, sys

base_datos=sys.argv[1]

tablas_Gestion = ['GestionCO2_consumo',
'GestionCO2_empresa',
'GestionCO2_personal',
'GestionCO2_personal_empresa',
'GestionCO2_viaje',
'GestionCO2_viaje_personal',
'GestionCO2_vehiculo',
'GestionCO2_generador',
'GestionCO2_edificio',
'GestionCO2_vehiculoconsumo',
'GestionCO2_edificioconsumo']

def get_cursor():
    conn = sqlite3.connect(base_datos)
    c=conn.cursor()
    return c
        
def get_tuplas(tabla):
    cur=get_cursor().execute("select * from "+tabla+";")
    res=cur.fetchall()
    cur.close()
    return res

def get_datos_tuplas(tabla):
    cur=get_cursor().execute("select * from "+tabla+";")
    res=cur.fetchall()
    res_col=cur.description
    cur.close()
    columnas=[]
    for element in res_col:
        columnas.append(element[0])
    return columnas

def EscribirTabla(tabla):
    datos_tuplas=get_datos_tuplas(tabla)
    with open('datos.txt','a+') as file:
        file.write('tuplas,{},{}\n'.format(tabla, datos_tuplas))
    tuplas=get_tuplas(tabla)
    with open('datos.txt','a+') as file:
        for (tupla) in tuplas:
            file.write('{},{}\n'.format(tabla, tupla))
        if not tuplas:
            file.write('{} no tiene tuplas\n'.format(tabla))
        
def Escribir_fichero():
    open('datos.txt','w')
    for (tabla) in tablas_Gestion:
        EscribirTabla(tabla);
       
if __name__ == '__main__':
    Escribir_fichero()
