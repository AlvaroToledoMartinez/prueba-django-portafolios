"""
APIs (guía Django-Styleguide)
=============================

Endpoints que reciben una petición HTTP y responden con JSON.

Convenciones de la guía que seguimos:

1) Una CLASE por endpoint, con nombre  <Entidad><Acción>Api
       ej: PortafolioListaApi, PortafolioEvolucionApi

2) La clase hereda de View y define un método por cada tipo de petición:
       def get(self, request): ...   -> atiende peticiones GET
   Si llega otro tipo (POST, DELETE, ...) Django responde solo con error 405.

3) Una API debe ser "delgada": solo
       a) lee y valida los parámetros de la petición,
       b) llama a un selector (lectura) o a un service (escritura),
       c) devuelve el resultado como JSON.
   Los cálculos NO van aquí, van en selectors.py / services.py.

Endpoints:
    GET /api/portafolios/
    GET /api/portafolios/<id>/evolucion/?fecha_inicio=2022-02-15&fecha_fin=2023-02-16
"""

from datetime import date

from django.http import HttpRequest, JsonResponse
from django.views import View

from portafolios.models import Portafolio
from portafolios.selectors import portafolio_listar, portafolio_obtener_evolucion


class PortafolioListaApi(View):
    """
    GET /api/portafolios/

    Devuelve la lista de portafolios disponibles.
    """

    def get(self, request: HttpRequest) -> JsonResponse:
        datos = []
        for portafolio in portafolio_listar():
            datos.append({
                "id": portafolio.id,
                "nombre": portafolio.nombre,
                "valor_inicial": portafolio.valor_inicial,
                "fecha_inicio": portafolio.fecha_inicio.isoformat(),
            })

        # safe=False permite devolver una lista (por defecto JsonResponse exige un diccionario)
        return JsonResponse(datos, safe=False)


class PortafolioEvolucionApi(View):
    """
    GET /api/portafolios/<portafolio_id>/evolucion/?fecha_inicio=AAAA-MM-DD&fecha_fin=AAAA-MM-DD

    Devuelve V_t y w_{i,t} para cada fecha del rango.
    """

    def get(self, request: HttpRequest, portafolio_id: int) -> JsonResponse:

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
        evolucion = portafolio_obtener_evolucion(
            portafolio=portafolio,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
        )

        return JsonResponse({
            "portafolio": portafolio.nombre,
            "fecha_inicio": fecha_inicio.isoformat(),
            "fecha_fin": fecha_fin.isoformat(),
            "datos": evolucion,
        })
