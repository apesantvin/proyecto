from django.db import models
from django.utils import timezone

# Create your models here.
class Empresa(models.Model):
    usuario = models.ManyToManyField('auth.User')
    nombre_empresa = models.CharField(max_length=50)
    telefono = models.IntegerField()
    correo = models.EmailField() 
    fecha_inscripcion = models.DateField('Fecha de inscripcion',default=timezone.now)
    
class Edificio(models.Model):
    empresa = models.ForeignKey('Empresa',on_delete=models.CASCADE)
    localizacion = models.CharField(max_length=50)
    fecha_adquisicion = models.DateField('Fecha contratacion',blank=True, null=True)
    
class Generador(models.Model):
    edificio = models.ForeignKey('Edificio',on_delete=models.CASCADE)
    medios = models.CharField('Tipo de Generador',max_length=50,help_text='Paneles Solares o Molinos eolicos')
    cantidad_generada = models.IntegerField(help_text='en KWH')
    fecha_generacion= models.DateField('Fecha de la generacion')
    
class Vehiculo(models.Model):
    empresa = models.ForeignKey('Empresa',on_delete=models.CASCADE)
    matricula = models.CharField(max_length=8)
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    fecha_compra = models.DateField('Fecha compra')
    
class Personal(models.Model):
    empresa = models.ManyToManyField('Empresa')
    nombre_persona = models.CharField(max_length=50)
    fecha_contratacion = models.DateField('Fecha contratacion')
    
class Viaje(models.Model):
    personal = models.ManyToManyField('Personal')
    distancia = models.IntegerField('KM recorridos')
    transporte = models.CharField(max_length=50)
    noches_hotel = models.IntegerField('Noches en hotel')
    
class Consumo(models.Model):
    tipo = models.CharField('¿Que ha consumido?',max_length=50,help_text='Agua, Electricidad, Aceite, Propano, Gas Natural, Gasolina o Diesel')
    cantidad_consumida = models.IntegerField()
    fecha_consumo= models.DateField('Fecha del consumo')
    
class EdificioConsumo(Consumo):
    edificio = models.ForeignKey('Edificio',on_delete=models.CASCADE)
    
class VehiculoConsumo(Consumo):
    personal = models.ForeignKey('Personal',on_delete=models.CASCADE)
    vehiculo = models.ForeignKey('Vehiculo',on_delete=models.CASCADE)
