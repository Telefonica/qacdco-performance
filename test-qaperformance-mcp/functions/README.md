# QA Performance Tool Calling Function

OpenWebUI **Pipe Function** que implementa **native tool calling** para análisis de performance QA via LiteLLM proxy con integración automática con MCPs.

## 🎯 **Qué hace**

Función **manifold** que aparece como modelo `qa-perf/gpt-4` en OpenWebUI y ejecuta automáticamente herramientas MCP para análisis de performance testing.

### **Capacidades principales:**
- ✅ **Tool calling nativo** con streaming
- ✅ **Iteraciones automáticas** (máx 5) hasta completar análisis
- ✅ **Integración LiteLLM**: Vía proxy unificado
- ✅ **Status updates** en tiempo real
- ✅ **Desplegables** para resultados de herramientas

## 🚀 **Instalación en OpenWebUI**

### **1. Copiar función**
1. Ve a **Admin Panel → Functions → Create New Function**
2. Copia todo el contenido de `qa_performance_tool_calling.py`
3. **Pega** en el editor y **Guarda**

### **2. Configurar Valves**
En la función creada, configura las **Valves**:

```yaml
LITELLM_BASE_URL: http://litellm:4000
LITELLM_API_KEY: sk-1234
MODEL_IDS: ["gpt-4"]                 # Modelos disponibles
MAX_ITERATIONS: 5                    # Máximo iteraciones
```

### **3. Activar MCPs**
En **Admin Panel → Settings → Models**, habilita los MCPs:
- ✅ `mcp_server_mysql`
- ✅ `mcp-performance-reporter`

## 📊 **Cómo funciona**

### **Flujo automático:**
```
Usuario: "Analiza ejecución 6994"
     ↓
🔄 Función detecta necesidad de datos
     ↓
🛠️ Tool Call 1: mysql_query → Obtiene métricas
     ↓
🛠️ Tool Call 2: get_report_link → Verifica reportes
     ↓
📊 Análisis completo con datos reales
```

### **Interface rica:**
- **Status updates**: `🔄 Análisis iterativo - Iteración 1/5`
- **Tool execution**: `🔍 Ejecutando mysql_query...`
- **Desplegables**: Parámetros y resultados formateados
- **Completión**: `✅ Análisis completado`

## 🎯 **Ejemplos de uso**

### **Análisis de performance:**
```
"Analiza la ejecución 6994"
"Compara TPS entre ejecución 6835 y 6824"
"¿Qué métricas tiene el dataset Consume IP mockbin API?"
```

### **Gestión de reportes:**
```
"Dame el link de descarga del reporte 6994"
"¿Qué reportes están disponibles para la ejecución 6835?"
"Lista los últimos 5 reportes generados"
```

## ⚙️ **Configuración avanzada**

### **Ajustar iteraciones:**
```yaml
MAX_ITERATIONS: 3  # Menos iteraciones para respuestas más rápidas
```

### **Configurar otros proveedores:**
En LiteLLM (`config/litellm_config.yaml`) puedes configurar diferentes proveedores:
```yaml
model_list:
  - model_name: gpt-4
    litellm_params:
      model: azure/gpt-4  # Azure OpenAI
      # model: openai/gpt-4  # OpenAI directo
      # model: anthropic/claude-3  # Anthropic
```

## 🔧 **Requisitos**

### **Sistema funcionando:**
- ✅ Docker compose con LiteLLM, MCPs y OpenWebUI
- ✅ MCPs configurados y funcionando
- ✅ Base de datos `qaperformance` accesible

### **En OpenWebUI:**
- ✅ Función copiada e instalada
- ✅ Valves configuradas correctamente
- ✅ MCPs activados en settings

## 🚨 **Troubleshooting**

### **Función no aparece como modelo:**
- Verificar que es tipo `manifold`
- Revisar logs de OpenWebUI
- Reiniciar contenedor OpenWebUI

### **Tool calls no funcionan:**
- Verificar MCPs en Settings → Models
- Comprobar conectividad: `curl http://localhost:8000`
- Revisar logs de contenedores MCP

### **Error de API:**
- Verificar URLs en Valves
- Comprobar LiteLLM: `curl http://localhost:4000/models`
- Verificar API keys válidas
