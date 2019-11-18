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

tabla_usuarios='auth_user'

def get_cursor():
    conn = sqlite3.connect(base_datos)
    c=conn.cursor()
    return c

def get_tables():
    cur=get_cursor().execute("select name from sqlite_master where type = 'table';")
    res=cur.fetchall()
    cur.close()
    tablas=[]
    for tabla in res:
        string = ''.join(tabla)
        tablas.append(string)
    return tablas
        
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
    print('tuplas,{},{}'.format(tabla, datos_tuplas))
    tuplas=get_tuplas(tabla)
    for (tupla) in tuplas:
        print('{},{}'.format(tabla, tupla))
    if not tuplas:
        print('{} no tiene tuplas\n'.format(tabla))
        
def Escribir_fichero():
    #for (tabla) in get_tables():
    for tabla in tablas_Gestion:
        EscribirTabla(tabla);
         
       
if __name__ == '__main__':
    Escribir_fichero()
