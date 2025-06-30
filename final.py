#Determinar cuántos usuarios "invitados" se han conectado en un período de tiempo y el tráfico (Input Octects + Output Octects) 
#que ha tenido cada uno. Debe incluir la posibilidad de ingresar un rango de fechas.
#Ahora incluye registro de valores rechazados con razones del rechazo - SOLO EN EL RANGO DE FECHAS

import pandas as pd
import re
from datetime import datetime, timedelta, date

# =================== VALIDACIONES ===================

EXPRESION_FECHA = re.compile(r"^((2019|202[0-3])\-(0[1-9]|1[0-2])\-(0[1-9]|[12][0-9]|3[01]))$")
EXPRESION_ID = re.compile(r"^\d{1,7}$")
EXPRESION_OCTECTS = re.compile(r"^\d+$")

def validar_formato_fecha(fecha_str: str) -> bool:
    """Valida si la fecha tiene el formato correcto YYYY-MM-DD"""
    return bool(EXPRESION_FECHA.match(fecha_str))

def validar_id(valor: str) -> bool:
    """Valida si el ID tiene formato numérico de 1 a 7 dígitos"""
    return bool(EXPRESION_ID.match(str(valor)))

def validar_octetos(valor: str) -> bool:
    """Valida si los octetos son números válidos"""
    return bool(EXPRESION_OCTECTS.match(str(valor)))

def validar_session_time(valor) -> bool:
    """Valida si el session time es un número válido"""
    return str(valor).isdigit()

def validar_mac_cliente(mac) -> bool:
    """Valida si la MAC del cliente no está vacía o es nula"""
    return not pd.isna(mac) and str(mac).strip() != ''

# =================== VALIDACIÓN DE REGISTROS ===================

def obtener_razones_rechazo(fila, fechas_rango):
    """
    Analiza un registro y retorna las razones por las que fue rechazado.
    """
    razones = []
    
    # Validar que el usuario sea 'invitado-deca'
    if fila['Usuario'] != "invitado-deca":
        razones.append("Usuario no es 'invitado-deca'")
    
    # Validar MAC Cliente
    if not validar_mac_cliente(fila['MAC_Cliente']):
        razones.append("MAC Cliente vacía o nula")
    
    # Validar ID
    if not validar_id(str(fila['ID'])):
        razones.append("ID no cumple formato válido (1-7 dígitos)")
    
    # Validar Input Octects
    if not validar_octetos(str(fila['Input_Octects'])):
        razones.append("Input Octects no es numérico válido")
    
    # Validar Output Octects
    if not validar_octetos(str(fila['Output_Octects'])):
        razones.append("Output Octects no es numérico válido")
    
    # Validar Session Time
    if not validar_session_time(fila['Session_Time']):
        razones.append("Session Time no es numérico válido")
    
    return razones

# =================== CARGA Y LIMPIEZA DE DATOS ===================

def cargar_y_preprocesar_csv(ruta: str) -> pd.DataFrame:
    """Carga y preprocesa el archivo CSV con los datos de conexiones"""
    df = pd.read_csv(ruta, low_memory=False)

    # Extraer solo las fechas en formato YYYY-MM-DD, accesor de Pandas 
    df['Inicio_de_Conexión_Dia'] = df['Inicio_de_Conexión_Dia'].str.extract(r'(\d{4}-\d{2}-\d{2})')
    df['FIN_de_Conexión_Dia'] = df['FIN_de_Conexión_Dia'].str.extract(r'(\d{4}-\d{2}-\d{2})')

    # Convertir a datetime para uso posterior si es necesario
    df['Inicio_de_Conexión'] = pd.to_datetime(df['Inicio_de_Conexión_Dia'], errors='coerce')
    df['FIN_de_Conexión'] = pd.to_datetime(df['FIN_de_Conexión_Dia'], errors='coerce')
    
    return df

# =================== UTILIDADES DE FECHAS ===================

def solicitar_fecha(mensaje: str) -> datetime:
    """Solicita al usuario una fecha y valida que tenga el formato correcto"""
    while True:
        entrada = input(f"{mensaje} (YYYY-MM-DD): ").strip()
        if validar_formato_fecha(entrada):
            try:
                return datetime.strptime(entrada, "%Y-%m-%d")
            except ValueError:
                pass
        print("Fecha inválida. Intenta nuevamente.")

