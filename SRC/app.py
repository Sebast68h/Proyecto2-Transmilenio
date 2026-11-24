import pandas as pd
import plotly.express as px
import streamlit as st
st.set_page_config(page_title="Troncal Caracas y Metro",layout="wide")
px.defaults.template="plotly_white"
colores={"zona":"#D52B1E","control":"#9A968E","nueva":"#D52B1E","cerrada":"#8E1B13","vecina":"#9A968E","directa":"#D52B1E",
         "cercana":"#F08A7E","norte":"#D52B1E","sur":"#9A968E","sí":"#D52B1E","no":"#C9C5BC","hoy":"#6B6B6B",
         "de las más cargadas":"#D52B1E","en obra o cerrada":"#C9C5BC","metro directa":"#8E1B13","metro cercana":"#F08A7E","(?)":"#C9C5BC"}
ruta="data/processed/"
comp=pd.read_csv(ruta+"comparacion_control.csv")
cambios=pd.read_csv(ruta+"cambio_estaciones.csv")
series=pd.read_csv(ruta+"series_diarias.csv")
ranking=pd.read_csv(ruta+"ranking_metro.csv")
zonas=pd.read_csv(ruta+"zonas_metro.csv",dtype={"codigo":str})
demanda=pd.read_csv(ruta+"demanda_pico.csv",dtype={"codigo":str})
tablas=[]
for est,n in [("calle72",7),("calle53",6),("calle26",5)]:
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
pagina=st.radio("Página",["Resumen","Reaperturas","Metro","Torniquetes"],horizontal=True,label_visibility="collapsed")
st.markdown("<div style='background:#D52B1E;padding:14px 22px;border-radius:10px;margin-bottom:12px'><h2 style='color:white;margin:0'>TRONCAL CARACAS · "+pagina.upper()+"</h2></div>",unsafe_allow_html=True)
if pagina=="Resumen":
    top=st.slider("Resaltar las estaciones más cargadas (cuántas)",0,9,3)
    st.write("¿Cómo se reacomoda la demanda cuando la Caracas recupera sus estaciones definitivas, y qué estaciones, por su demanda actual y su conexión con el metro, deben prepararse primero antes de 2028?")
    a,b,c,d=st.columns(4)
    nodo=ranking.sort_values("validaciones_pico").iloc[-1]
    c72=cambios[cambios["evento"]=="Calle 72"]
    a.metric("Reaperturas analizadas",3,str(series["fecha"].nunique())+" días hábiles",delta_color="off")
    b.metric("Nodo crítico",nodo["estacion_metro"],f"{nodo['validaciones_pico']:,.0f} validaciones en hora pico",delta_color="off")
    c.metric("Demanda de la 76 recuperada por la 72",f"{c72[c72['rol']=='nueva']['despues'].sum()/c72[c72['rol']=='cerrada']['antes'].sum():.0%}")
    d.metric("Uso máximo de los torniquetes",f"{(accesos['validaciones_maximo']/60/(accesos['torniquetes']*10)).max():.0%}","día más cargado, 10 pasajeros por minuto",delta_color="off")
    linea["tipo"]="en obra o cerrada"
    linea.loc[linea["validaciones_pico"].notna(),"tipo"]="hoy"
    linea.loc[linea["validaciones_pico"].rank(ascending=False)<=top,"tipo"]="de las más cargadas"
    estaciones=linea.assign(y=0,forma="estación",etiqueta=linea["estacion"],tamano=linea["validaciones_pico"].fillna(1500))
    metro=linea[linea["metro"]!=""].assign(y=0.5,forma="metro",etiqueta=linea["nombre_metro"],tamano=5000,tipo="metro "+linea["metro"])
    fig=px.scatter(pd.concat([estaciones,metro]),x="orden",y="y",size="tamano",size_max=35,color="tipo",symbol="forma",text="etiqueta",
                   color_discrete_map=colores,symbol_map={"estación":"circle","metro":"square"},hover_data={"validaciones_pico":":,.0f"},
                   title="Troncal Caracas de sur a norte (no a escala)")
    fig.add_hline(y=0,line_color="#D52B1E",line_width=8,layer="below")
    fig.update_traces(textposition="bottom center")
    fig.update_layout(height=450,xaxis_visible=False,yaxis_visible=False,yaxis_range=[-0.5,0.9],legend_title="")
    st.plotly_chart(fig,width="stretch")
    st.caption("Tamaño: validaciones en hora pico (noviembre 2026). Cuadros: estaciones del metro según los planos oficiales.")
    st.warning("Limitaciones: las validaciones son entradas pagas, no personas. En las estaciones 11, 14 y 15 del metro la demanda es un promedio de estaciones cercanas. No sabemos cuántos transbordos traerá el metro.")
