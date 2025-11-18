import os
import sys

# --- Configuración ---
# Sustituye con el ID o nombre de tu suscripción de Azure
# Puedes encontrarlo con: az account list --query "[].{Name:name, Id:id}" -o table
AZURE_SUBSCRIPTION_NAME_OR_ID = "Tu Nombre de Suscripción o ID Aquí"

# El nombre del archivo de salida será fijo o puedes añadir otro parámetro
OUTPUT_FILE = "providers_filtrados_microsoft.txt"

def filter_lines_starting_with_microsoft(input_filepath, output_filepath):
    """
    Lee un archivo de texto, filtra las líneas que NO comienzan con 'Microsoft',
    y escribe las líneas que sí cumplen el criterio en un nuevo archivo.

    Args:
        input_filepath (str): La ruta al archivo de texto de entrada.
        output_filepath (str): La ruta al archivo de texto de salida donde se guardarán
                                las líneas filtradas.
    """
    
    # Comprobar si el archivo de entrada existe
    if not os.path.exists(input_filepath):
        print(f"Error: El archivo de entrada '{input_filepath}' no se encontró.", file=sys.stderr)
        return False # Indicar fallo

    filtered_lines = []
    try:
        with open(input_filepath, 'r', encoding='utf-8') as infile:
            print(f"Leyendo el archivo: {input_filepath}")
            for line_num, line in enumerate(infile, 1):
                stripped_line = line.strip()
                
                if stripped_line.startswith("Microsoft"):
                    filtered_lines.append(line)
        
        print(f"Se encontraron {len(filtered_lines)} líneas que comienzan con 'Microsoft'.")

        with open(output_filepath, 'w', encoding='utf-8') as outfile:
            outfile.writelines(filtered_lines)
        
        print(f"Líneas filtradas guardadas en: {output_filepath}")
        return True # Indicar éxito

    except IOError as e:
        print(f"Error de E/S al procesar los archivos: {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}", file=sys.stderr)
        return False

# --- Uso del script ---
if __name__ == "__main__":
    # sys.argv[0] es el nombre del script mismo
    # sys.argv[1] será el primer argumento (el nombre del archivo de entrada)

    if len(sys.argv) < 2:
        print("Uso: python filter_providers.py <nombre_archivo_entrada.txt>", file=sys.stderr)
        print("Ejemplo: python filter_providers.py mis_providers.txt", file=sys.stderr)
        sys.exit(1) # Salir con código de error

    input_file_param = sys.argv[1] # Capturamos el primer parámetro como el nombre del archivo de entrada

    print("Iniciando el proceso de filtrado...")
    success = filter_lines_starting_with_microsoft(input_file_param, OUTPUT_FILE)
    
    if success:
        print("Proceso de filtrado completado exitosamente.")
    else:
        print("El proceso de filtrado falló.")
        sys.exit(1) # Salir con código de error si el filtrado no tuvo éxito