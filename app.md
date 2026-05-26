# Research Funding Knowledge Graph (RFKG) + PipeGrobid

## Objetivo

RFKG es la aplicacion completa para analizar financiacion cientifica mediante un Knowledge Graph RDF. PipeGrobid es igual de importante dentro del sistema: actua como motor de procesamiento documental, convierte PDFs en XML TEI con GROBID y proporciona la base sobre la que se construyen las entidades, topics, proyectos y relaciones del KG.

La aplicacion no es un visor generico de grafos. Esta orientada a preguntas de dominio: distribucion geografica de financiacion, ranking de organismos financiadores, grants/proyectos, papers asociados, topics, autores, acknowledgements y similitudes por paper.

## Flujo completo

```text
PipeGrobid -> KG RDF/TTL -> Fuseki -> research_api -> Streamlit
```

1. Los PDFs se colocan en `pdfs/`.
2. PipeGrobid usa GROBID para generar XML TEI en `xmls/`.
3. PipeGrobid y los scripts de `assigment_2` extraen acknowledgements, entidades, proyectos, topics y similitudes.
4. `gen_local_kg` construye el KG RDF local.
5. Fuseki carga el TTL y expone SPARQL.
6. `research_api` consulta Fuseki y devuelve JSON de dominio.
7. `research_frontend` muestra la app Streamlit.

## Stack Docker

El stack principal esta en `containers/docker-compose.yml`.

- `n8n`: orquesta el workflow completo.
- `grobid`: convierte PDFs en XML TEI.
- `pipegrobid`: imagen del pipeline principal para extraccion inicial.
- `python_runner`: ejecuta scripts Python llamados desde n8n con dependencias instaladas.
- `fuseki`: mantiene el Knowledge Graph y responde SPARQL.
- `research_api`: backend FastAPI que consulta Fuseki.
- `research_frontend`: frontend Streamlit que consume `research_api`.

Dentro de Docker, Streamlit usa `http://research_api:8000`. Desde el navegador se abre en `http://localhost:8501`. La API se puede inspeccionar en `http://localhost:8000/docs`.

## Prerrequisitos

- Docker Desktop levantado.
- PDFs de entrada en `pdfs/`.
- Archivo `containers/.env` creado a partir de `containers/.env.example`.
- Variables `GROQ_API_KEY` y `HF_TOKEN` rellenas si se ejecutan los pasos que usan LLM/HuggingFace.

## Levantar la app

Primera ejecucion:

```bash
docker compose -f containers/docker-compose.yml up --build -d
```

Ejecuciones posteriores:

```bash
docker compose -f containers/docker-compose.yml up -d
```

Servicios principales:

```text
n8n:              http://localhost:5678
research_api:     http://localhost:8000/docs
research_frontend http://localhost:8501
fuseki:           http://localhost:3030
```

## Ejecutar el workflow

1. Abrir n8n en `http://localhost:5678`.
2. Importar el workflow:

```text
containers/workflow/pipegrobid_workflow.json
```

3. Entrar en `pipegrobid_workflow`.
4. Ejecutarlo manualmente.
5. Esperar a que termine la extraccion, enriquecimiento, generacion del KG y carga en Fuseki.
6. En Streamlit, pulsar `Actualizar datos` para limpiar la cache y volver a consultar `research_api`.

El workflow usa `grobid` para generar XML, `pipegrobid` para el pipeline inicial, `python_runner` para scripts Python de los steps y `fuseki` como triplestore final.

## Backend `research_api`

`research_api` es la capa de dominio. Evita que el frontend tenga que escribir SPARQL y transforma respuestas de Fuseki en JSON plano.

La financiacion se interpreta como importes conocidos asociados a proyectos. Cuando no hay importe explicito, la API devuelve `funding_amount: null` y `funding_amount_known: false`, y el frontend lo muestra como `N/D`. Cuando el enriquecimiento online aporta moneda, los proyectos devuelven `currency` y los agregados devuelven `currencies`. Los rankings usan relaciones explicitas `schema:funder` de proyecto, no simples menciones en acknowledgements.

Endpoints principales:

- `GET /kg/summary`: resumen global del KG.
- `GET /kg/funding/countries`: ranking de paises, opcionalmente filtrado por `topic_id`.
- `GET /kg/funding/organizations`: ranking de organismos, opcionalmente filtrado por `topic_id`.
- `GET /kg/funding/topics`: cruce pais-topic.
- `GET /kg/papers`: listado filtrable por texto, topic, pais, organizacion y proyecto.
- `GET /kg/papers/{paper_id}`: detalle de paper, acknowledgements separados y fichas de personas con ORCID cuando existe.
- `GET /kg/projects`: proyectos/grants.
- `GET /kg/topics`: topics y papers asociados.
- `GET /kg/similarities/{paper_id}`: similitudes de un paper concreto.
- `POST /kg/query`: SPARQL avanzado para depuracion.

## Frontend `research_frontend`

La app Streamlit esta en `containers/research_frontend`.

Pantallas:

- `Overview`: estado de API/Fuseki y metricas globales.
- `Funding`: pantalla principal; rankings de paises y organismos, filtro por topic y paneles de caracteristicas KG.
- `Papers`: busqueda y detalle con filtros reales; muestra autores, acknowledgements, ORCID e informacion KG de personas.
- `Projects`: ficha de proyecto/grant y tabla completa bajo expander.
- `Topics`: lista de topics y navegacion a papers filtrados.
- `Similarities`: papers similares a un paper concreto.
- `SPARQL`: consola avanzada de depuracion.

La navegacion cruzada es parte de la app: Funding, Topics y Projects llevan a Papers filtrado; Paper detail lleva a Similarities; Similarities permite abrir el detalle de un paper similar.

## Indice de pasos del workflow

- [Step 1: ontologia y caso de uso](assigment_2/step_1/README.md)
  - [Caso de uso](assigment_2/step_1/docs/caso_de_uso.md)
  - [Fuentes](assigment_2/step_1/docs/fuentes.md)
- [Step 2: extraccion desde XML y NER](assigment_2/step_2/README.md)
  - [Parseo de XMLs generados por GROBID](assigment_2/step_2/xmls_parse/README.md)
  - [Evaluacion de modelos NER](assigment_2/step_2/ner_evaluation/README.md)
  - [Extraccion NER con LLM](assigment_2/step_2/ner_extraction/README.md)
- [Step 3: topics y similitudes](assigment_2/step_3/README.md)
  - [Topic modeling y paper similarities](assigment_2/step_3/topic_modeling/README.md)
- [Step 4: Knowledge Graph](assigment_2/step_4/README.md)
  - [Enriquecimiento online](assigment_2/step_4/online_enrichment/README.md)
  - [Generacion del KG local](assigment_2/step_4/gen_local_kg/README.md)
- [Backend research_api](containers/research_api/API_RESEARCH_API.md)
- [Frontend Streamlit](containers/research_frontend/README.md)

## Limitaciones

- Hay instancias o relaciones con datos no disponibles si no se encontraron entidades reconocibles o enriquecimiento externo.
- La financiacion por pais/organizacion se muestra como importe conocido asociado, no como reparto contable exacto.
- La moneda se conserva cuando el enriquecimiento online la proporciona, pero los rankings agregados pueden reunir importes en varias monedas y no realizan conversion entre divisas.
- No siempre se dispone de ORCID, afiliacion, pais o importe para todas las entidades.
