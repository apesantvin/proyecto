from django.shortcuts import render
from GestionCO2.models import *

def empresa_lista(request):
    datos = Empresa.objects.all()
    return render(request, 'GestionCO2/empresa_lista.html', {'datos':datos, 'Nombre':'Personas'})

# Create your views here.
