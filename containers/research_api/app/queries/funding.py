from queries.common import result_window_clause


def build_funding_countries_query(topic_id: int | None = None) -> str:
    """Agrupa la financiacion por pais para el caso de uso geografico."""
    if topic_id is not None:
        return f"""
SELECT ?country ?country_id ?name
       (COUNT(DISTINCT ?org) AS ?organizations)
       (COUNT(DISTINCT ?project) AS ?projects)
       (COUNT(DISTINCT ?paper) AS ?papers)
       (SUM(DISTINCT ?amount) AS ?funding_amount)
       (COUNT(DISTINCT ?amount) AS ?funding_amount_count)
       (GROUP_CONCAT(DISTINCT ?currency; separator="|") AS ?currencies)
WHERE {{
  # Ranking filtrado: pais -> organizacion -> proyecto -> paper -> topic.
  ?country a schema:Country ; schema:name ?name .
  BIND(REPLACE(STR(?country), "^.*[#/]", "") AS ?country_id)

  ?org schema:location ?country .
  ?project schema:funder ?org .
  ?paper g4:fundedByProject ?project .
  ?paperTopic g4:paper ?paper ; g4:topic g4:topic_{topic_id} .
  OPTIONAL {{ ?project g4:fundingAmount ?amount . }}
  OPTIONAL {{ ?project schema:currency ?currency . }}
}}
GROUP BY ?country ?country_id ?name
ORDER BY DESC(?papers) ?name
""".strip()

    return f"""
SELECT ?country ?country_id ?name
       (COUNT(DISTINCT ?org) AS ?organizations)
       (COUNT(DISTINCT ?project) AS ?projects)
       (COUNT(DISTINCT ?paper) AS ?papers)
       (SUM(DISTINCT ?amount) AS ?funding_amount)
       (COUNT(DISTINCT ?amount) AS ?funding_amount_count)
       (GROUP_CONCAT(DISTINCT ?currency; separator="|") AS ?currencies)
WHERE {{
  # Cada pais se cuenta aunque todavia no tenga financiacion enlazada.
  ?country a schema:Country ; schema:name ?name .
  BIND(REPLACE(STR(?country), "^.*[#/]", "") AS ?country_id)

  # Relacion pais -> organizacion -> proyecto -> paper.
  OPTIONAL {{
    ?org schema:location ?country .
    ?project schema:funder ?org .
    OPTIONAL {{ ?paper g4:fundedByProject ?project . }}
    OPTIONAL {{ ?project g4:fundingAmount ?amount . }}
    OPTIONAL {{ ?project schema:currency ?currency . }}
  }}
}}
GROUP BY ?country ?country_id ?name
ORDER BY DESC(?papers) ?name
""".strip()


def build_funding_organizations_query(
    limit: int = 50,
    topic_id: int | None = None,
) -> str:
    """Ranking de organismos financiadores y su impacto en papers/proyectos."""
    topic_filter = ""

    if topic_id is not None:
        topic_filter = f"""
  # Si hay topic seleccionado, el organismo solo cuenta cuando financia papers de ese topic.
  ?project schema:funder ?organization .
  ?paper g4:fundedByProject ?project .
  ?paperTopic g4:paper ?paper ; g4:topic g4:topic_{topic_id} .
  OPTIONAL {{ ?project g4:fundingAmount ?amount . }}
  OPTIONAL {{ ?project schema:currency ?currency . }}
"""
    else:
        topic_filter = """
  # Proyectos y papers financiados por la organizacion.
  OPTIONAL {
    ?project schema:funder ?organization .
    OPTIONAL { ?paper g4:fundedByProject ?project . }
    OPTIONAL { ?project g4:fundingAmount ?amount . }
    OPTIONAL { ?project schema:currency ?currency . }
  }
"""

    return f"""
SELECT ?organization ?organization_id ?name ?countryName
       (COUNT(DISTINCT ?project) AS ?projects)
       (COUNT(DISTINCT ?paper) AS ?papers)
       (SUM(DISTINCT ?amount) AS ?funding_amount)
       (COUNT(DISTINCT ?amount) AS ?funding_amount_count)
       (GROUP_CONCAT(DISTINCT ?currency; separator="|") AS ?currencies)
WHERE {{
  # Organizaciones financiadoras modeladas con schema.org.
  ?organization a schema:Organization ; schema:name ?name .
  BIND(REPLACE(STR(?organization), "^.*[#/]", "") AS ?organization_id)

  # Pais de la organizacion, si existe en el KG.
  OPTIONAL {{
    ?organization schema:location ?country .
    ?country schema:name ?countryName .
  }}

{topic_filter}
}}
GROUP BY ?organization ?organization_id ?name ?countryName
ORDER BY DESC(?papers) ?name
{result_window_clause(limit)}
""".strip()


