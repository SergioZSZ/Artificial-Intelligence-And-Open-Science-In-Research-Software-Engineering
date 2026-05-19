from pathlib import Path
from rdflib import Namespace

ROOT_PATH = Path(__file__).resolve().parents[4] 

INPUT_DIR = ROOT_PATH /"assigment_2" / "step_3" / "outputs"/ "topics" / "enriched_jsons"
OUTPUT_DIR = ROOT_PATH / "assigment_2" / "step_3" / "outputs"
OUTPUT_FILE = OUTPUT_DIR / "local_kg.ttl"
ONTOLOGY_FILE = ROOT_PATH / "assigment_2" / "step_1" / "ontology" / "ontology.ttl"

BASE = Namespace("https://g4.org/ontology/research-funding#")
SCHEMA = Namespace("https://schema.org/")
