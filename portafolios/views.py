"""
VIEWS (páginas HTML)
====================

A diferencia de apis.py (que devuelve JSON), una view devuelve una página HTML.

Esta view NO calcula nada: solo entrega la página con
    - la lista de portafolios,
    - las fechas por defecto para los filtros.
Luego, el JavaScript de la página llama a la API de la pregunta 4
(/api/portafolios/<id>/evolucion/) y dibuja los gráficos con Chart.js.
"""

from django.shortcuts import render

from portafolios.selectors import listar_portafolios, obtener_rango_fechas


def dashboard_view(request):
    fecha_min, fecha_max = obtener_rango_fechas()

    # Pasamos los portafolios como lista de diccionarios simples,
    # para poder enviarlos al JavaScript con el filtro json_script del template.
    portafolios = []
    for portafolio in listar_portafolios():
        portafolios.append({"id": portafolio.id, "nombre": portafolio.nombre})

    # "contexto" = las variables que el template puede usar con {{ nombre_variable }}
    contexto = {
        "portafolios": portafolios,
        "fecha_min": fecha_min.isoformat() if fecha_min else "",
        "fecha_max": fecha_max.isoformat() if fecha_max else "",
    }
    return render(request, "portafolios/dashboard.html", contexto)
