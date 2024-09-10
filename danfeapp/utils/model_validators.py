from django.forms import ValidationError
import base64
import vertexai
from vertexai.generative_models import GenerativeModel, Part, SafetySetting
import os
import re
import json
from project import settings
from pymongo import MongoClient


def ensure_txt_directory_exists():
    media_path = os.path.join(settings.MEDIA_ROOT, 'txt/')
    if not os.path.exists(media_path):
        os.makedirs(media_path)

def ensure_json_directory_exists():
    json_path = os.path.join(settings.MEDIA_ROOT, 'json/')
    if not os.path.exists(json_path):
        os.makedirs(json_path)

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
            if dados_json is None:
                raise ValidationError(f'A I.A. não conseguiu verificar se o arquivo {danfe.name} é um DANFE')
            if not dados_json.get('is_danfe'):
                raise ValidationError(f'A I.A. não identificou o arquivo {danfe.name} como um DANFE. A resposta da I.A. foi: {response_text}')
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
        if settings.DEBUG:
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
            text1 = os.getenv('GCLOUD_TEXT_PROMPT')

            dados_json, json_path = generate_danfe(document1,text1,danfe.name)
            print(f"\n\U00002705 Arquivo {danfe.name} salvo com sucesso!")
            return dados_json, json_path
            

    finally:
        os.remove(temp_path)

def generate_danfe(document1,text1,filename):
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
        if settings.DEBUG:
            print(response.text, end="")
        response_text += response.text        
        linha_json = re.search(r'`json(.*?)`', response_text, re.DOTALL)
        if linha_json:
            json_texto = linha_json.group(1)
            try:
                dados_json = json.loads(json_texto)
                if not isinstance(dados_json, dict):
                        raise ValidationError('O JSON gerado não é um dicionário válido')
            except json.JSONDecodeError as e:
                print(f"\n\U0000274C Error decoding JSON: {e}")
                raise ValidationError(f'Error decoding JSON: {e}')
        if dados_json:
            ensure_json_directory_exists()
            json_path = os.path.join(settings.MEDIA_ROOT, 'json/', filename.replace('.pdf', '.json'))
            json_filename = filename.replace('.pdf', '.json')
            try:
                with open(json_path, 'w') as output_file:
                    json.dump(dados_json, output_file, ensure_ascii=False, indent=4)
            finally:
                print(f"\n\U00002705 Arquivo {json_filename} salvo com sucesso em: {json_path}")
    
    return dados_json, json_path

# Função Para Inserir o JSON no Banco de Dados
def insert_json_danfe(dados_json):
    try:
        client = MongoClient(str(os.getenv('MONGODB_HOST')), int(os.getenv('MONGODB_PORT')))
        db = client[str(os.getenv('MONGODB_DB'))]
        colecao = db[str(os.getenv('MONGODB_COLLECTION'))]
        if client is not None and db is not None and colecao is not None:
            print(f"\n\U00002705 Conectado ao banco de dados {os.getenv('MONGODB_DB')} e coleção {os.getenv('MONGODB_COLLECTION')}")
            print(f"\n\U00002705 JSON PATH: {dados_json}")
            colecao.insert_one(dados_json)
            print(f"\n\U00002705 JSON inserido com sucesso no MongoDB.")
        else:
            raise ValidationError('Erro ao conectar ao banco de dados ou coleção não encontrada.')
        print(f"\n\U00002705 JSON inserido com sucesso no MongoDB.")
    
    except Exception as e:
        print(f"\n\U0000274C Ocorreu um erro ao inserir o JSON no MongoDB: {e}")
        raise ValidationError(f'Error inserting JSON: {e}')
    
    finally:
        client.close()
    
