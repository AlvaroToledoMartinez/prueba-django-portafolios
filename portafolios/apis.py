"""
APIs (guía Django-Styleguide)
=============================

Endpoints que reciben una petición HTTP y responden con JSON.

Según la guía, una API debe ser "delgada": solo
    1) lee y valida los parámetros de la petición,
    2) llama a un selector (lectura) o a un service (escritura),
    3) devuelve el resultado como JSON.
Los cálculos NO van aquí, van en selectors.py / services.py.

Endpoints:
    GET /api/portafolios/
    GET /api/portafolios/<id>/evolucion/?fecha_inicio=2022-02-15&fecha_fin=2023-02-16
"""

from datetime import date

from django.http import JsonResponse
from django.views.decorators.http import require_GET

from portafolios.models import Portafolio
from portafolios.selectors import listar_portafolios, obtener_evolucion_portafolio


@require_GET  # solo acepta peticiones GET (las de "leer")
def portafolios_lista_api(request):
    """
    GET /api/portafolios/

    Devuelve la lista de portafolios disponibles.
    """
    datos = []
    for portafolio in listar_portafolios():
        datos.append({
            "id": portafolio.id,
            "nombre": portafolio.nombre,
            "valor_inicial": portafolio.valor_inicial,
            "fecha_inicio": portafolio.fecha_inicio.isoformat(),
        })

    # safe=False permite devolver una lista (por defecto JsonResponse exige un diccionario)
    return JsonResponse(datos, safe=False)


@require_GET
def portafolio_evolucion_api(request, portafolio_id):
    """
    GET /api/portafolios/<portafolio_id>/evolucion/?fecha_inicio=AAAA-MM-DD&fecha_fin=AAAA-MM-DD

    Devuelve V_t y w_{i,t} para cada fecha del rango.
    """

    # ---- 1) Leer los parámetros de la URL (lo que va después del "?") ----
    texto_inicio = request.GET.get("fecha_inicio")
    texto_fin = request.GET.get("fecha_fin")

    # ---- 2) Validar ----
    # Si falta alguno -> error 400 (Bad Request = la petición está mal hecha)
    if texto_inicio is None or texto_fin is None:
        return JsonResponse(
            {"error": "Debe enviar los parámetros fecha_inicio y fecha_fin (formato AAAA-MM-DD)"},
            status=400,
        )

    # Convertir el texto "2022-02-15" a una fecha de Python
    try:
        fecha_inicio = date.fromisoformat(texto_inicio)
        fecha_fin = date.fromisoformat(texto_fin)
    except ValueError:
        return JsonResponse({"error": "Formato de fecha inválido, use AAAA-MM-DD"}, status=400)

    if fecha_inicio > fecha_fin:
        return JsonResponse({"error": "fecha_inicio debe ser menor o igual a fecha_fin"}, status=400)

    # Buscar el portafolio -> si no existe, error 404 (Not Found)
    try:
        portafolio = Portafolio.objects.get(id=portafolio_id)
    except Portafolio.DoesNotExist:
        return JsonResponse({"error": f"No existe el portafolio con id {portafolio_id}"}, status=404)

    # ---- 3) Calcular (en el selector) y responder ----
    evolucion = obtener_evolucion_portafolio(portafolio, fecha_inicio, fecha_fin)

    return JsonResponse({
        "portafolio": portafolio.nombre,
        "fecha_inicio": fecha_inicio.isoformat(),
        "fecha_fin": fecha_fin.isoformat(),
        "datos": evolucion,
    })
