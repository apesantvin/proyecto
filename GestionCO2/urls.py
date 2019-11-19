from django.urls import path
from . import views

urlpatterns = [
    path('', views.empresa_lista, name='empresa_lista'),
]
