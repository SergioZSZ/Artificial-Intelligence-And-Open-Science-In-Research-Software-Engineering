# Limitaciones de la FASE 2

- La calidad del KG depende de la calidad de los XMLs generados por GROBID y de los acknowledgements disponibles en cada paper.
- Algunos papers no tienen acknowledgements o no contienen entidades reconocibles, por lo que quedan con menos relaciones.
- Los modelos LLM usados para NER pueden variar con el tiempo si se consumen via API, incluso con temperatura baja.
- ORCID no siempre permite desambiguar personas con el mismo nombre; puede devolver un perfil que no corresponda exactamente al autor real.
- ORCID no siempre dispone de afiliacion actualizada.
- Wikidata no siempre dispone de pais para organizaciones supranacionales o ambiguas.
- OpenAIRE no siempre devuelve fechas, financiador o cantidad financiada para todos los proyectos.
- La financiacion se muestra como importe conocido asociado, no como reparto contable exacto por pais u organizacion.
- La moneda se conserva cuando el enriquecimiento online la proporciona, pero los rankings agregados pueden reunir importes en varias monedas y no realizan conversion entre divisas.
- No todos los papers o entidades tienen ORCID, pais, afiliacion o importe disponible.
- Las relaciones proyecto-financiador se infieren de forma conservadora para evitar relaciones all-to-all; esto reduce falsos positivos, pero puede dejar relaciones sin enlazar cuando el dato no es explicito.
- Fuseki debe tener cargado el TTL actualizado antes de consultar la app.
- El boton `Actualizar datos` de Streamlit solo limpia cache y vuelve a consultar la API; no reconstruye el KG.
