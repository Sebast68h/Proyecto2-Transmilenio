import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Troncal Caracas y Metro",layout="wide")

# Colores: rojo para lo importante y turquesa (su complementario) para comparar
ROJO="#D7262B"
ROJO_CLARO="#F28B82"
TURQUESA="#1B9AAA"
TURQUESA_CLARO="#8FD3DA"
GRIS="#3A3F44"
colores={"zona":ROJO,"control":TURQUESA,
         "nueva":ROJO,"cerrada":ROJO_CLARO,"vecina":TURQUESA,
         "directa":ROJO,"cercana":TURQUESA,
         "metro":ROJO,"transmilenio":TURQUESA}

# Datos
comparaciones=pd.read_csv("data/processed/comparacion_control.csv")
cambios=pd.read_csv("data/processed/cambio_estaciones.csv",dtype={"codigo":str})
series=pd.read_csv("data/processed/series_diarias.csv")
ranking=pd.read_csv("data/processed/ranking_metro.csv")
zonas=pd.read_csv("data/processed/zonas_metro.csv",dtype={"codigo":str})
demanda=pd.read_csv("data/processed/demanda_pico.csv",dtype={"codigo":str})
coordenadas=pd.read_csv("data/raw/coordenadas_caracas.csv",dtype={"codigo":str})

# Filtros
st.sidebar.header("Filtros")
eventos=st.sidebar.multiselect("Reapertura",["Calle 72","Calle 53","Calle 26"],default=["Calle 72","Calle 53","Calle 26"])
roles=st.sidebar.multiselect("Rol de la estación",["nueva","cerrada","vecina"],default=["nueva","cerrada","vecina"])
conexiones=st.sidebar.multiselect("Conexión con el metro",["directa","cercana"],default=["directa","cercana"])
st.sidebar.subheader("Torniquetes")
estaciones_torn=st.sidebar.multiselect("Estación",["Calle 72","Calle 53","Calle 26"],default=["Calle 72","Calle 53","Calle 26"])
accesos=st.sidebar.multiselect("Acceso",["norte","sur"],default=["norte","sur"])

comp_f=comparaciones[comparaciones["evento"].isin(eventos)]
cambios_f=cambios[cambios["evento"].isin(eventos)&cambios["rol"].isin(roles)]
series_f=series[series["evento"].isin(eventos)]
ranking_f=ranking[ranking["integracion"].isin(conexiones)]
zonas_f=zonas[zonas["integracion"].isin(conexiones)]

# Encabezado
st.title("Troncal Caracas: reaperturas y llegada del metro")
st.write("¿Cómo se reacomoda la demanda de TransMilenio cuando la Caracas recupera sus estaciones definitivas, y cuáles serán los nodos críticos cuando el metro entre en operación en 2028?")

# Tarjetas
a,b,c=st.columns(3)
dias=series_f["fecha"].nunique() if len(eventos)>0 else 0
a.metric("Reaperturas analizadas",len(eventos),str(dias)+" días hábiles",delta_color="off")
if len(ranking_f)>0:
    primero=ranking_f.sort_values("validaciones_pico",ascending=False).iloc[0]
    b.metric("Nodo crítico",primero["estacion_metro"],f'{primero["validaciones_pico"]:,.0f} validaciones en hora pico'.replace(",","."),delta_color="off")
else:
    b.metric("Nodo crítico","Sin datos")
nuevas=cambios[cambios["evento"].isin(eventos)&(cambios["rol"]=="nueva")]["despues"].sum()
cerradas=cambios[cambios["evento"].isin(eventos)&(cambios["rol"]=="cerrada")]["antes"].sum()
if cerradas>0:
    c.metric("Demanda recuperada por la estación nueva",f"{nuevas/cerradas:.0%}","frente a la estación que cerró",delta_color="off")
else:
    c.metric("Demanda recuperada por la estación nueva","Sin datos")

# Mapa
mapa=coordenadas.merge(demanda,on="codigo",how="left",validate="m:1")
mapa=mapa[(mapa["tipo"]=="metro")|mapa["validaciones_pico"].notna()]
mapa["tamano"]=mapa["validaciones_pico"].fillna(mapa["validaciones_pico"].max())
fig_mapa=px.scatter_map(mapa,lat="lat",lon="lon",color="tipo",size="tamano",hover_name="estacion",
                        hover_data={"validaciones_pico":":,.0f","tamano":False,"lat":False,"lon":False},
                        color_discrete_map=colores,zoom=12.3,height=480,map_style="carto-positron")
fig_mapa.update_layout(margin=dict(l=0,r=0,t=0,b=0),legend_title_text="")
st.plotly_chart(fig_mapa,width="stretch")
st.caption("Círculos turquesa: estaciones de TransMilenio de la Caracas que funcionan hoy (tamaño según demanda en hora pico). Rojo: estaciones del metro (ubicación aproximada según los planos oficiales).")

# Pestañas
tab1,tab2,tab3,tab4=st.tabs(["Reaperturas","Metro","Torniquetes","Conclusiones"])

