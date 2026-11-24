import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Troncal Caracas y Metro",layout="wide")

ROJO="#E6332A"
NARANJA="#FF6B3D"
ROSA="#FF3D7F"
AZUL="#6C72D9"
AZUL_OSCURO="#4B4F8C"
FONDO="#12122A"
TEXTO="#E8E8F5"
GRIS="#9A9AC0"
colores={"zona":ROJO,"control":AZUL,"nueva":ROJO,"cerrada":ROSA,"vecina":AZUL,
         "directa":ROJO,"cercana":NARANJA,"sí":ROJO,"no":AZUL,"norte":ROJO,"sur":AZUL}


def oscuro(fig,alto=380):
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font_color=TEXTO,height=alto,
                      title_x=0.5,margin=dict(l=20,r=20,t=60,b=20),legend=dict(orientation="h",y=-0.18,title_text=""))
    fig.update_xaxes(gridcolor=AZUL_OSCURO,zerolinecolor=AZUL_OSCURO)
    fig.update_yaxes(gridcolor=AZUL_OSCURO,zerolinecolor=AZUL_OSCURO)
    return fig


def encabezado(titulo,subtitulo):
    st.markdown(f"<div style='background:{ROJO};padding:16px 24px;border-radius:10px;margin-bottom:16px'>"
                f"<div style='color:white;font-size:28px;font-weight:700'>{titulo}</div>"
                f"<div style='color:#FFE1DE;font-size:15px'>{subtitulo}</div></div>",unsafe_allow_html=True)


def tarjeta(titulo,valor,detalle,color=TEXTO):
    st.markdown(f"<div style='text-align:center;padding:10px 0'>"
                f"<div style='color:{GRIS};font-size:14px'>{titulo}</div>"
                f"<div style='color:{color};font-size:36px;font-weight:700'>{valor}</div>"
                f"<div style='color:{GRIS};font-size:13px'>{detalle}</div></div>",unsafe_allow_html=True)


def anillo(titulo,valor,color):
    lleno=min(valor,1)
    fig=px.pie(values=[lleno,1-lleno],hole=0.72,color_discrete_sequence=[color,AZUL_OSCURO])
    fig.update_traces(textinfo="none",sort=False,hoverinfo="skip")
    fig.update_layout(showlegend=False,height=120,margin=dict(l=0,r=0,t=0,b=0),paper_bgcolor="rgba(0,0,0,0)",
                      annotations=[dict(text=f"{valor:.0%}",showarrow=False,font=dict(size=22,color=TEXTO))])
    st.markdown(f"<div style='text-align:center;color:{GRIS};font-size:14px'>{titulo}</div>",unsafe_allow_html=True)
    st.plotly_chart(fig,width="stretch",config={"displayModeBar":False})


def numero(x):
    return f"{x:,.0f}".replace(",",".")


comparaciones=pd.read_csv("data/processed/comparacion_control.csv")
cambios=pd.read_csv("data/processed/cambio_estaciones.csv",dtype={"codigo":str})
series=pd.read_csv("data/processed/series_diarias.csv")
ranking=pd.read_csv("data/processed/ranking_metro.csv")
zonas=pd.read_csv("data/processed/zonas_metro.csv",dtype={"codigo":str})
demanda=pd.read_csv("data/processed/demanda_pico.csv",dtype={"codigo":str})

estaciones=pd.DataFrame([
    [0,"Hortúa","09107",None,None],
    [1,"Hospital",None,"Estación 11","directa"],
    [2,"Tercer Milenio",None,None,None],
    [3,"Av. Jiménez","09128","Estación 12","directa"],
    [4,"Calle 19",None,None,None],
    [5,"Calle 22","09129",None,None],
    [6,"Calle 26","09114","Estación 13","cercana"],
    [7,"Av. 39","09130",None,None],
    [8,"Calle 45",None,"Estación 14","directa"],
    [9,"Calle 53","09131",None,None],
    [10,"Calle 57","09125",None,None],
    [11,"Calle 63",None,"Estación 15","directa"],
    [12,"Flores","09127",None,None],
    [13,"Calle 72","09122",None,None],
    [14,"Calle 76",None,"Estación 16","directa"],
],columns=["orden","estacion","codigo","metro","conexion"])
cruces=pd.DataFrame([[3,"Eje Ambiental / Américas"],[6,"Troncal Calle 26"],[15,"AutoNorte / Calle 80"]],columns=["orden","troncal"])
linea=estaciones.merge(demanda,on="codigo",how="left",validate="m:1")