def generar_fechas_en_rango(inicio: date, fin: date) -> list[str]:
    """Genera una lista de fechas en formato string dentro del rango especificado"""
    fechas = []
    actual = inicio
    while actual <= fin:
        fechas.append(actual.strftime("%Y-%m-%d"))
        actual += timedelta(days=1)
    return fechas

# =================== PROCESAMIENTO DE DATOS ===================

def procesar_registros_en_rango(df: pd.DataFrame, fechas_rango: list[str]):
    """
    Procesa todos los registros en el rango de fechas y los separa en válidos y rechazados.
    IMPORTANTE: Solo procesa registros que tengan al menos una fecha en el rango,
    pero valida que AMBAS fechas estén completamente dentro del rango.
    Retorna: (diccionario_usuarios_validos, lista_registros_rechazados)
    """
    usuarios_validos = {}
    registros_rechazados = []
    
    for index, fila in df.iterrows():
        # Verificar si el registro tiene al menos una fecha en el rango para considerarlo
        fecha_inicio = fila['Inicio_de_Conexión_Dia']
        fecha_fin = fila['FIN_de_Conexión_Dia']
        
        fecha_inicio_en_rango = not pd.isna(fecha_inicio) and fecha_inicio in fechas_rango
        fecha_fin_en_rango = not pd.isna(fecha_fin) and fecha_fin in fechas_rango
        
        # Si ninguna fecha está en el rango, saltar este registro completamente
        # (no es relevante para el análisis del período)
        if not fecha_inicio_en_rango or not fecha_fin_en_rango:
            continue
        
        # Obtener razones de rechazo para este registro
        # (aquí se validará que AMBAS fechas estén en el rango)
        razones_rechazo = obtener_razones_rechazo(fila, fechas_rango)
        
        # Si hay razones de rechazo, agregar a la lista de rechazados
        if razones_rechazo:
            registro_rechazado = {
                'Index_Original': index,
                'MAC_Cliente': str(fila['MAC_Cliente']) if not pd.isna(fila['MAC_Cliente']) else 'N/A',
                'Usuario': str(fila['Usuario']) if not pd.isna(fila['Usuario']) else 'N/A',
                'ID': str(fila['ID']) if not pd.isna(fila['ID']) else 'N/A',
                'Fecha_Inicio': str(fila['Inicio_de_Conexión_Dia']) if not pd.isna(fila['Inicio_de_Conexión_Dia']) else 'N/A',
                'Fecha_Fin': str(fila['FIN_de_Conexión_Dia']) if not pd.isna(fila['FIN_de_Conexión_Dia']) else 'N/A',
                'Input_Octects': str(fila['Input_Octects']) if not pd.isna(fila['Input_Octects']) else 'N/A',
                'Output_Octects': str(fila['Output_Octects']) if not pd.isna(fila['Output_Octects']) else 'N/A',
                'Session_Time': str(fila['Session_Time']) if not pd.isna(fila['Session_Time']) else 'N/A',
                'Razones_Rechazo': '; '.join(razones_rechazo),
                'Cantidad_Errores': len(razones_rechazo)
            }
            registros_rechazados.append(registro_rechazado)
            continue
        
        # Si el registro es válido (todas las validaciones pasaron), procesarlo
        procesar_usuario_valido(fila, usuarios_validos)
    
    return usuarios_validos, registros_rechazados

def procesar_usuario_valido(fila, usuarios_validos: dict):
    """Procesa un usuario válido y lo agrega o actualiza en el diccionario de resultados"""
    mac = fila['MAC_Cliente']
    id_usuario = int(fila['ID'])
    input_oct = int(fila['Input_Octects'])
    output_oct = int(fila['Output_Octects'])
    session_time = int(fila['Session_Time'])
    
    if mac not in usuarios_validos:
        usuarios_validos[mac] = {
            'Id_usuario': id_usuario,
            'Usuario': fila['Usuario'],
            'Session_Time': session_time,
            'Input_Octects': input_oct,
            'Output_Octects': output_oct
        }
    else:
        # Acumular valores para el mismo MAC
        usuarios_validos[mac]['Session_Time'] += session_time
        usuarios_validos[mac]['Input_Octects'] += input_oct
        usuarios_validos[mac]['Output_Octects'] += output_oct

# =================== ANÁLISIS Y ESTADÍSTICAS ===================

