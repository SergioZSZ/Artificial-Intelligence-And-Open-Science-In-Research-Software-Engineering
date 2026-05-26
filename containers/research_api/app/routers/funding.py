from fastapi import APIRouter, Query

from queries.funding import (
    build_funding_countries_query,
    build_funding_organizations_query,
    build_funding_topics_query,
)
from routers.common import (
    has_known_amount,
    id_from_uri,
    select_rows,
    split_pipe_values,
    to_int,
    to_optional_float,
)
from schemas.domain import CountryFunding, OrganizationFunding, TopicFunding


router = APIRouter(prefix="/funding")


@router.get("/countries", response_model=list[CountryFunding])
def funding_by_country(
    topic_id: int | None = Query(
        default=None,
        ge=0,
        description=(
            "Topic numerico del KG para filtrar el ranking de paises. "
            "Ejemplo: 0 equivale a g4:topic_0."
        ),
    ),
):
    """Distribucion geografica de financiacion, proyectos y papers."""
    rows = select_rows(build_funding_countries_query(topic_id=topic_id))
    countries: list[CountryFunding] = []

    for row in rows:
        country_id = row.get("country_id") or id_from_uri(row.get("country"))
        country = CountryFunding(
            country_id=country_id,
            name=row.get("name") or "",
            organizations=to_int(row.get("organizations")),
            projects=to_int(row.get("projects")),
            papers=to_int(row.get("papers")),
            funding_amount=to_optional_float(row.get("funding_amount")),
            funding_amount_known=has_known_amount(row),
            currencies=split_pipe_values(row.get("currencies")),
        )
        countries.append(country)

    return countries


@router.get("/topics", response_model=list[TopicFunding])
def funding_by_topic():
    """Distribucion de financiacion por pais y topic."""
    rows = select_rows(build_funding_topics_query())
    topic_funding_rows: list[TopicFunding] = []

    for row in rows:
        country_id = row.get("country_id") or id_from_uri(row.get("country"))
        topic_id = row.get("topic_id") or id_from_uri(row.get("topic"))
        topic_funding = TopicFunding(
            country_id=country_id,
            country=row.get("countryName") or "",
            topic_id=topic_id,
            topic=row.get("topicName"),
            keywords=row.get("keywords"),
            organizations=to_int(row.get("organizations")),
            projects=to_int(row.get("projects")),
            papers=to_int(row.get("papers")),
            funding_amount=to_optional_float(row.get("funding_amount")),
            funding_amount_known=has_known_amount(row),
            currencies=split_pipe_values(row.get("currencies")),
        )
        topic_funding_rows.append(topic_funding)

    return topic_funding_rows


@router.get("/organizations", response_model=list[OrganizationFunding])
def funding_by_organization(
    limit: int = Query(
        default=50,
        ge=1,
        le=200,
        description="Numero maximo de organizaciones financiadoras a devolver.",
    ),
    topic_id: int | None = Query(
        default=None,
        ge=0,
        description=(
            "Topic numerico del KG para filtrar organismos por papers financiados. "
            "Ejemplo: 0 equivale a g4:topic_0."
        ),
    ),
):
    """Ranking de organismos financiadores."""
    rows = select_rows(
        build_funding_organizations_query(limit=limit, topic_id=topic_id)
    )
    organizations: list[OrganizationFunding] = []

    for row in rows:
        organization_id = row.get("organization_id")

        if not organization_id:
            organization_id = id_from_uri(row.get("organization"))

        organization = OrganizationFunding(
            organization_id=organization_id,
            name=row.get("name") or "",
            country=row.get("countryName"),
            projects=to_int(row.get("projects")),
            papers=to_int(row.get("papers")),
            funding_amount=to_optional_float(row.get("funding_amount")),
            funding_amount_known=has_known_amount(row),
            currencies=split_pipe_values(row.get("currencies")),
        )
        organizations.append(organization)

    return organizations
