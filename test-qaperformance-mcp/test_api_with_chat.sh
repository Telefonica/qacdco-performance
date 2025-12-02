#!/bin/bash

# Configuración
OPENWEBUI_URL="http://localhost:3000"
API_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjM3NTBiMGVlLWVkNTMtNDY2OS1hZjljLWJhMGFjYTY2YjVjMSJ9.nWKGr_WkiQGPrpQi4scm3OEyeQq_hbBKdLI260o4Xro"
MODEL="performance_model.gpt-4"

# Prompt
PROMPT="Compara tps a traves del tiempo de la ejecución la execution_id=6835 y execution_id=6824 del molulo LALIGA del dataset Consume IP mockbin API. Dame un analisis de los resultados.
Al finalizar el análisis pon Resultado: PASSED ✅ , si se cumplen las siguientes condiciones:

El porcentaje de errores de ambos datasets es igual al 0%
El p95 de la segunda ejecución no supera en más de un 10% el p95 de tiempos de respuesta de la primera ejecución
Caso contrario pon Resultado: FAILED ❌.
No agregues explicaciones adicionales despues de eso"

# Listar modelos disponibles
echo "=== Listando modelos disponibles ==="
MODELS_RESPONSE=$(curl -s -X GET "${OPENWEBUI_URL}/api/models" \
  -H "Authorization: Bearer ${API_KEY}")

echo "$MODELS_RESPONSE" | jq -r '.data[]? | "- \(.id)"'
echo ""

echo "=== Creando nuevo chat en OpenWebUI ==="
echo ""

# Paso 1: Crear un nuevo chat
NEW_CHAT_PAYLOAD=$(cat <<EOF
{
  "chat": {
    "name": "Performance Test - LALIGA",
    "models": ["${MODEL}"]
  }
}
EOF
)

CREATE_CHAT_RESPONSE=$(curl -s -X POST "${OPENWEBUI_URL}/api/v1/chats/new" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_KEY}" \
  -d "$NEW_CHAT_PAYLOAD")

CHAT_ID=$(echo "$CREATE_CHAT_RESPONSE" | jq -r '.id // empty')

if [ -z "$CHAT_ID" ]; then
  echo "❌ Error: No se pudo crear el chat"
  echo "Respuesta: $CREATE_CHAT_RESPONSE"
  exit 1
fi

echo "✅ Chat creado con ID: $CHAT_ID"
echo "🔗 URL: ${OPENWEBUI_URL}/c/${CHAT_ID}"
echo ""

# Paso 2: Enviar mensaje al chat
echo "=== Enviando mensaje al chat ==="

CHAT_PAYLOAD=$(cat <<EOF
{
  "model": "${MODEL}",
  "messages": [
    {
      "role": "user",
      "content": $(echo "$PROMPT" | jq -Rs .)
    }
  ],
  "chat_id": "${CHAT_ID}",
  "tool_ids": ["mcp_mysql_query_post"]
}
EOF
)

RESPONSE=$(curl -s -X POST "${OPENWEBUI_URL}/api/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_KEY}" \
  -d "$CHAT_PAYLOAD")

# Extraer y mostrar la respuesta
echo ""
echo "=== Respuesta del modelo ==="
echo ""
CONTENT=$(echo "$RESPONSE" | jq -r '.choices[0].message.content // .error // "Error procesando respuesta"')
echo "$CONTENT"
echo ""
echo "=== Chat disponible en: ${OPENWEBUI_URL}/c/${CHAT_ID} ==="
