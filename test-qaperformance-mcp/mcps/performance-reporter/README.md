# QACDCO Performance Reporter MCP Server

MCP Server para gestionar reportes del sistema **qacdco-reporter-performance** via API REST.

## 🎯 Funcionalidades

### 📋 Herramientas Disponibles:

1. **`get_report`** - Descargar reporte DOCX por ID
   - Obtiene metadata via API Django
   - Descarga archivo DOCX y lo devuelve en Base64
   - Manejo de errores si no existe o no está generado

2. **`list_reports`** - Listar reportes disponibles
   - Filtro opcional por `execution_id`
   - Límite configurable de resultados
   - Estado de generación (Ready/Processing)

3. **`get_report_status`** - Estado de un reporte
   - Metadata completa del reporte
   - Estado de generación (Generated/Processing/Failed)
   - Información de ejecución y umbrales

4. **`generate_report`** - Generar nuevo reporte (🚀 Nuevo!)
   - Inicia generación asíncrona via API
   - Configurable threshold y tipo
   - Retorna ID para seguimiento

## 🚀 Instalación

```bash
cd mcp-performance-reporter
pip install -r requirements.txt
```

## ⚙️ Configuración

Variables de entorno:

```bash
export DJANGO_API_BASE="http://qacdco-performance.yourdomain.com:8000"
export API_TIMEOUT="30"  # Timeout en segundos
```

## 🔧 Configuración OpenWebUI

Agregar al `.mcp.json`:

```json
{
  "mcpServers": {
    "qacdco_performance_reporter": {
      "command": "python",
      "args": ["/path/to/mcp-performance-reporter/server.py"],
      "env": {
        "DJANGO_API_BASE": "http://your-django-server.com:8000",
        "API_TIMEOUT": "30"
      }
    }
  }
}
```

## 📝 Ejemplos de Uso desde OpenWebUI

### Consultas en Lenguaje Natural:

```
"Descarga el reporte ID 123"
"Lista todos los reportes de la ejecución 456"
"¿Cuál es el estado del reporte 789?"
"Genera un reporte para la ejecución 101 con threshold 95"
"¿Qué reportes están disponibles?"
```

### Respuestas del Sistema:

El MCP devuelve información estructurada con:
- ✅ Estados claros (Ready/Processing/Failed)
- 📊 Metadata completa (tamaño, fechas, ejecución)
- 📄 Archivos DOCX en formato Base64
- 🎯 Instrucciones para decodificar

## 🌐 API Endpoints Utilizados

El MCP consume estos endpoints del Django backend:

```
GET  /performance/reporter/api/1.0/reports/?id={id}
GET  /performance/reporter/api/1.0/reports/?execution_id={id}
POST /performance/reporter/api/1.0/reports/
GET  /media/{report_file_path}
```

## 📊 Formato de Salida

Los archivos DOCX se transfieren como **Base64** para compatibilidad MCP.

Para decodificar:
```bash
echo "BASE64_CONTENT" | base64 -d > report.docx
```

## 🔧 Deployment

### Características para Despliegue Distribuido:
- ✅ **Sin dependencias de filesystem** - Solo API calls
- ✅ **Configurable via environment** - URLs flexibles
- ✅ **Timeout configurable** - Para redes lentas
- ✅ **Test de conectividad** - Verifica API al arrancar
- ✅ **Manejo de errores robusto** - Logs detallados

### Recomendaciones:
1. Desplegar en contenedor Docker separado
2. Configurar variables de entorno apropiadas
3. Asegurar conectividad de red al Django backend
4. Monitorear logs para troubleshooting

## 🔮 Roadmap

- [ ] Autenticación/autorización API
- [ ] Cache de reportes frecuentemente accedidos
- [ ] Notificaciones de estado de generación
- [ ] Métricas de uso del MCP
- [ ] Integración con sistema de alertas