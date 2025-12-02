#!/bin/bash

# Configuración
OPENWEBUI_URL="http://localhost:3000"
API_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjM3NTBiMGVlLWVkNTMtNDY2OS1hZjljLWJhMGFjYTY2YjVjMSJ9.nWKGr_WkiQGPrpQi4scm3OEyeQq_hbBKdLI260o4Xro"  # Reemplazar con tu API key de OpenWebUI

# Prompt
PROMPT="Compara tps a traves del tiempo de la ejecución la execution_id=6835 y execution_id=6824 del molulo LALIGA del dataset Consume IP mockbin API. Dame un analisis de los resultados.
Al finalizar el análisis pon Resultado: PASSED ✅ , si se cumplen las siguientes condiciones:

El porcentaje de errores de ambos datasets es igual al 0%
El p95 de la segunda ejecución no supera en más de un 10% el p95 de tiempos de respuesta de la primera ejecución
Caso contrario pon Resultado: FAILED ❌.
No agregues explicaciones adicionales despues de eso"

# Construir el JSON payload
JSON_PAYLOAD=$(cat <<EOF
{
  "model": "gpt-4",
  "messages": [
    {
      "role": "user",
      "content": $(echo "$PROMPT" | jq -Rs .)
    }
  ],
  "stream": false
}
EOF
)

echo "=== Enviando request a OpenWebUI API ==="
echo ""

# Hacer el request
RESPONSE=$(curl -s -X POST "${OPENWEBUI_URL}/api/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_KEY}" \
  -d "$JSON_PAYLOAD")

# Extraer y mostrar la respuesta
echo "=== Respuesta ==="
echo ""
echo "$RESPONSE" | jq -r '.choices[0].message.content // .error // .'
echo ""
echo "=== Respuesta completa (JSON) ==="
echo "$RESPONSE" | jq .
