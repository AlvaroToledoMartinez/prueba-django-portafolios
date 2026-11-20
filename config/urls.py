"""
URLs principales del proyecto.

include("portafolios.urls") agrega todas las URLs definidas en portafolios/urls.py.
"""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('portafolios.urls')),
]
