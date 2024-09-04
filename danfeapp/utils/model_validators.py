from django.forms import ValidationError
import base64
import vertexai
from vertexai.generative_models import GenerativeModel, Part, SafetySetting
import os
import re
import json
from project import settings

def ensure_txt_directory_exists():
    media_path = os.path.join(settings.MEDIA_ROOT, 'txt/')
    if not os.path.exists(media_path):
        os.makedirs(media_path)

def validate_pdf(pdf):
    if not pdf.name.lower().endswith('.pdf'):
        raise ValidationError('O arquivo não é um PDF')

def validate_danfe(danfe):
    temp_path = f'/tmp/{danfe.name}'
    if not temp_path.lower().endswith('.pdf'):
        raise ValidationError('O arquivo não é um PDF')

    with open(temp_path, 'wb') as temp_file:
        for chunk in danfe.chunks():
            temp_file.write(chunk)

    try:
        with open(temp_path, 'rb') as file:
            data = file.read()
            document1 = Part.from_data(
                mime_type="application/pdf",
                data=base64.b64encode(data).decode("utf-8"),
            )
            text1 = """Considerando as características típicas de um DANFE (como a presença de informações específicas como CPF/CNPJ do emitente e destinatário, data de emissão, valor total, chave de acesso, etc.)
            Se o arquivo representar um Documento Auxiliar da Nota Fiscal Eletrônica(DANFE), retorne TRUE, se não retorne FALSE. A resposta tem que ser em um JSON com a estrutura: {"is_danfe": ""}"""
            
            response_text, dados_json = generate_validade(document1, text1)
            if not dados_json.get('is_danfe'):
                raise ValidationError('A I.A. não identificou o arquivo como um DANFE')
            if settings.DEBUG:
                ensure_txt_directory_exists()
                media_path = os.path.join(settings.MEDIA_ROOT, 'txt/', danfe.name.replace('.pdf', '.txt'))
                with open(media_path, 'w') as output_file:
                    output_file.write(response_text)
    finally:
        os.remove(temp_path)

def generate_validade(document1, text1):
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
    dados_json = None 
    
    for response in responses:
        print(response.text, end="")
        response_text += response.text        
        linha_json = re.search(r'`json(.*?)`', response_text, re.DOTALL)
        if linha_json:
            json_texto = linha_json.group(1)
            try:
                dados_json = json.loads(json_texto)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                raise ValidationError(f'Error decoding JSON: {e}')        
    
    return response_text, dados_json

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

def save_danfe(danfe):
    temp_path = f'/tmp/{danfe.name}'
    
    with open(temp_path, 'wb') as temp_file:
        for chunk in danfe.chunks():
            temp_file.write(chunk)
    
    try:
        with open(temp_path, 'rb') as file:
            data = file.read()
            document1 = Part.from_data(
                mime_type="application/pdf",
                data=base64.b64encode(data).decode("utf-8"),
            )

            dados_json = generate_danfe(document1)

    finally:
        ...    

def generate_danfe(document1):
    ...