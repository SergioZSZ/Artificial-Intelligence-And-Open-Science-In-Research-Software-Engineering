# Ampliacion de `research_api`

Este documento resume la parte nueva de la API backend que consulta el Knowledge Graph cargado en Fuseki. La app no necesita escribir SPARQL directamente: consume endpoints `/kg/...` que devuelven JSON limpio.

## Objetivo

`research_api` actua como capa de dominio entre la aplicacion Streamlit y Fuseki. Fuseki mantiene el KG RDF, y la API transforma consultas SPARQL en respuestas para pantallas de papers, financiacion, paises, organizaciones, proyectos, topics y similitudes por paper.

Se mantiene `POST /kg/query` para depuracion y consultas SPARQL manuales.

## Estructura

```text
containers/research_api/app/
|- main.py
|- core/
|  `- kg.py
|- queries/
|  |- common.py
|  |- overview.py
|  |- papers.py
|  |- funding.py
|  |- topics.py
|  `- similarities.py
|- routers/
|  |- common.py
|  |- kg.py
|  |- overview.py
|  |- papers.py
|  |- funding.py
|  |- projects.py
|  |- topics.py
|  |- similarities.py
|  `- query.py
|- schemas/
|  |- domain.py
|  `- fuseki.py
`- tests/
```

## Flujo

1. El frontend llama a un endpoint `/kg/...`.
2. El router tematico construye la query con un builder de `queries/`.
3. `core/kg.py` ejecuta la consulta contra Fuseki, anade prefijos y normaliza filas SELECT.
4. `routers/common.py` controla timeouts de Fuseki y ayuda a mapear filas.
5. El router convierte filas SPARQL en modelos Pydantic de `schemas/domain.py`.
6. La respuesta sale como JSON plano.

## Routers

Los prefijos de ruta viven en cada router:

- `routers/papers.py`: `APIRouter(prefix="/papers")`.
- `routers/funding.py`: `APIRouter(prefix="/funding")`.
- `routers/projects.py`: `APIRouter(prefix="/projects")`.
- `routers/topics.py`: `APIRouter(prefix="/topics")`.
- `routers/similarities.py`: `APIRouter(prefix="/similarities")`.
- `routers/query.py`: `APIRouter(prefix="/query")`.

`routers/kg.py` solo agrega esos routers. `main.py` anade el prefijo global `/kg`.

`core/config.py` centraliza la URL de Fuseki y el timeout (`FUSEKI_QUERY_URL`, `FUSEKI_TIMEOUT_SECONDS`). Los routers no deben duplicar esa configuracion.

## Endpoints

### Overview

- `GET /kg/info`: informacion basica del backend y del KG.
- `GET /kg/summary`: conteos generales de papers, autores, organizaciones, proyectos, paises, topics y similitudes.

### Papers

- `GET /kg/papers`: listado de papers con filtros por texto, topic, pais, organizacion y proyecto.
- `GET /kg/papers/{paper_id}`: detalle de un paper con autores, proyectos, financiadores, paises, topics y acknowledgements separados en organizaciones/personas. Tambien devuelve `authors_info` y `acknowledged_people_info` con ORCID, afiliacion, id KG y URI cuando el KG dispone de esos datos.

`paper_id` acepta formatos como `paper01`, `g4:paper01` o la URI completa del recurso.

Parametros utiles de `GET /kg/papers`:

- `search`: busqueda por titulo o abstract.
- `topic_id`, `country`, `organization`, `project`: filtros de exploracion.
- `limit` y `offset`: paginacion del listado.

### Funding y proyectos

- `GET /kg/funding/countries`: distribucion completa de financiacion por pais. Acepta `topic_id` para filtrar el ranking por area tematica.
- `GET /kg/funding/topics`: cruce pais-topic para ver que paises financian mas cada area tematica.
- `GET /kg/funding/organizations`: ranking de organismos financiadores. Usa `limit` para devolver el top N y acepta `topic_id` para contar solo organismos que financian papers de ese topic.
- `GET /kg/projects`: proyectos/grants con identificador, fechas, financiadores y papers. Usa `limit` y `offset`.

La pantalla `Funding` del frontend usa `topic_id` sobre paises y organizaciones para sustituir el heatmap por rankings filtrables y paneles de caracteristicas del KG.

Los importes se devuelven como financiacion conocida asociada, no como reparto exacto por pais u organismo. Por eso las respuestas incluyen:

- `funding_amount`: suma de importes conocidos cuando existen; puede ser `null`.
- `funding_amount_known`: indica si el KG tenia al menos un importe explicito para esa agregacion.

Las queries de financiacion usan la cadena `paper -> g4:fundedByProject -> schema:Project -> schema:funder -> schema:Organization -> schema:location -> schema:Country`. No usan `g4:acknowledges` para inferir financiadores, porque en acknowledgements puede haber organizaciones mencionadas que no son necesariamente el organismo financiador del proyecto.

### Topics y similitudes

- `GET /kg/topics`: topics detectados, keywords y papers asociados.
- `GET /kg/similarities/{paper_id}`: papers similares a un paper concreto, con score. Usa `limit` para devolver el top N.

El listado global de todas las similitudes se ha quitado de la API publica porque duplicaba informacion y no aportaba directamente al caso de uso de la aplicacion.

### SPARQL avanzado

- `POST /kg/query`: envia SPARQL libre a Fuseki.

## Tests

Los tests usan mocks de Fuseki para no depender de un servidor real:

- `test_domain_queries.py`: builders SPARQL y normalizacion de ids.
- `test_kg_router.py`: rutas publicas, prefijos de routers y JSON normalizado.

Comando recomendado:

```bash
cd containers/research_api/app
python -m pytest tests -q
```

## Declaracion de uso de IA

Se uso IA generativa como apoyo para estructurar las queries SPARQL, los schemas Pydantic y los endpoints necesarios para conectar Fuseki con el frontend. El resultado fue revisado, probado con mocks y validado durante la integracion con la app.
