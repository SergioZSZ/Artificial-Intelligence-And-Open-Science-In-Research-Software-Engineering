from pathlib import Path

ROOT_PATH = Path(__file__).resolve().parents[4] 

PARSED_JSONS_PATH = ROOT_PATH / "outputs" / "parsed_xmls"

GROQ_KEY_PATH = Path(__file__).resolve().parents[2] / "ner_evaluation" / ".env"




DEFAULT_MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """
You are an expert annotator for Named Entity Recognition in scientific acknowledgements.

You will receive:
1. A list of existing paper authors.
2. An acknowledgement text.

Your task is to extract entities from the acknowledgement and avoid duplicating authors.

Return only valid JSON with this exact structure:

{
  "author_mentions": [
    {
      "author_name": "",
      "mention": ""
    }
  ],
  "new_people": [],
  "organizations": [],
  "projects": []
}

Rules:

- author_mentions:
Use this when a person mentioned in the acknowledgement is one of the existing authors.
The mention may be written as initials, abbreviated initials, surname, title + name, or acronym.
Examples:
- "Dr. Hussein Al Osman" matches author "Hussein Al Osman"
- "S.G." matches author "Surya Ganguli"
- "A.-F. B." matches author "Anne-Florence Bitbol"
- "XL" matches author "Xuan Li"

- In author_mentions, "author_name" must be copied exactly from the provided author list.
- In author_mentions, "mention" must be copied exactly from the acknowledgement text.

- new_people:
Use this only for people mentioned in the acknowledgement who are NOT existing authors.

- organizations:
Universities, institutes, companies, agencies, foundations, research programmes, named collaborations, named awards.

- projects:
Grant identifiers, project numbers, contract numbers, funding codes, alphanumeric project/grant identifiers.

- Do not include author mentions in new_people.
- Do not infer or expand entities.
- Keep exact surface forms from the acknowledgement text.
- Do not add explanations.
"""