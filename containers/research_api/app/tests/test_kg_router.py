from fastapi.testclient import TestClient
import requests

from core import kg as kg_client
from routers import funding, papers, projects, query, similarities, topics
from main import app


client = TestClient(app)


def test_app_keeps_public_kg_routes_after_router_split():
    # Aunque el codigo este separado por temas, las URLs publicas siguen bajo /kg.
    paths = set()

    for route in app.routes:
        paths.add(route.path)

    assert "/kg/summary" in paths
    assert "/kg/papers" in paths
    assert "/kg/papers/{paper_id}" in paths
    assert "/kg/topics" in paths
    assert "/kg/projects" in paths
    assert "/kg/similarities/{paper_id}" in paths
    assert "/kg/funding/topics" in paths
    assert "/kg/authors" not in paths
    assert "/kg/similarities" not in paths
    assert "/kg/network/funding" not in paths
    assert "/kg/network/countries" not in paths


def test_domain_routers_declare_their_own_prefixes():
    # Los prefijos viven en cada router tematico, no repetidos en cada endpoint.
    assert papers.router.prefix == "/papers"
    assert funding.router.prefix == "/funding"
    assert projects.router.prefix == "/projects"
    assert topics.router.prefix == "/topics"
    assert similarities.router.prefix == "/similarities"
    assert query.router.prefix == "/query"


def test_openapi_documents_endpoint_parameters():
    # Las descripciones ayudan a entender la API desde Swagger/OpenAPI.
    schema = client.get("/openapi.json").json()

    papers_parameters = schema["paths"]["/kg/papers"]["get"]["parameters"]
    papers_descriptions = {
        parameter["name"]: parameter.get("description")
        for parameter in papers_parameters
    }

    assert papers_descriptions["search"]
    assert papers_descriptions["topic_id"]
    assert papers_descriptions["limit"]
    assert papers_descriptions["offset"]

    detail_parameters = schema["paths"]["/kg/papers/{paper_id}"]["get"]["parameters"]
    detail_descriptions = {
        parameter["name"]: parameter.get("description")
        for parameter in detail_parameters
    }

    assert detail_descriptions["paper_id"]

    similarity_parameters = schema["paths"]["/kg/similarities/{paper_id}"]["get"]["parameters"]
    similarity_descriptions = {
        parameter["name"]: parameter.get("description")
        for parameter in similarity_parameters
    }

    assert similarity_descriptions["paper_id"]
    assert similarity_descriptions["limit"]

    countries_parameters = schema["paths"]["/kg/funding/countries"]["get"]["parameters"]
    countries_descriptions = {
        parameter["name"]: parameter.get("description")
        for parameter in countries_parameters
    }
    assert countries_descriptions["topic_id"]

    organizations_parameters = schema["paths"]["/kg/funding/organizations"]["get"][
        "parameters"
    ]
    organizations_descriptions = {
        parameter["name"]: parameter.get("description")
        for parameter in organizations_parameters
    }
    assert organizations_descriptions["topic_id"]


def test_openapi_exposes_only_useful_public_parameters():
    # Evita parametros que puedan crear respuestas parciales poco utiles para la app.
    schema = client.get("/openapi.json").json()

    countries_parameters = schema["paths"]["/kg/funding/countries"]["get"].get(
        "parameters",
        [],
    )
    countries_parameter_names = {
        parameter["name"]
        for parameter in countries_parameters
    }

    assert countries_parameter_names == {"topic_id"}

    organizations_parameters = schema["paths"]["/kg/funding/organizations"]["get"][
        "parameters"
    ]
    organizations_parameter_names = {
        parameter["name"]
        for parameter in organizations_parameters
    }

    assert organizations_parameter_names == {"limit", "topic_id"}

    similarity_parameters = schema["paths"]["/kg/similarities/{paper_id}"]["get"][
        "parameters"
    ]
    similarity_parameter_names = {
        parameter["name"]
        for parameter in similarity_parameters
    }

    assert similarity_parameter_names == {"paper_id", "limit"}

    funding_topics_parameters = schema["paths"]["/kg/funding/topics"]["get"].get(
        "parameters",
        [],
    )

    assert funding_topics_parameters == []


