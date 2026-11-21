## De qué trata

Las obras del metro cambiaron por completo la troncal Caracas de TransMilenio. Entre 2024 y 2025 cerraron estaciones, abrieron temporales y movieron algunas rutas a la NQS y la carrera 10. En 2026 empezaron a abrir las estaciones definitivas, que van a quedar conectadas con el metro cuando empiece a operar en 2028.

Queremos entender qué pasa con los pasajeros cuando estas estaciones vuelven a abrir, y usar eso para saber qué estaciones de la Caracas deberían prepararse primero para la llegada del metro.

**Pregunta:** ¿Cómo se reacomoda la demanda de TransMilenio cuando la Caracas recupera sus estaciones definitivas, y cuáles de ellas serán los puntos críticos cuando llegue el metro en 2028?

**Para quién:** TransMilenio y la Secretaría de Movilidad.

## Qué queremos lograr

- Medir cuántos pasajeros ganaron las estaciones nuevas (Calle 26, Calle 72 y Calle 53) y qué pasó con las estaciones cercanas.
- Con ese patrón, estimar qué puede pasar cuando abran las definitivas que faltan.
- Hacer un ranking de las estaciones que deberían prepararse primero para el metro.

## Datos

- **Validaciones troncales** – TransMilenio. Período: _por definir_.
- **Estaciones troncales** – TransMilenio.
- **Estaciones de la Línea 1 del Metro** – Empresa Metro de Bogotá.
- **Cronología de cierres y aperturas** – la armamos nosotros con comunicados oficiales.


## Cómo lo hacemos

Para cada estación que abrió, comparamos las validaciones de unas semanas antes y después, tanto en la estación como en las que quedan cerca. Para no sacar conclusiones equivocadas, comparamos con una troncal que no tuvo cambios y tenemos en cuenta a los colados.

## Organización

- `data/raw`: datos originales, sin modificar.
- `data/processed`: datos limpios y unidos.
- `notebooks`: el análisis paso a paso.
- `src`: funciones que usamos varias veces.
- `outputs`: gráficos y tablas.
- `requirements.txt`: librerías necesarias.

Las validaciones originales no se suben porque pesan demasiado.

## Cómo correrlo

_Por completar._

## Resultados

_Por completar._

## Limitaciones

- Las validaciones muestran dónde se sube la gente, pero no por dónde viaja ni dónde se baja.
- Cuentan pagos, no personas: los colados no aparecen.
- Son pocos eventos, así que los resultados son una aproximación.
- El ranking de estaciones sirve para priorizar, no para predecir cuánta gente usará el metro.

## Equipo
- Juan Esteban Araque Velez
- Miguel Colmenares
- Sebastian Moreno
