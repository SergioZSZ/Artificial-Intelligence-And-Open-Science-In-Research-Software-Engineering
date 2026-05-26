import pytest

from queries.common import normalize_paper_id
from queries.funding import (
    build_funding_countries_query,
    build_funding_organizations_query,
    build_projects_query,
    build_funding_topics_query,
)
from queries.overview import build_summary_query
from queries.papers import build_paper_detail_query, build_papers_query
from queries.similarities import build_paper_similarities_query


def test_normalize_paper_id_accepts_plain_prefixed_and_uri_values():
    # El frontend puede enviar ids cortos, prefijados o URIs completas.
    assert normalize_paper_id("paper01") == "paper01"
    assert normalize_paper_id("g4:paper02") == "paper02"
    assert (
        normalize_paper_id("https://g4.org/ontology/research-funding#paper03")
        == "paper03"
    )


def test_normalize_paper_id_reuses_core_g4_prefix():
    # Evita duplicar la URI base g4 fuera del cliente/configuracion del KG.
    from core.kg import DEFAULT_PREFIXES

    paper_uri = DEFAULT_PREFIXES["g4"] + "paper04"

    assert normalize_paper_id(paper_uri) == "paper04"


def test_normalize_paper_id_rejects_invalid_values():
    # Evita construir SPARQL con identificadores que no pertenezcan a papers.
    with pytest.raises(ValueError):
        normalize_paper_id("not a paper")


def test_build_papers_query_applies_filters_and_pagination():
    # La lista de papers es el endpoint mas usado por busqueda y filtros.
    query = build_papers_query(
        search="agent",
        topic_id=0,
        country="United",
        organization="Science Foundation",
        project="IIS",
        limit=10,
        offset=5,
    )

    assert "?paper a g4:Paper" in query
    assert "LCASE(?title)" in query
    assert "?paperTopicFilter g4:paper ?paper" in query
    assert "g4:topic g4:topic_0" in query
    assert "LCASE(?countryName)" in query
    assert "LCASE(?orgName)" in query
    assert "LCASE(?projectName)" in query
    assert "LCASE(?projectIdentifier)" in query
    assert query.count("GROUP_CONCAT(DISTINCT") == 5
    assert "SELECT ?paper ?paper_id ?title ?date" in query
    assert "LIMIT 10" in query
    assert "OFFSET 5" in query


def test_build_paper_detail_query_separates_acknowledged_people_and_organizations():
    # La pantalla Papers necesita mostrar acknowledgements sin mezclar personas y organizaciones.
    query = build_paper_detail_query("paper01")

    assert "?paper g4:acknowledges ?acknowledgedOrganization" in query
    assert "?acknowledgedOrganization a schema:Organization" in query
    assert "?paper g4:acknowledges ?acknowledgedPerson" in query
    assert "?acknowledgedPerson a foaf:Person" in query
    assert "acknowledged_organizations" in query
    assert "acknowledged_people" in query


def test_build_paper_detail_query_includes_person_orcid_and_affiliation():
    # Autores y personas reconocidas deben poder mostrarse como ficha clicable.
    query = build_paper_detail_query("paper01")

    assert "?author schema:identifier ?authorOrcid" in query
    assert "?author schema:affiliation ?authorAffiliation" in query
    assert "?acknowledgedPerson schema:identifier ?acknowledgedPersonOrcid" in query
    assert "?acknowledgedPerson schema:affiliation ?acknowledgedPersonAffiliation" in query
    assert "authors_info" in query
    assert "acknowledged_people_info" in query


def test_build_summary_query_uses_independent_count_subqueries():
    # Evita OPTIONAL independientes que multiplican filas y pueden bloquear Fuseki.
    query = build_summary_query()

    assert query.count("SELECT (COUNT(DISTINCT") == 7
    assert "OPTIONAL { ?paper a g4:Paper" not in query
    assert "{ SELECT (COUNT(DISTINCT ?paper) AS ?papers)" in query


def test_build_funding_topics_query_connects_countries_to_topics():
    # Este cruce responde al caso de uso: que pais financia que areas tematicas.
    query = build_funding_topics_query()

    assert "?org schema:location ?country" in query
    assert "?project schema:funder ?org" in query
    assert "?paper g4:fundedByProject ?project" in query
    assert "?paperTopic g4:paper ?paper" in query
    assert "g4:topic ?topic" in query
    assert "schema:currency ?currency" in query
    assert "GROUP_CONCAT(DISTINCT ?currency" in query
    assert "GROUP BY ?country ?country_id ?countryName ?topic ?topic_id ?topicName ?keywords" in query


def test_funding_queries_track_whether_amount_is_known():
    # No todos los proyectos tienen importe; la API debe poder distinguir N/D de 0.
    countries_query = build_funding_countries_query()
    organizations_query = build_funding_organizations_query()
    topics_query = build_funding_topics_query()

    assert "COUNT(DISTINCT ?amount) AS ?funding_amount_count" in countries_query
    assert "COUNT(DISTINCT ?amount) AS ?funding_amount_count" in organizations_query
    assert "COUNT(DISTINCT ?amount) AS ?funding_amount_count" in topics_query
    assert "GROUP_CONCAT(DISTINCT ?currency" in countries_query
    assert "GROUP_CONCAT(DISTINCT ?currency" in organizations_query
    assert "GROUP_CONCAT(DISTINCT ?currency" in topics_query
    assert "COALESCE(SUM(DISTINCT ?amount), 0)" not in countries_query
    assert "COALESCE(SUM(DISTINCT ?amount), 0)" not in organizations_query


def test_build_projects_query_includes_project_currency():
    # La moneda viene del enriquecimiento online y se guarda como schema:currency del proyecto.
    query = build_projects_query()

    assert "?project schema:currency ?currency" in query
    assert "SELECT ?project ?project_id ?name ?identifier ?startDate ?endDate ?fundingAmount ?currency" in query
    assert "GROUP BY ?project ?project_id ?name ?identifier ?startDate ?endDate ?fundingAmount ?currency" in query


def test_build_funding_countries_query_can_filter_by_topic():
    # Funding debe poder responder "que paises financian papers de este topic".
    query = build_funding_countries_query(topic_id=1)

    assert "?paper g4:fundedByProject ?project" in query
    assert "?paperTopic g4:paper ?paper" in query
    assert "g4:topic g4:topic_1" in query
    assert "OPTIONAL {{\n    ?org schema:location ?country" not in query


def test_build_funding_organizations_query_can_filter_by_topic():
    # El ranking de organismos usa el mismo filtro tematico que la pantalla Funding.
    query = build_funding_organizations_query(limit=10, topic_id=1)

    assert "?project schema:funder ?organization" in query
    assert "?paper g4:fundedByProject ?project" in query
    assert "?paperTopic g4:paper ?paper" in query
    assert "g4:topic g4:topic_1" in query
    assert "LIMIT 10" in query


def test_build_paper_similarities_query_filters_by_paper_and_scores():
    # La app necesita similitudes de un paper concreto, no el listado global.
    query = build_paper_similarities_query("paper01", limit=25)

    assert "?similarity a g4:PaperSimilarity" in query
    assert "BIND(g4:paper01 AS ?paper)" in query
    assert "g4:paper1 ?paper" in query
    assert "g4:paper2 ?paper" in query
    assert "g4:score ?score" in query
    assert "LIMIT 25" in query
    assert "OFFSET" not in query
