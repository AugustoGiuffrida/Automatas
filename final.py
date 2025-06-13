import pandas as pd
import re
from datetime import datetime, timedelta, date

# =================== VALIDACIONES ===================

EXPRESION_FECHA = re.compile(r"^((2019|202[0-3])\-(0[1-9]|1[0-2])\-(0[1-9]|[12][0-9]|3[01]))$")
EXPRESION_ID = re.compile(r"^\d{1,7}$")
EXPRESION_OCTECTS = re.compile(r"^\d+$")

def validar_formato_fecha(fecha_str: str) -> bool:
    return bool(EXPRESION_FECHA.match(fecha_str))

def validar_id(valor: str) -> bool:
    return bool(EXPRESION_ID.match(str(valor)))

def validar_octetos(valor: str) -> bool:
    return bool(EXPRESION_OCTECTS.match(str(valor)))


# =================== CARGA Y LIMPIEZA DE DATOS ===================

def cargar_y_preprocesar_csv(ruta: str) -> pd.DataFrame:
    df = pd.read_csv(ruta, low_memory=False)

    df['Inicio_de_Conexión_Dia'] = df['Inicio_de_Conexión_Dia'].str.extract(r'(\d{4}-\d{2}-\d{2})')
    df['FIN_de_Conexión_Dia'] = df['FIN_de_Conexión_Dia'].str.extract(r'(\d{4}-\d{2}-\d{2})')

    df['Inicio_de_Conexión'] = pd.to_datetime(df['Inicio_de_Conexión_Dia'], errors='coerce')
    df['FIN_de_Conexión'] = pd.to_datetime(df['FIN_de_Conexión_Dia'], errors='coerce')
    
    return df


# =================== UTILIDADES ===================

def solicitar_fecha(mensaje: str) -> datetime:
    while True:
        entrada = input(f"{mensaje} (YYYY-MM-DD): ").strip()
        if validar_formato_fecha(entrada):
            try:
                return datetime.strptime(entrada, "%Y-%m-%d")
            except ValueError:
                pass
        print("Fecha inválida. Intenta nuevamente.")

def fechas_en_rango(inicio: date, fin: date) -> list[str]:
    fechas = []
    actual = inicio
    while actual <= fin:
        fechas.append(actual.strftime("%Y-%m-%d"))
        actual += timedelta(days=1)
    return fechas


# =================== PROCESAMIENTO DE USUARIOS ===================

def procesar_usuarios_invitados(df: pd.DataFrame, fechas: list[str]) -> dict:
    resultados = {}

    for index, fila in df.iterrows():
        if fila['Usuario'] != "invitado-deca":
            continue
        if fila['Inicio_de_Conexión_Dia'] not in fechas and fila['FIN_de_Conexión_Dia'] not in fechas:
            continue

        mac = fila['MAC_Cliente']
        id_usuario = int(fila['ID']) if validar_id(str(fila['ID'])) else 0
        input_oct = int(fila['Input_Octects']) if validar_octetos(str(fila['Input_Octects'])) else 0
        output_oct = int(fila['Output_Octects']) if validar_octetos(str(fila['Output_Octects'])) else 0
        session_time = int(fila['Session_Time']) if str(fila['Session_Time']).isdigit() else 0

        if mac not in resultados:
            resultados[mac] = {
                'Id_usuario': id_usuario,
                'Usuario': fila['Usuario'],
                'Session_Time': session_time,
                'Input_Octects': input_oct,
                'Output_Octects': output_oct
            }
        else:
            resultados[mac]['Session_Time'] += session_time
            resultados[mac]['Input_Octects'] += input_oct
            resultados[mac]['Output_Octects'] += output_oct

    print(f"Usuarios invitados conectados en el rango de fechas: {len(resultados)}")
    return resultados


# =================== EXPORTACIÓN ===================

def exportar_a_excel(dataset: dict, nombre_archivo: str):
    df = pd.DataFrame.from_dict(dataset, orient='index')
    df.index.name = 'MAC_Cliente'
    df.reset_index(inplace=True)

    df['Session_Time'] = df['Session_Time'].apply(lambda x: str(timedelta(seconds=x)))

    with pd.ExcelWriter(f"{nombre_archivo}.xlsx") as writer:
        df.to_excel(writer, sheet_name='Resultados', index=False)


# =================== MAIN ===================

def main():
    df = cargar_y_preprocesar_csv("file.csv")

    print(">>> Análisis de conexiones de usuarios 'invitados' por rango de fechas <<<\n")
    
    while True:
        fecha_inicio = solicitar_fecha("Fecha de inicio")
        fecha_fin = solicitar_fecha("Fecha de fin")

        if fecha_inicio > fecha_fin:
            print("La fecha inicial no puede ser posterior a la final.")
            continue

        fechas = fechas_en_rango(fecha_inicio.date(), fecha_fin.date())
        nombre_archivo = input("Nombre del archivo de salida (sin extensión): ").strip()

        dataset = procesar_usuarios_invitados(df, fechas)
        exportar_a_excel(dataset, nombre_archivo)

        continuar = input("\n¿Desea realizar otra búsqueda? (s/n): ").strip().lower()
        if continuar == 'n':
            break


if __name__ == "__main__":
    main()
