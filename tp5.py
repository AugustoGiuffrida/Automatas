#Determinar cuántos usuarios “invitados” se han conectado en un período de tiempo y el tráfico (Input Octects + Output Octects) 
#que ha tenido cada uno. Debe incluir la posibilidad de ingresar un rango de fechas. 
import pandas as pd
import re
from datetime import datetime,timedelta,date
#df=pd.read_csv("file.csv")
#usuarios=df['Usuario'].tolist()
expresion_hora=re.compile(r"^([0-1][0-9]|[2][0-3])\:[0-5][0-9]\:[0-5][0-9]$") #19:46:08 |2[0-3]
expresion_fecha=re.compile(r"^((2019|202[0-3])\-(0[1-9]|1[0-2])\-(0[1-9]|1[0-9]|2[0-9]|3[0-1]))$") ### 
# # for i in range(len(usuarios)):

# #     if usuarios[i]=="invitado-deca":
# #        print(f"Usuario {usuarios[i]} conectado en {df['Session_Time'][i]} segundos con {df['Input_Octects'][i]} Octects de entrada y {df['Output_Octects'][i]} Octects de salida")



def iterate_over_days(start_date, end_date):
    delta = timedelta(days=1)
    while start_date <= end_date:
        print(start_date.strftime("%Y-%m-%d"))
        # # for i in range(len(usuarios)):

# #     if usuarios[i]=="invitado-deca":
# #        print(f"Usuario {usuarios[i]} conectado en {df['Session_Time'][i]} segundos con {df['Input_Octects'][i]} Octects de entrada y {df['Output_Octects'][i]} Octects de salida")
        start_date += delta


def check_regular(string,expresion):
    if expresion.search(string):
        return True
    else:
        raise ValueError("Rango de fecha inválido. Por favor, usa de 2019 a 2023.") 



if __name__=="__main__":
    try:
        print("Ingrese un rango de fechas")

        initial_date = input("Fecha y hora (YYYY-MM-DD HH:MM:SS): ").strip()
        
        final_date = input("Fecha y hora (YYYY-MM-DD HH:MM:SS): ").strip()

        parsed_initial_date = datetime.strptime(initial_date, "%Y-%m-%d %H:%M:%S")
        parsed_final_date = datetime.strptime(final_date, "%Y-%m-%d %H:%M:%S")
        date=[parsed_initial_date.strftime("%Y-%m-%d"),parsed_final_date.strftime("%Y-%m-%d")]
        hora=[parsed_initial_date.strftime("%H:%M:%S"),parsed_final_date.strftime("%H:%M:%S")]
        
        for fecha in date:
            check_regular(fecha,expresion_fecha)
        for hora in hora:
            check_regular(hora,expresion_hora)
        iterate_over_days(datetime.strptime(date[0], "%Y-%m-%d").date(),datetime.strptime(date[1], "%Y-%m-%d").date())    
    except ValueError as e:
        print("Error:", e)
        exit()
        
        #2021-11-14 19:46:08
        #2021-11-19 20:46:08
        
