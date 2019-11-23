import datetime
import random
from django.core.management.base import BaseCommand
from GestionCO2.models import *
from django.contrib.auth.models import User

class Command(BaseCommand):
   
    def handle(self, *args, **options):
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
