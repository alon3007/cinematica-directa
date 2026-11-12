"""
en esta app quiero hacer una pagina web que permita al usuario ingresar la cantidad de 
piezas que se desea trabajar para mostrar e ingrese el angulo y le entregue la posicion
en el plano cartesiano


primero lo hare para una sola pieza donde el usuario ingrese la medida de la pieza 
y su angulo con dos coordenadas, para despues ir complejizando hasya llegar a tres coordenadas

"""
import streamlit as st
import numpy as np

st.title("Calculadora de Posición en el Plano Cartesiano con movimiento directo")

#entradas
longitud = st.number_input("Ingrese la longitud de la pieza:", min_value=0.0, value=1.0)

angulo = st.number_input("Ingrese el ángulo de la pieza (en grados):", min_value=0.0, max_value=360.0, value=0.0)

#proceso
posx = longitud * np.cos(np.deg2rad(angulo))
posy = longitud * np.sin(np.deg2rad(angulo))

#salida
st.write(f"La posición de la pieza es: ({posx:.2f}, {posy:.2f})")   