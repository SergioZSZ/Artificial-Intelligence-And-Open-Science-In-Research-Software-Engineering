"""Generate the RO-Crate metadata for RFKG + PipeGrobid.

The crate is intentionally metadata-first: it describes the project, the
software components, the workflow and the main datasets without copying large
runtime outputs such as PDFs, XMLs or enriched JSON files.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REPO_URL = "https://github.com/SergioZSZ/OS-IA-Pipegrobid"
READTHEDOCS_URL = "https://pipegrobid-software.readthedocs.io/es/latest/"
LICENSE_URL = "https://www.apache.org/licenses/LICENSE-2.0"
DOI_URL = "https://doi.org/10.5281/zenodo.18647861"
CRATE_DIR = Path("pipegrobid_RFKG")
CRATE_METADATA = CRATE_DIR / "ro-crate-metadata.json"
CRATE_README = CRATE_DIR / "README.md"


def repo_path(path: str) -> str:
    """Return the path as seen from the generated crate directory."""
    return f"../{path}"


def github_url(path: str) -> str:
    return f"{REPO_URL}/blob/main/{path}"


def context_entity(entity_id: str, entity_type: str | list[str], **properties: Any) -> dict[str, Any]:
    entity = {"@id": entity_id, "@type": entity_type}
    entity.update(properties)
    return entity


def reference(entity_id: str) -> dict[str, str]:
    return {"@id": entity_id}


def load_codemeta() -> dict[str, Any]:
    with Path("codemeta.json").open(encoding="utf-8") as file:
        return json.load(file)


def person_entities(codemeta: dict[str, Any]) -> list[dict[str, Any]]:
    people = []
    orcid_by_name = {
        "Sergio Zaballos Herrera": "https://orcid.org/0009-0000-3795-2767",
    }

    for author in codemeta.get("author", []):
        name_parts = [author.get("givenName", ""), author.get("familyName", "")]
        name = " ".join(part for part in name_parts if part).strip()
        if not name:
            continue

        fallback_id = f"#{name.replace(' ', '-').lower()}"
        person_id = orcid_by_name.get(name, author.get("@id", fallback_id))
        properties = {
            "name": name,
            "email": author.get("email"),
            "affiliation": author.get("affiliation"),
        }
        people.append(
            context_entity(
                person_id,
                "Person",
                **{key: value for key, value in properties.items() if value},
            )
        )

    return people


def file_entity(path: str, name: str, description: str, encoding_format: str) -> dict[str, Any]:
    return context_entity(
        repo_path(path),
        "File",
        name=name,
        description=description,
        encodingFormat=encoding_format,
        contentUrl=github_url(path),
    )


def dataset_entity(path: str, name: str, description: str, **properties: Any) -> dict[str, Any]:
    entity = context_entity(
        repo_path(path),
        "Dataset",
        name=name,
        description=description,
        contentUrl=github_url(path.rstrip("/")),
    )
    entity.update(properties)
    return entity


def software_entity(entity_id: str, name: str, description: str, path: str, **properties: Any) -> dict[str, Any]:
    entity = context_entity(
        entity_id,
        "SoftwareSourceCode",
        name=name,
        description=description,
        programmingLanguage="Python",
        codeRepository=reference(REPO_URL),
        contentUrl=github_url(path),
        license=reference(LICENSE_URL),
    )
    entity.update(properties)
    return entity


def action_entity(entity_id: str, name: str, description: str, **properties: Any) -> dict[str, Any]:
    entity = context_entity(
        entity_id,
        "Action",
        name=name,
        description=description,
    )
    entity.update(properties)
    return entity


def build_crate() -> dict[str, Any]:
    codemeta = load_codemeta()
    authors = person_entities(codemeta)
    author_refs = [reference(author["@id"]) for author in authors]

    root = context_entity(
        "./",
        "Dataset",
        name="Research Funding Knowledge Graph (RFKG) + PipeGrobid",
        description=(
            "Research Object for RFKG + PipeGrobid. RFKG is an application for "
            "analysing scientific funding through a Knowledge Graph, and "
            "PipeGrobid is the document-processing pipeline that transforms PDFs "
            "into TEI XML and initial extraction outputs used by the semantic phase."
        ),
        license=reference(LICENSE_URL),
        identifier=DOI_URL,
        url=reference(REPO_URL),
        datePublished="2026-05-25",
        keywords=[
            "research funding",
            "knowledge graph",
            "SPARQL",
            "Fuseki",
            "Streamlit",
            "GROBID",
            "TEI XML",
            "n8n",
            "FastAPI",
            "open science",
        ],
        author=author_refs,
        creator=author_refs,
        mainEntity=reference("#rfkg-application"),
        mentions=[
            reference("#pipegrobid-software"),
            reference("#local-kg"),
            reference("#n8n-workflow"),
            reference("#research-api"),
            reference("#research-frontend"),
        ],
        hasPart=[
            reference("#rfkg-application"),
            reference("#pipegrobid-software"),
            reference("#local-kg"),
            reference("#research-api"),
            reference("#research-frontend"),
            reference("#n8n-workflow"),
        ],
        subjectOf=[
            reference(repo_path("README.md")),
            reference(repo_path("app.md")),
            reference(READTHEDOCS_URL),
        ],
    )

    metadata_descriptor = context_entity(
        "ro-crate-metadata.json",
        "CreativeWork",
        about=reference("./"),
        conformsTo=reference("https://w3id.org/ro/crate/1.1"),
    )

    rfkg_application = context_entity(
        "#rfkg-application",
        ["SoftwareApplication", "CreativeWork"],
        name="Research Funding Knowledge Graph (RFKG)",
        description=(
            "Application for exploring scientific funding evidence from papers "
            "through a RDF Knowledge Graph, Fuseki, a FastAPI backend and a "
            "Streamlit frontend."
        ),
        applicationCategory="Research software",
        operatingSystem="Cross-platform",
        isBasedOn=[
            reference("#pipegrobid-software"),
            reference("#local-kg"),
            reference("#n8n-workflow"),
        ],
        softwareRequirements=[
            reference("#research-api"),
            reference("#research-frontend"),
            reference("#fuseki-service"),
            reference("#n8n-service"),
        ],
        subjectOf=[
            reference(repo_path("app.md")),
            reference(repo_path("docs/fase_2/index.md")),
            reference(repo_path("containers/research_api/API_RESEARCH_API.md")),
            reference(repo_path("containers/research_frontend/README.md")),
        ],
    )

    pipegrobid = software_entity(
        "#pipegrobid-software",
        "PipeGrobid",
        (
            "Python pipeline that uses GROBID to transform scientific PDFs into "
            "TEI XML and generate initial extraction outputs."
        ),
        "src/pipegrobid/",
        softwareVersion=codemeta.get("version", "1.4.0"),
        softwareRequirements=reference("#grobid-software"),
        runtimePlatform="Python and Docker",
        subjectOf=[
            reference(repo_path("README.md")),
            reference(repo_path("docs/index.md")),
            reference(repo_path("codemeta.json")),
            reference(repo_path("CITATION.cff")),
        ],
    )

    research_api = software_entity(
        "#research-api",
        "research_api",
        (
            "FastAPI backend that queries the RDF Knowledge Graph in Fuseki with "
            "SPARQL and exposes domain endpoints for RFKG."
        ),
        "containers/research_api/app/",
        softwareRequirements=reference("#fuseki-service"),
        subjectOf=reference(repo_path("containers/research_api/API_RESEARCH_API.md")),
    )

    research_frontend = software_entity(
        "#research-frontend",
        "research_frontend",
        (
            "Streamlit frontend for exploring funding countries, organizations, "
            "papers, projects, topics, acknowledgements, ORCID data and paper similarities."
        ),
        "containers/research_frontend/",
        softwareRequirements=reference("#research-api"),
        subjectOf=reference(repo_path("containers/research_frontend/README.md")),
    )

    local_kg = context_entity(
        "#local-kg",
        "Dataset",
        name="Local RFKG RDF Knowledge Graph",
        description=(
            "RDF/Turtle Knowledge Graph generated from processed papers, enriched "
            "entities, projects, topics and similarity data."
        ),
        encodingFormat="text/turtle",
        contentUrl=repo_path("assigment_2/step_4/outputs/local_kg.ttl"),
        isBasedOn=[
            reference(repo_path("xmls/")),
            reference(repo_path("assigment_2/step_1/")),
            reference(repo_path("assigment_2/step_2/")),
            reference(repo_path("assigment_2/step_3/")),
            reference(repo_path("assigment_2/step_4/")),
        ],
    )

    graph = [
        metadata_descriptor,
        root,
        *authors,
        context_entity(
            READTHEDOCS_URL,
            "CreativeWork",
            name="ReadTheDocs documentation",
            description="Published documentation for RFKG + PipeGrobid.",
        ),
        context_entity(REPO_URL, "CreativeWork", name="Project source repository", url=REPO_URL),
        context_entity(LICENSE_URL, "CreativeWork", name="Apache License 2.0", url=LICENSE_URL),
        context_entity(
            "https://w3id.org/ro/crate/1.1",
            "CreativeWork",
            name="RO-Crate 1.1 specification",
        ),
        rfkg_application,
        pipegrobid,
        research_api,
        research_frontend,
        context_entity(
            "#grobid-software",
            "SoftwareApplication",
            name="GROBID",
            description="Software for converting scientific PDFs into structured TEI XML.",
            url="https://github.com/kermitt2/grobid",
        ),
        context_entity(
            "#fuseki-service",
            "SoftwareApplication",
            name="Apache Jena Fuseki",
            description="SPARQL server used to publish and query the RFKG RDF dataset.",
            url="https://jena.apache.org/documentation/fuseki2/",
        ),
        context_entity(
            "#n8n-service",
            "SoftwareApplication",
            name="n8n",
            description="Workflow automation service used to orchestrate the RFKG pipeline.",
            url="https://n8n.io/",
        ),
        context_entity(
            "#streamlit-framework",
            "SoftwareApplication",
            name="Streamlit",
            description="Python framework used by the RFKG frontend.",
            url="https://streamlit.io/",
        ),
        context_entity(
            "#fastapi-framework",
            "SoftwareApplication",
            name="FastAPI",
            description="Python framework used by research_api.",
            url="https://fastapi.tiangolo.com/",
        ),
        file_entity("README.md", "Project README", "Main project overview and execution guide.", "text/markdown"),
        file_entity("app.md", "RFKG application guide", "Operational guide for the full RFKG application.", "text/markdown"),
        file_entity("docs/index.md", "ReadTheDocs index", "Documentation entry point for RFKG + PipeGrobid.", "text/markdown"),
        file_entity("docs/fase_2/index.md", "RFKG documentation index", "ReadTheDocs entry point for FASE 2.", "text/markdown"),
        file_entity("codemeta.json", "CodeMeta metadata", "Structured software metadata.", "application/json"),
        file_entity("CITATION.cff", "Citation metadata", "Citation information for the project.", "text/plain"),
        file_entity("LICENSE", "License file", "Apache 2.0 license text.", "text/plain"),
        file_entity("Dockerfile", "PipeGrobid Dockerfile", "Container definition for the FASE 1 pipeline.", "text/plain"),
        file_entity("docker-compose.yml", "Root Docker Compose file", "Compose file for the root PipeGrobid pipeline.", "text/yaml"),
        file_entity(
            "containers/docker-compose.yml",
            "RFKG Docker Compose file",
            "Main stack for RFKG, n8n, GROBID, Fuseki, API and frontend.",
            "text/yaml",
        ),
        file_entity(
            "containers/workflow/pipegrobid_workflow.json",
            "n8n RFKG workflow",
            "Workflow that orchestrates extraction, enrichment, KG generation and Fuseki loading.",
            "application/json",
        ),
        dataset_entity("src/pipegrobid/", "PipeGrobid source code", "Python source code for the document-processing pipeline."),
        dataset_entity("test/", "PipeGrobid tests", "Pytest test suite for the document-processing pipeline."),
        dataset_entity("pdfs/", "Input PDFs", "Directory where scientific PDFs are placed before running the pipeline."),
        dataset_entity("xmls/", "Generated TEI XML files", "TEI XML files generated from PDFs with GROBID and PipeGrobid."),
        dataset_entity("generated_files/", "PipeGrobid generated files", "Initial visual and text outputs generated by PipeGrobid."),
        dataset_entity("assigment_2/step_1/", "Step 1 ontology and use case", "Use case, sources and ontology for RFKG."),
        dataset_entity("assigment_2/step_2/", "Step 2 XML and NER", "XML parsing and NER extraction/evaluation for acknowledgements and entities."),
        dataset_entity("assigment_2/step_3/", "Step 3 topics and similarities", "Topic modeling and paper similarity generation."),
        dataset_entity("assigment_2/step_4/", "Step 4 enrichment and local KG", "Online enrichment and local RDF Knowledge Graph generation."),
        dataset_entity("assigment_2/step_4/outputs/", "Generated KG outputs", "Generated outputs for the local KG phase, referenced as a collection."),
        local_kg,
        action_entity(
            "#phase-1-pipegrobid-execution",
            "PipeGrobid PDF to TEI XML execution",
            "Runs PipeGrobid with GROBID to transform input PDFs into TEI XML and generated files.",
            instrument=reference("#pipegrobid-software"),
            object=reference(repo_path("pdfs/")),
            result=[reference(repo_path("xmls/")), reference(repo_path("generated_files/"))],
            isBasedOn=[reference(repo_path("Dockerfile")), reference(repo_path("docker-compose.yml"))],
        ),
        action_entity(
            "#n8n-workflow",
            "RFKG workflow execution",
            (
                "Runs the FASE 2 workflow: XML preparation, NER, topic modeling, "
                "online enrichment, local KG generation and Fuseki loading."
            ),
            instrument=[
                reference("#pipegrobid-software"),
                reference("#n8n-service"),
                reference("#grobid-software"),
            ],
            object=[reference(repo_path("pdfs/")), reference(repo_path("xmls/"))],
            result=[reference("#local-kg"), reference("#rfkg-application")],
            isBasedOn=[
                reference(repo_path("containers/docker-compose.yml")),
                reference(repo_path("containers/workflow/pipegrobid_workflow.json")),
            ],
        ),
        action_entity(
            "#rfkg-query-and-visualization",
            "RFKG query and visualization",
            "Publishes the local KG in Fuseki, queries it through research_api and visualizes it in Streamlit.",
            instrument=[
                reference("#fuseki-service"),
                reference("#research-api"),
                reference("#research-frontend"),
            ],
            object=reference("#local-kg"),
            result=reference("#rfkg-application"),
        ),
    ]

    return {
        "@context": "https://w3id.org/ro/crate/1.1/context",
        "@graph": graph,
    }


def write_crate(crate: dict[str, Any]) -> None:
    CRATE_DIR.mkdir(exist_ok=True)
    CRATE_METADATA.write_text(
        json.dumps(crate, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    CRATE_README.write_text(
        "# RO-Crate de RFKG + PipeGrobid\n\n"
        "Este directorio contiene el **RO-Crate** del proyecto **Research Funding "
        "Knowledge Graph (RFKG) + PipeGrobid**. Un RO-Crate es una forma "
        "estandarizada de describir un Research Object mediante metadatos JSON-LD: "
        "explica que contiene el proyecto, que software interviene, que datos se "
        "generan y como se relacionan las partes principales.\n\n"
        "## Archivo principal\n\n"
        "El archivo central es:\n\n"
        "```text\n"
        "ro-crate-metadata.json\n"
        "```\n\n"
        "Ese JSON-LD contiene el grafo de metadatos del proyecto. No es el Knowledge "
        "Graph RDF de la aplicacion, sino el grafo documental del propio proyecto: "
        "describe RFKG, PipeGrobid, sus datasets, servicios, workflow, documentacion "
        "y autores.\n\n"
        "## Entidad principal\n\n"
        "La entidad principal del RO-Crate es:\n\n"
        "```text\n"
        "#rfkg-application\n"
        "```\n\n"
        "Representa **Research Funding Knowledge Graph (RFKG)**, la aplicacion final "
        "que permite analizar financiacion cientifica a partir de papers procesados.\n\n"
        "RFKG se apoya en:\n\n"
        "- PipeGrobid, para convertir PDFs en XML TEI y generar las salidas iniciales.\n"
        "- El Knowledge Graph local, generado en RDF/Turtle.\n"
        "- Fuseki, para publicar y consultar el grafo mediante SPARQL.\n"
        "- `research_api`, para convertir consultas SPARQL en endpoints de dominio.\n"
        "- `research_frontend`, para visualizar la informacion en Streamlit.\n"
        "- n8n, para orquestar el workflow completo.\n\n"
        "## Papel de PipeGrobid\n\n"
        "PipeGrobid aparece como entidad clave:\n\n"
        "```text\n"
        "#pipegrobid-software\n"
        "```\n\n"
        "No se trata como un elemento secundario. Es el pipeline documental que "
        "alimenta la aplicacion RFKG: procesa PDFs cientificos con GROBID, genera "
        "XML TEI y produce las primeras salidas que despues se enriquecen y se "
        "transforman en Knowledge Graph.\n\n"
        "## Datos descritos\n\n"
        "El RO-Crate describe los datasets principales a nivel de coleccion:\n\n"
        "- `pdfs/`: PDFs de entrada.\n"
        "- `xmls/`: XML TEI generados.\n"
        "- `generated_files/`: salidas iniciales de PipeGrobid.\n"
        "- `assigment_2/step_1/`: caso de uso y ontologia.\n"
        "- `assigment_2/step_2/`: parseo XML y NER.\n"
        "- `assigment_2/step_3/`: topics y similitudes.\n"
        "- `assigment_2/step_4/`: enriquecimiento y generacion del KG.\n"
        "- `#local-kg`: Knowledge Graph local generado en `local_kg.ttl`.\n\n"
        "Por decision de granularidad, el RO-Crate no enumera cada PDF, XML o JSON "
        "enriquecido individualmente. Se documentan como colecciones para que el "
        "crate sea legible y no se convierta en un inventario demasiado grande.\n\n"
        "## Software y servicios descritos\n\n"
        "El crate incluye entidades para RFKG, PipeGrobid, `research_api`, "
        "`research_frontend`, GROBID, Fuseki, n8n, FastAPI y Streamlit.\n\n"
        "## Acciones y trazabilidad\n\n"
        "Tambien se describen acciones del flujo reproducible: ejecucion de "
        "PipeGrobid, ejecucion del workflow n8n y publicacion/consulta del KG "
        "mediante Fuseki, `research_api` y Streamlit.\n\n"
        "## Que no contiene\n\n"
        "El RO-Crate no copia datasets pesados ni estado de ejecucion local. En su "
        "lugar, referencia rutas del repositorio. No incluye caches, entornos "
        "virtuales, volumenes Docker, carpetas runtime, `ignore/`, `graphify-out/`, "
        "`grobid-master` ni cada archivo generado de forma individual.\n\n"
        "## Como regenerarlo\n\n"
        "Desde la raiz del repositorio:\n\n"
        "```bash\n"
        "python ro-crate.py\n"
        "```\n\n"
        "El script vuelve a generar este directorio y actualiza "
        "`ro-crate-metadata.json`.\n\n"
        "## Como interpretarlo\n\n"
        "Para leer el RO-Crate manualmente, abre `ro-crate-metadata.json`, busca la "
        "entidad `./`, revisa `mainEntity` y sigue relaciones como `isBasedOn`, "
        "`softwareRequirements`, `instrument`, `object` y `result`.\n\n"
        "En resumen: este RO-Crate documenta RFKG como resultado principal del "
        "proyecto y PipeGrobid como la pieza esencial que hace posible construir el "
        "Knowledge Graph desde documentos cientificos.\n",
        encoding="utf-8",
    )


def main() -> None:
    write_crate(build_crate())


if __name__ == "__main__":
    main()
