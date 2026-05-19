## Step 3, Topic Modeling, similarities de papers y generación y enriquecimiento del KG

Este Step consta de tres pasos fundamentales para el proyecto:

1. Realizar un TopicModeling de los papers procesados para relacionarlos con un Topic y con otros papers por similaridad, estableciendo un umbral de similaridad (a partir de BERTopic o Embeddings)

Embedding: Vector numérico que representa significado que sirve Comparar similitud semántica, búsqueda, clustering, recomendación

2. Creación del KG local a partir de la ontología formada y los datos obtenidos en los anteriores pasos.

3. Enriquecimiento del KG local a partir de los KG públicos declarados en las fuentes (`/assigment_2/step_1/docs/fuentes.md`)


Con este Step podemos nutrir nuestro grafo de conocimiento con estas partes de nuestra ontología:


![Ontología NER-TOPICS](/images/ontologia-ner-topics.png)





## Problemas encontrados
1. Alguna fecha de los papers no venía con formato Date, por lo que se modificó la ontología para que su tipo sea string en vez de date




