from django.shortcuts import render, get_object_or_404, redirect
from GestionCO2.models import *
from .forms import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import login as do_login
from django.contrib.auth.decorators import login_required
import sqlite3, csv, datetime
from django.contrib import messages
from datetime import date
import altair as alt
import pandas as pd

#Vistas Empresa
def empresa_lista(request):
    datos = Empresa.objects.all().order_by('nombre_empresa')
    if datos: 
        letras=[]
        empresa_por_alfabeto=[]
        misma_letra=[]
        for dato in datos:
            if dato.permitido_publicar:
                if dato.nombre_empresa[0] not in letras:
                    letras.append(dato.nombre_empresa[0])
                    empresa_por_alfabeto.append(misma_letra)
                    misma_letra=[]
                    misma_letra.append(dato)
                else:
                    misma_letra.append(dato)
        empresa_por_alfabeto.append(misma_letra)
        letras_palabras = []
        j=0
        for i in range(len(letras)):
            letras_palabras.append([])
            letras_palabras[i].append(letras[i])
            if len(empresa_por_alfabeto[j]) == 0:
                j=j+1
            letras_palabras[i].append(empresa_por_alfabeto[j])
            j=j+1
        return render(request, 'GestionCO2/lista_empresas.html', {'datos':letras_palabras,'indexado':letras})
    else:
        return render(request, 'GestionCO2/lista_empresas.html', {'datos':[],'indexado':[]})

def empresa_detalles(request,pk):
    empresa = get_object_or_404(Empresa, pk=pk)
    min_year=calcular_year_minimo(empresa)
    if min_year==0:
        datos=0
        min_year=timezone.now().year
    else:
        datos=1
    consumos=Factores_conversion.objects.first()
    co2_anual=calcular_CO2_year(pk, min_year,consumos)
    co2_edificios=calcular_CO2_edificios(pk, min_year,consumos)
    co2_vehiculos=calcular_CO2_vehiculos(pk, min_year,consumos)
    co2_viajes=calcular_CO2_viajes(pk, min_year)
    fecha1=[]
    cantidad1=[]
    for dato in co2_anual:
        fecha1.append(dato[0])
        cantidad1.append(dato[1])
    source = pd.DataFrame({
            'a': fecha1,
            'b': cantidad1
            })

    grafico=alt.Chart(source).mark_bar().encode(
        x='a',
        y='b'
    )
    grafico.save('GestionCO2/templates/graficos/grafico.html', embed_options={'renderer':'svg'})
    return render(request, 'GestionCO2/empresa_detalles_principales.html', {'empresa': empresa, 'anual':co2_anual, 'edificios':co2_edificios, 'vehiculos':co2_vehiculos, 'viajes':co2_viajes, 'datos':datos})

