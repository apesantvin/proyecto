from django.urls import path
from . import views

urlpatterns = [
    path('', views.empresa_lista, name='empresa_lista'),
    path('empresa/<int:pk>/', views.empresa_detalles, name='empresa_detalles'),
    path('añadir_empresa/', views.añadir_empresa, name='añadir_empresa'),
]
