from django import forms
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm      

class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = (
            'nombre_empresa', 
            'logo',
            'descripcion',
            'telefono',
            'correo',
            'permitido_publicar')
        
class leercsv(forms.Form):
    CSV=forms.FileField(required=False)

class mensajeForm(forms.ModelForm):
    class Meta:
        model = Mensaje
        fields = (
            'titulo',
            'texto')

class PersonalEmpresaForm(forms.ModelForm):
    class Meta:
        model = Personal
        fields = (
            'nombre_persona',
            'apellidos_persona',
            'fecha_contratacion')
        
class EdificioEmpresaForm(forms.ModelForm):
    class Meta:
        model = Edificio
        fields = (
            'nombre_edificio',
            'localizacion',
            'fecha_adquisicion')

class VehiculoEdificioForm(forms.ModelForm):
    class Meta:
        model = Vehiculo
        fields = (
            'tipo_tranporte',
            'matricula',
            'tamano',
            'fecha_compra')

class GeneradorEdificioForm(forms.ModelForm):
    def __init__(self, empresa, *args, **kwargs):
        super(GeneradorEdificioForm, self).__init__(*args, **kwargs)
        self.fields['edificio'].queryset = Edificio.objects.filter(empresa=empresa)
    class Meta:
        model = Generador
        fields = (
            'edificio',
            'medios',
            'cantidad_generada',
            'fecha_generacion'
            )

class ViajeForm(forms.ModelForm):
    def __init__(self, empresa, *args, **kwargs):
        super(ViajeForm, self).__init__(*args, **kwargs)
        self.fields['personal'].queryset = Personal.objects.filter(empresa=empresa)
    class Meta:
        model = Viaje
        fields = (
            'personal',
            'distancia',
            'transporte',
            'noches_hotel',
            'fecha_viaje',
            )

class ConsumoEdificioForm(forms.ModelForm):
    def __init__(self, empresa, *args, **kwargs):
        super(ConsumoEdificioForm, self).__init__(*args, **kwargs)
        self.fields['edificio'].queryset = Edificio.objects.filter(empresa=empresa)
        
    class Meta:
            model = EdificioConsumo
            fields = ('edificio',
                      'tipo',
                      'cantidad_consumida',
                      'fecha_consumo')
            
class ConsumoVehiculoForm(forms.ModelForm):
    def __init__(self, empresa, *args, **kwargs):
        super(ConsumoVehiculoForm, self).__init__(*args, **kwargs)
        self.fields['personal'].queryset = Personal.objects.filter(empresa=empresa)
        self.fields['vehiculo'].queryset = Vehiculo.objects.filter(empresa=empresa)
        
    class Meta:
            model = VehiculoConsumo
            fields = ('personal',
                      'vehiculo',
                      'tipo',
                      'cantidad_consumida',
                      'fecha_consumo')

class formularioregistroForm(UserCreationForm):
    email = forms.EmailField(required = True)
    first_name = forms.CharField(required = False)
    last_name = forms.CharField(required = False)
    birtday = forms.DateField(required = False)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')        

    def save(self,commit = True):   
        user = super(formularioregistroForm, self).save(commit = False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.birthday = self.cleaned_data['birtday']

        if commit:
            user.save()

        return user

class RespuestaForm(forms.ModelForm):
    class Meta:
        model = Respuesta
        fields = (
            'texto',)
