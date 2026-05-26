from pydantic import BaseModel, Field


class SummaryResponse(BaseModel):
    """Conteos generales para el dashboard inicial de la app."""

    papers: int = 0
    authors: int = 0
    organizations: int = 0
    projects: int = 0
    countries: int = 0
    topics: int = 0
    paper_similarities: int = 0


class PaperListItem(BaseModel):
    """Paper resumido para listados, busquedas y filtros."""

    paper_id: str
    uri: str | None = None
    title: str | None = None
    date: str | None = None
    authors: list[str] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)
    funders: list[str] = Field(default_factory=list)
    countries: list[str] = Field(default_factory=list)
    topics: list[str] = Field(default_factory=list)


class PersonInfo(BaseModel):
    """Persona enlazada al paper con datos utiles para mostrar una ficha."""

    person_id: str | None = None
    uri: str | None = None
    name: str
    orcid: str | None = None
    affiliation: str | None = None


class PaperDetail(PaperListItem):
    """Ficha completa de un paper concreto."""

    abstract: str | None = None
    acknowledged_organizations: list[str] = Field(default_factory=list)
    acknowledged_people: list[str] = Field(default_factory=list)
    authors_info: list[PersonInfo] = Field(default_factory=list)
    acknowledged_people_info: list[PersonInfo] = Field(default_factory=list)


class CountryFunding(BaseModel):
    """Resumen de financiacion agregada por pais."""

    country_id: str
    name: str
    organizations: int = 0
    projects: int = 0
    papers: int = 0
    funding_amount: float | None = None
    funding_amount_known: bool = False
    currencies: list[str] = Field(default_factory=list)


class OrganizationFunding(BaseModel):
    """Resumen de impacto de una organizacion financiadora."""

    organization_id: str
    name: str
    country: str | None = None
    projects: int = 0
    papers: int = 0
    funding_amount: float | None = None
    funding_amount_known: bool = False
    currencies: list[str] = Field(default_factory=list)


class TopicFunding(BaseModel):
    """Financiacion agregada por pais y topic."""

    country_id: str
    country: str
    topic_id: str
    topic: str | None = None
    keywords: str | None = None
    organizations: int = 0
    projects: int = 0
    papers: int = 0
    funding_amount: float | None = None
    funding_amount_known: bool = False
    currencies: list[str] = Field(default_factory=list)


class ProjectItem(BaseModel):
    """Proyecto o grant con sus financiadores y papers asociados."""

    project_id: str
    name: str | None = None
    identifier: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    funding_amount: float | None = None
    currency: str | None = None
    funding_amount_known: bool = False
    funders: list[str] = Field(default_factory=list)
    papers: list[str] = Field(default_factory=list)


class TopicItem(BaseModel):
    """Topic detectado en el KG y sus papers representativos."""

    topic_id: str
    name: str | None = None
    keywords: str | None = None
    papers_count: int = 0
    papers: list[str] = Field(default_factory=list)


class PaperSimilarityItem(BaseModel):
    """Relacion de similitud entre dos papers del KG."""

    similarity_id: str
    source_paper_id: str
    target_paper_id: str
    score: float = 0.0