@login_required
def empresa_configuracion(request, pk):
    tipo_consumo=['1','2','3','4']
    tipo_consumo_ve=['1','2','3']
    tama_vehiculo=['1','2','3']
    tipo_transporte=['1','2','3','4']
    medios=['1','2','3']
    e = get_object_or_404(Empresa, pk=pk)
    if request.method=='POST':
        form = leercsv(request.POST,request.FILES)
        if form.is_valid():
            CSV=form.save(commit=False)
            CSV.empresa=e
            CSV.save()
            with open('./media/'+str(CSV.CSV)) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=';')
                line_count = 0
                for row in csv_reader:
                    if line_count == 0:
                        if (e.nombre_empresa != row[0]):
                            messages.error(request, f'El nombre de la empresa en el csv ({row[0]}) no coincide')
                            return redirect('empresa_configuracion', pk=e.pk)
                        line_count += 1
                    else:
                        if row[0] == 'Personal':
                            Personal.objects.get_or_create(empresa=e, apellidos_persona=row[1], fecha_contratacion=row[2], nombre_persona=row[3])
                        elif row[0] == 'Vehiculo':
                            if row[3] in tama_vehiculo:
                                if row[4] in tipo_transporte:
                                    Vehiculo.objects.get_or_create(empresa=e, fecha_compra=row[1], matricula=row[2], tamano=row[3], tipo_tranporte=row[4])
                                else:
                                    messages.error(request, f'El tipo de transporte de la línea {line_count + 1} no existe en nuestra base de datos')
                                    return redirect('empresa_configuracion', pk=e.pk)
                            else:
                                messages.error(request, f'El tamaño del transporte de la línea {line_count + 1} no existe en nuestra base de datos')
                                return redirect('empresa_configuracion', pk=e.pk)
                        elif row[0] == 'Edificio':
                            Edificio.objects.get_or_create(empresa=e, nombre_edificio=row[1], localizacion=row[2],fecha_adquisicion=row[3])
                        elif row[0] == 'EdificioConsumo':
                            if row[2] in tipo_consumo:
                                edificios=Edificio.objects.filter(empresa=e)
                                nombre_edificios=[]
                                for edificio in edificios:
                                    nombre_edificios.append(edificio.nombre_edificio)
                                if row[1] in nombre_edificios:
                                    edif = Edificio.objects.get(empresa=e, nombre_edificio=row[1])
                                    f = row[4].split('-')
                                    if edif.fecha_adquisicion <= date(int(f[0]),int(f[1]),int(f[2])):
                                        EdificioConsumo.objects.get_or_create(edificio=edif, tipo=row[2], cantidad_consumida=row[3], fecha_consumo=row[4])
                                    else:
                                        messages.error(request, f'Las fechas introducidas en la linea {line_count + 1} no son correctas')
                                        return redirect('empresa_configuracion', pk=e.pk)
                                else:
                                    messages.error(request, f'El edificio de la línea {line_count + 1} no existe en la empresa')
                                    return redirect('empresa_configuracion', pk=e.pk)
                            else:
                                messages.error(request, f'Lo que usted ha consumido en la linea {line_count + 1} no existe en nuestra base de datos')
                                return redirect('empresa_configuracion', pk=e.pk)
                        elif row[0] == 'Generador':
                            if row[4] in medios:
                                edificios=Edificio.objects.filter(empresa=e)
                                nombre_edificios=[]
                                for edificio in edificios:
                                    nombre_edificios.append(edificio.nombre_edificio)
                                if row[1] in nombre_edificios:
                                    edif = Edificio.objects.get(empresa=e, nombre_edificio=row[1])
                                    f = row[3].split('-')
                                    if edif.fecha_adquisicion <= date(int(f[0]),int(f[1]),int(f[2])):
                                        EdificioConsumo.objects.get_or_create(edificio=edif, cantidad_generada=row[2], fecha_generacion=row[3], medios=row[4])
                                    else:
                                        messages.error(request, f'Las fechas introducidas en la linea {line_count + 1} no son correctas')
                                        return redirect('empresa_configuracion', pk=e.pk)
                                else:
                                    messages.error(request, f'El edificio de la línea {line_count + 1} no existe en la empresa')
                                    return redirect('empresa_configuracion', pk=e.pk)
                            else:
                                messages.error(request, f'El medio mediante el que usted ha generado en la linea {line_count + 1} no existe en nuestra base de datos')
                        elif row[0] == 'VehiculoConsumo':
                            if row[6] in tipo_consumo_ve:
                                vehiculos=Vehiculo.objects.filter(empresa=e)
                                personales=Personal.objects.filter(empresa=e)
                                nombre_personales=[]
                                matriculas=[]
                                for personal in personales:
                                    nombre_personales.append(str(personal.nombre_persona)+str(' ')+str(personal.apellidos_persona))
                                for vehiculo in vehiculos:
                                    matriculas.append(vehiculo.matricula)
                                persona=str(row[2])+str(' ')+str(row[1])
                                if (row[3] in matriculas) and (persona in nombre_personales):
                                    veh = Vehiculo.objects.get(empresa=e, matricula=row[3])
                                    pers = Personal.objects.get(empresa=e, apellidos_persona=row[1], nombre_persona=row[2])
                                    f = row[5].split('-')
                                    if veh.fecha_compra <= date(int(f[0]),int(f[1]),int(f[2])) and pers.fecha_contratacion <= date(int(f[0]),int(f[1]),int(f[2])):
                                        VehiculoConsumo.objects.get_or_create(personal=pers, vehiculo=veh, cantidad_consumida=row[4], fecha_consumo=row[5], tipo=row[6])
                                    else:
                                        messages.error(request, f'Las fechas introducidas en la linea {line_count + 1} no son correctas')
                                        return redirect('empresa_configuracion', pk=e.pk)
                                else:
                                    messages.error(request, f'La persona o el vehiculo de la línea {line_count + 1} no existe en la empresa')
                                    return redirect('empresa_configuracion', pk=e.pk)
                            else:
                                messages.error(request, f'El tipo de consumo que  usted ha generado en la linea {line_count + 1} no existe en nuestra base de datos')
                        elif row[0] == 'Viaje':
                            if row[6] in tipo_transporte:
                                personales=Personal.objects.filter(empresa=e)
                                nombre_personales=[]
                                for personal in personales:
                                    nombre_personales.append(str(personal.nombre_persona)+str(' ')+str(personal.apellidos_persona))
                                persona=str(row[2])+str(' ')+str(row[1])
                                if (persona in nombre_personales):
                                    pers = Personal.objects.get(empresa=e, apellidos_persona=row[1], nombre_persona=row[2])
                                    f = row[3].split('-')
                                    if pers.fecha_contratacion <= date(int(f[0]),int(f[1]),int(f[2])):
                                        Viaje.objects.get_or_create(fecha_viaje=row[3], personal=pers, distancia=row[4], transporte=row[5], noches_hotel=row[6])
                                    else:
                                        messages.error(request, f'Las fechas introducidas en la linea {line_count + 1} no son correctas')
                                        return redirect('empresa_configuracion', pk=e.pk)
                                else:
                                    messages.error(request, f'La persona de la línea {line_count + 1} no existe en la empresa')
                                    return redirect('empresa_configuracion', pk=e.pk)
                            else:
                                messages.error(request, f'El transporte que usted ha utilizado en la linea {line_count + 1} no existe en nuestra base de datos')
                        else:
                            messages.error(request, f'No se reconoce la linea {line_count + 1}')
                        line_count += 1
            messages.success(request, 'Datos del fichero añadidos con éxito')
            return redirect('empresa_configuracion', pk=e.pk)
    else:
        form = leercsv()
    return render(request, 'GestionCO2/empresa_configuracion.html', {'empresa': e,'form': form})

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
            messages.success(request, 'Personal añadido con éxito')
            return redirect('añadir_personal', pk=empresa.pk)
    else:
        form = PersonalEmpresaForm()
    return render(request, 'GestionCO2/añadir_datos_plantilla1.html', {'form': form, 'empresa': empresa, 'title':'Personal', 'error':error})

