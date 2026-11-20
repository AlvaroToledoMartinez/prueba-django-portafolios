"""
COMANDO: python manage.py cargar_datos
======================================

Django permite crear comandos propios para manage.py.
Basta con crear un archivo dentro de  <app>/management/commands/
y el nombre del archivo es el nombre del comando (cargar_datos).

Este comando solo llama a la función de la ETL que está en services.py.
(Según la guía Django-Styleguide, la lógica va en services, no en el comando.)

Uso:
    python manage.py cargar_datos
    python manage.py cargar_datos --ruta otro_archivo.xlsx --valor-inicial 500000000
"""

from django.core.management.base import BaseCommand

from portafolios.services import cargar_datos_excel


class Command(BaseCommand):
    help = "Carga los datos de datos.xlsx (activos, precios, portafolios y weights) a la base de datos"

    def add_arguments(self, parser):
        # Argumentos opcionales, con valores por defecto
        parser.add_argument("--ruta", default="datos.xlsx")
        parser.add_argument("--valor-inicial", type=float, default=1_000_000_000)

    def handle(self, *args, **options):
        # handle() es lo que se ejecuta al correr el comando
        ruta = options["ruta"]
        valor_inicial = options["valor_inicial"]

        self.stdout.write(f"Cargando datos desde {ruta} ...")

        total_precios, total_weights = cargar_datos_excel(ruta, valor_inicial)

        self.stdout.write(self.style.SUCCESS(
            f"Listo: {total_precios} precios y {total_weights} weights cargados."
        ))
