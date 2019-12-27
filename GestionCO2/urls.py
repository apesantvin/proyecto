from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.pagina_principal, name='pagina_principal'),
    path('lista_empresas', views.empresa_lista, name='empresa_lista'),
    path('empresa/<int:pk>/', views.empresa_detalles, name='empresa_detalles'),
    path('empresa/configuracion/<int:pk>/', views.empresa_configuracion, name='empresa_configuracion'),
    path('empresa/configuracion/cambios/<int:pk>/', views.empresa_configuracion_cambios, name='empresa_configuracion_cambios'),
    path('añadir_datos_empresa/<int:pk>/', views.añadir_datos_empresa, name='añadir_datos_empresa'),
    path('añadir_personal/<int:pk>/', views.añadir_personal, name='añadir_personal'),
    path('añadir_edificio/<int:pk>/', views.añadir_edificio, name='añadir_edificio'),
    path('añadir_vehiculo/<int:pk>/', views.añadir_vehiculo, name='añadir_vehiculo'),
    path('añadir_generador/<int:pk>/', views.añadir_generador, name='añadir_generador'),
    path('añadir_empresa/', views.añadir_empresa, name='añadir_empresa'),
    path('mensajes/<int:pk>/', views.mensajes, name='mensajes'),
    path('register', views.register, name='register'),
]+ static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
