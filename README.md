# Troncal Caracas: reaperturas y llegada del metro

Proyecto 2 de Aplicaciones en Ciencia de Datos (DATA1002), Universidad de los Andes.

Integrantes: Sebastián Moreno, Miguel, Juan y Mateo.

## Enlaces

- Dashboard: [pegar link .streamlit.app]
- Presentación: [reports/presentacion.pdf](reports/presentacion.pdf) · [Canva](https://www.canva.com/d/sj8RH_3zHK1KxVs)

## Problema

La troncal Caracas está en obras por el metro. Sus estaciones se cierran y reabren, y cada cambio mueve a miles de usuarios. En 2028 algunas tendrán conexión con el metro.

- Afectados: los usuarios de la Caracas.
- Quién decide: TransMilenio y la Secretaría de Movilidad (accesos, torniquetes y frecuencias).

## Pregunta

¿Cómo se reacomoda la demanda cuando la Caracas recupera sus estaciones definitivas, y qué estaciones, por su demanda actual y su conexión con el metro, deben prepararse primero antes de 2028?

## Datos

| Fuente | Origen | Qué aporta |
|---|---|---|
| Validaciones troncales | Datos abiertos TransMilenio, 2026 | Cuánta gente entra a cada estación |
| Planos de las estaciones del metro | Empresa Metro de Bogotá | Qué estaciones tendrán conexión |

Se unen por el código de la estación, con una tabla de zonas que dice qué estaciones de TransMilenio atienden cada estación del metro. Juntas permiten saber qué estaciones con metro tienen más demanda.

## Limpieza

- Dejamos solo las validaciones del día de cada archivo y un nombre por código.
- Quitamos festivos y el día de las marchas.
- Para el metro usamos solo noviembre, porque la Calle 22 estuvo cerrada en octubre.
- Sumamos las dos estaciones de la Av. Jiménez, que están en el mismo cruce.

## Conclusiones

1. Cuando una estación reabre, la gente se pasa en pocas semanas a la más cercana. La Calle 72 recibió el 103 % de la demanda de la 76.
2. La zona de la Calle 72 a 74 (estación 16 del metro) es el nodo crítico: casi 13.000 validaciones en hora pico, un 50 % más que la siguiente.
3. En los días más cargados, los accesos norte de la Calle 72 y de la Calle 26 llegarían al 81 % de su capacidad si los torniquetes piso a techo dejan pasar 10 personas por minuto.

## Recomendaciones

1. Agregar 2 torniquetes en el acceso norte de la Calle 72 (de 7 a 9) y 1 en el de la Calle 26 (de 5 a 6) antes de 2028, para quedar por debajo del 70 % en los días más cargados.
2. Diseñar la conexión de la estación 16 para al menos 13.000 validaciones en hora pico.
3. Reforzar las rutas en las primeras semanas después de abrir cada conexión.
4. Medir en campo los torniquetes piso a techo y la demanda de Hospital, Calle 45 y Calle 63 cuando abran.

## Limitaciones

- Las validaciones son entradas pagas, no personas.
- En las estaciones 11, 14 y 15 del metro la demanda es un promedio de estaciones cercanas.
- No sabemos cuántos transbordos traerá el metro.
- La Calle 26 solo tiene 8 días hábiles antes de la reapertura (no hay datos del 1 al 5 de junio y el 8 y el 15 fueron festivos), y además coincidió con vacaciones.
- Los 10 pasajeros por minuto por torniquete son un supuesto; hay que medirlo en campo.

## Estructura

```
├── data/
│   ├── raw/          datos originales (las validaciones se descargan del portal de TransMilenio)
│   └── processed/    tablas limpias que usa el dashboard
├── notebooks/        procesamiento, análisis, ranking y torniquetes
├── SRC/app.py        dashboard en Streamlit
├── reports/          presentación y justificación de estaciones
└── requirements.txt
```

Orden de los notebooks: `procesamiento_validaciones` → `analisis_3_estaciones` → `carga_estaciones_metro` → `ranking_metro` → `torniquetes`.

## Cómo correrlo

Desde la carpeta principal del repositorio:

```
pip install -r requirements.txt
python -m streamlit run SRC/app.py
```

## Fuentes

- TransMilenio S.A. Validaciones del componente troncal (datos abiertos).
- Empresa Metro de Bogotá. Planos de las estaciones 10 a 16.
- @VIDJCB (2026). Video de dron de la obra del metro. [pegar link]
