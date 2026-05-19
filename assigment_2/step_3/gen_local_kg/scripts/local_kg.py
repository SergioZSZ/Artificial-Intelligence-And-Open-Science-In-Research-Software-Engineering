from core import ROOT_PATH, INPUT_DIR,OUTPUT_DIR,OUTPUT_FILE, BASE, SCHEMA, ONTOLOGY_FILE
import json, re
from rdflib import Namespace,Graph , URIRef, Literal
from rdflib.namespace import RDF, RDFS, XSD, FOAF, DCTERMS, DC

#funciones auxiliares
## normalizació nde texto
def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"\s+", "_", text)
    return text



##obtencion de datos del todos los json
def obtain_json_files():
    return list(INPUT_DIR.glob("*.json"))


##creacion/inicializacion del grafo + añadir sus namespaces

def create_graph(ontology_file):
    g = Graph()

    # Cargar la ontología
    g.parse(ontology_file, format="turtle")

    # Reforzar prefijos para que el TTL salga legible
    g.bind("g4", BASE)
    g.bind("schema", SCHEMA)
    g.bind("foaf", FOAF)
    g.bind("dc", DC)
    g.bind("xsd",XSD)
    g.bind("dcterms",DCTERMS)
    g.bind("rdfs",RDFS)
    
    return g


## funciones para creacion de las uris del KG de las instancias del json
def paper_uri(paper_id: str) -> URIRef:
    return BASE[paper_id]


def person_uri(name: str) -> URIRef:
    return BASE[f"person_{slugify(name)}"]


def organization_uri(name: str) -> URIRef:
    return BASE[f"org_{slugify(name)}"]


def project_uri(name: str) -> URIRef:
    return BASE[f"project_{slugify(name)}"]


## funciones para añadir cada instancia de los jsons
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

    # ver si añadir aqui o posteriormente al obtener los datos de otros kgs
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


## relaciones 
def link_paper_author(g: Graph, paper: URIRef, person: URIRef):
    g.add((paper, SCHEMA.author, person))


def link_acknowledged_entity(g: Graph, paper: URIRef, entity: URIRef):
    g.add((paper, BASE.acknowledges, entity))


def link_paper_project(g: Graph, paper: URIRef, project: URIRef):
    g.add((paper, BASE.fundedByProject, project))


def link_project_funder(g: Graph, project: URIRef, org: URIRef):
    g.add((project, SCHEMA.funder, org))



##creacion del kg
def build_kg_from_jsons(json_files):
    g = create_graph(ONTOLOGY_FILE)

    for json_file in json_files:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        paper_data = data["paper"]

        # Usamos el local_id del JSON como identificador del paper
        paper_id = paper_data.get("local_id", json_file.stem)

        # Crear instancia del paper
        paper = add_paper(g, paper_id, paper_data)

        # -----------------------------
        # personas del paper
        # -----------------------------
        people = data.get("people", [])

        for person_data in people:
            if person_data.get("type") == "author":
                name = person_data.get("name")

                if name:
                    person = add_person(g, name)
                    link_paper_author(g, paper, person)
            
            elif person_data.get("type") == "acknowledged_person":
                link_acknowledged_entity(g, paper, person)


        # -----------------------------
        # Organizaciones reconocidas en acknowledgements
        # -----------------------------
        organizations = data.get("organizations", [])

        for org_data in organizations:
            org_name = org_data.get("name")

            if org_name:
                org = add_organization(g, org_name)

                #organizaciones/proyectos/personas reconocidas
                link_acknowledged_entity(g, paper, org)

        # -----------------------------
        # Proyectos reconocidos en acknowledgements
        # -----------------------------
        projects = data.get("projects", [])

        for project_data in projects:
            project_identifier = project_data.get("identifier")

            if project_identifier:
                project = add_project(g, project_identifier)

                # Relación específica paper -> proyecto
                link_paper_project(g, paper, project)

                # También queda registrado como entidad acknowledged
                link_acknowledged_entity(g, paper, project)

                # Guardamos el identificador del proyecto
                g.add((project, SCHEMA.identifier, Literal(project_identifier)))

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