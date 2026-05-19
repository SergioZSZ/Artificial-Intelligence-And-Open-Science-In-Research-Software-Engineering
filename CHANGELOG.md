
# Novedades

## Parseo de XMLs generados por grobid

- añadidos scripts para la extracción de información estructurada:

    - initial_parse.py:
        contiene funciones para el parseo de los datos estructurados del xml generado a partir
        del pdf con los que se puede nutrir el KG

        Actualmente permite extraer:

        - Información del paper:
            - título
            - abstract
            - fecha de publicación
            - identificador local
            - DOI pendiente de enriquecimiento externo

        - Información de autores:
            - nombre
            - orden de autoría
            - ORCID pendiente de enriquecimiento externo

        - Información de acknowledgements:
            - texto bruto de la sección
            - marcado como pendiente de extracción mediante LLM/NER

    - parse_grobid_xml.py:
        Contiene el flujo de parseo de los XML.

        Su función es:

        1. Recorrer los XML generados por GROBID.
        2. Aplicar las funciones de parseo definidas en `initial_parse.py`.
        3. Generar un JSON estructurado por cada paper.
        4. Guardar los resultados en la carpeta de salida correspondiente.
        

## NER y extracción de dichas entidades de los acknowledgements
- Realizado corpus (golden standar) y estudio sobre transformers y LLMs para obtener el mejor para nuestro proyecto (vencedor: LLM `llama-3.3-70b-versatile`)

- Uso de LLM ``llama-3.3-70b-versatile`` para reconocimiento de entidades en "acknowledgements". El objetivo es extraer:

    - personas mencionadas
    - organizaciones financiadoras
    - proyectos
    - identificadores de grants/awards
    - posibles relaciones entre proyectos y financiadores



## Próximas integraciones
- Generación de TopicModeling mediante Transformers (BERTopic) Estos resultados se utilizarán para nutrir el KG con:

    - instancias de `Topic`
    - keyword strings representativos
    - relación entre papers y topics
    - puntuación de pertenencia paper-topic



- Creación del KG a partir de:
    - datos estructurados extraídos directamente del XML
    - entidades extraídas mediante IA
    - topics generados mediante topic modeling

- Nutrir el KG con información procedente de fuentes externas:

    - **OpenAIRE**: proyectos de investigación, identificadores, acrónimos, convocatorias, financiadores, fechas y financiación cuando esté disponible.
    - **ORCID**: identificadores y metadatos públicos de autores.
    - **Wikidata**: información sobre organizaciones, países, identificadores externos y enlaces semánticos.