def test_summary_endpoint_returns_normalized_counts(monkeypatch):
    # El endpoint oculta la respuesta SPARQL cruda y devuelve contadores enteros.
    def fake_execute_sparql_query(query: str, query_type: str = "SELECT"):
        assert "COUNT(DISTINCT ?paper)" in query
        return {
            "query_type": query_type,
            "results": [
                {
                    "papers": "30",
                    "authors": "120",
                    "organizations": "45",
                    "projects": "12",
                    "countries": "8",
                    "topics": "2",
                    "paper_similarities": "18",
                }
            ],
            "raw_response": None,
            "raw_text": None,
            "status_code": 200,
        }

    monkeypatch.setattr(kg_client, "execute_sparql_query", fake_execute_sparql_query)

    response = client.get("/kg/summary")

    assert response.status_code == 200
    assert response.json() == {
        "papers": 30,
        "authors": 120,
        "organizations": 45,
        "projects": 12,
        "countries": 8,
        "topics": 2,
        "paper_similarities": 18,
    }


def test_summary_endpoint_returns_504_when_fuseki_times_out(monkeypatch):
    # Si Fuseki se queda pensando, la API debe responder controladamente.
    def fake_execute_sparql_query(query: str, query_type: str = "SELECT"):
        raise requests.exceptions.ReadTimeout("Fuseki query timeout")

    monkeypatch.setattr(kg_client, "execute_sparql_query", fake_execute_sparql_query)

    response = client.get("/kg/summary")

    assert response.status_code == 504
    assert response.json()["detail"] == "Fuseki query timeout."


def test_paper_detail_endpoint_returns_split_lists(monkeypatch):
    # El detalle convierte campos concatenados del SPARQL en listas normales.
    def fake_execute_sparql_query(query: str, query_type: str = "SELECT"):
        assert "g4:paper01" in query
        return {
            "query_type": query_type,
            "results": [
                {
                    "paper_id": "paper01",
                    "uri": "https://g4.org/ontology/research-funding#paper01",
                    "title": "Example paper",
                    "date": "2026-05-15",
                    "abstract": "Short abstract",
                    "authors": "Ada Lovelace|Grace Hopper",
                    "projects": "IIS-2229876",
                    "funders": "National Science Foundation",
                    "countries": "United States",
                    "topics": "0_reasoning_model_models_ai",
                    "acknowledged_organizations": "National Science Foundation|OpenAI",
                    "acknowledged_people": "Alan Turing|Katherine Johnson",
                    "authors_info": (
                        "Ada Lovelace~0000-0001-1111-1111~Analytical Engine Lab~"
                        "person_ada_lovelace~https://g4.org/ontology/research-funding#person_ada_lovelace"
                        "|Grace Hopper~0000-0002-2222-2222~US Navy~"
                        "person_grace_hopper~https://g4.org/ontology/research-funding#person_grace_hopper"
                    ),
                    "acknowledged_people_info": (
                        "Alan Turing~0000-0003-3333-3333~Bletchley Park~"
                        "person_alan_turing~https://g4.org/ontology/research-funding#person_alan_turing"
                        "|Katherine Johnson~~NASA~"
                        "person_katherine_johnson~https://g4.org/ontology/research-funding#person_katherine_johnson"
                    ),
                }
            ],
            "raw_response": None,
            "raw_text": None,
            "status_code": 200,
        }

    monkeypatch.setattr(kg_client, "execute_sparql_query", fake_execute_sparql_query)

    response = client.get("/kg/papers/paper01")

    assert response.status_code == 200
    assert response.json()["paper_id"] == "paper01"
    assert response.json()["authors"] == ["Ada Lovelace", "Grace Hopper"]
    assert response.json()["projects"] == ["IIS-2229876"]
    assert response.json()["acknowledged_organizations"] == [
        "National Science Foundation",
        "OpenAI",
    ]
    assert response.json()["acknowledged_people"] == [
        "Alan Turing",
        "Katherine Johnson",
    ]
    assert response.json()["authors_info"][0] == {
        "person_id": "person_ada_lovelace",
        "uri": "https://g4.org/ontology/research-funding#person_ada_lovelace",
        "name": "Ada Lovelace",
        "orcid": "0000-0001-1111-1111",
        "affiliation": "Analytical Engine Lab",
    }
    assert response.json()["acknowledged_people_info"][1] == {
        "person_id": "person_katherine_johnson",
        "uri": "https://g4.org/ontology/research-funding#person_katherine_johnson",
        "name": "Katherine Johnson",
        "orcid": None,
        "affiliation": "NASA",
    }


