"""
SERVICES (guía Django-Styleguide)
=================================

Aquí van las funciones que ESCRIBEN en la base de datos
(crear, actualizar o borrar filas).

    - Pregunta 2: ETL que lee datos.xlsx y guarda activos, portafolios, precios y weights.
    - Pregunta 3: (pendiente) cálculo y guardado de las cantidades iniciales c_{i,0}.
"""

import pandas as pd
from django.db import transaction

from portafolios.models import Activo, Portafolio, Precio, Weight


# =============================================================================
# PREGUNTA 2: ETL (Extract - Transform - Load)
# =============================================================================
#
#   E (Extract)   -> leer las hojas del Excel con pandas
#   T (Transform) -> convertir cada celda al formato que necesita la BD
#                    (ej: fecha de pandas -> fecha de Python, texto sin espacios)
#   L (Load)      -> guardar cada dato como una fila en su tabla
#
# Se usa "update_or_create" en vez de "create": si la fila ya existe la actualiza,
# y si no existe la crea. Así podemos correr la ETL varias veces sin duplicar datos.
# =============================================================================


def cargar_precios(ruta_excel):
    """
    Lee la hoja "Precios" y guarda los activos y sus precios p_{i,t}.

    La hoja tiene esta forma (una columna por activo, una fila por fecha):

        Dates       | EEUU    | Europa | ... | MM/Caja
        2022-02-15  | 9383.57 | 66.03  | ... | 104.64
        2022-02-16  | 9393.09 | 66.25  | ... | 104.64

    Devuelve cuántos precios se guardaron.
    """

    # ---- E: Extract ----
    tabla = pd.read_excel(ruta_excel, sheet_name="Precios")

    # Todas las columnas excepto la primera ("Dates") son nombres de activos
    nombres_activos = list(tabla.columns[1:])

    # ---- L: crear los activos (una fila por cada nombre) ----
    # Guardamos los objetos en un diccionario para no buscarlos en la BD cada vez:
    #   activos["EEUU"] -> <Activo: EEUU>
    activos = {}
    for nombre in nombres_activos:
        activo, creado = Activo.objects.update_or_create(nombre=nombre.strip())
        activos[nombre] = activo

    # ---- Recorrer la tabla fila por fila (cada fila es una fecha) ----
    cantidad_guardados = 0
    for _, fila in tabla.iterrows():

        # ---- T: Transform ----
        # pandas entrega la fecha como "Timestamp"; Django necesita un "date"
        fecha = fila["Dates"].date()

        for nombre in nombres_activos:
            valor = float(fila[nombre])

            # ---- L: Load ----
            Precio.objects.update_or_create(
                activo=activos[nombre],   # campos para BUSCAR la fila
                fecha=fecha,
                defaults={"valor": valor},  # campos que se ACTUALIZAN
            )
            cantidad_guardados += 1

    return cantidad_guardados


def cargar_weights(ruta_excel, valor_inicial):
    """
    Lee la hoja "weights" y guarda los portafolios y sus weights iniciales w_{i,0}.

    La hoja tiene esta forma (una fila por activo, una columna por portafolio):

        Fecha       | activos | portafolio 1 | portafolio 2
        2022-02-15  | EEUU    | 0.280        | 0.280
        2022-02-15  | Europa  | 0.087        | 0.067

    valor_inicial: V_0 que se le asigna a cada portafolio (ej: 1_000_000_000).

    Devuelve cuántos weights se guardaron.
    """

    # ---- E: Extract ----
    tabla = pd.read_excel(ruta_excel, sheet_name="weights")

    # Las columnas desde la tercera en adelante son los portafolios
    columnas_portafolios = list(tabla.columns[2:])  # ["portafolio 1", "portafolio 2"]

    # La fecha de inicio (t = 0) es la misma para todas las filas: tomamos la primera
    fecha_inicio = tabla["Fecha"][0].date()

    cantidad_guardados = 0
    for columna in columnas_portafolios:

        # ---- T + L: crear el portafolio ----
        # "portafolio 1" -> "Portafolio 1"
        portafolio, creado = Portafolio.objects.update_or_create(
            nombre=columna.strip().capitalize(),
            defaults={"valor_inicial": valor_inicial, "fecha_inicio": fecha_inicio},
        )

        # ---- Recorrer cada activo de este portafolio ----
        for _, fila in tabla.iterrows():

            # ---- T: Transform ----
            nombre_activo = fila["activos"].strip()
            fecha = fila["Fecha"].date()
            valor = float(fila[columna])

            # El activo ya debería existir (lo creó cargar_precios).
            # Si no existe, .get() lanza un error y nos avisa que el Excel tiene algo raro.
            activo = Activo.objects.get(nombre=nombre_activo)

            # ---- L: Load ----
            Weight.objects.update_or_create(
                portafolio=portafolio,
                activo=activo,
                fecha=fecha,
                defaults={"valor": valor},
            )
            cantidad_guardados += 1

    return cantidad_guardados


def cargar_datos_excel(ruta_excel, valor_inicial=1_000_000_000):
    """
    Función principal de la ETL: carga todo el archivo datos.xlsx.

    transaction.atomic() hace que todo se guarde "de una vez":
    si algo falla a la mitad, se deshace todo y la base de datos queda como estaba.
    (Además hace la carga mucho más rápida en SQLite.)
    """
    with transaction.atomic():
        # Primero los precios, porque ahí se crean los activos
        total_precios = cargar_precios(ruta_excel)
        # Después los weights, que necesitan que los activos ya existan
        total_weights = cargar_weights(ruta_excel, valor_inicial)

    return total_precios, total_weights
