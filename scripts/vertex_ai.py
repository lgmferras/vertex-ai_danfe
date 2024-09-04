import base64
import vertexai
from vertexai.generative_models import GenerativeModel, Part, SafetySetting, FinishReason
import vertexai.generative_models as generative_models
import os
import sys
import re
import json

generation_config = {
    "max_output_tokens": 8192,
    "temperature": 1,
    "top_p": 0.95,
}

safety_settings = [
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_ONLY_HIGH
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_ONLY_HIGH
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_ONLY_HIGH
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_ONLY_HIGH
    ),
]

text1 = os.getenv('GCLOUD_TEXT_PROMPT')

def generate():
    vertexai.init(project=str(os.getenv('GCLOUD_PROJECT_ID')), location=str(os.getenv('GCLOUD_LOCATION')))
    model = GenerativeModel(
        str(os.getenv('GCLOUD_MODEL')),
    )
    responses = model.generate_content(
        ["""Gere um exemplo de json com dados de um usuário de um sistema de cadastro de clientes."""],
        generation_config=generation_config,
        safety_settings=safety_settings,
        stream=True,
    )
    response_text = ""  
    dados_json = None  # Inicialize a variável dados_json
    for response in responses:
        response_text += response.text
        linha_json = re.search(r'```json(.*?)```', response_text, re.DOTALL)
        if linha_json:
            json_texto = linha_json.group(1).replace('""""','').replace('"""','').replace('""','').replace('\\\\"','').replace('\\n', ' ').replace('\n', '').replace('\\', '')
            dados_json = json.loads(json_texto)

    # Grava o JSON e o texto fora do loop
    if dados_json:
        with open(sys.argv[1].replace('.pdf', '.json'), 'w', encoding='utf-8') as saida_json:
            json.dump(dados_json, saida_json, ensure_ascii=False, indent=4)
    with open(sys.argv[1].replace('.pdf', '.txt'), 'w', encoding='utf-8') as saida_txt:
        saida_txt.write(response_text)

    return response_text, dados_json

response_text, dados_json = generate()


print("Texto da resposta:")
print(response_text)

print("\nDados JSON extraídos:")
print(dados_json)