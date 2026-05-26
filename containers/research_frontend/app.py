from typing import Any

import streamlit as st

from api_client import ApiClient, ApiClientError
from components import (
    dataframe_from_records,
    funding_records_for_display,
    funding_value_for_display,
    render_bar_chart,
    render_metric_grid,
    render_records_table,
    select_label,
    show_api_error,
    show_empty_state,
)


st.set_page_config(
    page_title="Research Funding KG",
    layout="wide",
    initial_sidebar_state="expanded",
)


PAGE_OPTIONS = [
    "Overview",
    "Funding",
    "Papers",
    "Projects",
    "Topics",
    "Similarities",
    "SPARQL",
]


@st.cache_resource
def get_api_client() -> ApiClient:
    return ApiClient()


@st.cache_data(ttl=60)
def load_summary() -> dict[str, Any]:
    return get_api_client().get_summary()


@st.cache_data(ttl=60)
def load_health() -> dict[str, Any]:
    return get_api_client().get_health()


@st.cache_data(ttl=60)
def load_kg_info() -> dict[str, Any]:
    return get_api_client().get_kg_info()


@st.cache_data(ttl=60)
def load_funding_countries(topic_id: int | str | None = None) -> list[dict[str, Any]]:
    return get_api_client().get_funding_countries(topic_id=topic_id)


@st.cache_data(ttl=60)
def load_funding_organizations(
    limit: int = 50,
    topic_id: int | str | None = None,
) -> list[dict[str, Any]]:
    return get_api_client().get_funding_organizations(limit=limit, topic_id=topic_id)


