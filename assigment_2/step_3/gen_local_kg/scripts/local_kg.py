from core import ROOT_PATH, INPUT_DIR, OUTPUT_DIR, OUTPUT_FILE, BASE, SCHEMA, ONTOLOGY_FILE
import json, re
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF, RDFS, XSD, FOAF, DCTERMS, DC


# =========================
# AUXILIARES
# =========================

def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"\s+", "_", text)
    return text


def obtain_json_files():
    return list(INPUT_DIR.glob("*.json"))


def create_graph(ontology_file):
    g = Graph()

    g.parse(ontology_file, format="turtle")

    g.bind("g4", BASE)
    g.bind("schema", SCHEMA)
    g.bind("foaf", FOAF)
    g.bind("dc", DC)
    g.bind("xsd", XSD)
    g.bind("dcterms", DCTERMS)
    g.bind("rdfs", RDFS)

    return g


# =========================
# URIS
# =========================

def paper_uri(paper_id: str) -> URIRef:
    return BASE[paper_id]


def person_uri(name: str) -> URIRef:
    return BASE[f"person_{slugify(name)}"]


def organization_uri(name: str) -> URIRef:
    return BASE[f"org_{slugify(name)}"]


def project_uri(name: str) -> URIRef:
    return BASE[f"project_{slugify(name)}"]


def topic_uri(topic_id: int) -> URIRef:
    return BASE[f"topic_{topic_id}"]


def paper_topic_similarity_uri(paper_id: str, topic_id: int) -> URIRef:
    return BASE[f"paper_topic_similarity_{paper_id}_topic_{topic_id}"]


def paper_similarity_uri(paper_id_1: str, paper_id_2: str) -> URIRef:
    paper_a, paper_b = sorted([paper_id_1, paper_id_2])
    return BASE[f"paper_similarity_{paper_a}_{paper_b}"]


# =========================
# INSTANCIAS
# =========================

def add_paper(g: Graph, paper_id: str, paper_data: dict) -> URIRef:
    paper = paper_uri(paper_id)

    g.add((paper, RDF.type, BASE.Paper))

    title = paper_data.get("title")
    abstract = paper_data.get("abstract")
    date = paper_data.get("published_date")
    doi = paper_data.get("doi")

    if title:
        g.add((paper, DC.title, Literal(title)))

    if date:
        g.add((paper, DC.date, Literal(date)))

    if abstract:
        g.add((paper, SCHEMA.abstract, Literal(abstract)))

    if doi:
        g.add((paper, SCHEMA.identifier, Literal(doi)))

    return paper


def add_person(g: Graph, name: str) -> URIRef:
    person = person_uri(name)

    g.add((person, RDF.type, FOAF.Person))
    g.add((person, SCHEMA.name, Literal(name)))

    return person


def add_organization(g: Graph, name: str) -> URIRef:
    org = organization_uri(name)

    g.add((org, RDF.type, SCHEMA.Organization))
    g.add((org, SCHEMA.name, Literal(name)))

    return org


def add_project(g: Graph, name: str) -> URIRef:
    project = project_uri(name)

    g.add((project, RDF.type, SCHEMA.Project))
    g.add((project, SCHEMA.name, Literal(name)))

    return project


def add_topic(g: Graph, topic_data: dict) -> URIRef:
    topic_id = topic_data["topic_id"]
    topic = topic_uri(topic_id)

    keywords = topic_data["keywords"]
    keywords_text = ", ".join([kw["word"] for kw in keywords])

    g.add((topic, RDF.type, BASE.Topic))
    g.add((topic, SCHEMA.name, Literal(topic_data["name"])))
    g.add((topic, SCHEMA.keywords, Literal(keywords_text)))

    # Guardamos los keywords con sus scores como string JSON
    g.add((
        topic,
        BASE.keywordVector,
        Literal(json.dumps(keywords, ensure_ascii=False))
    ))

    return topic


# =========================
# RELACIONES
# =========================

def link_paper_author(g: Graph, paper: URIRef, person: URIRef):
    g.add((paper, SCHEMA.author, person))


def link_acknowledged_entity(g: Graph, paper: URIRef, entity: URIRef):
    g.add((paper, BASE.acknowledges, entity))


