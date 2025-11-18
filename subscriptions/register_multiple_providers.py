import subprocess
import json
import sys
import os # Importar os para comprobar si el archivo existe

# --- Configuración ---
# Sustituye con el ID o nombre de tu suscripción de Azure
AZURE_SUBSCRIPTION_NAME_OR_ID = "SmartWifi Performance"

# Nombre del archivo de texto que contiene la lista de Resource Providers
PROVIDERS_FILE = "providers.txt"

def run_azure_cli_command(command_parts, error_message="Error al ejecutar comando de Azure CLI", suppress_output=False):
    """
    Ejecuta un comando de Azure CLI y maneja errores.
    Retorna la salida JSON si el comando es exitoso.
    """
    try:
        result = subprocess.run(
            command_parts,
            check=True,  # Lanza CalledProcessError si el código de salida no es 0
            capture_output=True,
            text=True,   # Para capturar la salida como texto
            encoding='utf-8' # Asegura la codificación correcta
        )
        if suppress_output:
            return None # No se necesita la salida
        
        # Algunos comandos no retornan JSON por defecto
        if result.stdout.strip().startswith('{') or result.stdout.strip().startswith('['):
            return json.loads(result.stdout)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"ERROR: {error_message}", file=sys.stderr)
        print(f"Comando fallido: {' '.join(e.cmd)}", file=sys.stderr)
        print(f"Salida estándar: {e.stdout}", file=sys.stderr)
        print(f"Salida de error: {e.stderr}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError:
        # Esto ocurre si la salida no es JSON, lo cual es esperado para algunos comandos
        return result.stdout.strip()
    except FileNotFoundError:
        print("ERROR: Azure CLI no encontrado. Asegúrate de que está instalado y en tu PATH.", file=sys.stderr)
        sys.exit(1)

def get_providers_from_file(file_path):
    """
    Lee los nombres de los Resource Providers de un archivo de texto.
    Cada línea del archivo es un nombre de proveedor.
    """
    if not os.path.exists(file_path):
        print(f"ERROR: El archivo de providers '{file_path}' no se encontró en el directorio actual.", file=sys.stderr)
        sys.exit(1)
    
    providers = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            provider = line.strip()
            if provider and not provider.startswith('#'): # Ignorar líneas vacías o comentarios
                providers.append(provider)
    if not providers:
        print(f"ADVERTENCIA: El archivo '{file_path}' está vacío o solo contiene comentarios. No hay providers para registrar.", file=sys.stderr)
    return providers

def register_resource_providers_from_list(subscription, providers_list):
    print("Iniciando sesión en Azure (si es necesario)...")
    # Redirigimos la salida de az login a /dev/null para no mostrar el mensaje de "abriendo navegador"
    # y porque no necesitamos procesar su salida.
    run_azure_cli_command(["az", "login", "--output", "none"], suppress_output=True)

    # Verificar si el login fue exitoso (comprobando una cuenta activa)
    try:
        run_azure_cli_command(["az", "account", "show", "--output", "none"], 
                              "No se pudo verificar la sesión de Azure. Por favor, ejecuta 'az login' manualmente.", 
                              suppress_output=True)
    except SystemExit: # Captura el sys.exit(1) de run_azure_cli_command
        sys.exit(1)


    print(f"Estableciendo la suscripción: '{subscription}'...")
    run_azure_cli_command(["az", "account", "set", "--subscription", subscription],
                          f"No se pudo establecer la suscripción '{subscription}'. Verifica el nombre/ID y los permisos.", 
                          suppress_output=True)

    if not providers_list:
        print("No hay Resource Providers válidos para procesar en el archivo. Finalizando.")
        return

    for provider_namespace in providers_list:
        print(f"\n--- Procesando Resource Provider: {provider_namespace} ---")
        try:
            provider_state = run_azure_cli_command(["az", "provider", "show", "--namespace", provider_namespace, "--query", "registrationState", "--output", "tsv"])
            
            if provider_state == "Registered":
                print(f"El Resource Provider '{provider_namespace}' ya está registrado. No se requiere ninguna acción.")
            else:
                print(f"Registrando el Resource Provider '{provider_namespace}'...")
                # Usamos --wait para que el comando espere a que el registro se complete
                run_azure_cli_command(["az", "provider", "register", "--namespace", provider_namespace, "--wait"],
                                      f"Fallo al registrar el Resource Provider '{provider_namespace}'.")
                print(f"¡El Resource Provider '{provider_namespace}' ha sido registrado exitosamente!")
            
            # Opcional: Mostrar el estado final después de cada registro
            final_state = run_azure_cli_command(["az", "provider", "show", "--namespace", provider_namespace, "--query", "registrationState", "--output", "tsv"])
            print(f"Estado final de '{provider_namespace}': {final_state}")

        except SystemExit:
            print(f"Continuando con el siguiente provider debido a un error con '{provider_namespace}'.", file=sys.stderr)
            # No salimos del script si falla un solo provider, solo informamos y continuamos
        except Exception as e:
            print(f"Ocurrió un error inesperado al procesar '{provider_namespace}': {e}", file=sys.stderr)
            print(f"Continuando con el siguiente provider.", file=sys.stderr)


if __name__ == "__main__":
    # 1. Obtener la lista de providers del archivo
    providers_to_register = get_providers_from_file(PROVIDERS_FILE)

    # 2. Ejecutar la función principal de registro
    register_resource_providers_from_list(AZURE_SUBSCRIPTION_NAME_OR_ID, providers_to_register)

    print("\nProceso de registro de Resource Providers finalizado para todos los proveedores en el archivo.")