def mostrar_resumen_analisis(usuarios_validos: dict, registros_rechazados: list):
    """Muestra un resumen simple del análisis realizado"""
    print(f"\n=== RESUMEN DEL ANÁLISIS ===")
    print(f"Usuarios invitados válidos encontrados: {len(usuarios_validos)}")
    print(f"Registros rechazados en el rango: {len(registros_rechazados)}")

# =================== EXPORTACIÓN ===================

def exportar_resultados_a_excel(usuarios_validos: dict, registros_rechazados: list, nombre_archivo: str):
    """
    Exporta los resultados a un archivo Excel con dos hojas:
    - Datos_Validados: Usuarios que cumplieron todos los criterios
    - Datos_Rechazados: Registros rechazados con razones detalladas
    """
    with pd.ExcelWriter(f"{nombre_archivo}.xlsx") as writer:
        # Exportar usuarios válidos
        exportar_usuarios_validos(usuarios_validos, writer)
        
        # Exportar registros rechazados
        exportar_registros_rechazados(registros_rechazados, writer)

def exportar_usuarios_validos(usuarios_validos: dict, writer):
    """Exporta los usuarios válidos a la hoja 'Datos_Validados'"""
    if usuarios_validos:
        df_validados = pd.DataFrame.from_dict(usuarios_validos, orient='index')
        df_validados.index.name = 'MAC_Cliente'
        df_validados.reset_index(inplace=True)
        
        # Convertir Session_Time a formato legible (HH:MM:SS)
        df_validados['Session_Time'] = df_validados['Session_Time'].apply(convertir_a_horas)
        
        df_validados.to_excel(writer, sheet_name='Datos_Validados', index=False)

def convertir_a_horas(segundos):
    """Convierte una cantidad de segundos a formato HH:MM:SS"""
    return str(timedelta(seconds=segundos))


def exportar_registros_rechazados(registros_rechazados: list, writer):
    """Exporta los registros rechazados a la hoja 'Datos_Rechazados'"""
    if registros_rechazados:
        df_rechazados = pd.DataFrame(registros_rechazados)
        df_rechazados.to_excel(writer, sheet_name='Datos_Rechazados', index=False)

# =================== INTERFAZ DE USUARIO ===================

def ejecutar_ciclo_analisis(df: pd.DataFrame):
    """Ejecuta el ciclo principal de análisis con interacción del usuario"""
    print(">>> Análisis de conexiones de usuarios 'invitados' por rango de fechas <<<")
    print(">>> Ahora incluye registro detallado de valores rechazados <<<\n")
    
    while True:
        # Solicitar rango de fechas
        fecha_inicio = solicitar_fecha("Fecha de inicio")
        fecha_fin = solicitar_fecha("Fecha de fin")

        if fecha_inicio > fecha_fin:
            print("La fecha inicial no puede ser posterior a la final.")
            continue

        # Generar lista de fechas en el rango
        fechas_rango = generar_fechas_en_rango(fecha_inicio.date(), fecha_fin.date())
        
        # Solicitar nombre del archivo
        nombre_archivo = input("Nombre del archivo de salida (sin extensión): ").strip()

        # Procesar datos
        usuarios_validos, registros_rechazados = procesar_registros_en_rango(df, fechas_rango)
        
        # Mostrar resumen simplificado
        mostrar_resumen_analisis(usuarios_validos, registros_rechazados)
        
        # Exportar resultados
        exportar_resultados_a_excel(usuarios_validos, registros_rechazados, nombre_archivo)
        
        print(f"\n✅ Archivo '{nombre_archivo}.xlsx' generado exitosamente.")
        print("📊 Contenido del archivo:")
        print("   - Hoja 'Datos_Validados': Usuarios que cumplieron todos los criterios")
        print("   - Hoja 'Datos_Rechazados': Registros rechazados con razones detalladas")
        print("   ⚠️  IMPORTANTE: Solo se muestran rechazos en el rango de fechas especificado")

        # Preguntar si continuar
        continuar = input("\n¿Desea realizar otra búsqueda? (s/n): ").strip().lower()
        if continuar == 'n':
            break

# =================== MAIN ===================

def main():
    """
    Función principal que coordina la ejecución del programa.
    """
    # Cargar datos (la función main no necesita saber cómo se cargan los datos)
    df = cargar_y_preprocesar_csv("file.csv")
    
    # Ejecutar análisis (la función main no necesita saber los detalles del análisis)
    ejecutar_ciclo_analisis(df)

if __name__ == "__main__":
    main() #2019-01-02 