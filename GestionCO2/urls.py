from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.empresa_lista, name='empresa_lista'),
    path('empresa/<int:pk>/', views.empresa_detalles, name='empresa_detalles'),
    path('añadir_empresa/', views.añadir_empresa, name='añadir_empresa'),
    path('register', views.register, name='register'),
]+ static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
