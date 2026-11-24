import pandas as pd
import plotly.express as px
import streamlit as st
st.set_page_config(page_title="Troncal Caracas y Metro",layout="wide")
px.defaults.template="plotly_dark"
colores={"zona":"#E6332A","control":"#6C72D9","nueva":"#E6332A","cerrada":"#FF3D7F","vecina":"#6C72D9","directa":"#E6332A",
         "cercana":"#FF6B3D","norte":"#E6332A","sur":"#6C72D9","sí":"#E6332A","no":"#6C72D9","hoy":"#E8E8F5",
         "sobre el umbral":"#FF6B3D","en obra o cerrada":"#4B4F8C","metro directa":"#E6332A","metro cercana":"#FF6B3D"}
ruta="data/processed/"
comp=pd.read_csv(ruta+"comparacion_control.csv")
cambios=pd.read_csv(ruta+"cambio_estaciones.csv")
series=pd.read_csv(ruta+"series_diarias.csv")
ranking=pd.read_csv(ruta+"ranking_metro.csv")
zonas=pd.read_csv(ruta+"zonas_metro.csv",dtype={"codigo":str})
demanda=pd.read_csv(ruta+"demanda_pico.csv",dtype={"codigo":str})
tablas=[]
for est,n in [("calle72",5),("calle53",6),("calle26",5)]:
    for acc in ["norte","sur"]:
        t=pd.read_csv(ruta+est+"-diarias/promedio_por_hora_"+acc+".csv")
        tablas.append(t.assign(fila=est.replace("calle","Calle ")+" "+acc,acceso=acc,torniquetes=n))
accesos=pd.concat(tablas,ignore_index=True)
linea=pd.DataFrame([["Hortúa","09107","",""],["Hospital","","directa","E11"],["Tercer Milenio","","",""],["Av. Jiménez","09128","directa","E12"],
                    ["Calle 19","","",""],["Calle 22","09129","",""],["Calle 26","09114","cercana","E13"],["Av. 39","09130","",""],
                    ["Calle 45","","directa","E14"],["Calle 53","09131","",""],["Calle 57","09125","",""],["Calle 63","","directa","E15"],
                    ["Flores","09127","",""],["Calle 72","09122","",""],["Calle 76","","directa","E16"]],columns=["estacion","codigo","metro","nombre_metro"])
linea["orden"]=range(len(linea))
linea=linea.merge(demanda,on="codigo",how="left",validate="m:1")
pagina=st.sidebar.radio("Página",["Resumen","Reaperturas","Metro","Torniquetes","Conclusiones"])
st.markdown("<div style='background:#E6332A;padding:14px 22px;border-radius:10px;margin-bottom:12px'><h2 style='color:white;margin:0'>TRONCAL CARACAS · "+pagina.upper()+"</h2></div>",unsafe_allow_html=True)
if pagina=="Resumen":
    umbral=st.sidebar.slider("Resaltar estaciones con demanda mayor a",0,14000,8000,step=500)
    st.write("¿Cómo se reacomoda la demanda cuando la Caracas recupera sus estaciones definitivas, y cuáles serán los nodos críticos cuando el metro entre en operación en 2028?")
    a,b,c,d=st.columns(4)
    top=ranking.sort_values("validaciones_pico").iloc[-1]
    c72=cambios[cambios["evento"]=="Calle 72"]
    a.metric("Reaperturas analizadas",3,str(series["fecha"].nunique())+" días hábiles",delta_color="off")
    b.metric("Nodo crítico",top["estacion_metro"],f"{top['validaciones_pico']:,.0f} validaciones en hora pico",delta_color="off")
    c.metric("Demanda de la 76 recuperada por la 72",f"{c72[c72['rol']=='nueva']['despues'].sum()/c72[c72['rol']=='cerrada']['antes'].sum():.0%}")
    d.metric("Uso máximo de los torniquetes",f"{(accesos['validaciones_promedio']/60/(accesos['torniquetes']*18)).max():.0%}","con 18 pasajeros por minuto",delta_color="off")
    linea["tipo"]="en obra o cerrada"
    linea.loc[linea["validaciones_pico"].notna(),"tipo"]="hoy"
    linea.loc[linea["validaciones_pico"]>=umbral,"tipo"]="sobre el umbral"
    estaciones=linea.assign(y=0,forma="estación",etiqueta=linea["estacion"],tamano=linea["validaciones_pico"].fillna(1500))
    metro=linea[linea["metro"]!=""].assign(y=0.5,forma="metro",etiqueta=linea["nombre_metro"],tamano=5000,tipo="metro "+linea["metro"])
    fig=px.scatter(pd.concat([estaciones,metro]),x="orden",y="y",size="tamano",size_max=35,color="tipo",symbol="forma",text="etiqueta",
                   color_discrete_map=colores,symbol_map={"estación":"circle","metro":"square"},hover_data={"validaciones_pico":":,.0f"},
                   title="Troncal Caracas de sur a norte (no a escala)")
    fig.add_hline(y=0,line_color="#E6332A",line_width=8,layer="below")
    fig.update_traces(textposition="bottom center")
    fig.update_layout(height=450,xaxis_visible=False,yaxis_visible=False,yaxis_range=[-0.5,0.9],legend_title="")
    st.plotly_chart(fig,width="stretch")
    st.caption("Tamaño: validaciones en hora pico (noviembre 2026). Cuadros: estaciones del metro según los planos oficiales.")
