# Topic Modeling y papers similarities
## Introducción
Para nutrir nuestro KG con los Topics y similaridades entre papers, se realizó un topic_modeling usando la herramienta `BERTopic` y Embeddings.

## Explicación
Primero se realiza el topic modeling. Cargando los jsons enriquecidos dentro de `/outputs/extrated_acknowledgements_parsed_xmls`, ya que se realizará a partir de sus campos `title`, `text` y `keywords`.

Tras ello, se inicializa `BERTopic` usando un Embedding llamado `all-MiniLM-L6-v2`(rápido, ligero y eficiente para este tipo de problemas) y con una configuración de HDBSCAN(usado para el clustering de los papers) y Umap(reducción de la dimensionalidad del Embedding) aceptable para el problema. A su vez, se usó un modelo de vectorización para eliminar las stopwords en inglés ya que son redundantes y aparecen en cantdidad, y configurar el uso de n-gramas de 1 o 2 palabras para mayor fiabilidad de pertenencia a los topics.

Tras entrenar el modelo con los textos de los documentos, se guarda en fichero  ``/assigment_2/step_3/outputs/topics/topics.json` con los topics encontrados por el modelo, con el nº de documentos pertenecientes a dicho topic, sus keywords, id y nombre establecido del topic (id + 4 primeras keywords)

Posteriormente, a partir de la información proporcionada por el modelo con el método `get_document_info(texts)`, se obtiene la pertenencia de los textos a los topics obtenidos, y con esa información se generan en el mismo directorio que `topics.json` los ficheros ``papers_report.txt` con un reporte visual de la pertenencia de los papers a los topics (usada para depurar y entender lo que devolvía el método) y `paper_topics.json`, su versión estructurada en json para enriquecer el KG con las relaciones de pertenencia a paper.

Por último, para generar las relaciones de similaridad entre papers, se reutilizan los mismos Embeddings generados con ``all-MiniLM-L6-v2``, ya que estos representan semánticamente cada paper en forma de vector. A partir de dichos vectores, se calcula la similitud coseno entre cada par de papers, obteniendo un score que indica cómo de similares son semánticamente entre sí (sólo se guardan los papers con scores superiores al 50%).

Con esta información se genera el fichero ``/assigment_2/step_3/outputs/topics/paper_similarities.json``, donde se guarda cada relación entre dos papers, indicando el paper origen, el paper destino, el score de similaridad, el topic asignado a cada uno y si ambos pertenecen al mismo topic. Este fichero será usado posteriormente para nutrir el KG con las relaciones isSimilar entre papers, usando el valor de similaridad como evidencia/peso de dicha relación.


## Replicación 
1. Se debe haber ejecutado el step_2 completo y tener el `HF_TOKEN` guardado en el .env de dicho step
2. ejecutar desde el directorio `/assigment_2/step_3/topic_modeling` el mandato `poetry run python ./scripts/topic_modeling.py`
3. *hacer script para enriquecer a partri de los outputs*



## DECLARACIÓN DE USO DE IA
Se usó IA generativa para :

- entender cómo funciona `BERTopic`, sus funciones y obtener una configuración óptima de HDBSCAN y UMAP. La configuraciónse ajustó al tamaño reducido del corpus, compuesto por 30 papers. En UMAP se empleó un número bajo de vecinos para capturar relaciones locales entre documentos, una distancia coseno adecuada para embeddings semánticos y una distancia mínima baja para favorecer la formación de grupos compactos. En HDBSCAN se redujo el tamaño mínimo de cluster y el número mínimo de muestras para permitir la detección de topics pequeños y evitar que demasiados documentos fueran clasificados como outliers. Esta configuración permite obtener una agrupación más flexible y adecuada para un conjunto documental reducido.

- En relación al topic modeling únicamente se usó para ayudar a entender y generar las similaridades entre papers.
