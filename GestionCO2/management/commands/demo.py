import datetime
import random
from django.core.management.base import BaseCommand
from GestionCO2.models import *
from django.contrib.auth.models import User

def Consumos():
        AddViaje()
        AddGenerador():
        for vehiculo in Vehiculo.objects.all():
            AddConsumoVehiculo(vehiculo)
        for ed in Edificio.objects.all():
            AddConsumoEdificio(ed)

def getPersona(empresa):
    e=Empresa.objects.get(nombre_empresa=empresa)
    p=Personal.objects.filter(empresa=e)
    for people in p:
        persona=people
        break
    return persona

def AddConsumoEdificio(edificio):
    for mes in range(3,5):
        for dia in range (1,15):
            for tipo, nombre_tipo in TIPOS_ED:
                for r in range(random.randint(1,5)):
                    c = EdificioConsumo()
                    c.fecha_consumo = datetime.datetime(2019, mes, dia)
                    c.edificio = edificio
                    c.cantidad_consumida = random.randint(1,10) * random.random()
                    c.tipo = tipo
                    c.save()
                    
def AddConsumoVehiculo(vehiculo):
    persona=Personal.objects.get(id=getPersona(vehiculo.empresa).id)
    for mes in range(2,4):
        i=30
        if mes==2:
            i=29
        for dia in range (15,i):
            for tipo, nombre_tipo in TIPOS_VE:
                for r in range(random.randint(1,3)):
                    c = VehiculoConsumo()
                    c.fecha_consumo = datetime.datetime(2019, mes, dia)
                    c.vehiculo = vehiculo
                    c.cantidad_consumida = random.randint(1,10) * random.random()
                    c.tipo = tipo
                    c.personal = persona
                    c.save()
                    
def AddViaje():
    for empresa in Empresa.objects.all():
        persona=Personal.objects.filter(id=getPersona(empresa).id)
        for mes in range(3,5):
            for dia in range (7,15):
                for transporte, nombre_transporte in TRANSPORTES2:
                    for r in range(random.randint(1,5)):
                        v = Viaje()
                        v.fecha_viaje= datetime.datetime(2019, mes, dia)
                        v.distancia = random.randint(1,10) * random.random()
                        v.transporte = transporte
                        v.noches_hotel = random.randint(1,10)
                        v.save()
                        v.personal.set(persona)
                        
def AddGenerador():
    for edificio in Edificio.objects.all():
        for mes in range(3,7):
            for dia in [1,13,28]:
                for medios, nombre_medios in FUENTES:
                    for r in range(random.randint(1,5)):
                        g = Generador()
                        g.fecha_generacion = datetime.datetime(2019, mes, dia)
                        g.cantidad_generada = random.randint(1,10000)
                        g.medios = medios
                        g.edificio = edificio
                        g.save()


class Command(BaseCommand):
            
    def handle(self, *args, **options):
        Consumos()
