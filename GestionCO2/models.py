from django.db import models
from django.utils import timezone
from urllib.request import urlopen
import json

TRANSPORTES2=(
    ('1', 'Coche'),
    ('2', 'Avión'),
    ('3', 'Autobus'),
    ('4', 'Tren'),
)

TIPOS_ED = (
    ('1', 'Agua'),
    ('2', 'Electricidad'),
    ('3', 'Aceite'),
    ('4', 'Propano'),
    ('5', 'Gas Natural'),
)

TIPOS_VE= (
    ('1', 'Electricidad'),
    ('2', 'Gasolina'),
    ('3', 'Diesel'),
)

FUENTES = (
    ('1', 'Paneles Solares'),
    ('2', 'Molinos Eólicos'),
    ('3', 'Otros...'),
)

# Create your models here.
class Empresa(models.Model):
    usuario = models.ForeignKey('auth.User',on_delete=models.CASCADE)
    nombre_empresa = models.CharField(max_length=50)
    logo=models.ImageField(upload_to='logos')
    descripcion = models.TextField()
    telefono = models.IntegerField()
    correo = models.EmailField() 
    fecha_inscripcion = models.DateField('Fecha de inscripcion',default=timezone.now)
    permitido_publicar= models.BooleanField(default=False)
    
    def publicar(self):
        self.permitido_publicar=True
        self.save()
    
    def __str__(self):
        return (self.nombre_empresa)
    
class Edificio(models.Model):
    empresa = models.ForeignKey('Empresa',on_delete=models.CASCADE)
    nombre_edificio= models.CharField(max_length=30)
    localizacion = models.CharField(max_length=50)
    fecha_adquisicion = models.DateField('Fecha contratación',blank=True, null=True)
    
    def __str__(self):
        return self.nombre_edificio
    
class Generador(models.Model):
    edificio = models.ForeignKey('Edificio',on_delete=models.CASCADE)
    medios = models.CharField('Tipo de Generador',max_length=50,choices=FUENTES)
    cantidad_generada = models.IntegerField(help_text='en KWH')
    fecha_generacion= models.DateField('Fecha de la generación')
    
    def __str__(self):
        return str(self.id)
    
class Vehiculo(models.Model):
    TRANSPORTES=(
        ('1', 'Coche'),
        ('2', 'Moto'),
        ('3', 'Autobus'),
        ('4', 'Camión'),
    )
    TAMANOS = (
        ('1', 'Pequeño'),
        ('2', 'Mediano'),
        ('3', 'Grande'),
    )
    empresa = models.ForeignKey('Empresa',on_delete=models.CASCADE)
    tipo_tranporte=models.CharField('Vehiculo',max_length=50,choices=TRANSPORTES)
    matricula = models.CharField(max_length=8)
    tamano = models.CharField('Tamaño',max_length=50,choices=TAMANOS)
    fecha_compra = models.DateField('Fecha compra')
    
    def __str__(self):
        return self.matricula

class Personal(models.Model):
    empresa = models.ForeignKey('Empresa',on_delete=models.CASCADE)
    nombre_persona = models.CharField('Nombre',max_length=25)
    apellidos_persona= models.CharField('Apellidos',max_length=30)
    fecha_contratacion = models.DateField('Fecha contratacion')
    
    def __str__(self):
        return '{0} {1}'.format(self.nombre_persona,self.apellidos_persona)

class Viaje(models.Model):
    fecha_viaje = models.DateField(default=timezone.now)
    personal = models.ManyToManyField('Personal')
    distancia = models.DecimalField(max_digits=5, decimal_places=2,default=0)
    transporte = models.CharField(max_length=50,choices=TRANSPORTES2)
    noches_hotel = models.IntegerField('Noches en hotel',default=0)
    
    @property
    def co2(self):
        if self.transporte == '1':
            api_url = 'https://api.triptocarbon.xyz/v1/footprint?activity=1&activityType=miles&country=def&mode=anyCar'
        elif self.transporte == '2':
            api_url = 'https://api.triptocarbon.xyz/v1/footprint?activity=1&activityType=miles&country=def&mode=anyFlight'
        elif self.transporte == '3':
            api_url = 'https://api.triptocarbon.xyz/v1/footprint?activity=1&activityType=miles&country=def&mode=bus'
        elif self.transporte == '4':
            api_url = 'https://api.triptocarbon.xyz/v1/footprint?activity=1&activityType=miles&country=def&mode=transitRail'
        response = urlopen(api_url)
        datos_web=json.loads(response.read())
            
        return float(self.distancia) * 0.621371 * float(datos_web['carbonFootprint'])

    def __str__(self):
        return '{0}'.format(self.fecha_viaje)
    
