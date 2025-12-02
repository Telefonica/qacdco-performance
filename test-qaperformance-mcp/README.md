# QA Performance MCP System

Sistema completo de análisis de performance QA que utiliza **OpenWebUI** + **LiteLLM** + **MCPs** + **Azure OpenAI** para proporcionar análisis inteligente y automatizado de métricas de testing de performance.

## 🎯 **Qué hace este sistema**

Plataforma conversacional que permite analizar datos de performance testing mediante **IA** con acceso directo a:
- **Base de datos MySQL** con métricas históricas de performance
- **Sistema de reportes** Django para descarga de informes
- **Tool calling nativo** para análisis automático e iterativo

### **Capacidades principales:**
- ✅ **Análisis comparativo** de ejecuciones de testing
- ✅ **Detección automática** de regresiones y cuellos de botella
- ✅ **Generación de gráficas** comparativas (TPS, latencia, error rates)
- ✅ **Links de descarga** de reportes DOCX automáticos
- ✅ **Consultas SQL** especializadas automáticas
- ✅ **Análisis iterativo** hasta obtener respuestas completas
- ✅ **Consultas PromQL** a Prometheus para métricas en tiempo real
- ✅ **Análisis de targets** y disponibilidad de servicios

## 🏗️ **Arquitectura del sistema**

```
Usuario ↔ OpenWebUI ↔ LiteLLM ↔ Azure OpenAI GPT-4
             ↓
        MCP Servers:
         ├─ MySQL MCP → Base de datos qaperformance
         ├─ Performance Reporter MCP → Sistema Django reportes
         └─ Prometheus MCP → Métricas en tiempo real
```

### **Componentes:**

| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| **OpenWebUI** | 3000 | Frontend conversacional con IA |
| **LiteLLM** | 4000 | Proxy unificado a Azure OpenAI |
| **MCP MySQL** | 8000 | Servidor MCP para base de datos QA |
| **MCP Performance Reporter** | 8001 | Servidor MCP para gestión de reportes |
| **MCP Prometheus** | 8002 | Servidor MCP para métricas de Prometheus |

## 🚀 **Inicio rápido**

### **1. Configuración inicial**
```bash
# Clonar y entrar al directorio
cd test-qaperformance-mcp

# Crear archivo .env
cp .env.example .env
# Editar .env con tus credenciales
```

### **2. Iniciar sistema**
```bash
# Construir e iniciar todos los servicios
docker-compose up -d --build

# Verificar estado de servicios
docker-compose ps
```

### **3. Acceso**
- **OpenWebUI**: http://localhost:3000
- **LiteLLM API**: http://localhost:4000

### **4. Configurar en OpenWebUI**
1. **Subir función**: Copiar `functions/qa_performance_tool_calling.py` en **Admin → Functions**
2. **Activar MCPs**: Habilitar en **Settings → Models**
3. **Usar modelo**: Seleccionar `qa-perf/gpt-4` en conversaciones

## 💡 **Ejemplos de uso**

### **Análisis comparativo:**
```
"Genera una gráfica comparativa de TPS entre ejecución 6835 y 6824 del módulo LALIGA"
```

### **Detección de problemas:**
```
"¿Por qué falló la ejecución 6994? Analiza métricas y errores"
```

### **Gestión de reportes:**
```
"Dame el link de descarga del reporte de la ejecución 6994"
```

### **Análisis histórico:**
```
"Compara las últimas 5 ejecuciones del dataset Consume IP mockbin API"
```

### **Consultas a Prometheus:**
```
"¿Cuál es el uso de CPU actual de los servicios en producción?"
```

```
"Muestra las métricas de latencia HTTP de las últimas 24 horas"
```

## 📊 **Base de datos QA Performance**

### **Tablas principales:**
- `performance_performanceproject`: Proyectos de testing
- `performance_performanceexecution`: Ejecuciones de pruebas
- `performance_performancemetrics`: Métricas agregadas (P90, P95, P99, TPS)
- `performance_performancedataset`: Conjuntos de datos de métricas
- `performance_performancerawdata`: Datos granulares de tiempo de respuesta

### **Métricas analizadas:**
- **Tiempos de respuesta**: Mediana, P90, P95, P99
- **Throughput**: Transacciones por segundo (TPS)
- **Error rates**: Tasas de error por transacción
- **Distribución de carga**: Métricas por número de hilos
- **Comparaciones históricas**: Baselines y regresiones

## 🔧 **Configuración avanzada**

