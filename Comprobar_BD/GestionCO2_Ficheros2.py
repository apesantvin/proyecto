from flask import Flask, render_template
import sqlite3, json, sys

base_datos=sys.argv[1]

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

def LeerDatos():
    datos = []
    with open('datos.txt') as file:
        for linea in file:
            datos.append(linea.strip().split(','))
    return datos

def formato_datos(datos,tuplas):
    sql_1=""
    if (datos[0]) in get_tables():
        sql = '"INSERT INTO ' + datos[0] + ' ('+tuplas+') VALUES ('
        for i in range(1,len(datos)):
            datos[i] = datos[i].translate(None, '()u')
            sql_1=sql_1+ ''.join(datos[i].strip().split('"'))
            sql_1=sql_1
            if i!=len(datos)-1:
                sql_1=sql_1+", "
        sql=sql+sql_1+')"'
        print(sql)
    return sql_1
    
def formato_tuplas(datos):
    tuplas=""
    if (datos[1]) in get_tables():
        for i in range(2,len(datos)):
            datos[i] = datos[i].translate(None, "[ u' ]")
            tuplas=tuplas+(datos[i])
            if i!=len(datos)-1:
                tuplas=tuplas+","
    return tuplas
    
def guardar_datos(datos):
    print("el fichero tiene "+repr(len(datos))+" filas")
    print
    tuplas_s=""
    for i in xrange(len(datos)):
        if (datos[i][0]=="tuplas"):
            tuplas=formato_tuplas(datos[i])
            tuplas_s=''.join(tuplas)
        else:
            formato = formato_datos(datos[i],tuplas_s)
            conn = sqlite3.connect(base_datos)
            c=conn.cursor()
            c.execute(formato)
            conn.commit()
            print("Fila anadida")
            c.close()
    

def Escribir_bbdd():
    datos = LeerDatos()
    guardar_datos(datos)   
              
if __name__ == '__main__':
    Escribir_bbdd()