torniquetes=pd.DataFrame([
    ["Calle 72","norte",5],["Calle 72","sur",5],
    ["Calle 53","norte",6],["Calle 53","sur",6],
    ["Calle 26","norte",5],["Calle 26","sur",5],
],columns=["estacion","acceso","torniquetes"])
tablas=[]
for i in range(len(torniquetes)):
    fila=torniquetes.iloc[i]
    carpeta="data/processed/"+fila["estacion"].lower().replace(" ","")+"-diarias/"
    promedio=pd.read_csv(carpeta+"promedio_por_hora_"+fila["acceso"]+".csv")
    promedio["estacion"]=fila["estacion"]
    promedio["acceso"]=fila["acceso"]
    promedio["torniquetes"]=fila["torniquetes"]
    tablas.append(promedio)
accesos=pd.concat(tablas,ignore_index=True)
accesos["fila"]=accesos["estacion"]+" - "+accesos["acceso"]

st.sidebar.markdown(f"<div style='color:{ROJO};font-size:22px;font-weight:700'>Troncal Caracas</div>",unsafe_allow_html=True)
pagina=st.sidebar.radio("Página",["Resumen","Reaperturas","Metro","Torniquetes","Conclusiones"])
st.sidebar.markdown("---")
st.sidebar.markdown(f"<div style='color:{ROJO};font-weight:700'>Filtros</div>",unsafe_allow_html=True)


if pagina=="Resumen":
    umbral=st.sidebar.slider("Resaltar estaciones con demanda mayor a",0,14000,8000,step=500)

    encabezado("TRONCAL CARACAS · REAPERTURAS Y METRO",
               "¿Cómo se reacomoda la demanda cuando la Caracas recupera sus estaciones definitivas, y cuáles serán los nodos críticos cuando el metro entre en operación en 2028?")

    c1,c2,c3,c4=st.columns(4)
    with c1.container(border=True):
        tarjeta("Reaperturas analizadas","3",str(series["fecha"].nunique())+" días hábiles")
    with c2.container(border=True):
        primero=ranking.sort_values("validaciones_pico",ascending=False).iloc[0]
        tarjeta("Nodo crítico",numero(primero["validaciones_pico"]),primero["estacion_metro"]+" · validaciones en hora pico",ROJO)
    with c3.container(border=True):
        nueva=cambios[(cambios["evento"]=="Calle 72")&(cambios["rol"]=="nueva")]["despues"].sum()
        cerrada=cambios[(cambios["evento"]=="Calle 72")&(cambios["rol"]=="cerrada")]["antes"].sum()
        anillo("Demanda de la 76 recuperada por la 72",nueva/cerrada,ROJO)
    with c4.container(border=True):
        uso_max=((accesos["validaciones_promedio"]/60)/(accesos["torniquetes"]*18)).max()
        anillo("Uso máximo de los torniquetes",uso_max,NARANJA)

    with st.container(border=True):
        fig=px.line(x=[-0.4,15.2],y=[0,0],title="Troncal Caracas · de sur a norte")
        fig.update_traces(line=dict(color=ROJO,width=9),hoverinfo="skip",showlegend=False)
        hoy=linea[linea["validaciones_pico"].notna()].copy()
        hoy["color"]=TEXTO
        hoy.loc[hoy["validaciones_pico"]>=umbral,"color"]=NARANJA
        fig.add_scatter(x=hoy["orden"],y=[0]*len(hoy),mode="markers",name="TransMilenio hoy (tamaño = demanda)",
                        marker=dict(size=12+hoy["validaciones_pico"]/650,color=hoy["color"],line=dict(color=AZUL_OSCURO,width=2)),
                        customdata=hoy[["estacion","validaciones_pico"]],
                        hovertemplate="%{customdata[0]}<br>%{customdata[1]:,.0f} validaciones en hora pico<extra></extra>")
        obra=linea[linea["validaciones_pico"].isna()]
        fig.add_scatter(x=obra["orden"],y=[0]*len(obra),mode="markers",name="En obra o cerrada",
                        marker=dict(size=12,color=FONDO,line=dict(color=GRIS,width=2)),
                        customdata=obra[["estacion"]],hovertemplate="%{customdata[0]}<br>En obra o cerrada<extra></extra>")
        fig.add_scatter(x=linea["orden"],y=[-0.3]*len(linea),mode="text",text=linea["estacion"],
                        textfont=dict(color=TEXTO,size=12),hoverinfo="skip",showlegend=False)
        directa=linea[linea["conexion"]=="directa"]
        cercana=linea[linea["conexion"]=="cercana"]
        fig.add_scatter(x=directa["orden"],y=[0.45]*len(directa),mode="markers+text",name="Metro: conexión directa",
                        text=directa["metro"].str.replace("Estación ","E"),textposition="top center",textfont=dict(color=TEXTO),
                        marker=dict(symbol="square",size=18,color=ROJO,line=dict(color="white",width=1)),
                        customdata=directa[["metro"]],hovertemplate="%{customdata[0]}<br>Conexión directa<extra></extra>")
        fig.add_scatter(x=cercana["orden"],y=[0.45]*len(cercana),mode="markers+text",name="Metro: conexión cercana",
                        text=cercana["metro"].str.replace("Estación ","E"),textposition="top center",textfont=dict(color=TEXTO),
                        marker=dict(symbol="square-open",size=18,color=NARANJA,line=dict(width=3)),
                        customdata=cercana[["metro"]],hovertemplate="%{customdata[0]}<br>Conexión cercana<extra></extra>")
        fig.add_scatter(x=cruces["orden"],y=[-0.62]*len(cruces),mode="markers+text",text="↔ "+cruces["troncal"],
                        textposition="bottom center",textfont=dict(color=GRIS,size=11),
                        marker=dict(symbol="line-ns",size=16,line=dict(color=AZUL,width=3)),hoverinfo="skip",showlegend=False)
        oscuro(fig,430)
        fig.update_xaxes(visible=False,range=[-0.8,15.8])
        fig.update_yaxes(visible=False,range=[-1.0,0.8])
        st.plotly_chart(fig,width="stretch")
        st.caption("Estaciones de TransMilenio en orden de sur a norte (no a escala). La demanda es el promedio de validaciones en hora pico en noviembre de 2026. La conexión con el metro sale de los planos oficiales de la Empresa Metro.")


