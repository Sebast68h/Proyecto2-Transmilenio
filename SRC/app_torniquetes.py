import pandas as pd
import plotly.express as px
import streamlit as st

estaciones = {
    "Calle 72": {
        "carpeta": "data/processed/calle72-diarias/",
        "torniquetes_norte": 5,   
        "torniquetes_sur": 5,  
        "dias": 15,              
    },
    "Calle 26": {
        "carpeta": "data/processed/calle26-diarias/",
        "torniquetes_norte": 5,   
        "torniquetes_sur": 5,     
        "dias": 14,              
    },
    "Calle 53": {
        "carpeta": "data/processed/calle53-diarias/",
        "torniquetes_norte": 6,  
        "torniquetes_sur": 6,     
        "dias": 14,               
    },
}

st.set_page_config(layout="wide")
st.title("Uso de torniquetes por acceso")

capacidad_por_torniquete = 20 
horas = list(range(4, 24)) # tupla

eleccion = st.selectbox("Estación", ["Todas", "Calle 72", "Calle 26", "Calle 53"])

if eleccion == "Todas":
    estaciones_a_mostrar = ["Calle 72", "Calle 26", "Calle 53"]
else:
    estaciones_a_mostrar = [eleccion]

filas_uso = {}           # uso promedio por hora, una fila por estación y acceso
for nombre_estacion in estaciones_a_mostrar:
    estacion = estaciones[nombre_estacion]

    for acceso in ["norte", "sur"]:
        promedio = pd.read_csv(estacion["carpeta"] + "promedio_por_hora_" + acceso + ".csv")
        promedio = promedio.set_index("hora").reindex(horas) # alinear las horas de 4 a 23, aunque falten algunas en el csv

        torniquetes = estacion["torniquetes_" + acceso] # cantidad de torniquetes en el acceso
        capacidad = torniquetes * capacidad_por_torniquete #capacidad total del acceso (pasajeros por minuto)
        uso = (promedio["validaciones_promedio"] / 60) / capacidad #porcentaje de uso del acceso (promedio de pasajeros por minuto / capacidad total)
        filas_uso[nombre_estacion + " _ " + acceso.capitalize()] = uso

st.subheader("Día promedio")
matriz_uso = pd.DataFrame(filas_uso).T
grafica = px.imshow(matriz_uso, color_continuous_scale="Blues", zmin=0, zmax=1,
                    aspect="auto", text_auto=".0%",
                    labels={"x": "Hora", "y": "", "color": "Uso"})

grafica.update_layout(height=150 + 45 * len(matriz_uso),
                      margin=dict(l=10, r=10, t=10, b=10),
                      coloraxis_colorbar=dict(orientation="h", y=-0.35, tickformat=".0%"))

st.plotly_chart(grafica)

dias_texto = ", ".join(nombre + ": " + str(estaciones[nombre]["dias"]) + " días"
                       for nombre in estaciones_a_mostrar)