"""
VIEWS (páginas HTML)
====================

A diferencia de apis.py (que devuelve JSON), una view devuelve una página HTML.

Esta view NO calcula nada: solo entrega la página con
    - la lista de portafolios,
    - las fechas por defecto para los filtros.
Luego, el JavaScript de la página llama a la API de la pregunta 4
(/api/portafolios/<id>/evolucion/) y dibuja los gráficos con Chart.js.

Igual que las APIs, es una clase con un método get().
"""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View

from portafolios.selectors import portafolio_listar, precio_obtener_rango_fechas


class PortafolioDashboardView(View):

    def get(self, request: HttpRequest) -> HttpResponse:
        fecha_min, fecha_max = precio_obtener_rango_fechas()

        # Pasamos los portafolios como lista de diccionarios simples,
        # para poder enviarlos al JavaScript con el filtro json_script del template.
        portafolios = []
        for portafolio in portafolio_listar():
            portafolios.append({"id": portafolio.id, "nombre": portafolio.nombre})

        # "contexto" = las variables que el template puede usar con {{ nombre_variable }}
        contexto = {
            "portafolios": portafolios,
            "fecha_min": fecha_min.isoformat() if fecha_min else "",
            "fecha_max": fecha_max.isoformat() if fecha_max else "",
        }
        return render(request, "portafolios/dashboard.html", contexto)