elif pagina=="Reaperturas":
    eventos=st.sidebar.multiselect("Reapertura",["Calle 72","Calle 53","Calle 26"],default=["Calle 72","Calle 53","Calle 26"])
    roles=st.sidebar.multiselect("Rol de la estación",["nueva","cerrada","vecina"],default=["nueva","cerrada","vecina"])
    a,b=st.columns(2)
    a.plotly_chart(px.bar(comp[comp["evento"].isin(eventos)],x="evento",y="cambio_pct",color="grupo",barmode="group",text="cambio_pct",
                          color_discrete_map=colores,title="Cambio % de las validaciones: zona vs control"),width="stretch")
    fig=px.line(series[series["evento"].isin(eventos)],x="fecha",y="validaciones",color="grupo",facet_col="evento",color_discrete_map=colores,title="Validaciones diarias antes y después")
    b.plotly_chart(fig.update_xaxes(matches=None,showticklabels=False),width="stretch")
    fig=px.bar(cambios[cambios["evento"].isin(eventos)&cambios["rol"].isin(roles)],x="cambio",y="estacion",color="rol",facet_col="evento",
               orientation="h",color_discrete_map=colores,title="Cambio en validaciones diarias por estación")
    st.plotly_chart(fig.update_yaxes(matches=None,showticklabels=True),width="stretch")
    st.info("En la 72 fue un reacomodo (la zona creció casi igual que el control), en la 53 llegaron usuarios nuevos y en la 26 influyeron las vacaciones. En los tres casos la gente cambió de estación dentro de la misma zona, no de troncal.")
elif pagina=="Metro":
    conexiones=st.sidebar.multiselect("Conexión con el metro",["directa","cercana"],default=["directa","cercana"])
    a,b=st.columns(2)
    a.plotly_chart(px.bar(ranking[ranking["integracion"].isin(conexiones)].sort_values("validaciones_pico"),x="validaciones_pico",y="estacion_metro",
                          color="integracion",orientation="h",text="validaciones_pico",color_discrete_map=colores,
                          title="Demanda en hora pico alrededor de cada estación del metro"),width="stretch")
    hoy=linea[linea["validaciones_pico"].notna()].sort_values("validaciones_pico",ascending=False)
    hoy["zona del metro"]=hoy["codigo"].isin(zonas["codigo"]).map({True:"sí",False:"no"})
    b.plotly_chart(px.bar(hoy,x="estacion",y="validaciones_pico",color="zona del metro",color_discrete_map=colores,
                          title="Demanda hoy en las estaciones de la Caracas"),width="stretch")
    st.dataframe(zonas[zonas["integracion"].isin(conexiones)],hide_index=True,width="stretch")
    st.info("La estación 16 (Calle 72 a 74) es el nodo crítico: casi 13.000 validaciones en hora pico, un 50 % más que la siguiente, y conexión directa con TransMilenio.")
elif pagina=="Torniquetes":
    filas=st.sidebar.multiselect("Estación y acceso",list(accesos["fila"].unique()),default=list(accesos["fila"].unique()))
    horas=st.sidebar.slider("Horas",4,23,(5,22))
    capacidad=st.sidebar.slider("Capacidad por torniquete piso a techo (pasajeros por minuto)",8,18,18)
    f=accesos[accesos["fila"].isin(filas)&accesos["hora"].between(horas[0],horas[1])].copy()
    f["uso"]=f["validaciones_promedio"]/60/(f["torniquetes"]*capacidad)
    st.plotly_chart(px.density_heatmap(f,x="hora",y="fila",z="uso",histfunc="sum",nbinsx=horas[1]-horas[0]+1,text_auto=".0%",range_color=[0,1],
                                       color_continuous_scale=["#4B4F8C","#F27F5D","#E6332A"],title="Uso de la capacidad de los torniquetes por hora"),width="stretch")
    a,b=st.columns(2)
    fig=px.bar(f.groupby(["fila","acceso"])["uso"].max().reset_index(),x="fila",y="uso",color="acceso",color_discrete_map=colores,title="Uso en la hora más cargada")
    a.plotly_chart(fig.add_hline(y=1,line_dash="dash",line_color="#FF3D7F"),width="stretch")
    b.plotly_chart(px.line(f,x="hora",y="validaciones_promedio",color="fila",title="Validaciones por hora en cada acceso"),width="stretch")
    st.caption("Uso = validaciones por minuto ÷ (torniquetes × capacidad). Los torniquetes piso a techo dejan pasar hasta 18 personas por minuto según los fabricantes; en la estación real pasan menos.")
else:
    a,b,c=st.columns(3)
    a.subheader("Hallazgos")
    a.write("La gente se pasó rápido a la estación nueva más cercana, sin cambiar de troncal. La zona de la Calle 72 y 74 es la más cargada y tendrá conexión directa con el metro.")
    b.subheader("Recomendaciones")
    b.write("Preparar primero la zona de la Calle 72 y 74 (accesos, torniquetes y frecuencias), tener lista la definitiva de la Av. Jiménez y medir Hospital, Calle 45 y Calle 63 cuando abran.")
    c.subheader("Limitaciones")
    c.write("Las validaciones son entradas pagas, no personas. En las estaciones 11, 14 y 15 la demanda es un promedio. No sabemos cuántos transbordos traerá el metro.")