elif pagina=="Reaperturas":
    eventos=st.sidebar.pills("Reapertura",["Calle 72","Calle 53","Calle 26"],selection_mode="multi",default=["Calle 72","Calle 53","Calle 26"])
    roles=st.sidebar.pills("Rol de la estación",["nueva","cerrada","vecina"],selection_mode="multi",default=["nueva","cerrada","vecina"])

    encabezado("REAPERTURAS","Qué pasó con la demanda 3 semanas antes y 3 semanas después de que reabrieron las estaciones definitivas")

    if len(eventos)==0:
        st.warning("Escoge al menos una reapertura en los filtros.")
    else:
        comp_f=comparaciones[comparaciones["evento"].isin(eventos)]
        series_f=series[series["evento"].isin(eventos)]
        cambios_f=cambios[cambios["evento"].isin(eventos)&cambios["rol"].isin(roles)]

        c1,c2=st.columns(2)
        with c1.container(border=True):
            fig=px.bar(comp_f,x="evento",y="cambio_pct",color="grupo",barmode="group",text="cambio_pct",
                       color_discrete_map=colores,title="Cambio % de las validaciones: zona vs control",
                       labels={"evento":"","cambio_pct":"Cambio (%)"})
            fig.update_traces(texttemplate="%{text:.1f}%")
            st.plotly_chart(oscuro(fig),width="stretch")
        with c2.container(border=True):
            fig=px.line(series_f,x="fecha",y="validaciones",color="grupo",facet_col="evento",markers=True,
                        color_discrete_map=colores,title="Validaciones diarias antes y después",
                        labels={"fecha":"","validaciones":"Validaciones por día"})
            fig.update_xaxes(matches=None,showticklabels=False)
            fig.for_each_annotation(lambda a:a.update(text=a.text.split("=")[-1]))
            st.plotly_chart(oscuro(fig),width="stretch")

        with st.container(border=True):
            if len(cambios_f)==0:
                st.warning("Escoge al menos un rol de estación.")
            else:
                fig=px.bar(cambios_f,x="cambio",y="estacion",color="rol",facet_col="evento",orientation="h",
                           color_discrete_map=colores,title="Cambio en validaciones diarias por estación",
                           labels={"cambio":"Cambio (validaciones por día)","estacion":""})
                fig.update_yaxes(matches=None,showticklabels=True)
                fig.for_each_annotation(lambda a:a.update(text=a.text.split("=")[-1]))
                st.plotly_chart(oscuro(fig,420),width="stretch")

        with st.container(border=True):
            st.markdown(f"<div style='color:{ROJO};font-weight:700'>Hallazgo</div>",unsafe_allow_html=True)
            st.write("En la Calle 72 la zona creció casi igual que el control: fue un reacomodo, la gente de la 76 se pasó a la 72, Héroes y Polo. En la Calle 53 la zona creció casi 5 puntos más que el control, así que llegaron usuarios nuevos. En la Calle 26 todo bajó por las vacaciones. En los tres casos la gente cambió de estación dentro de la misma zona, no de troncal.")


