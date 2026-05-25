# RO-Crate de RFKG + PipeGrobid

Este directorio contiene el **RO-Crate** del proyecto **Research Funding Knowledge Graph (RFKG) + PipeGrobid**. Un RO-Crate es una forma estandarizada de describir un Research Object mediante metadatos JSON-LD: explica que contiene el proyecto, que software interviene, que datos se generan y como se relacionan las partes principales.

## Archivo principal

El archivo central es:

```text
ro-crate-metadata.json
```

Ese JSON-LD contiene el grafo de metadatos del proyecto. No es el Knowledge Graph RDF de la aplicacion, sino el grafo documental del propio proyecto: describe RFKG, PipeGrobid, sus datasets, servicios, workflow, documentacion y autores.

## Entidad principal

La entidad principal del RO-Crate es:

```text
#rfkg-application
```

Representa **Research Funding Knowledge Graph (RFKG)**, la aplicacion final que permite analizar financiacion cientifica a partir de papers procesados.

RFKG se apoya en:

- PipeGrobid, para convertir PDFs en XML TEI y generar las salidas iniciales.
- El Knowledge Graph local, generado en RDF/Turtle.
- Fuseki, para publicar y consultar el grafo mediante SPARQL.
- `research_api`, para convertir consultas SPARQL en endpoints de dominio.
- `research_frontend`, para visualizar la informacion en Streamlit.
- n8n, para orquestar el workflow completo.

## Papel de PipeGrobid

PipeGrobid aparece como entidad clave:

```text
#pipegrobid-software
```

No se trata como un elemento secundario. Es el pipeline documental que alimenta la aplicacion RFKG: procesa PDFs cientificos con GROBID, genera XML TEI y produce las primeras salidas que despues se enriquecen y se transforman en Knowledge Graph.

## Datos descritos

El RO-Crate describe los datasets principales a nivel de coleccion:

- `pdfs/`: PDFs de entrada.
- `xmls/`: XML TEI generados.
- `generated_files/`: salidas iniciales de PipeGrobid.
- `assigment_2/step_1/`: caso de uso y ontologia.
- `assigment_2/step_2/`: parseo XML y NER.
- `assigment_2/step_3/`: topics y similitudes.
- `assigment_2/step_4/`: enriquecimiento y generacion del KG.
- `#local-kg`: Knowledge Graph local generado en `local_kg.ttl`.

Por decision de granularidad, el RO-Crate no enumera cada PDF, XML o JSON enriquecido individualmente. Se documentan como colecciones para que el crate sea legible y no se convierta en un inventario demasiado grande.

## Software y servicios descritos

El crate incluye entidades para RFKG, PipeGrobid, `research_api`, `research_frontend`, GROBID, Fuseki, n8n, FastAPI y Streamlit.

## Acciones y trazabilidad

Tambien se describen acciones del flujo reproducible: ejecucion de PipeGrobid, ejecucion del workflow n8n y publicacion/consulta del KG mediante Fuseki, `research_api` y Streamlit.

## Que no contiene

El RO-Crate no copia datasets pesados ni estado de ejecucion local. En su lugar, referencia rutas del repositorio. No incluye caches, entornos virtuales, volumenes Docker, carpetas runtime, `ignore/`, `graphify-out/`, `grobid-master` ni cada archivo generado de forma individual.

## Como regenerarlo

Desde la raiz del repositorio:

```bash
python ro-crate.py
```

El script vuelve a generar este directorio y actualiza `ro-crate-metadata.json`.

## Como interpretarlo

Para leer el RO-Crate manualmente, abre `ro-crate-metadata.json`, busca la entidad `./`, revisa `mainEntity` y sigue relaciones como `isBasedOn`, `softwareRequirements`, `instrument`, `object` y `result`.

En resumen: este RO-Crate documenta RFKG como resultado principal del proyecto y PipeGrobid como la pieza esencial que hace posible construir el Knowledge Graph desde documentos cientificos.
