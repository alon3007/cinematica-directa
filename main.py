"""
en esta app quiero hacer una pagina web que permita al usuario ingresar la cantidad de 
piezas que se desea trabajar para mostrar e ingrese el angulo y le entregue la posicion
en el plano cartesiano


primero lo hare para una sola pieza donde el usuario ingrese la medida de la pieza 
y su angulo con dos coordenadas, para despues ir complejizando hasya llegar a tres coordenadas

"""
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
 
 
 
COLORES = ["#1f77b4", "#ff2e0e"]  # un color por pieza (máximo 3 piezas)
 
 
def calcular_puntos(longitudes, angulos_rel):
    """Calcula dónde queda cada unión del brazo.
    xs[0], ys[0] es el origen; xs[1], ys[1] es el final de la pieza 1; etc."""
    xs = [0.0]
    ys = [0.0]
    angulo_acumulado = 0.0
 
    for k in range(len(longitudes)):
        # el ángulo de esta pieza se suma a los anteriores (porque es relativo)
        angulo_acumulado = angulo_acumulado + angulos_rel[k]
 
        # xs[k] es donde terminó la pieza anterior (para k = 0 es el origen)
        x_nuevo = xs[k] + longitudes[k] * np.cos(np.deg2rad(angulo_acumulado))
        y_nuevo = ys[k] + longitudes[k] * np.sin(np.deg2rad(angulo_acumulado))
 
        xs.append(x_nuevo)
        ys.append(y_nuevo)
 
    return xs, ys
 
 
def calcular_guias(xs, ys, longitudes, angulos_rel):
    """Calcula las líneas punteadas. En el final de cada pieza (menos la última)
    va la prolongación de esa pieza, con el largo de la pieza siguiente.
    Solo existe si el ángulo de la pieza siguiente es distinto de 0;
    si es 0, la lista de esa línea queda vacía."""
    guias_x = []
    guias_y = []
    angulo_anterior = angulos_rel[0]  # dirección de la pieza anterior (medida desde el eje X)
 
    for k in range(1, len(longitudes)):
        if angulos_rel[k] != 0:
            x_fin = xs[k] + longitudes[k] * np.cos(np.deg2rad(angulo_anterior))
            y_fin = ys[k] + longitudes[k] * np.sin(np.deg2rad(angulo_anterior))
            guias_x.append([xs[k], x_fin])
            guias_y.append([ys[k], y_fin])
        else:
            guias_x.append([])
            guias_y.append([])
 
        angulo_anterior = angulo_anterior + angulos_rel[k]
 
    return guias_x, guias_y
 
 
def angulos_parciales(angulos_rel, f):
    """Multiplica cada ángulo por f. Con f = 0 todos valen 0, con f = 1 quedan completos.
    Sirve para la animación: f va creciendo de 0 a 1."""
    resultado = []
    for k in range(len(angulos_rel)):
        resultado.append(angulos_rel[k] * f)
    return resultado
 
 
def crear_trazas(longitudes, angulos_rel):
    """Crea los dibujos de Plotly (trazas). Siempre en este orden:
    barras, arcos, líneas punteadas y, al final, las etiquetas."""
    xs, ys = calcular_puntos(longitudes, angulos_rel)
    guias_x, guias_y = calcular_guias(xs, ys, longitudes, angulos_rel)
    n = len(longitudes)
    trazas = []
 
    # una barra por pieza: de la unión k a la unión k+1
    for k in range(n):
        barra = go.Scatter(
            x=[xs[k], xs[k + 1]],
            y=[ys[k], ys[k + 1]],
            mode="lines+markers",
            line=dict(width=14, color=COLORES[k]),
            marker=dict(size=10, color="#333333"),
            hoverinfo="skip",
        )
        trazas.append(barra)
 
    # un arco por pieza, centrado en el inicio de esa pieza
    angulo_inicio = 0.0
    for k in range(n):
        angulo_fin = angulo_inicio + angulos_rel[k]
        t = np.deg2rad(np.linspace(angulo_inicio, angulo_fin, 40))
        radio = 0.3 * longitudes[k]
 
        arco_x = xs[k] + radio * np.cos(t)
        arco_y = ys[k] + radio * np.sin(t)
 
        arco = go.Scatter(
            x=arco_x,
            y=arco_y,
            mode="lines",
            line=dict(width=3, color="#d62728"),
            hoverinfo="skip",
        )
        trazas.append(arco)
        angulo_inicio = angulo_fin
 
    # una línea punteada por cada unión (vacía cuando el ángulo es 0)
    for j in range(len(guias_x)):
        guia = go.Scatter(
            x=guias_x[j],
            y=guias_y[j],
            mode="lines",
            line=dict(width=3, color="#7f7f7f", dash="dot"),
            hoverinfo="skip",
        )
        trazas.append(guia)
 
    # una sola traza con las etiquetas de todos los extremos
    etiquetas_x = []
    etiquetas_y = []
    textos = []
    for k in range(n):
        etiquetas_x.append(xs[k + 1])
        etiquetas_y.append(ys[k + 1])
        textos.append(f"({xs[k + 1]:.2f}, {ys[k + 1]:.2f})<br>θ<sub>{k + 1}</sub> = {angulos_rel[k]:.0f}°")
 
    etiquetas = go.Scatter(
        x=etiquetas_x,
        y=etiquetas_y,
        mode="text",
        text=textos,
        textposition="top right",
        textfont=dict(size=14),
        hoverinfo="skip",
    )
    trazas.append(etiquetas)
 
    return trazas
 
 