elif pagina=="Reaperturas":
    f1,f2=st.columns(2)
    eventos=f1.multiselect("Reaperturas",["Calle 72","Calle 53","Calle 26"],default=["Calle 72","Calle 53","Calle 26"])
    evento=f2.selectbox("Reapertura para ver por estación",["Calle 72","Calle 53","Calle 26"])
    a,b=st.columns(2)
    a.plotly_chart(px.bar(comp[comp["evento"].isin(eventos)],x="evento",y="cambio_pct",color="grupo",barmode="group",text="cambio_pct",
                          color_discrete_map=colores,title="Cambio % de las validaciones: zona vs control"),width="stretch")
    diaria=series[series["evento"].isin(eventos)&(series["grupo"]=="zona")].copy()
    diaria["fecha"]=pd.to_datetime(diaria["fecha"])
    promedio_antes=diaria[diaria["periodo"]=="antes"].groupby("evento")["validaciones"].mean().reset_index(name="promedio_antes")
    reapertura=diaria[diaria["periodo"]=="después"].groupby("evento")["fecha"].min().reset_index(name="reapertura")
    diaria=diaria.merge(promedio_antes,on="evento",validate="m:1").merge(reapertura,on="evento",validate="m:1")
    diaria["indice"]=(diaria["validaciones"]/diaria["promedio_antes"]*100).round(1)
    diaria["dia"]=(diaria["fecha"]-diaria["reapertura"]).dt.days
    linea_indice=px.scatter(diaria,x="dia",y="indice",color="evento",opacity=0.4,trendline="rolling",trendline_options=dict(window=5,min_periods=1),color_discrete_map={"Calle 72":"#D52B1E","Calle 53":"#8E1B13","Calle 26":"#F08A7E"},
                labels={"dia":"Días desde la reapertura","indice":"Índice (antes = 100)"},title="Tendencia de la zona: promedio de 5 días (promedio de antes = 100)")
    b.plotly_chart(linea_indice.add_hline(y=100,line_dash="dot").add_vline(x=0,line_dash="dot"),width="stretch")
    estaciones=cambios[cambios["evento"]==evento].copy()
    cerrada=estaciones[estaciones["rol"]=="cerrada"]["estacion"].iloc[0]
    nueva=estaciones[estaciones["rol"]=="nueva"]["estacion"].iloc[0]
    estaciones.loc[estaciones["rol"].isin(["cerrada","nueva"]),"estacion"]=cerrada+" → "+nueva
    estaciones=estaciones.groupby("estacion")[["antes","despues"]].sum().reset_index().sort_values("antes",ascending=False)
    puntos=pd.concat([estaciones.assign(periodo="antes",validaciones=estaciones["antes"]),estaciones.assign(periodo="después",validaciones=estaciones["despues"])])
    pesas=px.scatter(puntos,x="validaciones",y="estacion",color="periodo",color_discrete_map={"antes":"#B8B5AE","después":"#D52B1E"},
                     title="Validaciones diarias por estación antes → después: "+evento)
    for est,antes,despues in zip(estaciones["estacion"],estaciones["antes"],estaciones["despues"]):
        pesas.add_shape(type="line",x0=antes,x1=despues,y0=est,y1=est,line_color="#C9C5BC",line_width=3,layer="below")
    st.plotly_chart(pesas.update_traces(marker_size=14),width="stretch")
    st.info("Cuando una estación reabre, la gente se pasa en pocas semanas a la más cercana: la 72 recibió el 103 % de la demanda de la 76. En la 72 fue un reacomodo (la zona creció casi igual que el control), en la 53 llegaron usuarios nuevos y en la 26 influyeron las vacaciones. En los tres casos la gente cambió de estación dentro de la misma zona, no de troncal.")
    st.success("Recomendación: reforzar rutas en las primeras semanas de cada conexión con el metro, que es cuando la gente se reacomoda.")
