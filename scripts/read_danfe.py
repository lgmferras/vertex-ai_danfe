import base64
import vertexai
import vertexai.preview.generative_models as generative_models
from vertexai.generative_models import GenerativeModel, Part, SafetySetting, FinishReason
from dotenv import load_dotenv
import os
import sys
import re
import json


def load_and_verify_dotenv(filepath=os.path.join('dotenv_files', '.env')):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Arquivo .env não foi encontrado no caminho: {filepath}")
    
    load_dotenv(filepath)
    print(f"Arquivo .env carregado de: {filepath}")

load_and_verify_dotenv()


document1 = Part.from_data(
    mime_type="application/pdf",
    data=base64.b64encode(open(sys.argv[1], "rb").read()).decode("utf-8"),)

text1 = os.getenv('TEXT_PROMPT')


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

def generate():
    vertexai.init(project=str(os.getenv('PROJECT_ID')), location=str(os.getenv('LOCATION')))
    model = GenerativeModel(
        str(os.getenv('MODEL_NAME')),
    )
    responses = model.generate_content(
        [document1, text1],
        generation_config=generation_config,
        safety_settings=safety_settings,
        stream=True,
    )

    response_text = ""
    for response in responses:
        print(response.text, end="")
        response_text +=(response.text)
        linha_json = re.search(r'```json(.*?)```', response_text, re.DOTALL)
        if linha_json:
            json_texto = linha_json.group(1).replace('""','').replace('"""','').replace('""""','').replace('\\\\"','').replace('\\n', ' ').replace('\n', '').replace('\\', '')
            dados_json = json.loads(json_texto)
            mode = 'w' if not os.path.exists(sys.argv[1].replace('.pdf', '.json')) else 'a'
            with open(sys.argv[1].replace('.pdf', '.json'), mode, encoding='utf-8') as saida_json:
                json.dump(dados_json, saida_json, ensure_ascii=False, indent=4)           

    return response_text, dados_json

# generate()
# Chame a função generate e armazene as saídas nas variáveis
response_text, dados_json = generate()

# Agora, você pode utilizar essas variáveis conforme necessário
print("Texto da resposta:")
print(response_text)

print("\nDados JSON extraídos:")
print(dados_json)
