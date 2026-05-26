from fastapi import APIRouter, Query

from queries.funding import build_projects_query
from routers.common import id_from_uri, select_rows, split_pipe_values, to_optional_float
from schemas.domain import ProjectItem


router = APIRouter(prefix="/projects")


@router.get("", response_model=list[ProjectItem])
def list_projects(
    limit: int = Query(
        default=50,
        ge=1,
        le=200,
        description="Numero maximo de proyectos/grants a devolver.",
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Numero de proyectos/grants a saltar para paginacion.",
    ),
):
    """Listado de proyectos/grants enlazados con financiadores y papers."""
    rows = select_rows(build_projects_query(limit=limit, offset=offset))
    projects: list[ProjectItem] = []

    for row in rows:
        project_id = row.get("project_id") or id_from_uri(row.get("project"))
        project = ProjectItem(
            project_id=project_id,
            name=row.get("name"),
            identifier=row.get("identifier"),
            start_date=row.get("startDate"),
            end_date=row.get("endDate"),
            funding_amount=to_optional_float(row.get("fundingAmount")),
            currency=row.get("currency"),
            funding_amount_known=row.get("fundingAmount") not in (None, ""),
            funders=split_pipe_values(row.get("funders")),
            papers=split_pipe_values(row.get("papers")),
        )
        projects.append(project)

    return projects
