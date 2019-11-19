from django.shortcuts import render, get_object_or_404, redirect
from GestionCO2.models import *
from .forms import *

def empresa_lista(request):
    datos = Empresa.objects.all()
    return render(request, 'GestionCO2/lista_empresas.html', {'datos':datos, 'Nombre':'Personas'})

def empresa_detalles(request,pk):
    empresa = get_object_or_404(Empresa, pk=pk)
    return render(request, 'GestionCO2/empresa_detalles.html', {'empresa': empresa})

def añadir_empresa(request):
    if request.method == "Empresa":
        form = EmpresaForm(request.Empresa)
        if form.is_valid():
            empresa = form.save(commit=False)
            empresa.usuario = request.user
            empresa.fecha_inscripcion = timezone.now()
            empresa.save()
            return redirect('empresa_detalles', pk=empresa.pk)
    else:
        form = EmpresaForm()
    return render(request, 'GestionCO2/añadir_empresa.html', {'form': form})
# Create your views here.
