from django.shortcuts import render, get_object_or_404, redirect
from GestionCO2.models import *
from .forms import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import login as do_login
from django.contrib.auth.decorators import login_required

def empresa_lista(request):
    datos = Empresa.objects.all().order_by('nombre_empresa')
    if datos: 
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
    else:
        return render(request, 'GestionCO2/lista_empresas.html', {'datos':[],'indexado':[]})

def empresa_detalles(request,pk):
    empresa = get_object_or_404(Empresa, pk=pk)
    return render(request, 'GestionCO2/empresa_detalles_principales.html', {'empresa': empresa})

@login_required
def empresa_configuracion(request, pk):
    empresa = get_object_or_404(Empresa, pk=pk)
    if request.method=='POST':
        form = leercsv(request.POST,request.FILES)
        if form.is_valid():
            CSV=form.save(commit=False)
            return redirect('empresa_detalles', pk=empresa.pk)
    else:
        form = leercsv()
    return render(request, 'GestionCO2/empresa_configuracion.html', {'empresa': empresa,'form': form})

@login_required
def empresa_configuracion_cambios(request, pk):
    empresa = get_object_or_404(Empresa, pk=pk)
    return render(request, 'GestionCO2/empresa_configuracion_cambios.html', {'empresa': empresa})

@login_required
def añadir_datos_empresa(request, pk):
    empresa = get_object_or_404(Empresa, pk=pk)
    return render(request, 'GestionCO2/añadir_datos_empresa.html', {'empresa': empresa})

@login_required
def mensajes(request, pk):
    e = get_object_or_404(Empresa, pk=pk)
    lista_mensajes = Mensaje.objects.filter(empresa=e)
    return render(request, 'GestionCO2/mensajes.html',  {'empresa': e, 'lista_mensajes':lista_mensajes})

@login_required
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
    return render(request, 'GestionCO2/añadir_empresa.html', {'form': form} )

@login_required
def añadir_personal(request, pk):
    empresa = get_object_or_404(Empresa, pk=pk)
    error='Error'
    if request.method == "POST":
        form = PersonalEmpresaForm(request.POST,request.FILES)
        if form.is_valid():
            personal = form.save(commit=False)
            personal.empresa=empresa
            personal.save()
            return redirect('añadir_personal', pk=empresa.pk)
    else:
        form = PersonalEmpresaForm()
    return render(request, 'GestionCO2/añadir_datos_html.html', {'form': form, 'empresa': empresa, 'title':'Personal', 'error':error})

@login_required
def añadir_edificio(request, pk):
    empresa = get_object_or_404(Empresa, pk=pk)
    if request.method == "POST":
        form = EdificioEmpresaForm(request.POST)
        if form.is_valid():
            edificio = form.save(commit=False)
            edificio.empresa=empresa
            edificio.save()
            return redirect('añadir_edificio', pk=empresa.pk)
    else:
        form = EdificioEmpresaForm()
    return render(request, 'GestionCO2/añadir_datos_html.html', {'form': form, 'empresa': empresa, 'title':'Edificio', 'error':'Error'})

@login_required
def añadir_vehiculo(request, pk):
    empresa = get_object_or_404(Empresa, pk=pk)
    error='Error'
    if request.method == "POST":
        form = VehiculoEdificioForm(request.POST,request.FILES)
        if form.is_valid():
            vehiculo = form.save(commit=False)
            vehiculo.empresa=empresa
            vehiculo.save()
            return redirect('añadir_vehiculo', pk=empresa.pk)
    else:
        form = VehiculoEdificioForm()
    return render(request, 'GestionCO2/añadir_datos_html.html', {'form': form, 'empresa': empresa, 'title':'Vehículo', 'error':error})

@login_required
def añadir_generador(request, pk):
    e = get_object_or_404(Empresa, pk=pk)
    error='Error'
    edificios = Edificio.objects.filter(empresa=e)
    edificios_list = [edif.nombre_edificio for edif in edificios]
    if request.method == "POST":
        form = GeneradorEdificioForm(request.POST,edificios_list)
        if form.is_valid():
            generador = form.save(commit=False)
            generador.empresa=e
            generador.save()
            return redirect('añadir_generador', pk=e.pk)
    else:
        form = GeneradorEdificioForm(edificios_list)
    return render(request, 'GestionCO2/añadir_datos_html_generador.html', {'form': form, 'empresa': e, 'title':'consumo de Generador', 'error':error, 'edificios':edificios})

@login_required
def register(request):
    form = formularioregistroForm()
    form.fields['username'].help_text = None
    form.fields['password1'].help_text = None
    form.fields['password2'].help_text = None
    if request.method == 'POST':
        form = formularioregistroForm(request.POST)     # create form object
        if form.is_valid():
            user=form.save()
            if user is not None:
                do_login(request, user)
                return redirect('pagina_principal')
    return render(request, 'registration/register.html', {'form':form})

def pagina_principal(request):
    return render(request, 'GestionCO2/pagina_principal.html')
