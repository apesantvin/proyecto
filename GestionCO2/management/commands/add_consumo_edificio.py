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

class Command(BaseCommand):
            
    def handle(self, *args, **options):
        for ed in Edificio.objects.all():
            AddConsumoEdificio(ed)
