from pathlib import Path


ROOT_PATH = Path(__file__).resolve().parents[4] 
ENV_PATH = ROOT_PATH / "assigment_2" / "step_2" /"ner_evaluation"/ ".env"
INPUT_DIR = ROOT_PATH /"outputs" / "extrated_acknowledgements_parsed_xmls"
OUTPUT_DIR = ROOT_PATH / "assigment_2" / "step_3" / "outputs" /"topics"
