# Generación del KG local
## Introducción
Para terminar de nutrir nuestro KG, se genera un grafo local en formato `.ttl` a partir de los jsons ya enriquecidos en los pasos anteriores. Estos jsons contienen la información de los papers, autores, organizaciones, proyectos, países, topics y similaridades entre papers.

La generación se realiza usando la ontología creada en `/assigment_2/step_1/ontology/ontology.ttl`, por lo que el resultado final sigue las clases y relaciones definidas para nuestro caso de uso.

## Explicación

El script principal es `scripts/local_kg.py`. Primero carga la ontología con `rdflib` y después recorre todos los jsons encontrados en `/assigment_2/step_4/outputs`.

A partir de cada json se crean instancias de:
1. Papers, con título, abstract, fecha e identificador si existe.
2. Personas, distinguiendo autores y personas reconocidas en acknowledgements.
3. Organizaciones, añadiendo identificador, descripción y país cuando se dispone de ello.
4. Proyectos, usando su nombre o identificador y añadiendo fechas, descripción y financiación si existe.
5. Países, topics y relaciones de similaridad.

Con estas instancias se generan relaciones como:
- paper-autor mediante `schema:author`
- persona-organización mediante `schema:affiliation`
- paper-entidad reconocida mediante `acknowledges`
- paper-proyecto mediante `fundedByProject`
- proyecto-moneda mediante `schema:currency` cuando el enriquecimiento online la proporciona
- proyecto-organizacion financiadora mediante `schema:funder`, priorizando el `funder` explicito del proyecto
- organización-país mediante `schema:location`
- paper-topic y paper-paper usando los scores obtenidos en el topic modeling

El KG generado se guarda en:

`/assigment_2/step_4/outputs/local_kg.ttl`

## Replicación

Primero se deben haber generado los jsons enriquecidos de los pasos anteriores en `/assigment_2/step_4/outputs`.

Posteriormente, desde el directorio `/assigment_2/step_4/gen_local_kg`, instalar el entorno poetry con `poetry install --no-root` y ejecutar:

`poetry run python ./scripts/local_kg.py`

Por pantalla se mostrará el número de jsons encontrados, la ruta donde se guarda el KG y el número total de triples generados.

## Problemas encontrados
1. Algunos campos no están presentes en todos los jsons, por lo que se comprueba su existencia antes de generar cada triple.
2. Algunas afiliaciones pueden venir como string o como diccionario, por lo que se añadió una función auxiliar para leer ambos casos.
3. La relación entre proyectos y funders se trata de forma conservadora: si el proyecto trae `funder`, se usa ese valor; si no lo trae, solo se infiere en casos simples. Cuando hay varios proyectos y varias organizaciones reconocidas, no se crea una relación all-to-all para evitar asignar financiadores incorrectos.

## Declaración de uso de IA
Se usó IA generativa para:
-  estructurar parte del método `build_kg_from_jsons()` del script `local_kg.py` para cerciorarse de la total incorporación de propiedades y relaciones de las clases que se pueden incorporar con los datos contenidos en `/assigment_2/step_4/outputs` al KG local.