@login_required
def añadir_edificio(request, pk):
    empresa = get_object_or_404(Empresa, pk=pk)
    if request.method == "POST":
        form = EdificioEmpresaForm(request.POST)
        if form.is_valid():
            edificio = form.save(commit=False)
            edificio.empresa=empresa
            edificio.save()
            messages.success(request, 'Edificio añadido con éxito')
            return redirect('añadir_edificio', pk=empresa.pk)
    else:
        form = EdificioEmpresaForm()
    return render(request, 'GestionCO2/añadir_datos_plantilla1.html', {'form': form, 'empresa': empresa, 'title':'Edificio', 'error':'Error'})

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
            messages.success(request, 'Vehículo añadido con éxito')
            return redirect('añadir_vehiculo', pk=empresa.pk)
    else:
        form = VehiculoEdificioForm()
    return render(request, 'GestionCO2/añadir_datos_plantilla1.html', {'form': form, 'empresa': empresa, 'title':'Vehículo', 'error':error})

@login_required
def añadir_generador(request, pk):
    e = get_object_or_404(Empresa, pk=pk)
    error=0
    edificios = Edificio.objects.filter(empresa=e)
    if request.method == "POST":
        form = GeneradorEdificioForm(e,request.POST)
        if form.is_valid():
            generador = form.save(commit=False)
            if generador.fecha_generacion < generador.edificio.fecha_adquisicion:
                messages.error(request, 'Las fecha de la generación no es correcta. El edificio fue adquirido en una fecha posterior.')
                error=1
                return render(request, 'GestionCO2/añadir_datos_plantilla2.html', {'form': form, 'empresa': e, 'title':'Energía Generada', 'error':error, 'edificios':edificios})
            else:
                generador.save()
                messages.success(request, 'Energía generada añadido con éxito')
                return redirect('añadir_generador', pk=e.pk)
    else:
        form = GeneradorEdificioForm(e)
    return render(request, 'GestionCO2/añadir_datos_plantilla2.html', {'form': form, 'empresa': e, 'title':'Energía Generada', 'error':error, 'edificios':edificios})