def build_funding_topics_query() -> str:
    """Cruza paises financiadores con topics de papers financiados."""
    return """
SELECT ?country ?country_id ?countryName ?topic ?topic_id ?topicName ?keywords
       (COUNT(DISTINCT ?org) AS ?organizations)
       (COUNT(DISTINCT ?project) AS ?projects)
       (COUNT(DISTINCT ?paper) AS ?papers)
       (SUM(DISTINCT ?amount) AS ?funding_amount)
       (COUNT(DISTINCT ?amount) AS ?funding_amount_count)
       (GROUP_CONCAT(DISTINCT ?currency; separator="|") AS ?currencies)
WHERE {
  # Camino del caso de uso: pais -> organizacion -> proyecto -> paper -> topic.
  ?org schema:location ?country .
  ?country schema:name ?countryName .
  ?project schema:funder ?org .
  ?paper g4:fundedByProject ?project .
  ?paperTopic g4:paper ?paper ; g4:topic ?topic .

  # IDs cortos para que el frontend no dependa de URIs RDF completas.
  BIND(REPLACE(STR(?country), "^.*[#/]", "") AS ?country_id)
  BIND(REPLACE(STR(?topic), "^.*topic_", "") AS ?topic_id)

  # Informacion descriptiva del topic.
  OPTIONAL { ?topic schema:name ?topicName . }
  OPTIONAL { ?topic schema:keywords ?keywords . }
  OPTIONAL { ?project g4:fundingAmount ?amount . }
  OPTIONAL { ?project schema:currency ?currency . }
}
GROUP BY ?country ?country_id ?countryName ?topic ?topic_id ?topicName ?keywords
ORDER BY ?topic_id DESC(?papers) ?countryName
""".strip()


def build_projects_query(limit: int = 50, offset: int = 0) -> str:
    """Lista grants/proyectos con financiadores y papers asociados."""
    return f"""
SELECT ?project ?project_id ?name ?identifier ?startDate ?endDate ?fundingAmount ?currency
       (GROUP_CONCAT(DISTINCT ?funderName; separator="|") AS ?funders)
       (GROUP_CONCAT(DISTINCT ?paperId; separator="|") AS ?papers)
WHERE {{
  # Proyecto o grant detectado en el paper.
  ?project a schema:Project .
  BIND(REPLACE(STR(?project), "^.*[#/]", "") AS ?project_id)

  # Campos opcionales porque no todos los grants traen la misma informacion.
  OPTIONAL {{ ?project schema:name ?name . }}
  OPTIONAL {{ ?project schema:identifier ?identifier . }}
  OPTIONAL {{ ?project schema:startDate ?startDate . }}
  OPTIONAL {{ ?project schema:endDate ?endDate . }}
  OPTIONAL {{ ?project g4:fundingAmount ?fundingAmount . }}
  OPTIONAL {{ ?project schema:currency ?currency . }}
  OPTIONAL {{ ?project schema:funder ?funder . ?funder schema:name ?funderName . }}
  OPTIONAL {{
    ?paper g4:fundedByProject ?project .
    BIND(REPLACE(STR(?paper), "^.*[#/]", "") AS ?paperId)
  }}
}}
GROUP BY ?project ?project_id ?name ?identifier ?startDate ?endDate ?fundingAmount ?currency
ORDER BY ?project_id
{result_window_clause(limit, offset)}
""".strip()
