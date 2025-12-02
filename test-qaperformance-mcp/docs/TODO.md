## Test multisession maybe with user pass¿?

## Create chat persistence policy

## Add function button to generate interactive graphs

## TODO: Create my own especific image
## TODO: Revisar seguridad con Alex (amigo de David) pasos para que la herramienta cumpla estandares seguridad.

* Hace falta seguir mismo formato de front del departamento. (Hablar con Luis/Javi Ruiz)
Respecto a ese tema creo que lo mejor es modificar el frontend (hacer un script que lo modifique y que le dé un formato similar al que sigue el departamento)

* El mcp de mysql utilizado es de código abierto y por ahora tiene mantenimiento, pero quizás por politicas del departamento toque cambiarlo, he visto alguna solución más estándar de google (https://cloud.google.com/blog/products/ai-machine-learning/mcp-toolbox-for-databases-now-supports-model-context-protocol) (falta testearla)

*Arquitectura
MCPo benborla29/mcp-server-mysql@2.0.2 (MCP) <-> openwebui (frontend) <-> LiteLLM <--> AzureOpenIA(proveedor de IA)

* El sistema actual nos permite escalar significativamente en funcionalidades (generación de gráficos, guarda el chat de la sesión, mantiene contexto, facilidad de agregar nuevos mcps github, documentación etc)

* Funcionalidades que nos interesa tener? generación gráficas específicas
generación links para revisar la ejecución/proyecto que necesitas
MCP github para acceder al código fuente de los repositorios


** Limitar prompt injection
