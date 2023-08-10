import pandas as pd
import matplotlib.pyplot as plt
import time
import psutil

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

def leer_archivo():
    for archivo in ["UNI_CORR_500_01.txt","UNI_CORR_500_04.txt","UNI_CORR_500_08.txt"]:
        df = pd.read_csv(archivo, delimiter="\t", skiprows=3)
        df = df.rename(columns={"# PersID": "ID"})
        plt.hist2d(df["X"],df["Y"], bins=(40,30),cmap=plt.cm.inferno)
        barra_color = plt.colorbar()
        barra_color.set_label('Frecuencia')
        plt.xlabel('Coordenada X')
        plt.ylabel('Coordenada Y')
        plt.title('Frecuencia de peatones (Histograma 2D)')
        plt.show()
get_resource_info(leer_archivo)