@login_required
def añadir_viaje(request, pk):
    e = get_object_or_404(Empresa, pk=pk)
    error='ERROR'
    personal = Personal.objects.filter(empresa=e)
    if request.method == "POST":
        form = ViajeForm(e,request.POST)
        if form.is_valid():
            viaje = form.save(commit=True)
            viaje.save()
            messages.success(request, 'Viaje añadido con éxito')
            return redirect('añadir_viaje', pk=e.pk)
    else:
        form = ViajeForm(e)
    return render(request, 'GestionCO2/añadir_datos_plantilla2.html', {'form': form, 'empresa': e, 'title':'Viaje', 'error':error, 'edificios':personal})

@login_required
def añadir_consumoEdificio(request, pk):
    e = get_object_or_404(Empresa, pk=pk)
    error=0
    edificios = Edificio.objects.filter(empresa=e)
    if request.method == "POST":
        form = ConsumoEdificioForm(e,request.POST)
        if form.is_valid():
            consumo = form.save(commit=False)
            if consumo.fecha_consumo < consumo.edificio.fecha_adquisicion:
                messages.error(request, 'Las fecha de la generación no es correcta. El edificio fue adquirido en una fecha posterior.')
                error=1
                return render(request, 'GestionCO2/añadir_datos_plantilla2.html', {'form': form, 'empresa': e, 'title':'Consumo de Edificio', 'error':error, 'edificios':edificios})
            else:
                consumo.save()
                messages.success(request, 'Consumo edificio añadido con éxito')
                return redirect('añadir_consumoEdificio', pk=e.pk)
    else:
        form = ConsumoEdificioForm(e)
    return render(request, 'GestionCO2/añadir_datos_plantilla2.html', {'form': form, 'empresa': e, 'title':'Consumo de Edificio', 'error':error, 'edificios':edificios})

@login_required
def añadir_consumoVehiculo(request, pk):
    e = get_object_or_404(Empresa, pk=pk)
    error='Error'
    vehiculo = Vehiculo.objects.filter(empresa=e)
    personal = Personal.objects.filter(empresa=e)
    if request.method == "POST":
        form = ConsumoVehiculoForm(e,request.POST)
        if form.is_valid():
            consumo = form.save(commit=False)
            if consumo.fecha_consumo < consumo.vehiculo.fecha_compra:
                messages.error(request, 'Las fecha de la generación no es correcta. El vehículo fue adquirido en una fecha posterior.')
                error=1
                if consumo.fecha_consumo < consumo.personal.fecha_contratacion:
                    messages.error(request, 'Las fecha de la generación no es correcta. La persona fue contratada en una fecha posterior.')
                    error=1
                return render(request, 'GestionCO2/añadir_VehiculoConsumo.html', {'form': form, 'empresa': e, 'title':'Consumo de Vehiculo', 'error':error, 'vehiculo':vehiculo, 'personal':personal})
            else:
                if consumo.fecha_consumo < consumo.personal.fecha_contratacion:
                    messages.error(request, 'Las fecha de la generación no es correcta. La persona fue contratada en una fecha posterior.')
                    error=1
                    return render(request, 'GestionCO2/añadir_VehiculoConsumo.html', {'form': form, 'empresa': e, 'title':'Consumo de Vehiculo', 'error':error, 'vehiculo':vehiculo, 'personal':personal})
                else:
                    consumo.save()
                    messages.success(request, 'Consumo vehículo añadido con éxito')
                    return redirect('añadir_consumoVehiculo', pk=e.pk)
    else:
        form = ConsumoVehiculoForm(e)
    return render(request, 'GestionCO2/añadir_VehiculoConsumo.html', {'form': form, 'empresa': e, 'title':'Consumo de Vehiculo', 'error':error, 'vehiculo':vehiculo, 'personal':personal})

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

