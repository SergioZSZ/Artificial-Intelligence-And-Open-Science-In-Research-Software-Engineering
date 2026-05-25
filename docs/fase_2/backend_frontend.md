# Backend y frontend

## `research_api`

`research_api` vive en `containers/research_api/app` y expone endpoints de dominio sobre el KG. Mantiene `/kg/query` para SPARQL avanzado, pero la app consume principalmente endpoints cerrados que devuelven JSON plano.

Endpoints principales:

- `GET /kg/summary`: resumen global del KG.
- `GET /kg/funding/countries`: ranking de paises, filtrable por `topic_id`.
- `GET /kg/funding/organizations`: ranking de organismos, filtrable por `topic_id`.
- `GET /kg/funding/topics`: cruce pais-topic.
- `GET /kg/papers`: listado filtrable por texto, topic, pais, organizacion y proyecto.
- `GET /kg/papers/{paper_id}`: detalle de paper, autores, ORCID, acknowledgements, topics y financiacion.
- `GET /kg/projects`: proyectos/grants.
- `GET /kg/topics`: topics y papers asociados.
- `GET /kg/similarities/{paper_id}`: similitudes de un paper concreto.
- `POST /kg/query`: SPARQL avanzado para depuracion.

Las queries SPARQL estan organizadas por tema en `queries/<tema>.py`, y los routers en `routers/<tema>.py`.

## `research_frontend`

`research_frontend` vive en `containers/research_frontend` y usa Streamlit. Consume `research_api` mediante HTTP.

Pantallas:

- `Overview`: estado de servicios y resumen del KG.
- `Funding`: pantalla principal con ranking de paises, ranking de organismos y filtro por topic.
- `Papers`: filtros por desplegables, tabla de papers y detalle con autores, ORCID y acknowledgements.
- `Projects`: ficha de grants/proyectos.
- `Topics`: topics y navegacion hacia papers filtrados.
- `Similarities`: papers similares a un paper seleccionado.
- `SPARQL`: consola avanzada para depuracion.

## Navegacion cruzada

La app evita ser un conjunto de tablas aisladas:

- desde Funding se puede saltar a Papers filtrado por pais, organismo y topic;
- desde Topics se puede abrir Papers filtrado por topic;
- desde Projects se puede abrir Papers filtrado por proyecto;
- desde Paper detail se puede abrir Similarities;
- desde Similarities se puede abrir el detalle de un paper similar.

## Declaracion de uso de IA

En `research_api` se uso IA generativa como apoyo para estructurar queries SPARQL, schemas y endpoints necesarios para conectar Fuseki con el frontend. En `research_frontend` se uso IA generativa para generar y organizar la app Streamlit siguiendo la guia de los autores. Cada parte fue revisada, probada y evaluada durante el desarrollo.
