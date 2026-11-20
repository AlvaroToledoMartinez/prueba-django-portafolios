"""
COMANDO: python manage.py calcular_cantidades
=============================================

Calcula las cantidades iniciales c_{i,0} de todos los portafolios (pregunta 3),
las guarda en la tabla Cantidad y las muestra en pantalla.

Requisito: haber corrido antes  python manage.py cargar_datos
"""

from django.core.management.base import BaseCommand

from portafolios.services import cantidad_calcular_iniciales_todos


class Command(BaseCommand):
    help = "Calcula y guarda las cantidades iniciales c_{i,0} de cada portafolio"

    def handle(self, *args, **options) -> None:
        resultado = cantidad_calcular_iniciales_todos()

        for portafolio, cantidades in resultado.items():
            self.stdout.write("")
            self.stdout.write(self.style.SUCCESS(f"{portafolio}  (V_0 = {portafolio.valor_inicial:,.0f})"))
            self.stdout.write(f"{'Activo':<20}{'Cantidad c_i,0':>20}")
            self.stdout.write("-" * 40)

            for cantidad in cantidades:
                self.stdout.write(f"{cantidad.activo.nombre:<20}{cantidad.valor:>20,.4f}")
