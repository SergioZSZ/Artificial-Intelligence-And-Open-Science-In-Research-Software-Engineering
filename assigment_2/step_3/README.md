## Step 3, Topic Modeling, similarities de papers y generación y enriquecimiento del KG

Este Step consta de :

1. Realizar un TopicModeling de los papers procesados para relacionarlos con un Topic y con otros papers por similaridad, estableciendo un umbral de similaridad (a partir de BERTopic o Embeddings)

Embedding: Vector numérico que representa significado que sirve Comparar similitud semántica, búsqueda, clustering, recomendación


Con este Step podemos nutrir nuestro grafo de conocimiento con estas partes de nuestra ontología:


![Ontologia NER-TOPICS](/images/ontologia-ner-topics.png)






## Problemas encontrados
1. Alguna fecha de los papers no venía con formato Date, por lo que se modificó la ontología para que su tipo sea string en vez de date

2. La extracción de entidades usando Llama tiene un límite de tokens diario. Por lo que el workflow actualmente se puede ejecutar entre 1 y 2 veces diarias.




