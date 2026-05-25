# Online Enrichment

Enriquece los JSONs con topics y similarities añadiéndoles datos de tres fuentes externas:

- **OpenAIRE** → datos de proyectos: título, fechas y cantidad financiada
- **Wikidata** → datos de organizaciones: descripción y país
- **ORCID** → datos de personas: identificador único y afiliación

Los JSONs de entrada están en `outputs/topics/enriched_jsons/` y los resultados se guardan en `outputs/topics/kg_enriched/`.

---

## Scripts

### openaire.py

Consulta la API REST de OpenAIRE con el código del proyecto y extrae sus datos. Si no lo encuentra devuelve "None".

### wikidata.py

Consulta Wikidata con SPARQL buscando la organización por nombre en inglés y obteniendo su país.

### orcid.py

Busca una persona en dos pasos: primero obtiene el ORCID ID por nombre y apellido, luego con ese ID pide el perfil completo para sacar la afiliación.

### enrich_online.py

Script principal que coordina todo. Antes de llamar a las APIs hace dos limpiezas:

- **Identificadores de proyectos**: el LLM a veces devuelve el código con texto de más (por ejemplo: "grant agreement No. 851173"). Se extrae solo el código real con expresiones regulares. Los nombres de programas como por ejemplo "Horizon 2020" se descartan porque no son códigos de proyectos.
- **Nombres de organizaciones**: se quita el acrónimo entre paréntesis antes de buscar en Wikidata (por ejemplo "European Research Council (ERC)" pasa a ser "European Research Council").

---

## Replicación

```bash
cd assigment_2/step_4/online_enrichment/scripts
poetry run python enrich_online.py
```

---

## Limitaciones conocidas

- ORCID no permite buscar por iniciales ni pseudónimos y por tanto esas personas quedan sin datos.
- Wikidata no tiene país para organizaciones supranacionales como la UE y por tanto quedan sin país en el grafo.
- Algunos perfiles de ORCID están desactualizados y por tanto la afiliación puede quedar como "null".
- ORCID devuelve el primer perfil que coincide con el nombre y apellido buscados por lo que en el caso de que existan varias personas con el mismo nombre, puede que el perfil seleccionado no corresponda al autor real del paper.

---

## Declaración de uso de IA

Se usó IA generativa como apoyo en partes del desarrollo de los scripts, especialmente para resolver dudas técnicas concretas como el uso de expresiones regulares para limpiar identificadores de proyectos y la navegación por las respuestas JSON de las APIs. El resultado fue revisado y validado por el grupo.