elif pagina=="Metro":
    conexiones=st.multiselect("Conexión con el metro",["directa","cercana"],default=["directa","cercana"])
    a,b=st.columns(2)
    z=zonas[zonas["integracion"].isin(conexiones)]
    z=z.merge(z.groupby("estacion_metro").size().reset_index(name="n"),on="estacion_metro",validate="m:1")
    z["aporte"]=(z["validaciones_pico"]/z["n"]).round()
    fig=px.treemap(z,path=["estacion_metro","estacion_referencia"],values="aporte",color="integracion",color_discrete_map=colores,
                   title="Demanda en hora pico alrededor de cada estación del metro y de dónde sale")
    a.plotly_chart(fig.update_traces(textinfo="label+value"),width="stretch")
    hoy=linea[linea["validaciones_pico"].notna()].sort_values("validaciones_pico",ascending=False)
    hoy["zona del metro"]=hoy["codigo"].isin(zonas["codigo"]).map({True:"sí",False:"no"})
    b.plotly_chart(px.bar(hoy,x="estacion",y="validaciones_pico",color="zona del metro",color_discrete_map=colores,
                          title="Demanda hoy en las estaciones de la Caracas"),width="stretch")
    st.dataframe(zonas[zonas["integracion"].isin(conexiones)],hide_index=True,width="stretch")
    st.info("La estación 16 (Calle 72 a 74) es el nodo crítico: casi 13.000 validaciones en hora pico, un 50 % más que la siguiente, y conexión directa con la Calle 76 de TransMilenio.")
    st.success("Recomendación: diseñar la conexión de la estación 16 para al menos 13.000 validaciones en hora pico y medir la demanda de Hospital, Calle 45 y Calle 63 cuando abran.")
else:
    f1,f2,f3=st.columns(3)
    filas=f1.multiselect("Estación y acceso",list(accesos["fila"].unique()),default=list(accesos["fila"].unique()))
    horas=f2.slider("Horas",4,23,(5,22))
    capacidad=f3.slider("Capacidad por torniquete piso a techo (pasajeros por minuto)",8,18,10)
    f=accesos[accesos["fila"].isin(filas)&accesos["hora"].between(horas[0],horas[1])].copy()
    f["uso"]=f["validaciones_promedio"]/60/(f["torniquetes"]*capacidad)
    f["uso_dia_cargado"]=f["validaciones_maximo"]/60/(f["torniquetes"]*capacidad)
    st.plotly_chart(px.density_heatmap(f,x="hora",y="fila",z="uso",histfunc="sum",nbinsx=horas[1]-horas[0]+1,text_auto=".0%",range_color=[0,1],
                                       color_continuous_scale=["#F7F5F0","#F08A7E","#D52B1E"],title="Uso promedio de la capacidad de los torniquetes por hora"),width="stretch")
    a,b=st.columns(2)
    a.subheader("Uso en la hora pico del día más cargado")
    maximo=f.groupby("fila")["uso_dia_cargado"].max().reset_index()
    for fila,uso in zip(maximo["fila"],maximo["uso_dia_cargado"]):
        a.progress(min(uso,1.0),text=fila+": "+f"{uso:.0%}")
    b.plotly_chart(px.line(f,x="hora",y="validaciones_promedio",color="fila",title="Validaciones por hora en cada acceso"),width="stretch")
    st.caption("Uso = validaciones por minuto ÷ (torniquetes × capacidad). Los torniquetes piso a techo dejan pasar hasta 18 personas por minuto según los fabricantes; en la estación real pasan menos.")
    st.info("Los accesos norte de la Calle 72 y la Calle 26 llegarían al 81 % de su capacidad en los días más cargados con torniquetes piso a techo de 10 personas por minuto.")
    st.success("Recomendación: agregar 2 torniquetes en el acceso norte de la Calle 72 (de 7 a 9) y 1 en el de la Calle 26 (de 5 a 6), y medir en campo cuántas personas pasan por minuto.")
