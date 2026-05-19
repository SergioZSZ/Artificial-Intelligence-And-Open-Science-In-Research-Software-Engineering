from pathlib import Path
import json, os, shutil

from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import CountVectorizer
from hdbscan import HDBSCAN
from sklearn.metrics.pairwise import cosine_similarity
from umap import UMAP
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from core import OUTPUT_DIR, INPUT_DIR, ENV_PATH

load_dotenv(ENV_PATH)


'''
| Funcionalidad               | Qué te da                                                 | Uso en tu proyecto                          |
| --------------------------- | --------------------------------------------------------- | ------------------------------------------- |
| `fit_transform(docs)`       | Entrena el modelo y asigna un topic a cada documento      | Asignar temas a papers                      |
| `get_topic_info()`          | Tabla con topics, número de documentos y nombre del topic | Ver resumen de temas                        |
| `get_topic(topic_id)`       | Keywords principales de un topic                          | Crear instancia `Topic`                     |
| `get_document_info(docs)`   | Topic, probabilidad y metadatos por documento             | Crear relaciones Paper-Topic                |
| `visualize_documents()`     | Visualización de documentos agrupados                     | Ver qué papers se parecen                   |

'''

# obtiene la informacion de los papers necesaria para el topic modeling y trazabilidad
def get_data(dir):
    
    with open(dir, "r",encoding="utf-8") as f:
        data = json.load(f)
        paper = data["paper"]
        
        if paper is not None:
            id = paper["local_id"]
            title = paper["title"]
            process_text = f"{title} {paper['abstract']} {paper['keywords']}"
        
            response = {
                "id": id,
                "title":title,
                "text":process_text
            }

            return response
    return None



def get_bertopic():
    # 1º eliminacion de stopwords y realización de ngrams a partir de un modelo de vectorización
    vectorizer_model = CountVectorizer(
            stop_words="english",
            ngram_range=(1, 2)
        )
    
    # 2º configuracion de hbscan y umap y embeding 
    # embeding transforma a un vector los textos
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    
    # Umap reduce dimensionalidad de los embedings
    umap_model = UMAP(
        n_neighbors=5,
        n_components=2,
        min_dist=0.0,
        metric="cosine",
        random_state=42
    )

    # hdsbscan realiza el clustering de topics a partir de los embedings reducidos
    hdbscan_model = HDBSCAN(
        min_cluster_size=2,
        min_samples=1,
        metric="euclidean",
        cluster_selection_method="eom",
        prediction_data=True
    )

    bertopic = BERTopic(
        language="english",
        vectorizer_model=vectorizer_model,
        umap_model=umap_model,
        hdbscan_model=hdbscan_model
    )
    # 3º creacion de bertopic
    bertopic = BERTopic(language="english", vectorizer_model=vectorizer_model,
                        hdbscan_model=hdbscan_model, embedding_model=embedding_model,
                        umap_model=umap_model)

    return bertopic, embedding_model


# obtencion de topics
def get_topics(bertopic:BERTopic, topic_info):
    topics_json = []
    for topic_id in topic_info["Topic"].tolist():
        if topic_id == -1: #documentos sin outlier
            continue
        
        words = bertopic.get_topic(topic_id)
        # saca la columna de cada topic
        topic_row = topic_info[topic_info["Topic"] == topic_id].iloc[0]

        topic_data = {
            "topic_id": int(topic_id),
            "name": topic_row["Name"],
            "count": int(topic_row["Count"]),
            "keywords": [
                {
                    "word": word,
                    "score": float(score)
                }
                for word, score in words
            ]
        }

        topics_json.append(topic_data)
    return topics_json


# relacion paper_topic a partir de los scores sacados por bertopic asociados a cada paper
def paper_topic_link(document_info):
        #report
        report = OUTPUT_DIR/"papers_report.txt"

        

        with open(report, "w", encoding="utf-8") as f:
            f.write(document_info.to_string(index=False))
            
            # relacion paper-topic JSON
        paper_topics = []

        for _, row in document_info.iterrows():
            paper_topic = {
                "paper_id": row["paper_id"],
                "topic_id": int(row["Topic"]),
                "topic_name": row["Name"],
                "probability": float(row["Probability"]) if row["Probability"] is not None else None,
                "representative_document": bool(row["Representative_document"])
            }

            paper_topics.append(paper_topic)


        paper_topics_file = OUTPUT_DIR / "paper_topics.json"

        with open(paper_topics_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "paper_topics": paper_topics
                },
                f,
                indent=2,
                ensure_ascii=False
            )
        return paper_topics


#similaridades entre papers
def paper_similarities(embeddings, ids, assigned_topics, threshold=0.50):
    similarity_matrix = cosine_similarity(embeddings)

    paper_similarities_json = []

    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            similarity_score = float(similarity_matrix[i][j])

            if similarity_score >= threshold:
                paper_similarities_json.append({
                    "source_paper_id": ids[i],
                    "target_paper_id": ids[j],
                    "similarity_score": similarity_score,
                    "source_topic_id": int(assigned_topics[i]),
                    "target_topic_id": int(assigned_topics[j]),
                    "same_topic": bool(assigned_topics[i] == assigned_topics[j])
                })

    paper_similarities_file = OUTPUT_DIR / "paper_similarities.json"

    with open(paper_similarities_file, "w", encoding="utf-8") as f:
        json.dump(
            {
                "paper_similarities": paper_similarities_json
            },
            f,
            indent=2,
            ensure_ascii=False
        )






def main():
    
    topics = {}

    # truncado de output dir
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # extracción de textos e info para realizar topic modeling
    papers = sorted(INPUT_DIR.glob("*.json"))
    texts = []
    titles = []
    ids = []
    
    print("Papers encontrados:",len(papers))
    for paper in papers:
        data = get_data(paper)
        titles.append(data["title"])
        ids.append(data["id"])
        texts.append(data["text"])
        

    # entreno de bertopic
    
    bertopic, embedding_model = get_bertopic()
    embeddings = embedding_model.encode(
        texts,
        convert_to_numpy=True,
        show_progress_bar=True
)
    assigned_topics, probs = bertopic.fit_transform(texts, embeddings) 
        
    # obtencion de topics y guardado 
    topic_info = bertopic.get_topic_info()
    topics = get_topics(bertopic,topic_info)
    
    topics_file = OUTPUT_DIR / "topics.json"
    
    with open(topics_file,"w",encoding="utf-8") as f:
        json.dump(topics,f, indent=2)
        

    # relacion paper-topic json y report
    document_info = bertopic.get_document_info(texts)
    #limpieza del report
    document_info.insert(0, "paper_id", ids)
    document_info = document_info.drop(columns=["Document"])
    document_info = document_info.drop(columns=["Representation"])
    document_info = document_info.drop(columns=["Representative_Docs"])
    document_info = document_info.drop(columns=["Top_n_words"])

    
    paper_topic_link(document_info)

# similaridad de papers usando el mismo embbeding que bertopic

    paper_similarities(embeddings, ids, assigned_topics)
    
if __name__ == "__main__":
    main()
    