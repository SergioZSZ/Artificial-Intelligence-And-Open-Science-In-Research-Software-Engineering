
import re
from pathlib import Path

NS = {"tei": "http://www.tei-c.org/ns/1.0"}

ROOT_DIR = Path(__file__).resolve().parents[3]

# limpiar el texto de saltos de linea o espacios duplicados
def clean_text(value):
    if value is None:
        return None
    return re.sub(r"\s+", " ", value).strip()


# extrae todo el texto de un nodo XML.
def get_text(node):
    if node is None:
        return None
    return clean_text(" ".join(node.itertext()))

# prueba varios paths XPath y devuelve el primer texto encontrado
def first_text(root, paths):
    for path in paths:
        node = root.find(path, NS)
        value = get_text(node)

        if value:
            return value

    return None


def parse_paper(root, xml_path):
    '''
    Paper:
    - title
    - abstract
    - published_date
    '''
    
    # 1º id interno del paper 
    xml_path = Path(xml_path)
    paper_id = xml_path.stem.replace(".tei", "")
    
    # 2º title (paths donde se puede encontrar ordenados)
    title = first_text(root, [
        ".//tei:titleStmt/tei:title[@type='main']",
        ".//tei:titleStmt/tei:title",
        ".//tei:analytic/tei:title"
    ])
    
    # 3º abstract (solo encontrado en path de abstract)
    abstract = first_text(root, [
        ".//tei:profileDesc/tei:abstract"
    ])
    
    # 4º published date
    published_date = None
    date_node = root.find(".//tei:publicationStmt/tei:date[@type='published']", NS)
    
        # si existe la fecha, 1º vemos si está en atributo de nodo when o si no el texto
    if date_node is not None:
        published_date = date_node.attrib.get("when")
        
        if published_date is None:
            published_date = get_text(date_node)
            
    
    return {
    "local_id": paper_id,
    "title" : title,
    "abstract": abstract,
    "published_date": published_date,
    "doi": None
    }
    
            
def parse_people(bibl):
    """
    Person:
    - authors
    - author name
    """

    people = []

    # Si no existe el bloque bibliográfico, no podemos sacar autores.
    if bibl is None:
        return people

    # Buscamos solo los autores del paper principal.
    authors = bibl.findall(".//tei:analytic/tei:author", NS)

    for index, author in enumerate(authors, start=1):

        # Dentro de cada author buscamos el nombre de persona.
        pers_name = author.find("./tei:persName", NS)

        if pers_name is None:
            continue

        # GROBID suele separar el nombre en forename y surname.
        forenames = [
            get_text(forename)
            for forename in pers_name.findall("./tei:forename", NS)
        ]

        surname = get_text(pers_name.find("./tei:surname", NS))

        # Eliminamos valores None.
        name_parts = [name for name in forenames if name]

        if surname:
            name_parts.append(surname)

        # Si tenemos partes separadas, las unimos.
        if name_parts:
            author_name = clean_text(" ".join(name_parts))
        else:
            # Fallback por si GROBID no separó forename/surname.
            author_name = get_text(pers_name)

        # Si sigue sin haber nombre, no añadimos nada.
        if not author_name:
            continue

        people.append({
            "name": author_name,
            "author_order": index,
            "type": "author",
            "orcid": None
        })

    return people
    

    



def parse_acknowledgements(root):


    acknowledgements = []
    seen_texts = set()
        
    for div in root.findall(".//tei:text//tei:div", NS):
        div_type = div.attrib.get("type", "").lower()

        head = get_text(div.find("./tei:head", NS))
        head_lower = (head or "").lower()

        # type="acknowledgement" o head="ACKNOWLEDGMENTS"
        is_ack = (
            "acknowledg" in div_type
            or "acknowledg" in head_lower
        )

        if not is_ack:
            continue

        ack_text = get_text(div)

        if not ack_text:
            continue

        # Evitamos duplicados, porque algunos XML tienen el mismo acknowledgement
        # una vez por type y otra vez por head.
        if ack_text in seen_texts:
            continue

        seen_texts.add(ack_text)

        acknowledgements.append({
            "text": ack_text,
            "needs_llm_extraction": True
        })

    return acknowledgements
    