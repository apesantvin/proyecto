from django import forms

from .models import *

class EmpresaForm(forms.ModelForm):

    class Meta:
        model = Empresa
        fields = ( 'nombre_empresa', 'telefono', 'correo')