elif pagina=="Metro":
    conexiones=st.sidebar.pills("Conexión con el metro",["directa","cercana"],selection_mode="multi",default=["directa","cercana"])

    encabezado("NODOS CRÍTICOS PARA EL METRO","Cuánta gente de TransMilenio hay hoy en hora pico alrededor de cada estación del metro en la Caracas")

    if len(conexiones)==0:
        st.warning("Escoge al menos un tipo de conexión en los filtros.")
    else:
        ranking_f=ranking[ranking["integracion"].isin(conexiones)].sort_values("validaciones_pico")
        zonas_f=zonas[zonas["integracion"].isin(conexiones)]

        c1,c2=st.columns(2)
        with c1.container(border=True):
            fig=px.bar(ranking_f,x="validaciones_pico",y="estacion_metro",color="integracion",orientation="h",text="validaciones_pico",
                       color_discrete_map=colores,title="Demanda alrededor de cada estación del metro",
                       labels={"validaciones_pico":"Validaciones en hora pico","estacion_metro":""})
            fig.update_traces(texttemplate="%{text:,.0f}")
            fig.update_yaxes(categoryorder="total ascending")
            st.plotly_chart(oscuro(fig),width="stretch")
        with c2.container(border=True):
            hoy=linea[linea["validaciones_pico"].notna()].copy()
            hoy["con_metro"]="no"
            hoy.loc[hoy["codigo"].isin(zonas["codigo"]),"con_metro"]="sí"
            hoy=hoy.sort_values("validaciones_pico",ascending=False)
            fig=px.bar(hoy,x="estacion",y="validaciones_pico",color="con_metro",color_discrete_map=colores,
                       category_orders={"estacion":list(hoy["estacion"])},title="Demanda hoy en las estaciones de la Caracas",
                       labels={"estacion":"","validaciones_pico":"Validaciones en hora pico","con_metro":"Atiende zona del metro"})
            st.plotly_chart(oscuro(fig),width="stretch")

        c1,c2=st.columns([3,2])
        with c1.container(border=True):
            st.markdown(f"<div style='text-align:center;font-weight:700'>Estaciones de TransMilenio que atienden cada estación del metro</div>",unsafe_allow_html=True)
            st.dataframe(zonas_f[["estacion_metro","direccion","integracion","estacion_referencia","validaciones_pico"]],hide_index=True,width="stretch")
        with c2.container(border=True):
            st.markdown(f"<div style='color:{ROJO};font-weight:700'>Hallazgo</div>",unsafe_allow_html=True)
            st.write("La estación 16 (Calle 72 a 74) es el nodo crítico: casi 13.000 validaciones en hora pico, un 50 % más que la siguiente, y conexión directa con TransMilenio. Las estaciones 14, 12 y 15 tienen demandas parecidas. Donde hoy no hay estación, la demanda es el promedio de las dos más cercanas.")


