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
    path('añadir_empresa/', views.añadir_empresa, name='añadir_empresa'),
    path('register', views.register, name='register'),
    path('config', views.user_config, name='user_config'),
    path('change_password', views.change_password, name='change_password'),
]+ static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
