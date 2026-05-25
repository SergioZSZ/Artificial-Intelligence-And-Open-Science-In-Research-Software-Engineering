# FASE 2: Aplicacion sobre Knowledge Graph

La FASE 2 amplía PipeGrobid con una aplicacion basada en Knowledge Graph para analizar financiacion cientifica. A partir de PDFs procesados con GROBID se extraen metadatos, autores, acknowledgements, entidades, proyectos, topics y similitudes. El resultado se modela como RDF, se carga en Fuseki y se consulta desde una API y un frontend Streamlit.

Flujo general:

```text
PDFs -> GROBID -> XML TEI -> extraccion -> NER/enriquecimiento -> topics -> KG RDF -> Fuseki -> research_api -> Streamlit
```

Documentación de esta fase:

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
