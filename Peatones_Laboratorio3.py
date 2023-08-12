import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import psutil
import time

def get_resource_info(code_to_measure):
    resources_save_data = get_resource_usage(code_to_measure=code_to_measure)
    print(f"Métricas de funcionamiento del código:")
    print(f"Tiempo de CPU: {resources_save_data['tiempo_cpu']} segundos")
    print(f"Uso de memoria virtual: {resources_save_data['memoria_virtual']} MB")
    print(f"Uso de memoria residente: {resources_save_data['memoria_residente']} MB")
    print(f"Porcentaje de uso de CPU: {resources_save_data['%_cpu']} %")


# Función que devuelve el tiempo de CPU y el uso de memoria para un código dado
def get_resource_usage(code_to_measure):
    process = psutil.Process()
    #get cpu status before running the code
    cpu_percent = psutil.cpu_percent()
    start_time = time.time()
    code_to_measure()
    end_time = time.time()
    end_cpu_percent = psutil.cpu_percent() 
    cpu_percent = end_cpu_percent - cpu_percent
    cpu_percent = cpu_percent / psutil.cpu_count()
    
    return {
        'tiempo_cpu': end_time - start_time,
        'memoria_virtual': process.memory_info().vms / (1024 * 1024),  # Convertir a MB
        'memoria_residente': process.memory_info().rss / (1024 * 1024),  # Convertir a MB
        '%_cpu': cpu_percent # Porcentaje de uso de CPU
    }


def calculo_velocidad(grupo):
    grupo['velocidad'] = np.sqrt((grupo['X'].diff(periods=1)**2 + grupo['Y'].diff(periods=1)**2)) / (1/25)
    grupo['velocidad'].fillna(0, inplace=True)
    grupo['promedio_velocidad'] = grupo['velocidad'].mean()
    return grupo

def main():
    archivo_txt = "UNI_CORR_500_01.txt"
    df = pd.read_csv(archivo_txt, delimiter="\t", skiprows=3)
    
    grupo = df.groupby('# PersID', group_keys=False)
    df_vel = grupo.apply(calculo_velocidad)
    
    df_vel.to_csv("Data_Frame.txt", sep='\t', index=False)
    
    media=df_vel["promedio_velocidad"].mean()
    desvest=df_vel["promedio_velocidad"].std()
    print(f"Media: {media}")
    print(f"Desviación estándar: {desvest}")
    
    plt.figure(figsize=(10, 6))
    plt.hist(df_vel['promedio_velocidad'], bins=20, edgecolor='black')
    plt.xlabel('Velocidad Promedio')
    plt.ylabel('Frecuencia')
    plt.title('Histograma de Velocidades Promedio por Peatón')
    plt.tight_layout()
    plt.show()

get_resource_info(main)