from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('register', views.register, name='register'),
    path('', views.pagina_principal, name='pagina_principal'),
    path('lista_empresas', views.empresa_lista, name='empresa_lista'),
    path('empresa/<int:pk>/', views.empresa_detalles, name='empresa_detalles'),
    path('empresa/<int:pk>/publicar', views.publicar_empresa, name='publicar_empresa'),
    path('empresa_actualizacion/<int:pk>/', views.actualizar_datos, name='actualizar_datos'),
    path('empresa/configuracion/<int:pk>/', views.empresa_configuracion, name='empresa_configuracion'),
    path('añadir_datos_empresa/<int:pk>/', views.añadir_datos_empresa, name='añadir_datos_empresa'),
    path('añadir_personal/<int:pk>/', views.añadir_personal, name='añadir_personal'),
    path('añadir_edificio/<int:pk>/', views.añadir_edificio, name='añadir_edificio'),
    path('añadir_vehiculo/<int:pk>/', views.añadir_vehiculo, name='añadir_vehiculo'),
    path('añadir_generador/<int:pk>/', views.añadir_generador, name='añadir_generador'),
    path('añadir_viaje/<int:pk>/', views.añadir_viaje, name='añadir_viaje'),
    path('añadir_consumoEdificio/<int:pk>/', views.añadir_consumoEdificio, name='añadir_consumoEdificio'),
    path('añadir_consumoVehiculo/<int:pk>/', views.añadir_consumoVehiculo, name='añadir_consumoVehiculo'),
    path('añadir_empresa/', views.añadir_empresa, name='añadir_empresa'),
    path('mensajes/<int:pk>/', views.mensajes, name='mensajes'),
    path('mensaje/<int:pk>/<int:mensajePK>/', views.mensaje_detalles, name='mensaje_detalles'),
    path('añadir_mensaje/<int:pk>/', views.añadir_mensaje, name='añadir_mensaje'),
    path('inicio_experto', views.mensajes_todos_experto, name='inicio_experto'),
    path('ask_for_experto', views.ask_for_experto, name='ask_for_experto'),
    path('add_experto/<int:expertoPK>/', views.add_experto, name='add_experto'),
    path('eliminar_experto_autorizado/<int:expertoPK>/', views.eliminar_experto_autorizado, name='eliminar_experto_autorizado'),
    path('eliminar_peticion_experto/<int:expertoPK>/', views.eliminar_peticion_experto, name='eliminar_peticion_experto'),
    path('mensajes_experto', views.mensajes_experto, name='mensajes_experto'),
    path('mensajes_empresa/<int:pk>/', views.mensajes_empresa, name='mensajes_empresa'),
    path('mensajes_todos_experto', views.mensajes_todos_experto, name='mensajes_todos_experto'),
    path('experto_mensaje/<int:mensajePK>/', views.experto_mensaje, name='experto_mensaje'),
    path('experto_mensaje_detalles/<int:mensajePK>/', views.mensaje_detalles_experto, name='mensaje_detalles_experto'),
    path('lista_expertos_añadir', views.lista_expertos_añadir, name='lista_expertos_añadir'),
    path('lista_expertos_eliminar', views.lista_expertos_eliminar, name='lista_expertos_eliminar'),
    path('grafico/<int:Gpk>', views.mostrar_grafico, name='mostrar_grafico'),
]+ static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