@st.cache_data(ttl=60)
def load_papers(
    search: str | None = None,
    topic_id: int | str | None = None,
    country: str | None = None,
    organization: str | None = None,
    project: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[dict[str, Any]]:
    return get_api_client().get_papers(
        search=search,
        topic_id=topic_id,
        country=country,
        organization=organization,
        project=project,
        limit=limit,
        offset=offset,
    )


@st.cache_data(ttl=60)
def load_paper_detail(paper_id: str) -> dict[str, Any]:
    return get_api_client().get_paper_detail(paper_id)


@st.cache_data(ttl=60)
def load_projects(limit: int = 50, offset: int = 0) -> list[dict[str, Any]]:
    return get_api_client().get_projects(limit=limit, offset=offset)


@st.cache_data(ttl=60)
def load_topics(limit: int = 50, offset: int = 0) -> list[dict[str, Any]]:
    return get_api_client().get_topics(limit=limit, offset=offset)


@st.cache_data(ttl=60)
def load_similarities(paper_id: str, limit: int = 50) -> list[dict[str, Any]]:
    return get_api_client().get_similarities(paper_id=paper_id, limit=limit)


def set_page(page: str):
    st.session_state.page = page


def set_filter(name: str, value: Any):
    st.session_state[name] = value


def normalize_topic_id(value: str | int | None) -> int | None:
    """Convierte topic IDs de la UI al entero que espera `research_api`."""
    if value is None:
        return None

    text = str(value).strip()

    if not text:
        return None

    if text.isdigit():
        return int(text)

    if text.startswith("topic_"):
        suffix = text.removeprefix("topic_")

        if suffix.isdigit():
            return int(suffix)

    return None


def topic_option_label(topic: dict[str, Any] | None) -> str:
    """Etiqueta corta para desplegables de topics."""
    if topic is None:
        return "Todos"

    topic_id = topic.get("topic_id")
    label = topic.get("name") or topic.get("keywords") or "Sin nombre"

    if topic_id is None:
        return str(label)

    return f"topic_{topic_id} - {label}"


def person_option_label(person: dict[str, Any]) -> str:
    """Etiqueta de persona mostrando ORCID cuando el KG lo conoce."""
    name = person.get("name") or "Sin nombre"
    orcid = person.get("orcid")

    if orcid:
        return f"{name} · ORCID {orcid}"

    return name


def people_from_names(names: list[str]) -> list[dict[str, Any]]:
    """Fallback para respuestas antiguas que solo traigan nombres."""
    people: list[dict[str, Any]] = []

    for name in names:
        people.append({"name": name})

    return people


def render_person_profile(person: dict[str, Any]):
    """Ficha compacta de persona enlazada al KG."""
    st.write("Nombre:", person.get("name") or "Sin nombre")
    st.write("ORCID:", person.get("orcid") or "No disponible")
    st.write("Afiliacion:", person.get("affiliation") or "No disponible")
    st.write("ID KG:", person.get("person_id") or "No disponible")


def option_index_by_value(
    records: list[dict[str, Any]],
    key: str | tuple[str, ...],
    selected_value: Any,
) -> int:
    """Devuelve el indice del selectbox teniendo en cuenta la opcion inicial Todos."""
    if selected_value is None:
        return 0

    selected_text = str(selected_value)
    keys = (key,) if isinstance(key, str) else key

    for index, record in enumerate(records, start=1):
        for record_key in keys:
            value = record.get(record_key)

            if value is not None and str(value) == selected_text:
                return index

    return 0


def selected_record_value(record: dict[str, Any] | None, *keys: str) -> str | None:
    """Extrae el primer valor util de una fila seleccionada."""
    if record is None:
        return None

    for key in keys:
        value = record.get(key)

        if value:
            return str(value)

    return None


def top_records(records: list[dict[str, Any]], key: str, limit: int = 5) -> list[dict[str, Any]]:
    """Recorta rankings largos para que la vista principal no meta ruido."""
    records_with_value = []

    for record in records:
        if (record.get(key) or 0) > 0:
            records_with_value.append(record)

    sorted_records = sorted(
        records_with_value,
        key=lambda record: record.get(key) or 0,
        reverse=True,
    )

    return sorted_records[:limit]


def open_papers(**filters: Any):
    for key, value in filters.items():
        set_filter(key, value)

    set_page("Papers")
    st.rerun()


def open_paper_detail(paper_id: str):
    set_filter("selected_paper_id", paper_id)
    set_page("Papers")
    st.rerun()


def open_similarities(paper_id: str):
    set_filter("selected_paper_id", paper_id)
    set_page("Similarities")
    st.rerun()


def setup_state():
    defaults = {
        "page": "Funding",
        "selected_country": None,
        "selected_topic_id": None,
        "selected_organization": None,
        "selected_project": None,
        "selected_paper_id": None,
        "paper_search": "",
        "paper_offset": 0,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_sidebar():
    st.sidebar.title("Research KG")
    selected_page = st.sidebar.radio(
        "Navegacion",
        PAGE_OPTIONS,
        index=PAGE_OPTIONS.index(st.session_state.page),
    )

    if selected_page != st.session_state.page:
        set_page(selected_page)
        st.rerun()

    st.sidebar.divider()
    st.sidebar.caption("Filtros activos")
    st.sidebar.write("Pais:", st.session_state.selected_country or "Todos")
    st.sidebar.write("Topic:", st.session_state.selected_topic_id or "Todos")
    st.sidebar.write("Organizacion:", st.session_state.selected_organization or "Todas")
    st.sidebar.write("Proyecto:", st.session_state.selected_project or "Todos")

    if st.sidebar.button("Actualizar datos", use_container_width=True):
        st.cache_data.clear()
        st.sidebar.success("Cache limpiada. Consultando de nuevo la API.")
        st.rerun()

    if st.sidebar.button("Limpiar filtros", use_container_width=True):
        set_filter("selected_country", None)
        set_filter("selected_topic_id", None)
        set_filter("selected_organization", None)
        set_filter("selected_project", None)
        set_filter("paper_search", "")
        set_filter("paper_offset", 0)
        st.rerun()


def render_overview():
    st.title("Research Funding Knowledge Graph")
    st.caption("Resumen del KG y estado de los servicios principales.")

    try:
        health = load_health()
        info = load_kg_info()
        summary = load_summary()
    except ApiClientError as error:
        show_api_error(error)
        st.warning("La API esta levantada, pero Fuseki no responde.")
        return

    status_columns = st.columns(2)
    status_columns[0].success(f"API: {health.get('status', 'unknown')}")
    status_columns[1].info(f"KG store: {info.get('kg_store', 'unknown')}")

    render_metric_grid(summary)

    with st.expander("Informacion del backend"):
        st.json(info)


def render_funding():
    st.title("Funding")
    st.caption("Vista principal: rankings de financiacion filtrables por area tematica.")

    try:
        topics = load_topics(limit=100)
    except ApiClientError as error:
        show_api_error(error)
        st.warning("La API esta levantada, pero Fuseki no responde.")
        return

    topic_options = [None] + topics
    topic_index = option_index_by_value(
        topics,
        "topic_id",
        st.session_state.selected_topic_id,
    )
    selected_topic = st.selectbox(
        "Filtrar rankings por topic",
        topic_options,
        index=topic_index,
        format_func=topic_option_label,
        help="Topic del KG usado para contar solo paises y organismos que financian papers de esa area.",
        key="funding_topic_filter_selector",
    )
    selected_topic_id = None

    if selected_topic is not None:
        selected_topic_id = normalize_topic_id(selected_topic.get("topic_id"))

    set_filter("selected_topic_id", selected_topic_id)

    try:
        countries = load_funding_countries(topic_id=selected_topic_id)
        organizations = load_funding_organizations(limit=100, topic_id=selected_topic_id)
    except ApiClientError as error:
        show_api_error(error)
        st.warning("La API esta levantada, pero Fuseki no responde.")
        return

    if selected_topic_id is not None and not countries and not organizations:
        show_empty_state("No hay paises ni organismos asociados a este topic.")

    top_countries = top_records(countries, "papers", limit=5)
    top_organizations = top_records(organizations, "papers", limit=5)
    countries_with_papers = top_records(countries, "papers", limit=len(countries))
    organizations_with_papers = top_records(organizations, "papers", limit=len(organizations))

    st.subheader("Ranking de paises")
    render_bar_chart(
        top_countries,
        x="papers",
        y="name",
        title="Top 5 paises por papers financiados",
        empty_message="No hay paises financiadores para esta seleccion.",
    )
    render_records_table(
        funding_records_for_display(top_countries),
        empty_message="No hay paises financiadores para esta seleccion.",
    )

    selected_country = st.selectbox(
        "Ver caracteristicas de un pais",
        [None] + countries_with_papers,
        format_func=lambda country: (
            "Selecciona un pais"
            if country is None
            else select_label(country, ["name", "country_id"])
        ),
        key="funding_country_detail_selector",
    )

    if selected_country is not None:
        st.markdown("**Caracteristicas en el KG**")
        metrics = st.columns(3)
        metrics[0].metric("Organizaciones", selected_country.get("organizations", 0))
        metrics[1].metric("Proyectos", selected_country.get("projects", 0))
        metrics[2].metric("Papers", selected_country.get("papers", 0))
        st.write("Pais:", selected_country.get("name") or selected_country.get("country_id"))
        st.write("ID KG:", selected_country.get("country_id") or "No disponible")

        if st.button("Ver papers de este pais", use_container_width=True):
            open_papers(
                selected_country=selected_country.get("name"),
                selected_topic_id=selected_topic_id,
            )

    st.divider()
    st.subheader("Ranking de organismos")
    render_bar_chart(
        top_organizations,
        x="papers",
        y="name",
        title="Top 5 organismos por papers financiados",
        empty_message="No hay organismos financiadores para esta seleccion.",
    )
    render_records_table(
        funding_records_for_display(top_organizations),
        empty_message="No hay organismos financiadores para esta seleccion.",
    )

    selected_organization = st.selectbox(
        "Ver caracteristicas de un organismo",
        [None] + organizations_with_papers,
        format_func=lambda organization: (
            "Selecciona un organismo"
            if organization is None
            else select_label(organization, ["name", "organization_id"])
        ),
        key="funding_organization_detail_selector",
    )

    if selected_organization is not None:
        st.markdown("**Caracteristicas en el KG**")
        metrics = st.columns(3)
        metrics[0].metric("Pais", selected_organization.get("country") or "N/D")
        metrics[1].metric("Proyectos", selected_organization.get("projects", 0))
        metrics[2].metric("Papers", selected_organization.get("papers", 0))
        st.write("Organismo:", selected_organization.get("name") or "Sin nombre")
        st.write("ID KG:", selected_organization.get("organization_id") or "No disponible")

        if st.button("Ver papers de este organismo", use_container_width=True):
            open_papers(
                selected_organization=selected_organization.get("name"),
                selected_topic_id=selected_topic_id,
            )


def render_paper_detail(paper_id: str):
    try:
        paper = load_paper_detail(paper_id)
    except ApiClientError as error:
        show_api_error(error)
        return

    st.subheader(paper.get("title") or paper_id)
    st.caption(paper.get("date") or "Fecha no disponible")

    if paper.get("abstract"):
        st.write(paper["abstract"])
    else:
        show_empty_state("Este paper no tiene abstract registrado.")

    detail_columns = st.columns(4)
    detail_columns[0].write("Autores")
    detail_columns[0].write(", ".join(paper.get("authors", [])) or "Sin autores")
    detail_columns[1].write("Paises")
    detail_columns[1].write(", ".join(paper.get("countries", [])) or "Sin paises")
    detail_columns[2].write("Funders")
    detail_columns[2].write(", ".join(paper.get("funders", [])) or "Sin funders")
    detail_columns[3].write("Topics")
    detail_columns[3].write(", ".join(paper.get("topics", [])) or "Sin topics")

    st.markdown("**Personas**")
    person_columns = st.columns(2)
    authors_info = paper.get("authors_info") or people_from_names(paper.get("authors", []))
    acknowledged_people_info = paper.get("acknowledged_people_info") or people_from_names(
        paper.get("acknowledged_people", [])
    )

    with person_columns[0]:
        if authors_info:
            selected_author = st.selectbox(
                "Autores",
                authors_info,
                format_func=person_option_label,
                key=f"{paper_id}_author_selector",
            )
            render_person_profile(selected_author)
        else:
            show_empty_state("Este paper no tiene autores registrados.")

    with person_columns[1]:
        if acknowledged_people_info:
            selected_acknowledged_person = st.selectbox(
                "Personas reconocidas",
                acknowledged_people_info,
                format_func=person_option_label,
                key=f"{paper_id}_acknowledged_person_selector",
            )
            render_person_profile(selected_acknowledged_person)
        else:
            show_empty_state("Este paper no tiene personas reconocidas en acknowledgements.")

    st.markdown("**Acknowledgements**")
    acknowledgement_columns = st.columns(2)
    acknowledged_organizations = paper.get("acknowledged_organizations", [])
    acknowledged_people = paper.get("acknowledged_people", [])

    acknowledgement_columns[0].write("Organizaciones")
    acknowledgement_columns[0].write(
        ", ".join(acknowledged_organizations) or "Sin organizaciones reconocidas"
    )
    acknowledgement_columns[1].write("Personas")
    acknowledgement_columns[1].write(
        ", ".join(acknowledged_people) or "Sin personas reconocidas"
    )

    if st.button("Ver papers similares", use_container_width=True):
        open_similarities(paper_id)


def render_papers():
    st.title("Papers")
    st.caption("Busqueda y detalle de papers del Knowledge Graph.")

    try:
        countries = load_funding_countries()
        topics = load_topics(limit=100)
        organizations = load_funding_organizations(limit=200)
        projects = load_projects(limit=200)
    except ApiClientError as error:
        show_api_error(error)
        st.warning("La API esta levantada, pero Fuseki no responde.")
        return

    search = st.text_input(
        "Buscar",
        value=st.session_state.paper_search,
        placeholder="Titulo, abstract o identificador",
        help="Texto a buscar en titulo o abstract.",
    )
    set_filter("paper_search", search)

    filters = st.columns(4)
    selected_country = filters[0].selectbox(
        "Pais",
        [None] + countries,
        index=option_index_by_value(
            countries,
            "name",
            st.session_state.selected_country,
        ),
        format_func=lambda country: (
            "Todos"
            if country is None
            else select_label(country, ["name", "country_id"])
        ),
        help="Pais de la organizacion financiadora enlazada al paper.",
    )
    selected_topic = filters[1].selectbox(
        "Topic",
        [None] + topics,
        index=option_index_by_value(
            topics,
            "topic_id",
            st.session_state.selected_topic_id,
        ),
        format_func=topic_option_label,
        help="Topic asignado al paper por el pipeline de topic modeling.",
    )
    selected_organization = filters[2].selectbox(
        "Organizacion",
        [None] + organizations,
        index=option_index_by_value(
            organizations,
            "name",
            st.session_state.selected_organization,
        ),
        format_func=lambda organization: (
            "Todas"
            if organization is None
            else select_label(organization, ["name", "organization_id"])
        ),
        help="Organismo financiador conectado al proyecto del paper.",
    )
    selected_project = filters[3].selectbox(
        "Proyecto",
        [None] + projects,
        index=option_index_by_value(
            projects,
            ("name", "identifier", "project_id"),
            st.session_state.selected_project,
        ),
        format_func=lambda project: (
            "Todos"
            if project is None
            else select_label(project, ["name", "identifier", "project_id"])
        ),
        help="Grant o proyecto que financia el paper.",
    )

    limit = st.slider("Resultados por pagina", min_value=10, max_value=200, value=50, step=10)
    offset = st.number_input("Offset", min_value=0, value=int(st.session_state.paper_offset), step=limit)

    country = selected_record_value(selected_country, "name")
    topic_id = None

    if selected_topic is not None:
        topic_id = normalize_topic_id(selected_topic.get("topic_id"))

    organization = selected_record_value(selected_organization, "name")
    project = selected_record_value(selected_project, "name", "identifier", "project_id")

    set_filter("selected_country", country)
    set_filter("selected_topic_id", topic_id)
    set_filter("selected_organization", organization)
    set_filter("selected_project", project)

    try:
        papers = load_papers(
            search=search or None,
            topic_id=topic_id,
            country=country or None,
            organization=organization or None,
            project=project or None,
            limit=limit,
            offset=int(offset),
        )
    except ApiClientError as error:
        show_api_error(error)
        return

    if not papers:
        show_empty_state("No hay papers para los filtros seleccionados.")
        return

    dataframe = dataframe_from_records(papers)
    st.dataframe(dataframe, use_container_width=True, hide_index=True)

    paper_options = {
        f"{paper.get('paper_id')} - {paper.get('title') or 'Sin titulo'}": paper.get("paper_id")
        for paper in papers
    }
    selected_label = st.selectbox("Abrir detalle", list(paper_options.keys()))

    if st.button("Abrir paper", use_container_width=True):
        set_filter("selected_paper_id", paper_options[selected_label])
        st.rerun()

    selected_paper_id = st.session_state.selected_paper_id

    if selected_paper_id:
        render_paper_detail(selected_paper_id)


def render_projects():
    st.title("Projects")
    st.caption("Exploracion rapida de grants y proyectos enlazados con papers.")

    try:
        projects = load_projects(limit=200)
    except ApiClientError as error:
        show_api_error(error)
        return

    if not projects:
        show_empty_state("No hay proyectos asociados en el KG.")
        return

    selected_project = st.selectbox(
        "Proyecto",
        projects,
        index=option_index_by_value(
            projects,
            ("name", "identifier", "project_id"),
            st.session_state.selected_project,
        ),
        format_func=lambda project: select_label(project, ["name", "identifier", "project_id"]),
        help="Proyecto o grant extraido de los acknowledgements y enlazado al KG.",
    )

    st.subheader("Caracteristicas en el KG")
    metric_columns = st.columns(3)
    metric_columns[0].metric("Funders", len(selected_project.get("funders", [])))
    metric_columns[1].metric("Papers", len(selected_project.get("papers", [])))
    metric_columns[2].metric(
        "Financiacion conocida",
        funding_value_for_display(selected_project),
    )
    st.write("Currency:", selected_project.get("currency") or "No disponible")

    st.write("Nombre:", selected_project.get("name") or "Sin nombre")
    st.write("Identifier:", selected_project.get("identifier") or "No disponible")
    st.write("Inicio:", selected_project.get("start_date") or "No disponible")
    st.write("Fin:", selected_project.get("end_date") or "No disponible")

    funders = selected_project.get("funders") or []
    papers = selected_project.get("papers") or []
    st.write("Funders:", ", ".join(funders) if funders else "Sin funders")
    st.write("Papers:", ", ".join(papers) if papers else "Sin papers")

    if st.button("Ver papers de este proyecto", use_container_width=True):
        project_value = selected_project.get("name") or selected_project.get("identifier")
        open_papers(selected_project=project_value)

    with st.expander("Tabla completa de proyectos"):
        render_records_table(projects, empty_message="No hay proyectos asociados en el KG.")


def render_topics():
    st.title("Topics")
    st.caption("Topics, keywords y papers representativos.")

    try:
        topics = load_topics(limit=100)
    except ApiClientError as error:
        show_api_error(error)
        return

    if not topics:
        show_empty_state("No hay topics registrados en el KG.")
        return

    dataframe = dataframe_from_records(topics)
    st.dataframe(dataframe, use_container_width=True, hide_index=True)

    topic_options = {
        select_label(topic, ["name", "keywords", "topic_id"]): topic
        for topic in topics
    }
    selected_topic_label = st.selectbox("Topic para explorar papers", list(topic_options.keys()))
    selected_topic = topic_options[selected_topic_label]

    if st.button("Ver papers de este topic", use_container_width=True):
        open_papers(selected_topic_id=selected_topic.get("topic_id"))


def render_similarities():
    st.title("Similarities")
    st.caption("Papers similares a un paper concreto.")

    paper_id = st.text_input(
        "Paper ID",
        value=st.session_state.selected_paper_id or "",
        placeholder="paper01",
    )

    if not paper_id:
        show_empty_state("Selecciona un paper para consultar similitudes.")
        return

    try:
        similarities = load_similarities(paper_id=paper_id, limit=50)
    except ApiClientError as error:
        show_api_error(error)
        return

    if not similarities:
        show_empty_state("Este paper no tiene similitudes registradas.")
        return

    dataframe = dataframe_from_records(similarities)
    st.dataframe(dataframe, use_container_width=True, hide_index=True)

    options = {
        f"{row.get('target_paper_id')} - score {row.get('score', 0)}": row.get("target_paper_id")
        for row in similarities
    }
    selected = st.selectbox("Abrir paper similar", list(options.keys()))

    if st.button("Abrir detalle del paper similar", use_container_width=True):
        open_paper_detail(options[selected])


def render_sparql():
    st.title("SPARQL")
    st.caption("Consulta avanzada para depuracion.")

    default_query = "SELECT * WHERE { ?s ?p ?o } LIMIT 10"
    query = st.text_area("Query", value=default_query, height=240)
    query_type = st.selectbox("Tipo", ["SELECT", "ASK", "CONSTRUCT"], index=0)

    if st.button("Ejecutar query", use_container_width=True):
        try:
            result = get_api_client().run_sparql_query(query=query, query_type=query_type)
        except ApiClientError as error:
            show_api_error(error)
            return

        st.json(result)


def main():
    setup_state()
    render_sidebar()

    page = st.session_state.page

    if page == "Overview":
        render_overview()
    elif page == "Funding":
        render_funding()
    elif page == "Papers":
        render_papers()
    elif page == "Projects":
        render_projects()
    elif page == "Topics":
        render_topics()
    elif page == "Similarities":
        render_similarities()
    elif page == "SPARQL":
        render_sparql()


if __name__ == "__main__":
    main()
