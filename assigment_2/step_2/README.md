## Step 2, acknowledgements NER

Este Step consta de 3 pasos fundamentales para el proyecto:

1. Extracción de la información estructurada encontrada en los xmls generados por GROBID a partir de los papers seleccionados.

2. Creación del corpus (golden standar) ubicado en `/corpus`, creado y validado por el Grupo 4 de OpenScience + estudio de Transformers/LLMs de Groq y HughingFace para seleccionar el más adecuado para el NER de los acknowledgements de nuestros papers.

3. La extracción de las entidades reconocidas mediante el LLM acordado en el estudio (``llama-3.3-70b-versatile``) obteniendo personas (evitando duplicados de cualquier tipo), organizaciones y proyectos de dichos acknowledgements.


Con este Step podemos nutrir nuestro grafo de conocimiento con estas partes de nuestra ontología:


![Ontología NER](/images/ontologia-ner.png)
