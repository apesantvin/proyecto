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
            if dato.permitido_publicar or dato.usuario==request.user:
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
        lista_tus_empresas=[]
        if request.user.is_authenticated:
            lista_tus_empresas=Empresa.objects.filter(usuario=request.user)
        return render(request, 'GestionCO2/lista_empresas.html', {'datos':letras_palabras,'indexado':letras, 'lista_tus_empresas':lista_tus_empresas})
    else:
        return render(request, 'GestionCO2/lista_empresas.html', {'datos':[],'indexado':[],'lista_tus_empresas':[]})

def empresa_detalles(request,pk):
    empresa = get_object_or_404(Empresa, pk=pk)
    consumos=Factores_conversion.objects.first()
    co2_anual=CO2_Empresa_Año.objects.filter(empresa=empresa,Graf='1')
    co2_edificios=CO2_Empresa_Año.objects.filter(empresa=empresa,Graf='2')
    co2_viajes=CO2_Empresa_Año.objects.filter(empresa=empresa,Graf='3')
    co2_vehiculos=CO2_Empresa_Año.objects.filter(empresa=empresa,Graf='4')
    def crear_gráficas(lista,numero):
        fecha1=[]
        cantidad1=[]
        for dato in lista:
            fecha1.append(dato.Año)
            cantidad1.append(float(dato.CO2_generado))
        source = pd.DataFrame({
                'a': fecha1,
                'b': cantidad1
                })

        grafico=alt.Chart(source).mark_bar().encode(
            x='a',
            y='b'
        )
        grafico.save('GestionCO2/templates/graficos/grafico'+str(numero)+'.html')
    if co2_anual.exists() or co2_edificios.exists() or co2_viajes.exists() or co2_vehiculos.exists():
        datos=1
        crear_gráficas(co2_anual,'1')
        crear_gráficas(co2_edificios,'2')
        crear_gráficas(co2_viajes,'3')
        crear_gráficas(co2_vehiculos,'4')
    else:
        datos=0
    return render(request, 'GestionCO2/empresa_detalles_principales.html', {'empresa': empresa, 'edificios':co2_edificios, 'vehiculos':co2_vehiculos, 'viajes':co2_viajes, 'datos':datos})

def mostrar_grafico (request, Gpk):
    return render(request, 'graficos/grafico'+str(Gpk)+'.html')

@login_required
def publicar_empresa (request,pk):
    empresa = get_object_or_404(Empresa, pk=pk)
    empresa.publicar()
    return redirect('empresa_detalles', pk=empresa.pk)

