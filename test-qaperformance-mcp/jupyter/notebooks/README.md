# Notebooks de Análisis QA Performance

Este directorio contiene los notebooks de JupyterLab para análisis de rendimiento.

## Configuración de conexión a MySQL

Para conectar a la base de datos desde tus notebooks, usa:

```python
import pymysql
from sqlalchemy import create_engine

# Configuración de conexión
engine = create_engine(
    'mysql+pymysql://qawebservices:QAteam321.@10.95.132.195:3306/qaperformance'
)

# Ejemplo de consulta
import pandas as pd
df = pd.read_sql("SELECT * FROM performance_performanceexecution LIMIT 10", engine)
```

## Librerías disponibles

- **Análisis de datos**: pandas, numpy, matplotlib, plotly, seaborn
- **Documentos**: python-docx, openpyxl, reportlab
- **Base de datos**: pymysql, sqlalchemy
- **Gráficos**: kaleido, bokeh
- **Utilidades**: requests, jupyter-widgets, Pillow

## Acceso

JupyterLab estará disponible en: http://localhost:8888

Token de acceso: `qaperformance-token`