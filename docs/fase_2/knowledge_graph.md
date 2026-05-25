# Knowledge Graph

## Salida RDF

El KG local se genera como Turtle en:

```text
assigment_2/step_4/outputs/local_kg.ttl
```

La generacion usa `rdflib` y parte de los JSONs enriquecidos de `assigment_2/step_4/outputs`.

## Entidades modeladas

![Ontologia completa del KG](../images/completa.png)

- Papers con titulo, abstract, fecha e identificador.
- Personas, separando autores y personas reconocidas en acknowledgements.
- Organizaciones con nombre, identificador, descripcion y pais cuando existe.
- Proyectos/grants con identificador, fechas, financiador e importe conocido cuando existe.
- Paises.
- Topics.
- Relaciones de similitud entre papers.

## Criterio para financiadores

La relacion proyecto-financiador se trata de forma conservadora:

- si el proyecto trae `funder`, se usa ese valor;
- si no lo trae, solo se infiere en casos simples;
- si hay varios proyectos y varias organizaciones reconocidas en el mismo paper, no se crea una relacion all-to-all.

Esto evita interpretar cualquier organizacion mencionada en acknowledgements como financiadora real.

## Financiacion conocida

Los importes se muestran como financiacion conocida asociada. Si no existe `g4:fundingAmount`, la API devuelve `funding_amount: null` y `funding_amount_known: false`. La app lo muestra como `N/D` para no confundir ausencia de dato con financiacion cero.

## Fuseki

Fuseki mantiene el KG y expone consultas SPARQL. `research_api` es quien consulta Fuseki; el frontend nunca ejecuta SPARQL directamente salvo la pantalla avanzada que envia consultas al endpoint `/kg/query`.
