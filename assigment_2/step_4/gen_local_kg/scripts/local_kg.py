from core import ROOT_PATH, INPUT_DIR, OUTPUT_DIR, OUTPUT_FILE, BASE, SCHEMA, ONTOLOGY_FILE
import json, re
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF, RDFS, XSD, FOAF, DCTERMS, DC


# =========================
# AUXILIARES
# =========================

def slugify(text: str) -> str:
    text = str(text).lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"\s+", "_", text)
    return text


def normalized_name(text: str | None) -> str:
    if not text:
        return ""

    return slugify(text)


def obtain_json_files():
    return list(INPUT_DIR.glob("*.json"))


def remove_same_as_triples(g: Graph):
    """
    Elimina schema:sameAs del KG generado.

    Lo hacemos porque, aunque el script no genere sameAs,
    si la ontología todavía contiene esa propiedad, al parsearla
    aparecería igualmente en la salida final.
    """

    same_as = SCHEMA.sameAs

    for triple in list(g.triples((same_as, None, None))):
        g.remove(triple)

    for triple in list(g.triples((None, same_as, None))):
        g.remove(triple)

    for triple in list(g.triples((None, None, same_as))):
        g.remove(triple)


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

    remove_same_as_triples(g)

    return g


def get_value_from_string_or_dict(data, key: str = "name"):
    """
    Permite leer datos que puedan venir como string o como dict.

    Ejemplo:
    "United States"

    o:

    {
      "name": "United States",
      "identifier": "Q30"
    }
    """

    if isinstance(data, str):
        return data

    if isinstance(data, dict):
        return data.get(key)

    return None


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


def country_uri(name: str = None, identifier: str = None) -> URIRef:
    """
    Si tenemos identificador externo tipo Wikidata Q30,
    lo usamos para que la URI local sea más estable.
    """

    value = identifier if identifier else name
    return BASE[f"country_{slugify(value)}"]


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


def add_person(g: Graph, person_data: dict) -> URIRef | None:
    name = person_data.get("name")

    if not name:
        return None

    person = person_uri(name)

    g.add((person, RDF.type, FOAF.Person))
    g.add((person, SCHEMA.name, Literal(name)))

    identifier = person_data.get("identifier")

    if identifier:
        g.add((person, SCHEMA.identifier, Literal(identifier)))

    return person


def add_organization(
    g: Graph,
    name: str,
    identifier: str = None,
    description: str = None
) -> URIRef | None:
    if not name:
        return None

    org = organization_uri(name)

    g.add((org, RDF.type, SCHEMA.Organization))
    g.add((org, SCHEMA.name, Literal(name)))

    if identifier:
        g.add((org, SCHEMA.identifier, Literal(identifier)))

    if description:
        g.add((org, SCHEMA.description, Literal(description)))

    return org


def add_project(g: Graph, project_data: dict) -> URIRef | None:
    """
    Crea un proyecto.

    En los JSON enriquecidos normalmente viene:
    {
      "identifier": "IIS-2229876",
      "type": "acknowledged_project"
    }

    Como no siempre hay name, usamos identifier como nombre local.
    """

    identifier = project_data.get("identifier")
    name = project_data.get("name") or identifier

    if not name:
        return None

    project = project_uri(name)

    g.add((project, RDF.type, SCHEMA.Project))
    g.add((project, SCHEMA.name, Literal(name)))

    if identifier:
        g.add((project, SCHEMA.identifier, Literal(identifier)))

    description = project_data.get("description")
    start_date = project_data.get("start_date")
    end_date = project_data.get("end_date")
    funding_amount = project_data.get("funding_amount")
    currency = project_data.get("currency")

    if description:
        g.add((project, SCHEMA.description, Literal(description)))

    if start_date:
        g.add((project, SCHEMA.startDate, Literal(start_date, datatype=XSD.date)))

    if end_date:
        g.add((project, SCHEMA.endDate, Literal(end_date, datatype=XSD.date)))

    if funding_amount not in (None, ""):
        g.add((project, BASE.fundingAmount, Literal(float(funding_amount), datatype=XSD.decimal)))

    if currency:
        g.add((project, SCHEMA.currency, Literal(currency)))

    return project


def add_country(g: Graph, country_data) -> URIRef | None:
    """
    Crea país a partir de dict o string.

    Dict esperado:
    {
      "name": "United States",
      "identifier": "Q30"
    }
    """

    if isinstance(country_data, str):
        name = country_data
        identifier = None

    elif isinstance(country_data, dict):
        name = country_data.get("name")
        identifier = country_data.get("identifier")

    else:
        return None

    if not name:
        return None

    country = country_uri(name=name, identifier=identifier)

    g.add((country, RDF.type, SCHEMA.Country))
    g.add((country, SCHEMA.name, Literal(name)))

    if identifier:
        g.add((country, SCHEMA.identifier, Literal(identifier)))

    return country


def add_topic(g: Graph, topic_data: dict) -> URIRef:
    topic_id = topic_data["topic_id"]
    topic = topic_uri(topic_id)

    keywords = topic_data.get("keywords", [])
    keywords_text = ", ".join([kw["word"] for kw in keywords if kw.get("word")])

    g.add((topic, RDF.type, BASE.Topic))

    if topic_data.get("name"):
        g.add((topic, SCHEMA.name, Literal(topic_data["name"])))

    if keywords_text:
        g.add((topic, SCHEMA.keywords, Literal(keywords_text)))

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