### **Variables de entorno (.env):**
```bash
# Clave secreta OpenWebUI (generar con: openssl rand -base64 32)
WEBUI_SECRET_KEY=your-secret-key-here

# Configuración MySQL (ya configurada para entorno QA)
MYSQL_HOST=10.95.132.195
MYSQL_USER=qawebservices
MYSQL_PASS=QAteam321.
MYSQL_DB=qaperformance

# API Django reportes
DJANGO_API_BASE=http://qacdco.hi.inet
API_TIMEOUT=30

# Prometheus
PROMETHEUS_URL=http://qacdo-performance-prometheus-qacdo-services-pre.apps.ocp-epg.hi.inet/
PROMETHEUS_URL_SSL_VERIFY=false
PROMETHEUS_DISABLE_LINKS=false
```

### **Configuración LiteLLM (`config/litellm_config.yaml`):**
```yaml
model_list:
  - model_name: gpt-4
    litellm_params:
      model: azure/gpt-4-deployment-name
      api_base: https://your-instance.openai.azure.com
      api_key: os.environ/AZURE_OPENAI_API_KEY
      api_version: "2024-02-01"
```

## 📁 **Estructura del proyecto**

```
test-qaperformance-mcp/
├── docs/                           # 📚 Documentación
│   ├── system-prompts/            # System prompts especializados
│   ├── architecture/              # Diagramas de arquitectura
│   └── TODO.md                    # Roadmap y mejoras
├──
├── functions/                      # ⚙️ OpenWebUI Functions
│   └── qa_performance_tool_calling.py  # Función principal
├──
├── mcps/                          # 🔌 MCP Servers
│   ├── mysql/                     # Servidor MCP MySQL
│   ├── performance-reporter/      # Servidor MCP reportes
│   └── prometheus/                # Servidor MCP Prometheus
├──
├── config/                        # ⚙️ Configuraciones
│   └── litellm_config.yaml       # Config LiteLLM
├──
└── docker-compose.yml             # 🐳 Orquestación servicios
```

## 🔒 **Seguridad y limitaciones**

### **Medidas de seguridad:**
- ✅ **Solo lectura** en operaciones críticas de BD
- ✅ **Credenciales limitadas** al entorno de testing
- ✅ **Aislamiento** por contenedores Docker
- ✅ **Variables de entorno** para secretos

### **Limitaciones actuales:**
- **Acceso limitado** a base de datos específica `qaperformance`
- **Solo reportes** disponibles en sistema Django
- **Dependencia** de disponibilidad de Azure OpenAI

## 🛠️ **Comandos útiles**

### **Gestión de servicios:**
```bash
# Iniciar sistema
docker-compose up -d

# Ver logs en tiempo real
docker-compose logs -f

# Reiniciar servicio específico
docker-compose restart mcp-mysql

# Detener todo
docker-compose down

# Limpiar volúmenes (reset completo)
docker-compose down -v
```

### **Verificar conectividad:**
```bash
# LiteLLM
curl http://localhost:4000/models

# MCP MySQL
curl http://localhost:8000

# MCP Performance Reporter
curl http://localhost:8001

# MCP Prometheus
curl http://localhost:8002

# OpenWebUI
curl http://localhost:3000
```

## 📈 **Casos de uso**

### **Para analistas QA:**
- Comparación de rendimiento entre versiones
- Identificación de regresiones de performance
- Análisis de distribución de tiempos de respuesta
- Detección de transacciones problemáticas

### **Para DevOps:**
- Monitoreo de tendencias de capacidad
- Análisis de estabilidad del sistema
- Optimización de recursos basada en métricas históricas

### **Para gestión:**
- Reportes ejecutivos de performance
- Análisis de costos de testing
- Métricas de calidad y SLAs

## 🚨 **Troubleshooting**

### **OpenWebUI no arranca:**
- Verificar `WEBUI_SECRET_KEY` en `.env`
- Comprobar puertos disponibles
- Revisar logs: `docker-compose logs open-webui`

### **MCPs no funcionan:**
- Verificar conectividad a base de datos
- Comprobar credenciales MySQL en `.env`
- Revisar logs MCP: `docker-compose logs mcp-mysql`

### **LiteLLM errores:**
- Verificar configuración Azure OpenAI en `config/litellm_config.yaml`
- Comprobar API keys válidas
- Test directo: `curl http://localhost:4000/models`

---

**🎯 Objetivo:** Sistema defensivo para análisis inteligente de métricas QA que combina IA conversacional moderna con acceso directo a datos especializados de performance testing.