# Sistema de Análisis de Rendimiento QA - Test Performance MCP

## 🎯 Descripción General

Este proyecto implementa un sistema completo de análisis de rendimiento QA que utiliza tecnologías modernas para crear una plataforma escalable de consulta y análisis de métricas de performance. El sistema está diseñado como una solución defensiva para analizar y monitorear el rendimiento de aplicaciones en entornos de testing.

## 🏗️ Arquitectura del Sistema

El proyecto utiliza una arquitectura multi-contenedor basada en Docker con los siguientes componentes:

```
Arquitectura: MCP benborla29/mcp-server-mysql@2.0.2 ↔ OpenWebUI ↔ LiteLLM ↔ Azure OpenAI
```

### Componentes Principales:

1. **OpenWebUI** (Puerto 3000)
   - Frontend web interactivo para consultas
   - Interfaz de chat con IA para análisis de datos
   - Persistencia de sesiones y contexto

2. **LiteLLM Proxy** (Puerto 4000)
   - Proxy de abstracción para múltiples proveedores de IA
   - Configurado para Azure OpenAI
   - Gestión unificada de APIs

3. **MCP MySQL Server** (Puerto 8000)
   - Servidor MCP (Model Context Protocol) especializado
   - Conexión directa a base de datos MySQL de QA Performance
   - Operaciones de solo lectura (sin INSERT/UPDATE/DELETE)

## 🗄️ Base de Datos QA Performance

El sistema se conecta a una base de datos MySQL llamada `qaperformance` que contiene:

### Tablas Principales:
- **performance_performanceproject**: Proyectos de testing
- **performance_performanceexecution**: Ejecuciones de pruebas
- **performance_performancedataset**: Conjuntos de datos de métricas
- **performance_performancemetrics**: Métricas agregadas (percentiles, TPS, error rates)
- **performance_performancerawdata**: Datos granulares de tiempo de respuesta

### Métricas Clave Analizadas:
- Tiempos de respuesta (median, P90, P95, P99)
- Transacciones por segundo (TPS)
- Tasas de error
- Distribución de carga por hilos
- Métricas del sistema bajo prueba

## 🔧 Configuración Técnica

### Docker Compose Services:

1. **LiteLLM Service**
   - Imagen: `ghcr.io/berriai/litellm:main-latest`
   - Configuración via `litellm_config.yaml`
   - Proxy para Azure OpenAI GPT-4

2. **MCP MySQL Service**
   - Build personalizado via `Dockerfile.mcp-mysql`
   - Base: `nikolaik/python-nodejs:python3.11-nodejs20`
   - Herramientas: mcpo, uv
   - Paquete: `@benborla29/mcp-server-mysql@2.0.2`

3. **OpenWebUI Service**
   - Imagen: `ghcr.io/open-webui/open-webui:main`
   - Integración con LiteLLM como backend
   - Volumen persistente para datos

### Variables de Entorno:
- Conexión MySQL: `MYSQL_HOST=10.95.101.164`
- Credenciales: Usuario y contraseña de test
- Base de datos: `qaperformance`
- Permisos: Solo lectura (operaciones destructivas deshabilitadas)

## 📊 Funcionalidades del Sistema

### Capacidades Actuales:
- ✅ Análisis comparativo entre ejecuciones de pruebas
- ✅ Identificación de cuellos de botella y regresiones
- ✅ Generación automática de queries SQL especializadas
- ✅ Interpretación contextual de métricas de performance
- ✅ Detección de patrones y tendencias históricas
- ✅ Cálculo de estadísticas descriptivas avanzadas

### Tipos de Análisis Soportados:
- **Pruebas de Carga (Load)**: Comportamiento bajo carga normal
- **Pruebas de Estrés (Stress)**: Límites de capacidad
- **Pruebas de Resistencia (Endurance)**: Estabilidad a largo plazo

## 🚀 Funcionalidades Planificadas (TODO.md)

### Mejoras Técnicas:
- Implementación de autenticación multisesión
- Políticas de persistencia de chat avanzadas
- Botón de generación de gráficos interactivos
- Mejoras en el sistema de prompting y retries

### Escalabilidad:
- Integración con MCP de GitHub para análisis de código fuente
- Generación de enlaces directos a ejecuciones/proyectos
- Gráficos específicos personalizables
- Mejor comprensión semántica de la estructura de base de datos

## 🔒 Seguridad y Limitaciones

### Medidas de Seguridad:
- Acceso de solo lectura a la base de datos
- Operaciones destructivas explícitamente deshabilitadas
- Credenciales limitadas al entorno de testing
- Aislamiento por contenedores Docker

### Limitaciones Actuales:
- No modificación de datos (INSERT/UPDATE/DELETE bloqueados)
- Acceso limitado a base de datos específica `qaperformance`
- Dependencia de disponibilidad de Azure OpenAI
- Datos de raw data no siempre disponibles para todos los datasets

## 📈 Casos de Uso

### Para Analistas QA:
- Comparación de rendimiento entre versiones
- Identificación de regresiones de performance
- Análisis de distribución de tiempos de respuesta
- Detección de transacciones problemáticas

### Para DevOps:
- Monitoreo de tendencias de capacidad
- Análisis de estabilidad del sistema
- Optimización de recursos basada en métricas históricas

### Para Gestión:
- Reportes ejecutivos de performance
- Análisis de costos de testing
- Métricas de calidad y SLAs

## 🛠️ Comandos de Operación

### Iniciar el Sistema:
```bash
docker-compose up -d
```

### Acceso:
- **Frontend**: http://localhost:3000
- **LiteLLM API**: http://localhost:4000
- **MCP Server**: http://localhost:8000

### Detener el Sistema:
```bash
docker-compose down
```

## 📋 Estado del Proyecto

**Estado Actual**: Funcional en entorno de testing
**Objetivo**: Sistema de análisis defensivo para métricas de QA
**Escalabilidad**: Arquitectura preparada para integración de nuevos MCPs y funcionalidades

El proyecto representa una solución moderna y escalable para el análisis de performance en entornos QA, combinando tecnologías de IA conversacional con acceso directo a datos de métricas especializadas.