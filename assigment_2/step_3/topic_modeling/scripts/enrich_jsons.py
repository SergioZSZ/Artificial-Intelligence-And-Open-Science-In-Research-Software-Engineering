from pathlib import Path
import json
import shutil

from core import INPUT_DIR, OUTPUT_DIR


TOPICS_FILE = OUTPUT_DIR / "topics.json"
PAPER_TOPICS_FILE = OUTPUT_DIR / "paper_topics.json"
PAPER_SIMILARITIES_FILE = OUTPUT_DIR / "paper_similarities.json"

ENRICHED_DIR = OUTPUT_DIR / "enriched_jsons"


def main():
    # cargar jsons de topics
    with open(TOPICS_FILE, "r", encoding="utf-8") as f:
        topics = json.load(f)

    with open(PAPER_TOPICS_FILE, "r", encoding="utf-8") as f:
        paper_topics = json.load(f)["paper_topics"]

    with open(PAPER_SIMILARITIES_FILE, "r", encoding="utf-8") as f:
        paper_similarities = json.load(f)["paper_similarities"]

    # topic_id -> topic completo
    topics_by_id = {
        topic["topic_id"]: topic
        for topic in topics
    }

    # paper_id -> topic asignado
    paper_topics_by_id = {}

    for relation in paper_topics:
        paper_id = relation["paper_id"]
        topic_id = relation["topic_id"]

        topic = topics_by_id[topic_id]

        paper_topics_by_id[paper_id] = {
            "topic_id": topic_id,
            "name": relation["topic_name"],
            "probability": relation["probability"],
            "representative_document": relation["representative_document"],
            "keywords": topic["keywords"]
        }

    # paper_id -> papers similares
    similar_papers_by_id = {}

    for relation in paper_similarities:
        source_id = relation["source_paper_id"]
        target_id = relation["target_paper_id"]

        # relación source -> target
        similar_papers_by_id.setdefault(source_id, []).append({
            "paper_id": target_id,
            "similarity_score": relation["similarity_score"],
            "source_topic_id": relation["source_topic_id"],
            "target_topic_id": relation["target_topic_id"],
            "same_topic": relation["same_topic"]
        })

        # relación target -> source
        similar_papers_by_id.setdefault(target_id, []).append({
            "paper_id": source_id,
            "similarity_score": relation["similarity_score"],
            "source_topic_id": relation["target_topic_id"],
            "target_topic_id": relation["source_topic_id"],
            "same_topic": relation["same_topic"]
        })

    # crear carpeta de salida
    if ENRICHED_DIR.exists():
        shutil.rmtree(ENRICHED_DIR)

    ENRICHED_DIR.mkdir(parents=True, exist_ok=True)

    # enriquecer cada JSON
    for json_file in sorted(INPUT_DIR.glob("*.json")):
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        paper_id = data["paper"]["local_id"]

        # sustituye el [] de topics por el topic real
        data["topics"] = [
            paper_topics_by_id[paper_id]
        ]

        # añade una nueva clave con los papers similares
        data["similar_papers"] = similar_papers_by_id.get(paper_id, [])

        output_file = ENRICHED_DIR / json_file.name

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(
            f"{paper_id} enriquecido | "
            f"topics: {len(data['topics'])} | "
            f"similar_papers: {len(data['similar_papers'])}"
        )

    print(f"\nJSONs enriquecidos guardados en: {ENRICHED_DIR}")


if __name__ == "__main__":
    main()