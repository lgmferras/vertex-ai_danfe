import base64
import vertexai
from vertexai.generative_models import GenerativeModel, Part, SafetySetting, FinishReason
import vertexai.preview.generative_models as generative_models


def generate():
  vertexai.init(project="vast-math-424814-d4", location="us-central1")
  model = GenerativeModel(
    "gemini-1.5-pro-001",
  )
  responses = model.generate_content(
      [text1],
      generation_config=generation_config,
      safety_settings=safety_settings,
      stream=True,
  )

  for response in responses:
    print(response.text, end="")

text1 = """Docker + python + django + google vertex-ai + git

Estou iniciando um projeto com os programas acima, minha estrutura de arquivos e diretórios está abaixo, me ajude a completar o que falta nos arquivos de configuração abaixo, como por exemplo as variáveis de ambiente do mongodb no .env, Dockerfile, commands.sh, requirements.txt, etc...

tree -a
.
├── danfeapp
│  └── requirements.txt
├── docker-compose.yml
├── Dockerfile
├── .dockerignore
├── dotenv_files
│  └── .env
├── .gitignore
├── README.md
└── scripts
  └── commands.sh

Conteúdo:

└── scripts
  └── commands.sh:

#!/bin/sh

# O shell irá encerrar a execução do script quando um comando falhar
set -e

while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
 echo \"🟡 Waiting for Postgres Database Startup ($POSTGRES_HOST $POSTGRES_PORT) ...\"
 sleep 2
done

echo \"✅ Postgres Database Started Successfully ($POSTGRES_HOST:$POSTGRES_PORT)\"

echo \'Executando Collect Static\'
python manage.py collectstatic --noinput
echo \'Executando Migrations\'
python manage.py makemigrations --noinput
echo \'Executando Migrations\'
python manage.py migrate --noinput
echo \'Executando Runserver\'
python manage.py runserver 0.0.0.0:8000


├── docker-compose.yml:

services:
 danfeapp:
  container_name: danfeapp
  build:
   context: .
  ports:
   - 8080:8000 # Mapeia a porta 8080 do host para a porta 8000 do container
  volumes:
   - ./danfeapp:/danfeapp
   - ./data/web/static:/data/web/static/
   - ./data/web/media:/data/web/media/
  env_file:
   - ./dotenv_files/.env
  depends_on:
   - psql
   - mongodb

 psql:
  container_name: psql
  image: postgres:13-alpine
  volumes:
   - ./data/postgres/data:/var/lib/postgresql/data/
  env_file:
  - ./dotenv_files/.env

 mongodb:
  container_name: mongodb
  image: mongo:latest
  ports:
   - 27017:27017 # Porta padrão do MongoDB
  volumes:
   - ./data/mongodb:/data/db
  env_file:
   - ./dotenv_files/.env # Usa o mesmo arquivo .env para o MongoDB


├── dotenv_files
│  └── .env:

SECRET_KEY=\"CHANGE-ME\"

# 0 False, 1 True
DEBUG=\"1\"

# Comma Separated values
ALLOWED_HOSTS=\"127.0.0.1, localhost\"

DB_ENGINE=\"django.db.backends.postgresql\"
POSTGRES_DB=\"danfe_django\"
POSTGRES_USER=\"danfe_user\"
POSTGRES_PASSWORD=\"danfe_password\"
POSTGRES_HOST=\"psql\"
POSTGRES_PORT=\"5432\"

LANGUAGE_CODE=\"pt-br\"
TIME_ZONE=\"America/Sao_Paulo\"

├── Dockerfile:

FROM python:3.11.3-alpine3.18
LABEL maintainer=\"lgmferras@gmail.com\"

# Essa variável de ambiente é usada para controlar se o Python deve
# gravar arquivos de bytecode (.pyc) no disco. 1 = Não, 0 = Sim
ENV PYTHONDONTWRITEBYTECODE 1

# Define que a saída do Python será exibida imediatamente no console ou em
# outros dispositivos de saída, sem ser armazenada em buffer.
# Em resumo, você verá os outputs do Python em tempo real.
ENV PYTHONUNBUFFERED 1

# Copia a pasta \"danfeapp\" e \"scripts\" para dentro do container.
COPY danfeapp /danfeapp
COPY scripts /scripts

# Entra na pasta danfeapp no container
WORKDIR /danfeapp

# A porta 8000 estará disponível para conexões externas ao container
# É a porta que vamos usar para o Django.
EXPOSE 8000

# RUN executa comandos em um shell dentro do container para construir a imagem.
# O resultado da execução do comando é armazenado no sistema de arquivos da
# imagem como uma nova camada.
# Agrupar os comandos em um único RUN pode reduzir a quantidade de camadas da
# imagem e torná-la mais eficiente.
RUN python -m venv /venv && \\
 /venv/bin/pip install --upgrade pip && \\
 /venv/bin/pip install -r /danfeapp/requirements.txt && \\
 adduser --disabled-password --no-create-home duser && \\
 mkdir -p /data/web/static && \\
 mkdir -p /data/web/media && \\
 chown -R duser:duser /venv && \\
 chown -R duser:duser /data/web/static && \\
 chown -R duser:duser /data/web/media && \\
 chmod -R 755 /data/web/static && \\
 chmod -R 755 /data/web/media && \\
 chmod -R +x /scripts

# Adiciona a pasta scripts e venv/bin
# no $PATH do container.
ENV PATH=\"/scripts:/venv/bin:$PATH\"

# Muda o usuário para duser
USER duser

# Executa o arquivo scripts/commands.sh
CMD [\"commands.sh\"]


├── danfeapp
│  └── requirements.txt:

Django>=4.2.1,<4.3
psycopg2-binary>=2.9.6,<2.10
Pillow>=9.5.0,<9.6"""

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