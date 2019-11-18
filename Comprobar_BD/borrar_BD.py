from flask import Flask, render_template
import sqlite3, json, sys

base_datos=sys.argv[1]

def get_tables():
    conn = sqlite3.connect(base_datos)
    c=conn.cursor()
    cur=c.execute("select name from sqlite_master where type = 'table';")
    res=cur.fetchall()
    cur.close()
    tablas=[]
    for tabla in res:
        string = ''.join(tabla)
        tablas.append(string)
    return tablas


if __name__ == '__main__':
    conn = sqlite3.connect(base_datos)
    c=conn.cursor()
    for tabla in get_tables():
        c.execute("delete from "+tabla)
        conn.commit()
        print("Tabla borrada");
    c.close()
    
