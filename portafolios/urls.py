"""
URLs de la app portafolios: conectan cada dirección con la clase que la atiende.

- <int:portafolio_id> significa: "aquí va un número, pásalo al método get()
  como el argumento portafolio_id".
- .as_view() convierte la clase en algo que Django puede llamar como una función.
"""

from django.urls import path

from portafolios.apis import PortafolioEvolucionApi, PortafolioListaApi
from portafolios.views import PortafolioDashboardView

urlpatterns = [
    # Página con los gráficos (pregunta 5): http://127.0.0.1:8000/
    path("", PortafolioDashboardView.as_view(), name="dashboard"),

    # APIs (pregunta 4)
    path("api/portafolios/", PortafolioListaApi.as_view(), name="portafolios-lista"),
    path(
        "api/portafolios/<int:portafolio_id>/evolucion/",
        PortafolioEvolucionApi.as_view(),
        name="portafolio-evolucion",
    ),
]
