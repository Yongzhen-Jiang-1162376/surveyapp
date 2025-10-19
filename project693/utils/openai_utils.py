from openai import OpenAI
import os
from project693.dao.plant_dao import PlantDAO


# fetch plant description from OpenAI
def fetch_plant_info_from_openai(name):
    prompt = f"Provide a short, informative description of the plant '{name}' including whether it is invasive, within 2-3 paragraphs. Use **bold** for important words."

    # Use the Responses API
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    try:
        response = client.responses.create(
            # model="gpt-5-nano",
            model="gpt-4.1-nano",
            input=[
                {"role": "system", "content": "You are a helpful botanist assistant."},
                {"role": "user", "content": prompt}
            ],
            text={
                "format": {
                    "type": "text"
                }
            },
            max_output_tokens=5000
        )
    except Exception as e:
        print({e})
        response = None
    
    if response:
        description = response.output_text or ""
    else:
        description = ""
    return description


# save AI-generated plant description
def save_ai_generated_plant_info(plant_id):
    plant_dao = PlantDAO()
    plant = plant_dao.get_plant_by_id(plant_id)
    
    name = plant.name
    
    # call open ai api to fetch plant description
    description = fetch_plant_info_from_openai(name)
    
    # if we fetched the ai powered description, then update the db 
    if description:
        plant_dao.update_plant_ai_description(plant_id, description)
