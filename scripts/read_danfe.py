import base64
import vertexai
from vertexai.generative_models import GenerativeModel, Part, SafetySetting
import os
import sys
import re
import json

document1 = Part.from_data(
    mime_type="application/pdf",
    data=base64.b64encode(open(sys.argv[1], "rb").read()).decode("utf-8"),)

text1 = os.getenv('GCLOUD_TEXT_PROMPT')


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

def generate():
    vertexai.init(project=str(os.getenv('GCLOUD_PROJECT_ID')), location=str(os.getenv('GCLOUD_LOCATION')))
    model = GenerativeModel(
        str(os.getenv('GCLOUD_MODEL')),
    )
    responses = model.generate_content(
        [document1, text1],
        generation_config=generation_config,
        safety_settings=safety_settings,
        stream=True,
    )
    response_text = ""
    dados_json = None  # Initialize the variable

    for response in responses:        
        response_text += response.text
        linha_json = re.search(r'`json(.*?)`', response_text, re.DOTALL)
        if linha_json:
            # json_texto = linha_json.group(1).replace('""""','').replace('"""','').replace('""','').replace('\\\\"','').replace('\\n', ' ').replace('\n', '').replace('\\', '')
            json_texto = linha_json.group(1)
            try:
                dados_json = json.loads(json_texto)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                # Optional: Handle the error here, e.g., log the error, retry, etc.
                pass  # You can add custom handling here

    # Grava o JSON e o texto fora do loop
    if dados_json:
        with open(sys.argv[1].replace('.pdf', '.json'), 'w', encoding='utf-8') as saida_json:
            json.dump(dados_json, saida_json, ensure_ascii=False, indent=4)
    with open(sys.argv[1].replace('.pdf', '.txt'), 'w', encoding='utf-8') as saida_txt:
        saida_txt.write(response_text)

    return response_text, dados_json

# generate()
# Chame a função generate e armazene as saídas nas variáveis
response_text, dados_json = generate()

# Agora, você pode utilizar essas variáveis conforme necessário
print("Texto da resposta:")
print(response_text)

print("\nDados JSON extraídos:")
print(dados_json)
