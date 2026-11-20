"""
MODELOS (tablas de la base de datos)
====================================

Cada clase de este archivo se convierte en una TABLA en la base de datos.
Cada atributo (models.CharField, models.FloatField, ...) se convierte en una COLUMNA.

Relación con las fórmulas del enunciado:

    Activo      -> cada uno de los N = 17 activos (i)
    Portafolio  -> portafolio 1 y portafolio 2, con su valor inicial V_0
    Precio      -> p_{i,t}  : precio del activo i en la fecha t
    Weight      -> w_{i,0}  : peso inicial del activo i en un portafolio
    Cantidad    -> c_{i,0}  : cantidad del activo i en un portafolio (constante en el tiempo)

¿Y los montos x_{i,t}, los weights w_{i,t} y el valor V_t?
    NO se guardan en tablas: se CALCULAN cuando se necesitan, usando
        x_{i,t} = p_{i,t} * c_{i,0}
        V_t     = suma de x_{i,t} sobre todos los activos
        w_{i,t} = x_{i,t} / V_t
    Así evitamos guardar datos repetidos que podrían quedar desactualizados.
"""

from django.db import models


class BaseModel(models.Model):
    """
    Modelo "padre" que le agrega a todos los demás dos columnas útiles:
    cuándo se creó la fila y cuándo se modificó por última vez.
    (Recomendación de la guía Django-Styleguide.)

    'abstract = True' significa que Django NO crea una tabla para BaseModel;
    solo copia sus columnas en los modelos que heredan de él.
    """

    created_at = models.DateTimeField(auto_now_add=True)  # se llena solo al crear
    updated_at = models.DateTimeField(auto_now=True)      # se actualiza solo al guardar

    class Meta:
        abstract = True


class Activo(BaseModel):
    """
    Un activo invertible. Ejemplos: "EEUU", "Europa", "MM/Caja".
    """

    # unique=True: no pueden existir dos activos con el mismo nombre
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self) -> str:
        # Texto que se muestra cuando imprimimos el objeto (y en el admin)
        return self.nombre


class Portafolio(BaseModel):
    """
    Un portafolio de inversión.

    - valor_inicial: V_0, en dólares (ej: 1.000.000.000)
    - fecha_inicio:  la fecha t = 0 (ej: 15/02/2022)
    """

    nombre = models.CharField(max_length=100, unique=True)
    valor_inicial = models.FloatField()
    fecha_inicio = models.DateField()

    def __str__(self) -> str:
        return self.nombre


class Precio(BaseModel):
    """
    p_{i,t}: el precio de UN activo en UNA fecha.

    Ejemplo de una fila:  activo=EEUU, fecha=2022-02-15, valor=9383.57
    """

    # ForeignKey = "esta fila apunta a un Activo".
    # on_delete=models.CASCADE: si se borra el activo, se borran sus precios.
    # related_name="precios": permite escribir activo.precios.all()
    activo = models.ForeignKey(Activo, on_delete=models.CASCADE, related_name="precios")
    fecha = models.DateField()
    valor = models.FloatField()

    class Meta:
        # Un activo no puede tener dos precios distintos el mismo día
        constraints = [
            models.UniqueConstraint(fields=["activo", "fecha"], name="precio_unico_por_activo_y_fecha"),
        ]
        ordering = ["fecha"]

    def __str__(self) -> str:
        return f"{self.activo} | {self.fecha} | {self.valor}"


class Weight(BaseModel):
    """
    w_{i,0}: el peso inicial (%) de un activo dentro de un portafolio.

    Se guarda como decimal: 0.28 significa 28%.
    Ejemplo: portafolio=Portafolio 1, activo=EEUU, fecha=2022-02-15, valor=0.28
    """

    portafolio = models.ForeignKey(Portafolio, on_delete=models.CASCADE, related_name="weights")
    activo = models.ForeignKey(Activo, on_delete=models.CASCADE, related_name="weights")
    fecha = models.DateField()
    valor = models.FloatField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["portafolio", "activo", "fecha"],
                name="weight_unico_por_portafolio_activo_fecha",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.portafolio} | {self.activo} | {self.valor}"


class Cantidad(BaseModel):
    """
    c_{i,0}: cuántas unidades del activo tiene el portafolio.

    Se calcula una sola vez (pregunta 3) con:
        c_{i,0} = (w_{i,0} * V_0) / p_{i,0}
    y luego se mantiene constante en el tiempo (pregunta 4).
    """

    portafolio = models.ForeignKey(Portafolio, on_delete=models.CASCADE, related_name="cantidades")
    activo = models.ForeignKey(Activo, on_delete=models.CASCADE, related_name="cantidades")
    valor = models.FloatField()

    class Meta:
        # Cada portafolio tiene UNA sola cantidad por activo
        constraints = [
            models.UniqueConstraint(fields=["portafolio", "activo"], name="cantidad_unica_por_portafolio_activo"),
        ]

    def __str__(self) -> str:
        return f"{self.portafolio} | {self.activo} | {self.valor}"
