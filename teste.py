import base64
import vertexai
# import vertexai.preview.generative_models as generative_models
from vertexai.generative_models import GenerativeModel, Part, SafetySetting, FinishReason
from dotenv import load_dotenv
import os
import sys


def load_and_verify_dotenv(filepath=os.path.join('dotenv_files', '.env')):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Arquivo .env não foi encontrado no caminho: {filepath}")
    
    load_dotenv(filepath)
    print(f"Arquivo .env carregado de: {filepath}")

load_and_verify_dotenv()


def generate():
    vertexai.init(project=str(os.getenv('PROJECT_ID')), location=str(os.getenv('LOCATION')))
    model = GenerativeModel(
        str(os.getenv('MODEL_NAME')),
    )
    responses = model.generate_content(
        [text1],
        generation_config=generation_config,
        safety_settings=safety_settings,
        stream=True,
    )

    response_text = ""
    for response in responses:
        print(response.text, end="")
        response_text +=(response.text)
        with open('response.txt', 'a') as file:
            file.write(response.text)

    return response_text


text1 = """Explique o que é python em três parágrafos."""

generation_config = {
    "max_output_tokens": 8192,
    "temperature": 1,
    "top_p": 0.95,
}

safety_settings = [
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
    ),
]

generate()