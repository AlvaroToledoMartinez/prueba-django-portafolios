"""
URLs de la app portafolios: conectan cada dirección con la función que la atiende.

<int:portafolio_id> significa: "aquí va un número, pásalo a la función
como el argumento portafolio_id".
"""

from django.urls import path

from portafolios.apis import portafolio_evolucion_api, portafolios_lista_api
from portafolios.views import dashboard_view

urlpatterns = [
    # Página con los gráficos (pregunta 5): http://127.0.0.1:8000/
    path("", dashboard_view, name="dashboard"),

    # APIs (pregunta 4)
    path("api/portafolios/", portafolios_lista_api, name="portafolios-lista"),
    path(
        "api/portafolios/<int:portafolio_id>/evolucion/",
        portafolio_evolucion_api,
        name="portafolio-evolucion",
    ),
]