def link_person_affiliation(g: Graph, person: URIRef, organization: URIRef):
    g.add((person, SCHEMA.affiliation, organization))


def link_acknowledged_entity(g: Graph, paper: URIRef, entity: URIRef):
    g.add((paper, BASE.acknowledges, entity))


def link_paper_project(g: Graph, paper: URIRef, project: URIRef):
    g.add((paper, BASE.fundedByProject, project))


def link_project_funder(g: Graph, project: URIRef, org: URIRef):
    g.add((project, SCHEMA.funder, org))


def link_organization_country(g: Graph, org: URIRef, country: URIRef):
    g.add((org, SCHEMA.location, country))


def infer_project_funders(
    project_data: dict,
    projects_count: int,
    org_by_name: dict[str, URIRef],
) -> list[URIRef]:
    """
    Evita enlazar todos los proyectos con todas las organizaciones del paper.

    - Si el proyecto trae `funder`, esa fuente manda sobre la inferencia.
    - Sin funder explicito, una sola organizacion puede aplicarse a varios grants.
    - Sin funder explicito, un solo proyecto puede recibir las organizaciones del paper.
    - Varios proyectos y varias organizaciones no se enlazan all-to-all.
    """
    explicit_funder = project_data.get("funder")

    if explicit_funder:
        normalized_funder = normalized_name(explicit_funder)

        for org_name, org in org_by_name.items():
            if normalized_name(org_name) == normalized_funder:
                return [org]

        return []

    if len(org_by_name) == 1:
        return list(org_by_name.values())

    if projects_count == 1:
        return list(org_by_name.values())

    return []


def add_paper_topic_similarity(g: Graph, paper: URIRef, paper_id: str, topic_data: dict):
    topic_id = topic_data["topic_id"]

    topic = add_topic(g, topic_data)

    relation = paper_topic_similarity_uri(paper_id, topic_id)

    probability = topic_data.get("probability")

    g.add((relation, RDF.type, BASE.PaperTopicSimilarity))
    g.add((relation, BASE.paper, paper))
    g.add((relation, BASE.topic, topic))
    g.add((relation, BASE.algorihtm, Literal("BERTopic")))

    if probability is not None:
        g.add((relation, BASE.score, Literal(float(probability), datatype=XSD.float)))


def add_paper_similarity(g: Graph, source_paper_id: str, similarity_data: dict):
    target_paper_id = similarity_data.get("paper_id")

    if not target_paper_id:
        return

    paper_a, paper_b = sorted([source_paper_id, target_paper_id])

    relation = paper_similarity_uri(paper_a, paper_b)

    g.add((relation, RDF.type, BASE.PaperSimilarity))
    g.add((relation, BASE.paper1, paper_uri(paper_a)))
    g.add((relation, BASE.paper2, paper_uri(paper_b)))

    similarity_score = similarity_data.get("similarity_score")

    if similarity_score is not None:
        g.add((relation, BASE.score, Literal(float(similarity_score), datatype=XSD.float)))

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
        # Países
        # -----------------------------
        countries = data.get("countries", [])
        country_by_name = {}

        for country_data in countries:
            country = add_country(g, country_data)
            country_name = get_value_from_string_or_dict(country_data, "name")

            if country and country_name:
                country_by_name[country_name] = country

        # -----------------------------
        # Personas
        # -----------------------------
        people = data.get("people", [])

        for person_data in people:
            person = add_person(g, person_data)

            if not person:
                continue

            person_type = person_data.get("type")

            if person_type == "author":
                link_paper_author(g, paper, person)

            elif person_type == "acknowledged_person":
                link_acknowledged_entity(g, paper, person)

            # Afiliación del autor/persona
            affiliation = person_data.get("affiliation")

            if affiliation:
                affiliation_name = get_value_from_string_or_dict(affiliation, "name")

                if affiliation_name:
                    affiliation_org = add_organization(g, affiliation_name)
                    link_person_affiliation(g, person, affiliation_org)

        # -----------------------------
        # Organizaciones
        # -----------------------------
        organizations = data.get("organizations", [])
        acknowledged_organizations = []
        org_by_name = {}

        for org_data in organizations:
            org_name = org_data.get("name")

            if not org_name:
                continue

            org = add_organization(
                g,
                name=org_name,
                identifier=org_data.get("identifier"),
                description=org_data.get("description")
            )

            if not org:
                continue

            acknowledged_organizations.append(org)
            org_by_name[org_name] = org
            link_acknowledged_entity(g, paper, org)

            # País de la organización
            country_name = org_data.get("country")

            if country_name:
                country = country_by_name.get(country_name)

                if not country:
                    country = add_country(g, {"name": country_name})
                    country_by_name[country_name] = country

                if country:
                    link_organization_country(g, org, country)

        # -----------------------------
        # Proyectos
        # -----------------------------
        projects = data.get("projects", [])
        projects_count = len(projects)

        for project_data in projects:
            project = add_project(g, project_data)

            if not project:
                continue

            link_paper_project(g, paper, project)
            link_acknowledged_entity(g, paper, project)

            # Preferimos el funder explicito del proyecto. Cuando no existe,
            # solo inferimos relaciones en casos simples para evitar all-to-all.
            explicit_funder = project_data.get("funder")

            if explicit_funder:
                explicit_funder_org = add_organization(g, explicit_funder)

                if explicit_funder_org:
                    link_project_funder(g, project, explicit_funder_org)

                continue

            for org in infer_project_funders(project_data, projects_count, org_by_name):
                link_project_funder(g, project, org)

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
