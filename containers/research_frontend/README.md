# Research Frontend

Frontend Streamlit para consultar `research_api` y visualizar el Knowledge Graph de financiacion cientifica.

## Objetivo

La pantalla principal de la demo es `Funding`, con:

- ranking top 5 de paises financiadores;
- ranking top 5 de organizaciones financiadoras;
- filtro por topic aplicado a ambos rankings;
- panel de caracteristicas del pais u organismo seleccionado;
- navegacion directa hacia `Papers` con los filtros elegidos.

Las tablas de Funding muestran `financiacion conocida asociada`. Si el KG no tiene un importe explicito para esa agregacion, la app muestra `N/D` en lugar de `0`, para no confundir ausencia de dato con financiacion cero.
Los rankings ocultan filas con cero papers financiados para que el top 5 no se llene con paises u organismos sin evidencia en el KG.

La pantalla `Papers` usa desplegables cargados desde el KG para pais, topic,
organizacion y proyecto, evitando tener que escribir filtros a mano.
En el detalle de cada paper tambien se muestran los acknowledgements reconocidos,
separando organizaciones y personas.
Autores y personas reconocidas se pueden seleccionar para ver su ficha con ORCID,
afiliacion e identificador KG cuando esos datos existen.

Pantallas disponibles:

- `Overview`: estado de servicios y resumen del KG.
- `Funding`: rankings filtrables y navegacion hacia papers.
- `Papers`: busqueda, filtros y detalle.
- `Projects`: ficha de proyecto/grant y tabla completa.
- `Topics`: topics y salto a papers filtrados.
- `Similarities`: papers similares por paper.
- `SPARQL`: vista avanzada de depuracion.

Tras ejecutar el workflow de n8n y actualizar Fuseki, el boton `Actualizar datos`
limpia la cache de Streamlit y consulta de nuevo la API.

## Ejecucion local

```bash
cd containers/research_frontend
poetry install
$env:RESEARCH_API_URL="http://localhost:8000"
poetry run streamlit run app.py
```

## Ejecucion con Docker Compose

Desde la raiz del repo:

```bash
docker compose -f containers/docker-compose.yml up --build -d research_frontend
```

La app queda disponible en:

```text
http://localhost:8501
```

## Tests

```bash
cd containers/research_frontend
poetry run pytest -q
```

Los tests mockean el cliente HTTP para no depender de Fuseki ni de `research_api` levantados.

## Declaracion de uso de IA

Se uso IA generativa para generar y estructurar el frontend Streamlit siguiendo la guia de los autores. Cada pantalla, flujo de navegacion, estado vacio e integracion con la API fue revisado, probado y evaluado durante el desarrollo.
