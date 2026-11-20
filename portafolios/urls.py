"""
URLs de la app portafolios: conectan cada dirección con la función que la atiende.

<int:portafolio_id> significa: "aquí va un número, pásalo a la función
como el argumento portafolio_id".
"""

from django.urls import path

from portafolios.apis import portafolio_evolucion_api, portafolios_lista_api

urlpatterns = [
    path("api/portafolios/", portafolios_lista_api, name="portafolios-lista"),
    path(
        "api/portafolios/<int:portafolio_id>/evolucion/",
        portafolio_evolucion_api,
        name="portafolio-evolucion",
    ),
]
