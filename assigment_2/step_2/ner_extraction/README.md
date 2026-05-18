# NER_EXTRACTION
## Introducción
Debido al análisis realizado en la evaluación de modelos de NER, se realiza usando el modelo `llama-3.3-70b-versatile`.

Para ello, se ha generado un entorno poetry con las dependencias necesarias para su uso y lectura de ficheros .env:
- Groq
- python-dotenv

## Explicación
Con la ejecución del script `llama_extraction.py` se realiza la extracción de los acknowledgements de los ficheros jsons contenidos en el directorio `/outputs/parsed_xmls`, se usa el modelo para reconocer entidades y se nutren los datos con dichas entidades reconocidas.


Se nutren de manera que:
- Las organizaciones y proyectos reconocidos se añaden a los campos del json
- Se evitan personas duplicadas obtenidas entre los autores y los acknowledgements reconociéndolos el LLM aunque no sean exactamente el mismo texto
- se guarda un campo `authors_mention` en el json para comprobar las duplicidades encontradas entre los acknowledgements y los autores.

Si no hay acknowledgements en el paper el json no sufre cambios.

Por último, se generan los jsons nutridos en el directorio `/outputs/extrated_acknowledgements_parsed_xmls`

## Replicación de la extracción
Para llevar a cabo la replicación, es necesario haber generado anteriormente los jsons parseados ejecutando el mandato desde la raíz del repositorio `poetry run python ./src/pipegrobid/flow/parse_grobid_xml.py`.

También es necesario generar tu token Groq y escribirlo en un .env dentro `/assigment_2/step_2/ner_evaluation/` siguiendo las indicaciones del `.env.example`

Posteriormente, desde el directorio `/assigment_2/step_2/ner_extraction` ejecutar el mandato `poetry run python ./scripts/llama_extraction.py` para obtener los jsons nutridos.


## DECLARACIÓN DE USO DE IA
No se usó ningún tipo de IA generativa para buscar el mejor prompt que enviarle al LLM, revisado y aprobado por el Grupo 4 de OpenScience.
