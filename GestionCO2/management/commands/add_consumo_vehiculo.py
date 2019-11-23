import datetime
import random
from django.core.management.base import BaseCommand
from GestionCO2.models import *
from django.contrib.auth.models import User


def getPersona(empresa):
    e=Empresa.objects.get(nombre_empresa=empresa)
    p=Personal.objects.filter(empresa=e)
    for people in p:
        persona=people
        break
    return persona
                    
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
                    

class Command(BaseCommand):
            
    def handle(self, *args, **options):
        for vehiculo in Vehiculo.objects.all():
            AddConsumoVehiculo(vehiculo)
