[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18647861.svg)](https://doi.org/10.5281/zenodo.18647861)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)
[![GitHub release](https://img.shields.io/github/v/release/SergioZSZ/OS-IA-Pipegrobid?include_prereleases)](https://github.com/SergioZSZ/OS-IA-Pipegrobid/releases)
[![Project Status: Active](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active)

# Research Funding Knowledge Graph (RFKG) + PipeGrobid

Mas documentacion en: https://pipegrobid-software.readthedocs.io/es/latest/

RFKG es una aplicacion para analizar financiacion cientifica a partir de papers procesados como Knowledge Graph. PipeGrobid es el pipeline documental que transforma PDFs en XML TEI con GROBID y genera las salidas iniciales necesarias para alimentar la parte semantica.

El proyecto se organiza en dos fases igualmente importantes: la FASE 1 construye el procesamiento reproducible de documentos cientificos, y la FASE 2 convierte esas extracciones en una app KG con n8n, Fuseki, `research_api` y Streamlit.

## FASE 1: pipeline PDF -> XML -> salidas

Flujo:

```text
PDF -> GROBID -> TEI XML -> extraccion -> limpieza NLP -> visualizacion y TXT
```

El pipeline principal vive en `src/pipegrobid/` y genera:

- `xmls/`: XML TEI obtenidos desde GROBID.
- `generated_files/keyword_cloud.png`: nube de palabras de abstracts.
- `generated_files/figures_visualization.png`: visualizacion de figuras por paper.
- `generated_files/links_per_paper.txt`: enlaces detectados por paper.

### Ejecucion con Docker Compose

1. Colocar PDFs en `pdfs/`.
2. Abrir Docker Desktop.
3. Ejecutar desde la raiz:

```bash
docker compose up --build pipegrobid
docker compose down
```

### Ejecucion local con Poetry

Levantar GROBID:

```bash
docker run -t --rm -p 8070:8070 grobid/grobid:0.7.2
```

Instalar y ejecutar:

```bash
poetry install
poetry run pipegrobid
```

Tests:

```bash
poetry run pytest -v
```

## FASE 2: RFKG, app Knowledge Graph

La FASE 2 construye RFKG sobre las salidas de PipeGrobid. Convierte los papers procesados en un KG RDF para responder preguntas sobre financiacion cientifica: paises financiadores, organismos, proyectos, topics, autores, acknowledgements, ORCID y papers similares.

Flujo:

```text
PipeGrobid -> KG RDF/TTL -> Fuseki -> research_api -> Streamlit
```

Stack principal:

- `n8n`: workflow completo.
- `grobid`: conversion PDF -> XML TEI.
- `pipegrobid`: pipeline inicial.
- `python_runner`: scripts Python de los steps.
- `fuseki`: triplestore SPARQL.
- `research_api`: API FastAPI sobre el KG.
- `research_frontend`: app Streamlit.

Levantar la app completa:

```bash
docker compose -f containers/docker-compose.yml up --build -d
```

Ejecuciones posteriores:

```bash
docker compose -f containers/docker-compose.yml up -d
```

URLs:

- n8n: `http://localhost:5678`
- API: `http://localhost:8000/docs`
- Frontend: `http://localhost:8501`
- Fuseki: `http://localhost:3030`

Para ejecutar el workflow, importar en n8n:

```text
containers/workflow/pipegrobid_workflow.json
```

Despues de actualizar el KG en Fuseki, usar `Actualizar datos` en Streamlit para limpiar cache y volver a consultar la API.

Documento operativo completo: [app.md](app.md).

## Indice de la FASE 2

- [Step 1: ontologia y caso de uso](assigment_2/step_1/README.md)
  - [Caso de uso](assigment_2/step_1/docs/caso_de_uso.md)
  - [Fuentes](assigment_2/step_1/docs/fuentes.md)
- [Step 2: XML y NER](assigment_2/step_2/README.md)
  - [Parseo XML](assigment_2/step_2/xmls_parse/README.md)
  - [Evaluacion NER](assigment_2/step_2/ner_evaluation/README.md)
  - [Extraccion NER con LLM](assigment_2/step_2/ner_extraction/README.md)
- [Step 3: topics y similitudes](assigment_2/step_3/README.md)
  - [Topic modeling](assigment_2/step_3/topic_modeling/README.md)
- [Step 4: Knowledge Graph](assigment_2/step_4/README.md)
  - [Enriquecimiento online](assigment_2/step_4/online_enrichment/README.md)
  - [Generacion KG local](assigment_2/step_4/gen_local_kg/README.md)
- [Backend research_api](containers/research_api/API_RESEARCH_API.md)
- [Frontend Streamlit](containers/research_frontend/README.md)

## Estructura principal

```text
src/pipegrobid/              paquete principal de la FASE 1
test/                        tests del paquete principal
docs/                        documentacion ReadTheDocs por fases
assigment_2/                 steps de ontologia, NER, topics y KG
containers/                  stack Docker, n8n, Fuseki, API y frontend
pdfs/                        PDFs de entrada
xmls/                        XML TEI generados
generated_files/             salidas visuales y TXT
outputs/                     salidas usadas por el stack/workflow
```

## Declaracion de uso de IA

Se uso IA generativa como apoyo en distintas partes del proyecto, siempre bajo supervision y validacion de los autores:

- Parseo XML: ayuda para localizar nodos TEI relevantes y para generar/entender el codigo inicial de extraccion.
- Evaluacion NER: los LLMs Groq y Qwen fueron objeto de estudio; tambien se uso IA conversacional para apoyar scripts, informe y documentacion. El gold standard fue anotado manualmente.
- Extraccion NER: ayuda para revisar y estructurar scripts relacionados con la extraccion de personas, organizaciones y proyectos.
- Topic modeling: ayuda para entender BERTopic, HDBSCAN, UMAP y la generacion de similitudes entre papers.
- Enriquecimiento online: apoyo en expresiones regulares, limpieza de identificadores y navegacion de respuestas JSON de APIs externas.
- Generacion del KG local: apoyo para estructurar `build_kg_from_jsons()` y comprobar la incorporacion de clases, propiedades y relaciones.
- Backend `research_api`: apoyo para estructurar queries SPARQL, schemas y endpoints necesarios para conectar Fuseki con el frontend.
- Frontend Streamlit: se uso IA generativa para generar la app siguiendo la guia de los autores, revisando, probando y evaluando cada parte generada.
- Estructuramiento y uso de ro-crate.py para crear el RO
## Limitaciones

- GROBID debe estar levantado para generar XMLs.
- Algunos enlaces extraidos desde PDFs pueden traer fragmentos adicionales por como GROBID reconstruye el texto.
- La financiacion de la app se muestra como importe conocido asociado, no como reparto contable exacto.
- Los JSONs enriquecidos pueden traer `currency`, pero la API y el frontend aun no muestran la moneda asociada al importe; se deja como mejora para futuras versiones.
- No todos los papers o entidades tienen ORCID, pais, afiliacion o importe disponible.
- ORCID puede devolver perfiles ambiguos si hay varias personas con el mismo nombre.
- Wikidata no siempre dispone de pais para organizaciones supranacionales.