#Vistas Experto
@login_required
def mensajes_experto(request):
    lista_mensajes = Mensaje.objects.filter(respondido=0)
    explicacion='Aqui podras ver los mensajes que han mandado las empresas y todavía estan sin responder. Pulsando en cada uno de ellos, podrás responder a dicho mensaje. '
    return render(request, 'experto/inicio_experto.html',  {'lista_mensajes':lista_mensajes, 'add':explicacion})

@login_required
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

@login_required
def mensaje_detalles_experto(request, mensajePK):
    m = get_object_or_404(Mensaje, pk=mensajePK)
    return render(request, 'experto/mensaje_detalles_experto.html',  {'m' : m})

@login_required
def ask_for_experto(request):
    Experto.objects.create(usuario=request.user, id_usuario=request.user.id)
    return (mensajes_todos_experto(request))

@login_required
def add_experto(request, expertoPK):
    experto = get_object_or_404(Experto, pk=expertoPK)
    experto.autorizar()
    lista_expertos = Experto.objects.filter(autorizado=0)
    return render(request, 'experto/lista_expertos_añadir.html',  {'lista_expertos':lista_expertos})

@login_required
def eliminar_peticion_experto(request, expertoPK):
    experto = get_object_or_404(Experto, pk=expertoPK)
    experto.delete()
    lista_expertos = Experto.objects.filter(autorizado=0)
    return render(request, 'experto/lista_expertos_añadir.html',  {'lista_expertos':lista_expertos})

@login_required
def eliminar_experto_autorizado(request, expertoPK):
    experto = get_object_or_404(Experto, pk=expertoPK)
    experto.desautorizar()
    lista_expertos = Experto.objects.filter(autorizado=0)
    return render(request, 'experto/lista_expertos_eliminar.html',  {'lista_expertos':lista_expertos})

@login_required
def mensajes_empresa(request, pk):
    empresa = get_object_or_404(Empresa, pk=pk)
    lista_mensajes = Mensaje.objects.filter(empresa=empresa)
    explicacion='Aqui podras ver los mensajes que han mandado la empresa '+str(empresa)+'. Pulsando en cada uno de ellos, podrás ver la respuesta en caso de que tenga, caso contrario podrás responder al mensaje.'
    return render(request, 'experto/lista_mensajes_empresa.html',  {'lista_mensajes':lista_mensajes, 'add':explicacion})

@login_required
def lista_expertos_añadir(request):
    lista_expertos = Experto.objects.filter(autorizado=0)
    return render(request, 'experto/lista_expertos_añadir.html',  {'lista_expertos':lista_expertos})

@login_required
def lista_expertos_eliminar(request):
    lista_expertos = Experto.objects.filter(autorizado=1)
    return render(request, 'experto/lista_expertos_eliminar.html',  {'lista_expertos':lista_expertos})

@login_required
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

#Vistas CO2 generado
#CO2 generado por los edificios de una empresa en un año determinado
def edificio_year(empresa, year, consumo):
    edificios_consumos=[]
    fecha_edificio='fecha_adquisicion'
    edificios=Edificio.objects.filter(empresa=empresa).order_by(fecha_edificio)
    consumo_edificios=0;
    for edificio in edificios:
        fecha=edificio.fecha_adquisicion.year
        if (fecha <= year):
            consumo_edificios=consumo_edificios+edificio_consumo(edificio, year, consumo)
    return consumo_edificios

