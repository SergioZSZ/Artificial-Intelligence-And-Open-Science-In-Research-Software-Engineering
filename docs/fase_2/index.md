# FASE 2: Research Funding Knowledge Graph (RFKG)

RFKG es la aplicacion basada en Knowledge Graph que analiza financiacion cientifica a partir de papers procesados por PipeGrobid. PipeGrobid sigue siendo una pieza esencial: convierte PDFs en XML TEI con GROBID y proporciona la base documental sobre la que la fase semantica extrae metadatos, autores, acknowledgements, entidades, proyectos, topics y similitudes.

El resultado se modela como RDF, se carga en Fuseki y se consulta desde `research_api` y un frontend Streamlit.

Flujo general:

```text
PipeGrobid -> NER/enriquecimiento -> topics -> KG RDF -> Fuseki -> research_api -> Streamlit
```

Documentacion de esta fase:

- [Caso de uso y ontologia](caso_uso_ontologia.md)
- [Pipeline de datos](pipeline_datos.md)
- [Knowledge Graph](knowledge_graph.md)
- [Stack Docker y workflow](stack_workflow_app.md)
- [Backend y frontend](backend_frontend.md)
- [Limitaciones](limitaciones.md)

Fuentes principales en el repositorio:

- `assigment_2/step_1`: caso de uso, fuentes y ontologia.
- `assigment_2/step_2`: parseo de XMLs y NER de acknowledgements.
- `assigment_2/step_3`: topic modeling y similitudes entre papers.
- `assigment_2/step_4`: enriquecimiento y generacion del KG local.
- `containers/`: stack Docker, n8n, Fuseki, API y frontend.
- `app.md`: documento operativo de la app completa.
