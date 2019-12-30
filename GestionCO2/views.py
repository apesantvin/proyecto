from django.shortcuts import render, get_object_or_404, redirect
from GestionCO2.models import *
from .forms import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import login as do_login
from django.contrib.auth.decorators import login_required
import sqlite3

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
def mensaje_detalles(request, pk, mensajePK):
    e = get_object_or_404(Empresa, pk=pk)
    m = get_object_or_404(Mensaje, pk=mensajePK)
    return render(request, 'GestionCO2/mensaje_detalles.html',  {'empresa': e, 'm' : m})
@login_required
def añadir_mensaje(request, pk):
    e = get_object_or_404(Empresa, pk=pk)
    if request.method == "POST":
        form = mensajeForm(request.POST)
        if form.is_valid():
            mensaje = form.save(commit=False)
            mensaje.empresa = e
            mensaje.fecha_publicacion=timezone.now()
            mensaje.preguntar()
            return redirect('mensajes', pk=e.pk)
    else:
        form = mensajeForm()
    return render(request, 'GestionCO2/añadir_mensaje.html', {'empresa': e, 'form':form})
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
    edificios = Edificio.objects.filter(empresa=e)
    error='Error'
    if request.method == "POST":
        form = GeneradorEdificioForm(request.POST,request.FILES)
        if form.is_valid():
            generador = form.save(commit=False)
            if generador.edificio in edificios:
                generador.save()
                return redirect('añadir_generador', pk=e.pk)
            else:
                error='No tienes dominio sobre el edificio. No pertenece a la empresa '
    else:
        form = GeneradorEdificioForm()
    return render(request, 'GestionCO2/añadir_datos_html.html', {'form': form, 'empresa': e, 'title':'consumo de Generador', 'error':error})

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

def mensajes_experto(request):
    lista_mensajes = Mensaje.objects.filter(respondido=0)
    explicacion='Aqui podras ver los mensajes que han mandado las empresas y todavía estan sin responder. Pulsando en cada uno de ellos, podrás responder a dicho mensaje. '
    return render(request, 'experto/inicio_experto.html',  {'lista_mensajes':lista_mensajes, 'add':explicacion})
        

def experto_mensaje(request, mensajePK):
    mensaje = get_object_or_404(Mensaje, pk=mensajePK)
    if request.method == "POST":
        form = RespuestaForm(request.POST)
        if form.is_valid():
            respuesta = form.save(commit=False)
            respuesta.mensaje = mensaje
            respuesta.fecha_publicacion_respuesta=timezone.now()
            respuesta.save()
            mensaje.responder()
            return redirect('mensaje_detalles_experto', mensajePK=mensaje.pk)
    else:
        form = RespuestaForm()
    return render(request, 'experto/experto_mensaje.html',  {'form': form, 'm':mensaje})

def mensaje_detalles_experto(request, mensajePK):
    m = get_object_or_404(Mensaje, pk=mensajePK)
    return render(request, 'experto/mensaje_detalles_experto.html',  {'m' : m})

def ask_for_experto(request):
    form = ExpertoForm(request.POST,request.FILES)
    if form.is_valid():
        experto = form.save(commit=False)
        experto.usuario = request.user
        experto.id_usuario = request.user.id
        experto.save()
    return (mensajes_todos_experto(request))

def add_experto(request, expertoPK):
    experto = get_object_or_404(Experto, pk=expertoPK)
    experto.autorizar()
    lista_expertos = Experto.objects.filter(autorizado=0)
    return render(request, 'experto/lista_expertos_añadir.html',  {'lista_expertos':lista_expertos})

def mensajes_empresa(request, pk):
    empresa = get_object_or_404(Empresa, pk=pk)
    lista_mensajes = Mensaje.objects.filter(empresa=empresa)
    explicacion='Aqui podras ver los mensajes que han mandado la empresa '+str(empresa)+'. Pulsando en cada uno de ellos, podrás ver la respuesta en caso de que tenga, caso contrario podrás responder al mensaje.'
    return render(request, 'experto/lista_mensajes_empresa.html',  {'lista_mensajes':lista_mensajes, 'add':explicacion})

def lista_expertos_añadir(request):
    lista_expertos = Experto.objects.filter(autorizado=0)
    return render(request, 'experto/lista_expertos_añadir.html',  {'lista_expertos':lista_expertos})
    
def mensajes_todos_experto(request):
    no_experto=0;
    lista_expertos = Experto.objects.all()
    if lista_expertos.exists():
        for l in lista_expertos:
            if request.user.id == l.id_usuario:
                if l.autorizado==0:
                    no_experto=0;
                    return render(request, 'experto/base_base_experto.html', {'experto':no_experto})
                else:
                    no_experto=0;
                    lista_mensajes = Mensaje.objects.all()
                    explicacion='Aqui podras ver los mensajes que han mandado las empresas que ya están respondidos. '
                    return render(request, 'experto/inicio_experto.html',  {'lista_mensajes':lista_mensajes, 'add':explicacion})
            else:
                if request.user.is_superuser:
                    lista_mensajes = Mensaje.objects.all()
                    explicacion='Aqui podras ver los mensajes que han mandado las empresas que ya están respondidos. '
                    return render(request, 'experto/inicio_experto.html',  {'lista_mensajes':lista_mensajes, 'add':explicacion})
                else:
                    no_experto=1;
    else:
        if request.user.is_superuser:
            lista_mensajes = Mensaje.objects.all()
            explicacion='Aqui podras ver los mensajes que han mandado las empresas que ya están respondidos. '
            return render(request, 'experto/inicio_experto.html',  {'lista_mensajes':lista_mensajes, 'add':explicacion})
        else:
            no_experto=1;
    if no_experto==1:
        return render(request, 'experto/base_base_experto.html', {'experto':no_experto})