#Co2 generado en un edificio y un año                
def edificio_consumo(edificio, year, consumo):
    agua=edificio_consumo_tipo(edificio, year, consumo.Edificio_consumo_Agua,'1')
    electricidad=edificio_consumo_elec(edificio, year, consumo.Edificio_consumo_Electricidad,'2')
    aceite=edificio_consumo_tipo(edificio, year, consumo.Edificio_consumo_Aceite,'3')
    propano=edificio_consumo_tipo(edificio, year, consumo.Edificio_consumo_Propano,'4')
    gasNatural=edificio_consumo_tipo(edificio, year, consumo.Edificio_consumo_GasNatural,'5')
    return agua+aceite+electricidad+propano+gasNatural

#Co2 generado por un consumo en un edificio y un año
def edificio_consumo_tipo(edificio, year, consumo, tipo):
    total_consumo=0
    consumos=EdificioConsumo.objects.filter(edificio=edificio,tipo=tipo)
    for c in consumos:
        fecha=c.fecha_consumo.year
        if (fecha==year):
            total_consumo=total_consumo+(float(c.cantidad_consumida)*float(consumo))
    return total_consumo

def edificio_consumo_elec(edificio, year, consumo, tipo):
    total_consumo=0;
    consumos=EdificioConsumo.objects.filter(edificio=edificio,tipo=tipo).order_by('fecha_consumo')
    fecha_ant=date(year-1,12,31)
    fecha=date(year,1,1)
    generado=0
    indice=0
    huella=0
    while fecha.year<year+1 and indice<len(consumos):
        if fecha_ant<fecha:
            generado=generado+calcular_energiaGenerada(edificio, fecha)
        if consumos[indice].fecha_consumo==fecha:
            co2=float(consumos[indice].cantidad_consumida)-generado
            fecha_ant=fecha
            indice=indice+1
            if co2<=0:
                generado=abs(co2)
                huella = huella+0
            else:
                huella=huella+co2*float(consumo)
        elif consumos[indice].fecha_consumo<fecha:
            fecha_ant=fecha
            indice=indice+1
        else:
            fecha=fecha+datetime.timedelta(days=1)
    return huella

#Energía generada de por generadores (no genera co2)
def calcular_energiaGenerada(edificio, fecha):
    generado=0
    generadores=Generador.objects.filter(edificio=edificio, fecha_generacion=fecha)
    for generador in generadores:
        generado=generado+float(generador.cantidad_generada)
    return generado           

#CO2 generado por los vehiculos de una empresa en año determinado
def vehiculo_year(empresa, year, consumo):
    fecha_vehiculo='fecha_compra'
    vehiculos=Vehiculo.objects.filter(empresa=empresa).order_by(fecha_vehiculo)
    consumo_vehiculo=0;
    for vehiculo in vehiculos:
        fecha=vehiculo.fecha_compra.year
        if (fecha <= year):
            consumo_vehiculo=consumo_vehiculo+vehiculo_consumo(vehiculo, year, consumo)
    return consumo_vehiculo

#Co2 generado en un vehiculo y un año                
def vehiculo_consumo(vehiculo, year, consumo):
    electricidad=vehiculo_consumo_tipo(vehiculo, year, consumo.Vehiculo_consumo_Electricidad,'1')
    gasolina=vehiculo_consumo_tipo(vehiculo, year, consumo.Vehiculo_consumo_Gasolina,'2')
    diesel=vehiculo_consumo_tipo(vehiculo, year, consumo.Vehiculo_consumo_Diesel,'3')
    return electricidad+gasolina+diesel

#Co2 generado por un consumo en un vehiculo y un año
def vehiculo_consumo_tipo(vehiculo, year, consumo, tipo):
    total_consumo=0;
    consumos=VehiculoConsumo.objects.filter(vehiculo=vehiculo,tipo=tipo)
    for c in consumos:
        fecha=c.fecha_consumo.year
        if (fecha==year):
            total_consumo=total_consumo+(float(c.cantidad_consumida)*float(consumo))
    return total_consumo