def test_paper_similarities_endpoint_returns_pairs_with_scores(monkeypatch):
    # El endpoint de similitudes se pide para un paper concreto.
    def fake_execute_sparql_query(query: str, query_type: str = "SELECT"):
        assert "?similarity a g4:PaperSimilarity" in query
        assert "g4:paper01" in query
        return {
            "query_type": query_type,
            "results": [
                {
                    "similarity_id": "similarity01",
                    "source_paper_id": "paper01",
                    "target_paper_id": "paper02",
                    "score": "0.91",
                }
            ],
            "raw_response": None,
            "raw_text": None,
            "status_code": 200,
        }

    monkeypatch.setattr(kg_client, "execute_sparql_query", fake_execute_sparql_query)

    response = client.get("/kg/similarities/paper01")

    assert response.status_code == 200
    assert response.json() == [
        {
            "similarity_id": "similarity01",
            "source_paper_id": "paper01",
            "target_paper_id": "paper02",
            "score": 0.91,
        }
    ]


def test_funding_countries_returns_null_when_amount_is_unknown(monkeypatch):
    # Sin g4:fundingAmount no debe mostrarse como 0: es financiacion desconocida.
    def fake_execute_sparql_query(query: str, query_type: str = "SELECT"):
        assert "funding_amount_count" in query
        return {
            "query_type": query_type,
            "results": [
                {
                    "country_id": "country_us",
                    "name": "United States",
                    "organizations": "1",
                    "projects": "2",
                    "papers": "3",
                    "funding_amount_count": "0",
                }
            ],
            "raw_response": None,
            "raw_text": None,
            "status_code": 200,
        }

    monkeypatch.setattr(kg_client, "execute_sparql_query", fake_execute_sparql_query)

    response = client.get("/kg/funding/countries")

    assert response.status_code == 200
    assert response.json()[0]["funding_amount"] is None
    assert response.json()[0]["funding_amount_known"] is False


def test_funding_topics_endpoint_returns_country_topic_distribution(monkeypatch):
    # Este endpoint reemplaza networks como analisis principal del caso de uso.
    def fake_execute_sparql_query(query: str, query_type: str = "SELECT"):
        assert "?paperTopic g4:paper ?paper" in query
        return {
            "query_type": query_type,
            "results": [
                {
                    "country_id": "country_us",
                    "countryName": "United States",
                    "topic_id": "0",
                    "topicName": "AI reasoning",
                    "keywords": "reasoning,models,ai",
                    "organizations": "3",
                    "projects": "5",
                    "papers": "12",
                    "funding_amount": "2500000",
                    "funding_amount_count": "1",
                    "currencies": "EUR",
                }
            ],
            "raw_response": None,
            "raw_text": None,
            "status_code": 200,
        }

    monkeypatch.setattr(kg_client, "execute_sparql_query", fake_execute_sparql_query)

    response = client.get("/kg/funding/topics")

    assert response.status_code == 200
    assert response.json() == [
        {
            "country_id": "country_us",
            "country": "United States",
            "topic_id": "0",
            "topic": "AI reasoning",
            "keywords": "reasoning,models,ai",
            "organizations": 3,
            "projects": 5,
            "papers": 12,
            "funding_amount": 2500000.0,
            "funding_amount_known": True,
            "currencies": ["EUR"],
        }
    ]


def test_projects_endpoint_returns_currency(monkeypatch):
    # La app de proyectos debe mostrar la moneda extraida desde online_enrichment.
    def fake_execute_sparql_query(query: str, query_type: str = "SELECT"):
        assert "?project schema:currency ?currency" in query
        return {
            "query_type": query_type,
            "results": [
                {
                    "project_id": "project_erc_example",
                    "name": "ERC Example",
                    "identifier": "ERC-123",
                    "startDate": "2024-01-01",
                    "endDate": "2026-01-01",
                    "fundingAmount": "1498210",
                    "currency": "EUR",
                    "funders": "European Research Council",
                    "papers": "paper13",
                }
            ],
            "raw_response": None,
            "raw_text": None,
            "status_code": 200,
        }

    monkeypatch.setattr(kg_client, "execute_sparql_query", fake_execute_sparql_query)

    response = client.get("/kg/projects")

    assert response.status_code == 200
    assert response.json()[0]["funding_amount"] == 1498210.0
    assert response.json()[0]["currency"] == "EUR"
    assert response.json()[0]["funding_amount_known"] is True