@login_required
def actualizar_datos(request,pk):
    empresa = get_object_or_404(Empresa, pk=pk)
    consumos=Factores_conversion.objects.first()
    co2_edificios=calcular_consumo_Edificio(empresa,consumos)
    co2_vehiculos=calcular_consumo_vehiculos(empresa,consumos)
    co2_viajes=calcular_consumo_viajes(empresa,consumos)
    co2_anual=[]
    for datos in co2_edificios:
        co2_anual.append(datos)
    for datos in co2_vehiculos:
        co2_anual.append(datos)
    for datos in co2_viajes:
        co2_anual.append(datos)
    co2_anual=ordenar_agrupar(co2_anual)
    TotalAños=CO2_Empresa_Año.objects.filter(empresa=empresa,Graf='1')
    for dato in TotalAños:
        dato.delete()
    for dato in co2_anual:
        CO2_Empresa_Año.objects.create(empresa=empresa,Año=dato[0],CO2_generado=float(dato[1]),Graf='1')
        
    TotalAños=CO2_Empresa_Año.objects.filter(empresa=empresa,Graf='2')
    for dato in TotalAños:
        dato.delete()
    for dato in co2_edificios:
        CO2_Empresa_Año.objects.create(empresa=empresa,Año=dato[0],CO2_generado=float(dato[1]),Graf='2')
        
    TotalAños=CO2_Empresa_Año.objects.filter(empresa=empresa,Graf='3')
    for dato in TotalAños:
        dato.delete()
    for dato in co2_viajes:
        CO2_Empresa_Año.objects.create(empresa=empresa,Año=dato[0],CO2_generado=float(dato[1]),Graf='3')
        
    TotalAños=CO2_Empresa_Año.objects.filter(empresa=empresa,Graf='4')
    for dato in TotalAños:
        dato.delete()
    for dato in co2_vehiculos:
        CO2_Empresa_Año.objects.create(empresa=empresa,Año=dato[0],CO2_generado=float(dato[1]),Graf='4')

    return redirect('empresa_detalles', pk=empresa.pk)

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
                            return render(request, 'GestionCO2/empresa_configuracion.html', {'empresa': e,'form': form})
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
                                    return render(request, 'GestionCO2/empresa_configuracion.html', {'empresa': e,'form': form})
                            else:
                                messages.error(request, f'El tamaño del transporte de la línea {line_count + 1} no existe en nuestra base de datos')
                                return render(request, 'GestionCO2/empresa_configuracion.html', {'empresa': e,'form': form})
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
                                        return render(request, 'GestionCO2/empresa_configuracion.html', {'empresa': e,'form': form})
                                else:
                                    messages.error(request, f'El edificio de la línea {line_count + 1} no existe en la empresa')
                                    return render(request, 'GestionCO2/empresa_configuracion.html', {'empresa': e,'form': form})
                            else:
                                messages.error(request, f'Lo que usted ha consumido en la linea {line_count + 1} no existe en nuestra base de datos')
                                return render(request, 'GestionCO2/empresa_configuracion.html', {'empresa': e,'form': form})
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
                                        Generador.objects.get_or_create(edificio=edif, cantidad_generada=row[2], fecha_generacion=row[3], medios=row[4])
                                    else:
                                        messages.error(request, f'Las fechas introducidas en la linea {line_count + 1} no son correctas')
                                        return render(request, 'GestionCO2/empresa_configuracion.html', {'empresa': e,'form': form})
                                else:
                                    messages.error(request, f'El edificio de la línea {line_count + 1} no existe en la empresa')
                                    return render(request, 'GestionCO2/empresa_configuracion.html', {'empresa': e,'form': form})
                            else:
                                messages.error(request, f'El medio mediante el que usted ha generado en la linea {line_count + 1} no existe en nuestra base de datos')
                                return render(request, 'GestionCO2/empresa_configuracion.html', {'empresa': e,'form': form})
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
                                        return render(request, 'GestionCO2/empresa_configuracion.html', {'empresa': e,'form': form})
                                else:
                                    messages.error(request, f'La persona o el vehiculo de la línea {line_count + 1} no existe en la empresa')
                                    return render(request, 'GestionCO2/empresa_configuracion.html', {'empresa': e,'form': form})
                            else:
                                messages.error(request, f'El tipo de consumo que  usted ha generado en la linea {line_count + 1} no existe en nuestra base de datos')
                                return render(request, 'GestionCO2/empresa_configuracion.html', {'empresa': e,'form': form})
                        elif row[0] == 'Viaje':
                            if row[5] in tipo_transporte:
                                personales=Personal.objects.filter(empresa=e)
                                nombre_personales=[]
                                for personal in personales:
                                    nombre_personales.append(str(personal.nombre_persona)+str(' ')+str(personal.apellidos_persona))
                                persona=str(row[2])+str(' ')+str(row[1])
                                if (persona in nombre_personales):
                                    pers = Personal.objects.get(empresa=e, apellidos_persona=row[1], nombre_persona=row[2])
                                    f = row[3].split('-')
                                    if pers.fecha_contratacion <= date(int(f[0]),int(f[1]),int(f[2])):
                                        vi=Viaje.objects.get_or_create(fecha_viaje=row[3],distancia=row[4], transporte=row[5],noches_hotel=row[6])
                                        vi[0].personal.add(pers)
                                        vi[0].save()
                                    else:
                                        messages.error(request, f'Las fechas introducidas en la linea {line_count + 1} no son correctas')
                                        return render(request, 'GestionCO2/empresa_configuracion.html', {'empresa': e,'form': form})
                                else:
                                    messages.error(request, f'La persona de la línea {line_count + 1} no existe en la empresa')
                                    return render(request, 'GestionCO2/empresa_configuracion.html', {'empresa': e,'form': form})
                            else:
                                messages.error(request, f'El transporte que usted ha utilizado en la linea {line_count + 1} no existe en nuestra base de datos')
                                return render(request, 'GestionCO2/empresa_configuracion.html', {'empresa': e,'form': form})
                        else:
                            messages.error(request, f'No se reconoce la linea {line_count + 1}')
                            return render(request, 'GestionCO2/empresa_configuracion.html', {'empresa': e,'form': form})
                        line_count += 1
            messages.success(request, 'Datos del fichero añadidos con éxito')
            return render(request, 'GestionCO2/empresa_configuracion.html', {'empresa': e,'form': form})
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