def crear_figura(longitudes, angulos_rel, n_frames=30):
    """Arma un solo gráfico con todas las piezas en su posición final
    y una animación donde cada ángulo va de 0° hasta su valor final."""
 
    # 1) Estado final: lo que se ve apenas se carga la página
    trazas = crear_trazas(longitudes, angulos_rel)
 
    # 2) Frames de la animación: el mismo dibujo, con los ángulos creciendo de 0 a su valor
    frames = []
    for f in np.linspace(0, 1, n_frames):
        angulos_f = angulos_parciales(angulos_rel, f)
        frames.append(go.Frame(data=crear_trazas(longitudes, angulos_f)))
 
    # 3) Rango automático: se calcula con todos los puntos por los que pasa el brazo
    #    (uniones y puntas de las líneas punteadas)
    todos_x = []
    todos_y = []
    for f in np.linspace(0, 1, 60):
        angulos_f = angulos_parciales(angulos_rel, f)
        xs, ys = calcular_puntos(longitudes, angulos_f)
        guias_x, guias_y = calcular_guias(xs, ys, longitudes, angulos_f)
 
        todos_x = todos_x + xs
        todos_y = todos_y + ys
        for j in range(len(guias_x)):
            todos_x = todos_x + guias_x[j]
            todos_y = todos_y + guias_y[j]
 
    largo_total = sum(longitudes)
    if largo_total > 0:
        margen = 0.35 * largo_total
    else:
        margen = 1.0
    rango_x = [min(todos_x) - margen, max(todos_x) + margen]
    rango_y = [min(todos_y) - margen, max(todos_y) + margen]
 
    # 4) Diseño del gráfico
    fig = go.Figure(data=trazas, frames=frames)
    fig.update_layout(
        template="plotly_white",
        height=520,
        showlegend=False,
        margin=dict(l=10, r=10, t=60, b=10),
        xaxis=dict(title="X (cm)", range=rango_x,
                   zeroline=True, zerolinewidth=2, zerolinecolor="gray"),
        yaxis=dict(title="Y (cm)", range=rango_y,
                   scaleanchor="x", scaleratio=1,  # escala 1:1 para que el ángulo se vea real
                   zeroline=True, zerolinewidth=2, zerolinecolor="gray"),
        updatemenus=[dict(
            type="buttons",
            showactive=False,
            x=0, y=1.12, xanchor="left", yanchor="top",
            buttons=[dict(
                label="▶ Animar",
                method="animate",
                args=[None, dict(
                    frame=dict(duration=40, redraw=True),
                    transition=dict(duration=0),
                    fromcurrent=False,
                )],
            )],
        )],
    )
    return fig
 
 
 
#entradas
st.title("Calculadora de Posición en el Plano Cartesiano con movimiento directo")

longitud1 = st.number_input("Ingrese la longitud de la pieza:", min_value=0.0, value=1.0)

angulo1 = st.number_input("Ingrese el ángulo de la pieza (en grados):", min_value=0.0, max_value=360.0, value=0.0)

longitud2 = st.number_input("Ingrese la longitud de la segunda pieza:", min_value=0.0, value=1.0)

rel2 = angulo1 + st.number_input("Ingrese el ángulo de la segunda pieza (en grados):", min_value=-360.0, max_value=360.0, value=0.0)

angulo2 = rel2 - angulo1
#proceso
posx1 = longitud1 * np.cos((angulo1*2*np.pi)/360)
posy1 = longitud1 * np.sin((angulo1*2*np.pi)/360)

posx2 = posx1 + longitud2 * np.cos((rel2*2*np.pi)/360)
posy2 = posy1 + longitud2 * np.sin((rel2*2*np.pi)/360)

#salida en forma de tabla 
data = {"Coordenada X": [posx1, posx2], "Coordenada Y": [posy1, posy2],}
tabla = pd.DataFrame(
    data,
    index=["Fin de la pieza 1", "Fin de la pieza 2"],
)
tabla.index.name = "Punto"


st.table(tabla)


#salida en forma de gráfico
st.plotly_chart(crear_figura([longitud1, longitud2], [angulo1, angulo2]))
 
