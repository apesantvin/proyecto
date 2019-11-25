from django.shortcuts import render, get_object_or_404, redirect
from GestionCO2.models import *
from .forms import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as do_login

def empresa_lista(request):
    datos = Empresa.objects.all().order_by('nombre_empresa')
    letras=[]
    letras.append(datos[0].nombre_empresa[0])
    empresa_por_alfabeto=[]
    misma_letra=[]
    for dato in datos:
        #if dato.permitido_publicar:
            if dato.nombre_empresa[0] not in letras:
                letras.append(dato.nombre_empresa[0])
                empresa_por_alfabeto.append(misma_letra)
                misma_letra=[]
                misma_letra.append(dato)
            else:
                misma_letra.append(dato)
    empresa_por_alfabeto.append(misma_letra)
    letras_palabras = []
    for i in range(len(letras)):
        letras_palabras.append([])
        letras_palabras[i].append(letras[i])
        letras_palabras[i].append(empresa_por_alfabeto[i])
    return render(request, 'GestionCO2/lista_empresas.html', {'datos':letras_palabras,'indexado':letras})

def empresa_detalles(request,pk):
    empresa = get_object_or_404(Empresa, pk=pk)
    return render(request, 'GestionCO2/empresa_detalles.html', {'empresa': empresa})

def añadir_empresa(request):
    if request.method == "POST":
        form = EmpresaForm(request.POST,request.FILES)
        if form.is_valid():
            empresa = form.save(commit=False)
            empresa.nombre_empresa=empresa.nombre_empresa.capitalize()
            empresa.usuario = request.user
            empresa.fecha_inscripcion = timezone.now()
            empresa.save()
            return redirect('empresa_detalles', pk=empresa.pk)
    else:
        form = EmpresaForm()
    return render(request, 'GestionCO2/añadir_empresa.html', {'form': form})

def register(request):
    form = UserCreationForm()
    form.fields['username'].help_text = None
    form.fields['password1'].help_text = None
    form.fields['password2'].help_text = None
    if request.method == "POST":
        form = UserCreationForm(data=request.POST)

        if form.is_valid():
            user = form.save()
            if user is not None:
                do_login(request, user)
                return redirect('/')
    return render(request, "registration/register.html", {'form': form})
