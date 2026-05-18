from pathlib import Path
import json
import xml.etree.ElementTree as et
from natsort import natsorted

from auxiliar import parse_acknowledgements, parse_paper, parse_people

# Namespace de TEI
NS = {"tei": "http://www.tei-c.org/ns/1.0"}

ROOT_DIR = Path(__file__).resolve().parents[3]


# crea el json y le hace dump
def create_json(
    paper: dict,
    people: dict,
    acknowledgements: dict,
    output_file: Path
) -> Path:

    json_parse = {
        "paper": paper,
        "people": people,
        "organizations": [],
        "projects": [],
        "countries": [],
        "topics": [],
        "acknowledgements": acknowledgements
    }

    with output_file.open("w", encoding="utf-8") as f:
        json.dump(json_parse, f, indent=2, ensure_ascii=False)

    return output_file


# parseo de un solo paper
def parse_xml(xml_path: Path, output_file: Path) -> Path:
    tree = et.parse(xml_path)
    root = tree.getroot()

    bibl = root.find(".//tei:sourceDesc/tei:biblStruct", NS)

    paper = parse_paper(root, xml_path)

    if bibl is not None:
        people = parse_people(bibl)
    else:
        print(f"    WARNING: {xml_path.name} no tiene biblStruct")
        people = []

    acknowledgements = parse_acknowledgements(root)

    return create_json(
        paper=paper,
        people=people,
        acknowledgements=acknowledgements,
        output_file=output_file
    )


# parseo de todos los xmls
def parse_all():
    xmls_dir = ROOT_DIR / "outputs" / "xmls"
    output_dir = ROOT_DIR / "outputs" / "parsed_xmls"

    # Comprobamos que la carpeta de XMLs exista
    if not xmls_dir.exists():
        raise FileNotFoundError(f"ERROR: No existe la carpeta de XMLs: {xmls_dir}")

    # Creamos carpeta de salida
    output_dir.mkdir(parents=True, exist_ok=True)

    # Limpiamos JSONs antiguos para que no se acumulen
    for old_json in output_dir.glob("*.json"):
        old_json.unlink()

    # Buscamos solo ficheros que acaben en .tei.xml
    xml_files = [
        file_name
        for file_name in xmls_dir.iterdir()
        if file_name.name.endswith(".tei.xml")
    ]

    # Orden natural: paper1, paper2, ..., paper10
    xml_files = natsorted(xml_files, key=lambda path: path.name)

    if not xml_files:
        raise FileNotFoundError(f"ERROR: No se encontraron XMLs .tei.xml en: {xmls_dir}")

    generated_jsons = []
    failed_xmls = []

    # Procesamos los XML uno a uno
    for i, xml_path in enumerate(xml_files, start=1):
        print(f"Parseando {xml_path.name}...")

        # Guarda como paper_01.json, paper_02.json, ...
        output_file = output_dir / f"paper_{i:02d}.json"

        try:
            output_json = parse_xml(xml_path, output_file)
            generated_jsons.append(output_json)

        except Exception as e:
            print(f"    ERROR parseando {xml_path.name}: {e}")
            failed_xmls.append(xml_path.name)
            continue

    print(f"\nXML procesados correctamente: {len(generated_jsons)}")
    print(f"XML con error: {len(failed_xmls)}")

    if failed_xmls:
        print("\nXMLs que han fallado:")
        for xml in failed_xmls:
            print(f"    {xml}")

    return generated_jsons


if __name__ == "__main__":
    parse_all()