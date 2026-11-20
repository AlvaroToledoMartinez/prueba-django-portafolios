# Portafolios de inversión en Django

Proyecto que modela portafolios de inversión, carga los datos de `datos.xlsx`,
calcula las cantidades iniciales y muestra la evolución del valor total (V_t)
y de los weights (w_{i,t}) mediante una API y gráficos.

## Cómo correrlo

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py cargar_datos          # Pregunta 2: ETL
.\.venv\Scripts\python.exe manage.py calcular_cantidades   # Pregunta 3: c_{i,0}
.\.venv\Scripts\python.exe manage.py runserver
```

- Gráficos (pregunta 5): http://127.0.0.1:8000/
- API (pregunta 4): http://127.0.0.1:8000/api/portafolios/1/evolucion/?fecha_inicio=2022-02-15&fecha_fin=2023-02-16
- Admin: http://127.0.0.1:8000/admin/ (antes: `manage.py createsuperuser`)

## Estructura (guía Django-Styleguide)

```
config/                     configuración del proyecto (settings, urls principales)
portafolios/
├── models.py               tablas: Activo, Portafolio, Precio, Weight, Cantidad
├── services.py             funciones que ESCRIBEN en la BD (ETL, cálculo de c_{i,0})
├── selectors.py            funciones que solo LEEN de la BD (evolución de V_t y w_{i,t})
├── apis.py                 endpoints JSON (clases *Api)
├── views.py                página HTML con los gráficos
├── urls.py                 rutas de la app
├── admin.py                panel de administración
├── templates/portafolios/dashboard.html   gráficos con Chart.js
└── management/commands/    comandos cargar_datos y calcular_cantidades
```

### Convenciones aplicadas

| Regla de la guía | Cómo se aplica aquí |
|---|---|
| La lógica de negocio va en **services** (escritura) y **selectors** (lectura) | `services.py` y `selectors.py`; las APIs, views y comandos solo los llaman |
| Nombres `<entidad>_<acción>` | `precio_cargar_desde_excel`, `cantidad_calcular_iniciales`, `portafolio_obtener_evolucion` |
| Argumentos keyword-only (`*`) | `cantidad_calcular_iniciales(*, portafolio: Portafolio)` |
| Type hints | en todos los services, selectors, APIs y views |
| APIs delgadas, una clase por endpoint `<Entidad><Acción>Api` | `PortafolioListaApi`, `PortafolioEvolucionApi` |
| `BaseModel` con `created_at` / `updated_at` | heredado por todos los modelos |

### Funciones

| Archivo | Función / clase | Pregunta |
|---|---|---|
| services.py | `precio_cargar_desde_excel`, `weight_cargar_desde_excel`, `datos_cargar_desde_excel` | 2 |
| services.py | `cantidad_calcular_iniciales`, `cantidad_calcular_iniciales_todos` | 3 |
| selectors.py | `portafolio_listar`, `portafolio_obtener_evolucion`, `precio_obtener_rango_fechas` | 4 y 5 |
| apis.py | `PortafolioListaApi`, `PortafolioEvolucionApi` | 4 |
| views.py | `PortafolioDashboardView` | 5 |

### Simplificaciones respecto a la guía

La guía usa Django REST Framework (`APIView` y serializers para validar entradas y
salidas). Aquí se usa `View` y `JsonResponse` de Django con validación manual,
para que el código sea más corto y fácil de seguir. La estructura y las
responsabilidades de cada capa son las mismas.
