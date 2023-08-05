import numpy as np
import matplotlib.pyplot as plt
import time
import psutil

def frecuencia_xy (coordenadas):
    coord_xy = [tuple(coordenadas[i][:2]) for i in range (len(coordenadas))]
    coord_xy_unicos = {}
    for i in coord_xy:
        if i in coord_xy_unicos:
            coord_xy_unicos[i] += 1
        else:
            coord_xy_unicos[i] = 1

    maximo_xy = max(coord_xy_unicos.values())
    for i in coord_xy_unicos:
        if coord_xy_unicos[i] == maximo_xy:
            print(f"Coordenada {i}: se repite {maximo_xy} veces")

def frecuencia_dict (coordenadas, pos):
    eje={coord[pos]: 0 for coord in coordenadas}
    if pos == 0:
        aux="X"
    else:
        aux="Y"

    for fila in range (len(coordenadas)):
        coord=coordenadas[fila][pos]
        if coord in eje.keys():
            eje[coord]+=1 #Frecuencia

    max_frec_eje=max(eje.values())
    num_mas_eje=[numero for numero, frecuencia_eje in eje.items() if frecuencia_eje==max_frec_eje]
    print(f"Coordenada(s) que más se repite(n) en {aux}: {num_mas_eje} con un recuento de {max_frec_eje} oportunidades")

def mts_pixel(coordenadas,pos):###conversion de metros a pixeles en y###
    lista_pixel = []
    for i in coordenadas:
        aux = i[pos]
        if pos == 0:
            pixel = (35.556*float(aux)+320)
            lista_pixel.append(pixel)
        else:
            pixel = (-96 * float(aux)) + 480 
            lista_pixel.append(pixel)
    return lista_pixel

def get_resource_info(code_to_measure):
    resources_save_data = get_resource_usage(code_to_measure=code_to_measure)
    print(f"Metricas de funcionamiento del código:")
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

def main (coordenadas):
    #Mayor Frecuencia Metros
    frecuencia_dict(coordenadas,0)
    frecuencia_dict(coordenadas,1)
    frecuencia_xy(coordenadas)

    #Conversion a pixel
    pixels_x = mts_pixel(coordenadas[:],0)
    pixels_y = mts_pixel(coordenadas[:],1)
    redondeados_x = [int(round(valor, 0)) for valor in pixels_x]
    redondeados_y = [int(round(valor, 0)) for valor in pixels_y]
    coordenadas_pixel= list(zip(redondeados_x, redondeados_y))

    #Mayor Frecuencia Pixel
    frecuencia_dict(coordenadas_pixel,0)
    frecuencia_dict(coordenadas_pixel,1)
    frecuencia_xy(coordenadas_pixel)

    #Matriz de calor(de chat gpt el codigo)
    tamaño_x = 640
    tamaño_y = 480
    matriz = np.zeros((tamaño_y, tamaño_x))

    for coord in coordenadas_pixel:
        x, y = coord

        if 0 <= x < tamaño_x and 0 <= y < tamaño_y:
            matriz[y, x] += 1  

    # Crear el mapa de calor
    plt.imshow(matriz, cmap='hot', interpolation='nearest')
    plt.colorbar()
    plt.title('Mapa de Calor')
    plt.show()


f=open('UNI_CORR_500_01.txt','r')
coordenadas= [[float(coord) for coord in row.split()[-3:]] 
              for row in f.readlines()[4:]] #Coordenadas x, y, z
f.close

get_resource_info(lambda: main(coordenadas))
