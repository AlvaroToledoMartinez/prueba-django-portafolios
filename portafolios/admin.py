"""
ADMIN
=====

Registrar un modelo aquí hace que aparezca en el panel de administración
(http://127.0.0.1:8000/admin/), donde se pueden ver, crear, editar y borrar filas
sin escribir código. Muy útil para revisar que los datos se cargaron bien.
"""

from django.contrib import admin

from portafolios.models import Activo, Cantidad, Portafolio, Precio, Weight


@admin.register(Activo)
class ActivoAdmin(admin.ModelAdmin):
    list_display = ["id", "nombre"]  # columnas que se ven en la lista


@admin.register(Portafolio)
class PortafolioAdmin(admin.ModelAdmin):
    list_display = ["id", "nombre", "valor_inicial", "fecha_inicio"]


@admin.register(Precio)
class PrecioAdmin(admin.ModelAdmin):
    list_display = ["activo", "fecha", "valor"]
    list_filter = ["activo"]  # filtro lateral por activo


@admin.register(Weight)
class WeightAdmin(admin.ModelAdmin):
    list_display = ["portafolio", "activo", "fecha", "valor"]
    list_filter = ["portafolio"]


@admin.register(Cantidad)
class CantidadAdmin(admin.ModelAdmin):
    list_display = ["portafolio", "activo", "valor"]
    list_filter = ["portafolio"]
