import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import KDTree
import math
import streamlit as st 
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

#Función para mapa de calor (histograma)
def mapa_calor(df, bins_x, bins_y):
    # Crear una figura y un eje
    fig, ax = plt.subplots(figsize=(10, 6))

    # Crear el histograma 2D
    hist = ax.hist2d(df["X"], df["Y"], bins=(bins_x, bins_y), cmap=plt.cm.inferno)

    # Añadir una barra de color
    barra_color = plt.colorbar(hist[3], ax=ax)
    barra_color.set_label('Frecuencia')

    # Establecer etiquetas de los ejes y el título
    ax.set_xlabel('Coordenada X')
    ax.set_ylabel('Coordenada Y')
    ax.set_title('Frecuencia de peatones (Histograma 2D)')
    #plt.show()
    st.pyplot(fig)

# Función para calcular la velocidad
def calculo_velocidad(grupo):
    grupo['velocidad'] = np.sqrt((grupo['X'].diff(periods=1)**2 + grupo['Y'].diff(periods=1)**2)) / (1/25)
    grupo['velocidad'].fillna(0, inplace=True)
    return grupo

def hist_velocidad(df_filtered, bins):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(df_filtered['velocidad'], bins=bins, color='#00538b', alpha=0.7)
    ax.set_xlabel('Velocidad de cada Peatón')
    ax.set_ylabel('Frecuencia')
    ax.set_title('Distribución de Velocidad de Peatones')
    st.pyplot(fig)

# Función para calcular sk
def calcular_distancia(row, variable1):
    x2 = variable1[0]
    y2 = variable1[1]
    x1 = row["X"]
    y1 = row["Y"]
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def buscar_peatones_cercanos(dataframe, frame_interes):
    df_frame = dataframe[dataframe["Frame"] == frame_interes]
    coordinates = df_frame[["X", "Y"]].values
    tree = KDTree(coordinates)
    radius = 3.0
    
    for peaton_ID in df_frame["# PersID"]:
        query_point = coordinates[df_frame["# PersID"] == peaton_ID]
        neighbor_indices = tree.query_ball_point(query_point, radius)
        neighbor_indices = [index for index in neighbor_indices[0] if df_frame["# PersID"].iloc[index] != peaton_ID]
        
        cantidad_peatones_vecinos = len(neighbor_indices)
        dataframe.loc[(dataframe["# PersID"] == peaton_ID) & (dataframe["Frame"] == frame_interes), "CantidadVecinos"] = cantidad_peatones_vecinos
        
        neighbor_indices_dataframe = df_frame.iloc[neighbor_indices]
        distancias = neighbor_indices_dataframe.apply(calcular_distancia, variable1=query_point[0], axis=1)
        suma_distancias = distancias.sum()
        
        dataframe.loc[(dataframe["# PersID"] == peaton_ID) & (dataframe["Frame"] == frame_interes), "DistanciaTotal"] = suma_distancias
        
        if cantidad_peatones_vecinos > 0:
            sk = suma_distancias / cantidad_peatones_vecinos
            dataframe.loc[(dataframe["# PersID"] == peaton_ID) & (dataframe["Frame"] == frame_interes), "sk"] = sk

def scatter_plot(sk, velocidad):
    # Crear el scatter plot
    fig, ax = plt.subplots(figsize=(10, 6))

    # Hacer el gráfico de dispersión
    ax.scatter(sk, velocidad, alpha=0.5)
    ax.set_xlabel('sk')
    ax.set_ylabel('Velocidad de Peatón')
    ax.set_title('Scatter Plot: sk vs Velocidad de Peatón')
    ax.grid(True)
    #plt.show()
    st.pyplot(fig)

def main():
    st.title('Análisis de Peatones')

    # Leer el archivo de datos original
    archivo_txt = "UNI_CORR_500_01.txt"
    df = pd.read_csv(archivo_txt, delimiter="\t", skiprows=3)
    with st.sidebar: 
        st.write("Definir tamaño de los ejes del Mapa de Calor")
        bins_x = st.slider('Número de Bins en el eje X:', min_value=1, max_value=50, value=40)
        bins_y = st.slider('Número de Bins en el eje Y:', min_value=1, max_value=50, value=30)
        st.write("Bins eje x =", bins_x)
        st.write("Bins eje y =", bins_y)

    # Mapa de calor
    st.header('Mapa de Calor')
    mapa_calor(df, bins_x, bins_y)

    # Dividir por peatón
    grupo = df.groupby('# PersID', group_keys=False)
    df_vel = grupo.apply(calculo_velocidad)

    # Agregar columnas
    df["DistanciaTotal"] = 0.0
    df["CantidadVecinos"] = 0
    df["sk"] = 0.0

    # Obtener todos los frames únicos en el DataFrame
    frames_unicos = df["Frame"].unique()

    # Realizar búsqueda de peatones cercanos para todos los frames
    for frame_interes in frames_unicos:
        buscar_peatones_cercanos(df_vel, frame_interes)

    # Filtrar los puntos con velocidad distinta de cero
    df_filtered = df_vel[df_vel['velocidad'] != 0]
    with st.sidebar:
        st.write("Definir tamaño del eje de Velocidad")
        bins_velocidad = st.slider('Número de Bins en el gráfico de Velocidad:', min_value=1, max_value=50, value=50)
        st.write("Bins eje x =", bins_velocidad)

    st.header('Gráfico de Velocidad')
    hist_velocidad(df_filtered, bins_velocidad)
    
    # Promedio de sk
    promedio_sk = round(df_filtered['sk'].mean(),4)
    min_sk = round(df_filtered['sk'].min(),4)
    max_sk = round(df_filtered['sk'].max(),4)
    mediana_sk = round(df_filtered['sk'].median(),4)
    varianza_sk = round(df_filtered['sk'].var(),4)
    desv_sk = round(df_filtered['sk'].std(),4)

    st.header('Estadísticas descriptivas de sk')
    data = {'Estadístico': ['Promedio', 'Mínimo', 'Máximo', 'Mediana', 'Desviación Estándar', 'Varianza'],
            'Valor': [promedio_sk, min_sk, max_sk, mediana_sk, desv_sk, varianza_sk]}

    estadisticos = pd.DataFrame(data)
    st.table(estadisticos)

    # Scatter plot
    st.header('Scatter Plot: sk vs Velocidad de Peatón')
    scatter_plot(df_filtered['sk'], df_filtered['velocidad'])

    # Mostrar los primeros 10 registros de df_filtered
    st.header('Los primeros 10 registros')
    st.write(df_filtered.head(10))
get_resource_info(main)