class Consumo(models.Model):
    cantidad_consumida = models.DecimalField(max_digits=5, decimal_places=2)
    fecha_consumo= models.DateField('Fecha del consumo')
    
class EdificioConsumo(Consumo):
    edificio = models.ForeignKey('Edificio',on_delete=models.CASCADE)
    tipo = models.CharField('¿Que ha consumido?',max_length=50,choices=TIPOS_ED)
    
    def __str__(self):
        return str(self.id)
    
class VehiculoConsumo(Consumo):
    personal = models.ForeignKey('Personal',on_delete=models.CASCADE)
    vehiculo = models.ForeignKey('Vehiculo',on_delete=models.CASCADE)
    tipo = models.CharField('¿Que ha consumido?',max_length=50,choices=TIPOS_VE)
    
    def __str__(self):
        return str(self.id)
    
class Mensaje (models.Model):
    empresa = models.ForeignKey('Empresa',on_delete=models.CASCADE)        
    titulo = models.CharField(max_length=200)        
    texto = models.TextField()        
    fecha_publicacion_mensaje = models.DateTimeField(default=timezone.now)        
    respondido = models.IntegerField(default=0)
    
    def responder(self):
        self.respondido = 1
        self.save()
        
    def preguntar(self):
        self.respondido = 0
        self.save()
        
    def __str__(self):
        return self.titulo
    
class Respuesta(models.Model):
    mensaje = models.ForeignKey('Mensaje', on_delete=models.CASCADE, related_name='respuestas')
    texto = models.TextField(default='', blank=True, null=True)  
    fecha_publicacion_respuesta = models.DateTimeField(default=timezone.now)    

    def __str__(self):
        return self.texto

class Experto(models.Model):
    usuario = models.ForeignKey('auth.User',on_delete=models.CASCADE)
    id_usuario = models.IntegerField(default=0, unique=True)
    autorizado = models.IntegerField(default=0)
    
    def desautorizar(self):
        self.autorizado = 0
        self.save()
    
    def autorizar(self):
        self.autorizado = 1
        self.save()
    
    def __str__(self):
        return str(self.usuario)
    
class CSVs(models.Model):
    empresa = models.ForeignKey('Empresa',on_delete=models.CASCADE)
    CSV=models.FileField(upload_to='CSVs/')
    fecha_subida=models.DateTimeField(default=timezone.now)
    
class Factores_conversion(models.Model):
    #Kilogramos de CO2 por persona en las 8 horas medias de trabajo
    persona = models.DecimalField(max_digits=5, decimal_places=2,default=0.72*60*8)
    #Kilogramos de CO2 por litro
    Edificio_consumo_Agua = models.DecimalField(max_digits=5, decimal_places=2,default=0)
    Edificio_consumo_Aceite = models.DecimalField(max_digits=5, decimal_places=2,default=0)
    #Kilogramos de CO2 por kWh
    Edificio_consumo_Electricidad = models.DecimalField(max_digits=5, decimal_places=2,default=0.35)
    #Kilogramos de CO2 por Kg de propano
    Edificio_consumo_Propano = models.DecimalField(max_digits=5, decimal_places=2,default=2.938)
    #Kilogramos de CO2 por kWh 
    Edificio_consumo_GasNatural = models.DecimalField(max_digits=5, decimal_places=2,default=0.203)
    #Kilogramos de CO2 por kWh de electricidad consumido
    Vehiculo_consumo_Electricidad = models.DecimalField(max_digits=5, decimal_places=2,default=2.97)
    #Kilogramos de CO2 por litro de combusible
    Vehiculo_consumo_Gasolina = models.DecimalField(max_digits=5, decimal_places=2,default=2.157)
    Vehiculo_consumo_Diesel = models.DecimalField(max_digits=5, decimal_places=2,default=2.493)
    
    def __str__(self):
        return 'Factores'+str(self.pk)
