from django.contrib import admin
from .models import *

admin.site.register(Empresa)
admin.site.register(Edificio)
admin.site.register(Generador)
admin.site.register(Personal)
admin.site.register(Vehiculo)
admin.site.register(Viaje)
admin.site.register(EdificioConsumo)
admin.site.register(VehiculoConsumo)
# Register your models here.