with tab1:
    if len(comp_f)==0:
        st.warning("Escoge al menos una reapertura en los filtros.")
    else:
        col1,col2=st.columns(2)
        fig1=px.bar(comp_f,x="evento",y="cambio_pct",color="grupo",barmode="group",text="cambio_pct",
                    color_discrete_map=colores,title="Cambio % de las validaciones: zona vs control",
                    labels={"evento":"","cambio_pct":"Cambio (%)","grupo":""})
        fig1.update_traces(texttemplate="%{text:.1f}%")
        col1.plotly_chart(fig1,width="stretch")
        fig2=px.line(series_f,x="fecha",y="validaciones",color="grupo",line_dash="evento",markers=True,
                     color_discrete_map=colores,title="Validaciones diarias antes y después",
                     labels={"fecha":"","validaciones":"Validaciones por día","grupo":"","evento":""})
        col2.plotly_chart(fig2,width="stretch")
        if len(cambios_f)==0:
            st.warning("Escoge al menos un rol de estación.")
        else:
            fig3=px.bar(cambios_f,x="cambio",y="estacion",color="rol",facet_col="evento",orientation="h",
                        color_discrete_map=colores,title="Cambio en validaciones diarias por estación",
                        labels={"cambio":"Cambio (validaciones por día)","estacion":"","rol":""})
            fig3.update_yaxes(matches=None,showticklabels=True)
            st.plotly_chart(fig3,width="stretch")
        st.caption("Promedio de días hábiles: 3 semanas antes y 3 después de cada reapertura. Control: troncal AutoNorte.")

with tab2:
    if len(ranking_f)==0:
        st.warning("Escoge al menos un tipo de conexión en los filtros.")
    else:
        col1,col2=st.columns(2)
        ranking_f=ranking_f.sort_values("validaciones_pico",ascending=False)
        fig4=px.bar(ranking_f,x="estacion_metro",y="validaciones_pico",color="integracion",text="validaciones_pico",
                    color_discrete_map=colores,category_orders={"estacion_metro":list(ranking_f["estacion_metro"])},
                    title="Demanda de TransMilenio alrededor de cada estación del metro",
                    labels={"estacion_metro":"","validaciones_pico":"Validaciones en hora pico","integracion":"Conexión"})
        fig4.update_traces(texttemplate="%{text:,.0f}")
        col1.plotly_chart(fig4,width="stretch")
        caracas=coordenadas[coordenadas["tipo"]=="transmilenio"].merge(demanda,on="codigo",how="inner",validate="1:1")
        caracas["con_metro"]="no"
        caracas.loc[caracas["codigo"].isin(zonas["codigo"]),"con_metro"]="sí"
        caracas=caracas.sort_values("validaciones_pico",ascending=False)
        fig5=px.bar(caracas,x="estacion",y="validaciones_pico",color="con_metro",
                    color_discrete_map={"sí":ROJO,"no":TURQUESA},category_orders={"estacion":list(caracas["estacion"])},
                    title="Demanda hoy en las estaciones de la Caracas",
                    labels={"estacion":"","validaciones_pico":"Validaciones en hora pico","con_metro":"Atiende zona del metro"})
        col2.plotly_chart(fig5,width="stretch")
        st.dataframe(zonas_f[["estacion_metro","direccion","integracion","estacion_referencia","validaciones_pico"]],hide_index=True)
        st.caption("Hora pico: 6 a 9 a. m. y 5 a 8 p. m., días hábiles de noviembre de 2026. Donde hoy no hay estación, se promedian las dos más cercanas.")

with tab3:
    torniquetes={"Calle 72":{"carpeta":"data/processed/calle72-diarias/","norte":5,"sur":5},
                 "Calle 53":{"carpeta":"data/processed/calle53-diarias/","norte":6,"sur":6},
                 "Calle 26":{"carpeta":"data/processed/calle26-diarias/","norte":5,"sur":5}}
    if len(estaciones_torn)==0 or len(accesos)==0:
        st.warning("Escoge al menos una estación y un acceso en los filtros.")
    else:
        filas={}
        for nombre in estaciones_torn:
            for acceso in accesos:
                promedio=pd.read_csv(torniquetes[nombre]["carpeta"]+"promedio_por_hora_"+acceso+".csv")
                promedio=promedio.set_index("hora").reindex(range(4,24))
                capacidad=torniquetes[nombre][acceso]*20
                filas[nombre+" - "+acceso]=(promedio["validaciones_promedio"]/60)/capacidad
        matriz=pd.DataFrame(filas).T
        fig6=px.imshow(matriz,color_continuous_scale=["#FFFFFF",ROJO_CLARO,ROJO],zmin=0,zmax=1,aspect="auto",text_auto=".0%",
                       labels={"x":"Hora","y":"","color":"Uso"},title="Uso de la capacidad de los torniquetes por hora")
        st.plotly_chart(fig6,width="stretch")
        st.caption("Uso = validaciones por minuto ÷ (torniquetes × 20 pasajeros por minuto). Capacidad por torniquete: ITDP, The BRT Planning Guide.")

with tab4:
    st.subheader("Hallazgos")
    st.write("Cuando reabrieron las estaciones definitivas, la gente se pasó rápido a la estación nueva más cercana, sin cambiar de troncal. En la Calle 72 fue un reacomodo, en la Calle 53 llegaron usuarios nuevos y en la Calle 26 influyeron las vacaciones.")
    st.write("La estación 16 del metro (Calle 72 a 74) es el nodo crítico: su zona tiene casi 13.000 validaciones en hora pico, un 50 % más que la siguiente, y tendrá conexión directa con TransMilenio.")
    st.subheader("Recomendaciones")
    st.write("Preparar primero la zona de la Calle 72 y 74 (accesos, torniquetes y frecuencias). Tener lista la definitiva de la Av. Jiménez antes de 2028. Medir la demanda de Hospital, Calle 45 y Calle 63 cuando abran.")
    st.subheader("Limitaciones")
    st.write("Las validaciones son entradas pagas, no personas, y no cuentan los transbordos internos. En la 11, 14 y 15 la demanda es un promedio de estaciones cercanas. No sabemos cuántos transbordos traerá el metro.")
