#Determinar cuántos usuarios “invitados” se han conectado en un período de tiempo y el tráfico (Input Octects + Output Octects) 
#que ha tenido cada uno. Debe incluir la posibilidad de ingresar un rango de fechas. 
import pandas as pd
import re
from datetime import datetime,timedelta,date
df=pd.read_csv("file.csv")


# Eliminar cualquier contenido no válido antes de la fecha
df['Inicio_de_Conexión_Dia'] = df['Inicio_de_Conexión_Dia'].str.extract(r'(\d{4}-\d{2}-\d{2})')
df['FIN_de_Conexión_Dia'] = df['FIN_de_Conexión_Dia'].str.extract(r'(\d{4}-\d{2}-\d{2})')

# Combinar fecha y hora en columnas datetime reales
df['Inicio_de_Conexión'] = pd.to_datetime(df['Inicio_de_Conexión_Dia'] + ' ' + df['Inicio_de_Conexión_Hora'])
df['FIN_de_Conexión'] = pd.to_datetime(df['FIN_de_Conexión_Dia'] + ' ' + df['FIN_de_Conexión_Hora'])


#usuarios=df['Usuario'].tolist()
expresion_hora=re.compile(r"^([0-1][0-9]|[2][0-3])\:[0-5][0-9]\:[0-5][0-9]$") #19:46:08 |2[0-3]
expresion_fecha=re.compile(r"^((2019|202[0-3])\-(0[1-9]|1[0-2])\-(0[1-9]|1[0-9]|2[0-9]|3[0-1]))$") ### 


def main():
    print("Ingrese el rango de fechas y horas para la búsqueda de usuarios 'invitados'.")
    
    fecha_inicio = solicitar_fecha_hora("Fecha y hora inicial")
    fecha_fin = solicitar_fecha_hora("Fecha y hora final")

    fechas_en_rango = iterate_over_days(fecha_inicio.date(), fecha_fin.date())
    dataset=get_users(fechas_en_rango)
    to_excel(dataset)

def solicitar_fecha_hora(mensaje):
    while True:
        entrada = input(f"{mensaje} (YYYY-MM-DD HH:MM:SS): ").strip()
        try:
            fecha_str, hora_str = entrada.split()
            check_regular(fecha_str, expresion_fecha)
            check_regular(hora_str, expresion_hora)
            return datetime.strptime(entrada, "%Y-%m-%d %H:%M:%S")
        except (ValueError, IndexError):
            print("Formato inválido. Intenta nuevamente con el formato correcto.")


def iterate_over_days(start_date, end_date):
    diference_between_dates=[]

    delta = timedelta(days=1)
    while start_date <= end_date:

        diference_between_dates.append(start_date.strftime("%Y-%m-%d"))
        start_date += delta
    return diference_between_dates


def get_users(diference_between_dates):
    encontrados = 0
    resultados=[]
    for index, row in df.iterrows(): #index es el numero de la fila y row el contenido
        if row['Usuario'] == "invitado-deca" and (
            row['Inicio_de_Conexión_Dia'] in diference_between_dates or 
            row['FIN_de_Conexión_Dia'] in diference_between_dates):
            encontrados += 1
            #esto exportarlo al excel
            resultados.append({'Usuario':[row['Usuario']],
                     'Session_Time':[row['Session_Time']],
                     'Input_Octects':[row['Input_Octects']],
                     'Output_Octects':[row['Output_Octects']]})
    return resultados
    
def to_excel(dataset):
    df=pd.DataFrame(dataset)
    with pd.ExcelWriter('resultados.xlsx') as writer:
        df.to_excel(writer, sheet_name='Resultados')
def check_regular(string,expresion):
    if expresion.search(string):
        return True
    else:
        raise ValueError


if __name__=="__main__":
    #print(df.columns)
    #print(df.dtypes)

    main()
    #2019-01-02 08:56:28
    #2019-01-02 09:17:18
        