def ordenar_agrupar(lista):
    lista.sort()
    nuevamatriz=[]
    nuevamatriz.append([])
    i=0
    nuevamatriz[0].append(lista[0][0])
    nuevamatriz[0].append(0)
    for dato in lista:
        if dato[0]==nuevamatriz[i][0]:
            nuevamatriz[i][1]=nuevamatriz[i][1]+dato[1]
        else:
            nuevamatriz.append([])
            i=i+1
            nuevamatriz[i].append(dato[0])
            nuevamatriz[i].append(dato[1])
    return nuevamatriz

def calcular_consumo_Edificio(empresa,factores):
    edificios=Edificio.objects.filter(empresa=empresa)
    matriz=[]
    i=0
    for edificio in edificios:
        consumos=EdificioConsumo.objects.filter(edificio=edificio)
        for consumo in consumos:
            matriz.append([])
            matriz[i].append(consumo.fecha_consumo.year)
            factor=0
            if consumo.tipo=='1' or consumo.tipo=='Agua' :
                factor=float(factores.Edificio_consumo_Agua)
            elif consumo.tipo=='2' or consumo.tipo=='Electricidad' :
                factor=float(factores.Edificio_consumo_Electricidad)
            elif consumo.tipo=='3' or consumo.tipo=='Aceite' :
                factor=float(factores.Edificio_consumo_Aceite)
            elif consumo.tipo=='4' or consumo.tipo=='Propano':
                factor=float(factores.Edificio_consumo_Propano)
            elif consumo.tipo=='5' or consumo.tipo=='Gas Natural' :
                factor=float(factores.Edificio_consumo_GasNatural)
            matriz[i].append(float(consumo.cantidad_consumida)*factor)
            i=i+1
    if matriz != []:
        nuevamatriz=ordenar_agrupar(matriz)
    else:
        nuevamatriz=matriz
    return nuevamatriz

def calcular_consumo_vehiculos(empresa,factores):
    vehiculos=Vehiculo.objects.filter(empresa=empresa)
    matriz=[]
    i=0
    for vehiculo in vehiculos:
        consumos=VehiculoConsumo.objects.filter(vehiculo=vehiculo)
        for consumo in consumos:
            matriz.append([])
            matriz[i].append(consumo.fecha_consumo.year)
            factor=0
            if consumo.tipo=='1' or consumo.tipo=='Electricidad' :
                factor=float(factores.Vehiculo_consumo_Electricidad)
            elif consumo.tipo=='2' or consumo.tipo=='Gasolina' :
                factor=float(factores.Vehiculo_consumo_Gasolina)
            elif consumo.tipo=='3' or consumo.tipo=='Diesel':
                factor=float(factores.Vehiculo_consumo_Diesel)
            matriz[i].append(float(consumo.cantidad_consumida)*factor)
            i=i+1
    if matriz != []:
        nuevamatriz=ordenar_agrupar(matriz)
    else:
        nuevamatriz=matriz
    return nuevamatriz

def calcular_consumo_viajes(empresa,factores):
    viajes=Viaje.objects.all()
    matriz=[]
    i=0
    for viaje in viajes:
        pers = viaje.personal.all()
        if pers[0].empresa==empresa:
            matriz.append([])
            matriz[i].append(viaje.fecha_viaje.year)
            matriz[i].append(viaje.co2+viaje.noches_hotel*float(factores.Viaje_consumo_noches))
            i=i+1
    if matriz != []:
        nuevamatriz=ordenar_agrupar(matriz)
    else:
        nuevamatriz=matriz
    return nuevamatriz
