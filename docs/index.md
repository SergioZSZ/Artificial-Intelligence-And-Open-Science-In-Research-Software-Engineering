[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18647861.svg)](https://doi.org/10.5281/zenodo.18647861)
![GitHub License](https://img.shields.io/github/license/SergioZSZ/Artificial-Intelligence-And-Open-Science-In-Research-Software-Engineering)
[![GitHub release](https://img.shields.io/github/v/release/SergioZSZ/Artificial-Intelligence-And-Open-Science-In-Research-Software-Engineering?include_prereleases)](https://github.com/SergioZSZ/Artificial-Intelligence-And-Open-Science-In-Research-Software-Engineering/releases)

# Research Funding Knowledge Graph (RFKG) + PipeGrobid

Esta documentacion describe el sistema RFKG + PipeGrobid. RFKG es la aplicacion final para analizar financiacion cientifica mediante un Knowledge Graph; PipeGrobid es el pipeline documental que convierte PDFs cientificos en XML TEI y genera la base necesaria para construir ese grafo.

La documentacion esta organizada en dos fases:

- **FASE 1**: construccion de PipeGrobid como pipeline reproducible para convertir PDFs en XML TEI, extraer abstracts, figuras y enlaces, y generar salidas visuales.
- **FASE 2**: construccion de RFKG como aplicacion basada en Knowledge Graph para analizar financiacion cientifica con n8n, Fuseki, `research_api` y Streamlit.

La FASE 2 se documenta en [Research Funding Knowledge Graph](fase_2/index.md).

## Objetivo del proyecto

El objetivo del proyecto es construir una cadena reproducible capaz de:

- procesar documentos cientificos en PDF mediante GROBID y PipeGrobid;
- extraer informacion estructurada desde XML TEI;
- enriquecer entidades, proyectos, autores, acknowledgements y topics;
- generar un Knowledge Graph RDF;
- consultarlo desde Fuseki mediante `research_api`;
- visualizarlo en la app Streamlit RFKG.

El flujo del proyecto es:

```text
PipeGrobid -> KG RDF/TTL -> Fuseki -> research_api -> Streamlit
```

## Estructura del proyecto

```text
/
|-- generated_files/        # Archivos generados por PipeGrobid
|-- pdfs/                   # PDFs de entrada
|-- xmls/                   # XML TEI generados por GROBID/PipeGrobid
|-- src/pipegrobid/         # Paquete principal de PipeGrobid
|-- test/                   # Tests del paquete principal
|-- assigment_2/            # Steps de ontologia, NER, topics y KG
|-- containers/             # Stack Docker, n8n, Fuseki, API y frontend
|-- docs/                   # Documentacion ReadTheDocs
|-- app.md                  # Documento operativo de RFKG
|-- CITATION.cff            # Como citar el software
|-- codemeta.json           # Metadatos del proyecto
|-- LICENSE                 # Licencia Apache 2.0
|-- README.md               # Documentacion principal
|-- poetry.lock             # Resolucion de dependencias
`-- pyproject.toml          # Metadatos y dependencias Python
```
