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

class Command(BaseCommand):
   
    def handle(self, *args, **options):
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
