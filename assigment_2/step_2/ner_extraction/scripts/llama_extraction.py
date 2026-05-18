import json, os, shutil, re
from core import DEFAULT_MODEL, ROOT_PATH, PARSED_JSONS_PATH, SYSTEM_PROMPT, GROQ_KEY_PATH
from dotenv import load_dotenv
from groq import Groq




load_dotenv(GROQ_KEY_PATH)
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise RuntimeError(f"No se encontró GROQ_API_KEY en {GROQ_KEY_PATH}")


# cliente de groq para peticiones
client = Groq(api_key=api_key)






# funciones auxiliares
## extraccion de autores del json parseado
def get_authors(json_data: dict) -> list[str]:
    return [
        person.get("name")
        for person in json_data.get("people", [])
        if person.get("type") == "author" and person.get("name")
    ]
    
    
## extraccion del acknowledgement del json parseado
def extract_acknowledgement(data: dict) -> str:
    acknowledgement_list = data.get("acknowledgements", "")
    if not acknowledgement_list :
        
        return ""

    acknowledgement = acknowledgement_list[0].get("text")
    return acknowledgement

## función para que llama procese un acknowledgement
def call_llama(acknowledgement_text: str, authors: list[str]):
    user_prompt = {
        "authors": authors,
        "acknowledgement_text": acknowledgement_text
    }
    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": json.dumps(user_prompt, ensure_ascii=False)
            }
        ]
    )

    content = response.choices[0].message.content
    return json.loads(content)


## funcion para nutrir los parsed jsons con los generado del acknowledgement
def feed_json(llama_result: dict,json_data: dict):
    
    mentions = llama_result["author_mentions"]
    people = llama_result["new_people"]
    orgs = llama_result["organizations"]
    projects = llama_result["projects"]
    
    # guardamos menciones para ver cuales son nosotros
    json_data["authors_mentions"] = mentions
    
    
    # personas ya existentes para no duplicar
    existing_people = {
        person.get("name", "").lower()
        for person in json_data["people"]
        if isinstance(person, dict)
    }
    # añadir personas, orgs y  projectos a los datos cargados del json
    for person in people:
        
        if not person or person.lower() in existing_people:
            continue    
        
        json_data["people"].append({
            "name": person,
            "author_order": None,
            "type": "acknowledged_person",
            "orcid": None
        })
        existing_people.add(person.lower())
        
    
    for org in orgs:    
        json_data["organizations"].append({
            "name": org,
            "type": "acknowledged_organization"
        })
        
    for project in projects:
        json_data["projects"].append({
            "identifier": project,
            "type": "acknowledged_project"
        })
        
        
    return json_data






# MAIN
def main():
    
    # creacion de carpeta y truncado
    jsons_dir = ROOT_PATH / "outputs" / "extrated_acknowledgements_parsed_xmls"

    if jsons_dir.exists():
        shutil.rmtree(jsons_dir)

    jsons_dir.mkdir(parents=True, exist_ok=True)
    
    #obtencion de los jsons parseados
    json_files = sorted(PARSED_JSONS_PATH.glob("*.json"))
    print(f"JSONs encontrados: {len(json_files)}")

    # extracción de los acknowledgements y autores envio a llama
    for json_file in json_files:
        print("=" * 80)
        print(f"Procesando: {json_file.name}")

        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        acknowledgement_text = extract_acknowledgement(data)
        authors = get_authors(data)
        
        #si no hay se copia el json original
        if not acknowledgement_text:
            print("No tiene acknowledgements. Se copia sin cambios.")

            output_file = jsons_dir / json_file.name

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            continue
        
        llama_result = call_llama(acknowledgement_text,authors)

        # nutrir los json con lo generado en llama
        final_json = feed_json(llama_result,data)
        
        # generar el fichero json
        output_file = jsons_dir / json_file.name

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(final_json, f, ensure_ascii=False, indent=2)

        print(f"JSON generado: {output_file}")
        
        
        
        
        
        
        # 
        print()


if __name__ == "__main__":
    main()