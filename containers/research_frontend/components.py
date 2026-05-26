from collections.abc import Iterable
from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st


def dataframe_from_records(records: list[dict[str, Any]]) -> pd.DataFrame:
    """Convierte respuestas JSON de la API en DataFrame sin romper con listas vacias."""
    if not records:
        return pd.DataFrame()

    return pd.DataFrame(records)


def show_empty_state(message: str):
    """Estado vacio consistente para que la app no parezca rota sin datos."""
    st.info(message)


def show_api_error(error: Exception):
    """Mensaje de error legible para problemas entre Streamlit, API y Fuseki."""
    st.error(str(error))


def funding_value_for_display(record: dict[str, Any]) -> float | str:
    """Muestra importes desconocidos como N/D, no como 0."""
    if not record.get("funding_amount_known"):
        return "N/D"

    amount = record.get("funding_amount")

    if amount is None:
        return "N/D"

    currency = record.get("currency")

    if currency:
        return f"{amount} {currency}"

    currencies = record.get("currencies") or []

    if currencies:
        return f"{amount} ({', '.join(currencies)})"

    return amount


def funding_records_for_display(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Renombra la columna de importes para evitar interpretarla como reparto exacto."""
    display_records: list[dict[str, Any]] = []

    for record in records:
        display_record = dict(record)
        display_record.pop("funding_amount_known", None)
        display_record.pop("funding_amount", None)
        display_record.pop("currency", None)
        display_record.pop("currencies", None)
        display_record["financiacion conocida asociada"] = funding_value_for_display(record)
        display_records.append(display_record)

    return display_records


def render_metric_grid(summary: dict[str, Any]):
    """Muestra los conteos principales del KG en una cuadricula compacta."""
    metrics = [
        ("Papers", summary.get("papers", 0)),
        ("Autores", summary.get("authors", 0)),
        ("Organizaciones", summary.get("organizations", 0)),
        ("Proyectos", summary.get("projects", 0)),
        ("Paises", summary.get("countries", 0)),
        ("Topics", summary.get("topics", 0)),
        ("Similitudes", summary.get("paper_similarities", 0)),
    ]

    columns = st.columns(4)

    for index, metric in enumerate(metrics):
        label, value = metric
        columns[index % 4].metric(label, value)


def render_bar_chart(
    records: list[dict[str, Any]],
    x: str,
    y: str,
    title: str,
    empty_message: str,
    top_n: int = 5,
):
    """Grafico de ranking para paises u organizaciones financiadoras."""
    dataframe = dataframe_from_records(records)

    if dataframe.empty:
        show_empty_state(empty_message)
        return

    ranking = dataframe.sort_values(x, ascending=False).head(top_n)

    figure = px.bar(
        ranking.sort_values(x, ascending=True),
        x=x,
        y=y,
        orientation="h",
        title=title,
        text=x,
        color=x,
        color_continuous_scale="Tealgrn",
    )
    figure.update_layout(
        coloraxis_showscale=False,
        margin=dict(l=12, r=12, t=44, b=8),
        height=300,
    )
    figure.update_traces(hovertemplate="%{y}<br>%{x}<extra></extra>")
    st.plotly_chart(
        figure,
        use_container_width=True,
        config={"displayModeBar": False},
    )


def select_label(
    item: dict[str, Any],
    preferred_keys: Iterable[str],
    fallback: str = "Sin nombre",
) -> str:
    """Etiqueta humana para filas que pueden venir con campos opcionales."""
    for key in preferred_keys:
        value = item.get(key)

        if value:
            return str(value)

    return fallback


def render_records_table(records: list[dict[str, Any]], empty_message: str):
    """Tabla reusable con estado vacio explicito."""
    dataframe = dataframe_from_records(records)

    if dataframe.empty:
        show_empty_state(empty_message)
        return

    st.dataframe(dataframe, use_container_width=True, hide_index=True)