elif pagina=="Torniquetes":
    est_t=st.sidebar.pills("Estación",["Calle 72","Calle 53","Calle 26"],selection_mode="multi",default=["Calle 72","Calle 53","Calle 26"])
    acc_t=st.sidebar.pills("Acceso",["norte","sur"],selection_mode="multi",default=["norte","sur"])
    horas=st.sidebar.slider("Horas",4,23,(5,22))
    capacidad=st.sidebar.slider("Capacidad por torniquete piso a techo (pasajeros por minuto)",8,18,18)

    encabezado("TORNIQUETES","Qué tan cerca están los accesos de su capacidad en cada hora del día")

    acc_f=accesos[accesos["estacion"].isin(est_t)&accesos["acceso"].isin(acc_t)&accesos["hora"].between(horas[0],horas[1])].copy()
    if len(acc_f)==0:
        st.warning("Escoge al menos una estación y un acceso en los filtros.")
    else:
        acc_f["uso"]=(acc_f["validaciones_promedio"]/60)/(acc_f["torniquetes"]*capacidad)

        with st.container(border=True):
            fig=px.density_heatmap(acc_f,x="hora",y="fila",z="uso",histfunc="sum",text_auto=".0%",nbinsx=horas[1]-horas[0]+1,
                                   color_continuous_scale=[AZUL_OSCURO,NARANJA,ROJO],range_color=[0,1],
                                   title="Uso de la capacidad de los torniquetes por hora",labels={"hora":"Hora","fila":"","uso":"Uso"})
            fig.update_layout(coloraxis_colorbar=dict(title="Uso",tickformat=".0%"))
            st.plotly_chart(oscuro(fig,380),width="stretch")

        c1,c2=st.columns(2)
        with c1.container(border=True):
            maximo=acc_f.groupby(["fila","acceso"])["uso"].max().reset_index()
            fig=px.bar(maximo,x="fila",y="uso",color="acceso",text="uso",color_discrete_map=colores,
                       title="Uso en la hora más cargada",labels={"fila":"","uso":"Uso"})
            fig.update_traces(texttemplate="%{text:.0%}")
            fig.update_yaxes(tickformat=".0%",range=[0,1.1])
            fig.add_hline(y=1,line_dash="dash",line_color=ROSA,annotation_text="capacidad máxima",annotation_font_color=ROSA)
            st.plotly_chart(oscuro(fig),width="stretch")
        with c2.container(border=True):
            fig=px.line(acc_f,x="hora",y="validaciones_promedio",color="fila",markers=True,
                        title="Validaciones por hora en cada acceso",labels={"hora":"Hora","validaciones_promedio":"Validaciones por hora"},
                        color_discrete_sequence=[ROJO,AZUL,NARANJA,"#A3A8F0",ROSA,GRIS])
            st.plotly_chart(oscuro(fig),width="stretch")

        st.caption("Uso = validaciones por minuto ÷ (torniquetes × capacidad). Las estaciones nuevas tienen torniquetes piso a techo (tambor giratorio). Los fabricantes indican hasta 18 pasajeros por minuto con control de acceso, en condiciones ideales; en la estación real (tarjeta, maletas, filas) pasan menos, por eso el slider deja bajar la capacidad. Promedio de los días hábiles después de cada reapertura.")


elif pagina=="Conclusiones":
    encabezado("CONCLUSIONES","Qué encontramos, qué recomendamos y qué no podemos saber con estos datos")

    c1,c2,c3=st.columns(3)
    with c1.container(border=True):
        st.markdown(f"<div style='color:{ROJO};font-size:20px;font-weight:700'>Hallazgos</div>",unsafe_allow_html=True)
        st.write("Cuando reabrieron las estaciones definitivas, la gente se pasó rápido a la estación nueva más cercana, sin cambiar de troncal.")
        st.write("La zona de la Calle 72 y 74 (estación 16 del metro) es la más cargada de la Caracas y tendrá conexión directa con el metro.")
    with c2.container(border=True):
        st.markdown(f"<div style='color:{NARANJA};font-size:20px;font-weight:700'>Recomendaciones</div>",unsafe_allow_html=True)
        st.write("Preparar primero la zona de la Calle 72 y 74: accesos, torniquetes y frecuencias.")
        st.write("Tener lista la definitiva de la Av. Jiménez antes de 2028.")
        st.write("Medir la demanda de Hospital, Calle 45 y Calle 63 cuando abran.")
    with c3.container(border=True):
        st.markdown(f"<div style='color:{AZUL};font-size:20px;font-weight:700'>Limitaciones</div>",unsafe_allow_html=True)
        st.write("Las validaciones son entradas pagas, no personas, y no cuentan los transbordos internos.")
        st.write("En las estaciones 11, 14 y 15 la demanda es un promedio de estaciones cercanas.")
        st.write("No sabemos cuántos transbordos traerá el metro.")

    with st.container(border=True):
        st.markdown(f"<div style='color:{GRIS};font-weight:700'>Fuentes</div>",unsafe_allow_html=True)
        st.write("Validaciones del componente troncal (datos abiertos de TransMilenio, 2026). Planos de las estaciones 10 a 16 (Empresa Metro de Bogotá). Video de dron de la obra (@VIDJCB, noviembre 2026). ITDP, The BRT Planning Guide.")