def link_paper_project(g: Graph, paper: URIRef, project: URIRef):
    g.add((paper, BASE.fundedByProject, project))


def link_project_funder(g: Graph, project: URIRef, org: URIRef):
    g.add((project, SCHEMA.funder, org))


def add_paper_topic_similarity(g: Graph, paper: URIRef, paper_id: str, topic_data: dict):
    topic_id = topic_data["topic_id"]

    topic = add_topic(g, topic_data)

    relation = paper_topic_similarity_uri(paper_id, topic_id)

    g.add((relation, RDF.type, BASE.PaperTopicSimilarity))
    g.add((relation, BASE.paper, paper))
    g.add((relation, BASE.topic, topic))
    g.add((relation, BASE.score, Literal(float(topic_data["probability"]), datatype=XSD.float)))
    g.add((relation, BASE.algorihtm, Literal("BERTopic")))


def add_paper_similarity(g: Graph, source_paper_id: str, similarity_data: dict):
    target_paper_id = similarity_data["paper_id"]

    paper_a, paper_b = sorted([source_paper_id, target_paper_id])

    relation = paper_similarity_uri(paper_a, paper_b)

    g.add((relation, RDF.type, BASE.PaperSimilarity))
    g.add((relation, BASE.paper1, paper_uri(paper_a)))
    g.add((relation, BASE.paper2, paper_uri(paper_b)))
    g.add((relation, BASE.score, Literal(float(similarity_data["similarity_score"]), datatype=XSD.float)))
    g.add((relation, BASE.algorihtm, Literal("all-MiniLM-L6-v2 + cosine_similarity")))


# =========================
# CREACIÓN DEL KG
# =========================

def build_kg_from_jsons(json_files):
    g = create_graph(ONTOLOGY_FILE)

    for json_file in json_files:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        paper_data = data["paper"]

        paper_id = paper_data.get("local_id", json_file.stem)

        # -----------------------------
        # Paper
        # -----------------------------
        paper = add_paper(g, paper_id, paper_data)

        # -----------------------------
        # Personas
        # -----------------------------
        people = data.get("people", [])

        for person_data in people:
            name = person_data.get("name")

            if person_data.get("type") == "author":
                if name:
                    person = add_person(g, name)
                    link_paper_author(g, paper, person)

            elif person_data.get("type") == "acknowledged_person":
                if name:
                    person = add_person(g, name)
                    link_acknowledged_entity(g, paper, person)

        # -----------------------------
        # Organizaciones
        # -----------------------------
        organizations = data.get("organizations", [])

        for org_data in organizations:
            org_name = org_data.get("name")

            if org_name:
                org = add_organization(g, org_name)
                link_acknowledged_entity(g, paper, org)

        # -----------------------------
        # Proyectos
        # -----------------------------
        projects = data.get("projects", [])

        for project_data in projects:
            project_identifier = project_data.get("identifier")

            if project_identifier:
                project = add_project(g, project_identifier)

                link_paper_project(g, paper, project)
                link_acknowledged_entity(g, paper, project)

                g.add((project, SCHEMA.identifier, Literal(project_identifier)))

        # -----------------------------
        # Topics del paper
        # -----------------------------
        topics = data.get("topics", [])

        for topic_data in topics:
            add_paper_topic_similarity(g, paper, paper_id, topic_data)

        # -----------------------------
        # Papers similares
        # -----------------------------
        similar_papers = data.get("similar_papers", [])

        for similarity_data in similar_papers:
            add_paper_similarity(g, paper_id, similarity_data)

    return g


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if not ONTOLOGY_FILE.exists():
        raise FileNotFoundError(f"No se encontró la ontología: {ONTOLOGY_FILE}")

    if not INPUT_DIR.exists():
        raise FileNotFoundError(f"No se encontró el directorio de entrada: {INPUT_DIR}")

    json_files = obtain_json_files()

    print(f"JSONs encontrados: {len(json_files)}")

    g = build_kg_from_jsons(json_files)

    g.serialize(destination=OUTPUT_FILE, format="turtle")

    print(f"KG generado correctamente en: {OUTPUT_FILE}")
    print(f"Número total de triples: {len(g)}")


if __name__ == "__main__":
    main()