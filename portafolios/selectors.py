"""
SELECTORS (guía Django-Styleguide)
==================================

Aquí van las funciones que solo LEEN de la base de datos (no modifican nada).
Siguen las mismas convenciones que services.py:
nombre <entidad>_<acción>, argumentos keyword-only (*) y type hints.

Pregunta 4: calcular la evolución de x_{i,t}, V_t y w_{i,t} entre dos fechas.

    Las cantidades son constantes:   c_{i,t} = c_{i,0}
    Monto de cada activo:            x_{i,t} = p_{i,t} * c_{i,0}
    Valor del portafolio:            V_t     = suma de x_{i,t} (sobre todos los activos)
    Weight de cada activo:           w_{i,t} = x_{i,t} / V_t
"""

from datetime import date

from django.db.models import Max, Min, QuerySet

from portafolios.models import Cantidad, Portafolio, Precio


def portafolio_listar() -> QuerySet[Portafolio]:
    """Devuelve todos los portafolios ordenados por id."""
    return Portafolio.objects.all().order_by("id")


def precio_obtener_rango_fechas() -> tuple[date | None, date | None]:
    """
    Devuelve la primera y la última fecha con precios: (fecha_min, fecha_max).
    Si no hay precios cargados, devuelve (None, None).

    aggregate() le pide a la BD que calcule algo sobre TODA la tabla
    (aquí el mínimo y el máximo de la columna fecha) y devuelve un diccionario:
        {"fecha_min": date(2022, 2, 15), "fecha_max": date(2023, 2, 16)}
    """
    rango = Precio.objects.aggregate(fecha_min=Min("fecha"), fecha_max=Max("fecha"))
    return rango["fecha_min"], rango["fecha_max"]


def portafolio_obtener_evolucion(*, portafolio: Portafolio, fecha_inicio: date, fecha_fin: date) -> list[dict]:
    """
    Calcula V_t y w_{i,t} para cada fecha entre fecha_inicio y fecha_fin (incluidas).

    Devuelve una lista con un diccionario por fecha:
        [
            {
                "fecha": "2022-02-15",
                "valor_total": 1000000000.0,                     <- V_t
                "weights": {"EEUU": 0.28, "Europa": 0.087, ...}  <- w_{i,t}
            },
            ...
        ]
    """

    # ------------------------------------------------------------------
    # PASO 1: traer las cantidades c_{i,0} del portafolio (1 consulta a la BD)
    # ------------------------------------------------------------------
    # Las guardamos en un diccionario:  { id_del_activo: cantidad }
    cantidades: dict[int, float] = {}
    for cantidad in Cantidad.objects.filter(portafolio=portafolio):
        cantidades[cantidad.activo_id] = cantidad.valor

    # ------------------------------------------------------------------
    # PASO 2: traer los precios p_{i,t} entre las fechas (1 consulta a la BD)
    # ------------------------------------------------------------------
    # - fecha__gte = "fecha mayor o igual que"  (gte = greater than or equal)
    # - fecha__lte = "fecha menor o igual que"  (lte = less than or equal)
    # - activo_id__in = solo los activos que tienen cantidad en este portafolio
    # - select_related("activo") trae el nombre del activo en la MISMA consulta
    #   (si no, Django haría una consulta extra por cada precio)
    precios = (
        Precio.objects
        .filter(
            fecha__gte=fecha_inicio,
            fecha__lte=fecha_fin,
            activo_id__in=cantidades.keys(),
        )
        .select_related("activo")
        .order_by("fecha", "activo_id")
    )

    # ------------------------------------------------------------------
    # PASO 3: calcular los montos x_{i,t} y agruparlos por fecha
    # ------------------------------------------------------------------
    # montos_por_fecha = {
    #     fecha1: {"EEUU": x, "Europa": x, ...},
    #     fecha2: {...},
    # }
    montos_por_fecha: dict[date, dict[str, float]] = {}
    for precio in precios:
        x = precio.valor * cantidades[precio.activo_id]  # x_{i,t} = p_{i,t} * c_{i,0}

        if precio.fecha not in montos_por_fecha:
            montos_por_fecha[precio.fecha] = {}
        montos_por_fecha[precio.fecha][precio.activo.nombre] = x

    # ------------------------------------------------------------------
    # PASO 4: para cada fecha calcular V_t y los weights w_{i,t}
    # ------------------------------------------------------------------
    resultado: list[dict] = []
    for fecha, montos in montos_por_fecha.items():

        # V_t = suma de todos los montos de esa fecha
        valor_total = 0.0
        for x in montos.values():
            valor_total += x

        # w_{i,t} = x_{i,t} / V_t
        weights: dict[str, float] = {}
        for nombre_activo, x in montos.items():
            weights[nombre_activo] = x / valor_total

        resultado.append({
            "fecha": fecha.isoformat(),   # date -> texto "2022-02-15"
            "valor_total": valor_total,
            "weights": weights,
        })

    return resultado
