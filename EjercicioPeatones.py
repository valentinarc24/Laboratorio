import numpy as np
import matplotlib.pyplot as plt
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

f=open('UNI_CORR_500_01.txt','r')
coordenadas= [[float(coord) for coord in row.split()[-3:]] 
              for row in f.readlines()[4:]] #Coordenadas x, y, z
f.close

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


"""
minimo_xy = min(coord_xy_frecuencia)
for i in range (len(coord_xy_frecuencia)):
    if coord_xy_frecuencia[i] == minimo_xy:
        print(f"Coordenada {coord_xy_unicos[i]}: se repite {coord_xy_frecuencia[i]} veces")
"""