#CO2 generado por los viajes de una empresa en año determinado
def viaje_year(empresa, year):
    co2_total=0;
    viajes=Viaje.objects.all()
    for viaje in viajes:
        fecha=viaje.fecha_viaje.year
        if (fecha==year):
            v='ok'
            personas=viaje.personal.all()
            for p in personas:
                if p.empresa != empresa:
                    v='not'
            if v=='ok':
                co2_total=co2_total+float(viaje.co2)
    return co2_total

#Calcular CO2 generado por la empresa en todos los años
def calcular_CO2_year(pk, min_year, consumos):
    empresa=get_object_or_404(Empresa, pk=pk)
    today_year=date.today().year
    matriz_co2=[]
    for year in range(min_year, today_year+1):
        co2_year=[]
        co2_year.append(year)
        edificio=edificio_year(empresa, year, consumos)
        vehiculo=vehiculo_year(empresa, year, consumos)
        viaje=viaje_year(empresa, year)
        co2_year.append(edificio+vehiculo+viaje)
        matriz_co2.append(co2_year)
    return matriz_co2

#Calcular CO2 generado por los edificios de la empresa en todos los años
def calcular_CO2_edificios(pk, min_year, consumos):
    empresa=get_object_or_404(Empresa, pk=pk)
    today_year=date.today().year
    matriz_co2=[]
    for year in range(min_year, today_year+1):
        co2_edificio=[]
        co2_edificio.append(year)
        co2_edificio.append(edificio_year(empresa, year, consumos))
        matriz_co2.append(co2_edificio)
    return matriz_co2

#Calcular CO2 generado por los vehiculos de la empresa en todos los años
def calcular_CO2_vehiculos(pk, min_year, consumos):
    empresa=get_object_or_404(Empresa, pk=pk)
    today_year=date.today().year
    matriz_co2=[]
    for year in range(min_year, today_year+1):
        co2_vehiculos=[]
        co2_vehiculos.append(year)
        co2_vehiculos.append(vehiculo_year(empresa, year, consumos))
        matriz_co2.append(co2_vehiculos)
    return matriz_co2

#Calcular CO2 generado por los viajes de la empresa en todos los años
def calcular_CO2_viajes(pk, min_year):
    empresa=get_object_or_404(Empresa, pk=pk)
    today_year=date.today().year
    matriz_co2=[]
    for year in range(min_year, today_year+1):
        co2_viajes=[]
        co2_viajes.append(year)
        co2_viajes.append(viaje_year(empresa, year))
        matriz_co2.append(co2_viajes)
    return matriz_co2

#Calculo del menor año del que ce conoce consumo
def calcular_year_minimo(empresa):
    fecha_consumo='fecha_consumo'
    edificios=Edificio.objects.filter(empresa=empresa)
    vehiculos=Vehiculo.objects.filter(empresa=empresa)
    personal=Personal.objects.filter(empresa=empresa)
    viajes=Viaje.objects.all()
    fecha_edificio=timezone.now().date()
    fecha_vehiculo=timezone.now().date()
    fecha_persona=timezone.now().date()
    ed=0
    ve=0
    vi=0
    for edificio in edificios:
        consumo_edificio=EdificioConsumo.objects.filter(edificio=edificio).order_by('fecha_consumo')
        if consumo_edificio.count() != 0:
            fecha_edificio=min(fecha_edificio, consumo_edificio[0].fecha_consumo)
            ed=ed+1
    for vehiculo in vehiculos:
        consumo_vehiculo=VehiculoConsumo.objects.filter(vehiculo=vehiculo).order_by('fecha_consumo')
        if consumo_vehiculo.count() != 0:
            fecha_vehiculo=min(fecha_vehiculo, consumo_vehiculo[0].fecha_consumo)
            vi=vi+1
    for viaje in viajes:
        personas=viaje.personal.all()
        for persona in personas:
            if persona.empresa==empresa:
                fecha_persona=min(fecha_persona,viaje.fecha_viaje)
                ve=ve+1
    fecha_minima=min(fecha_persona,fecha_vehiculo,fecha_edificio)
    if ed==0 and ve==0 and vi==0:
        return 0
    else:
        return fecha_minima.year
