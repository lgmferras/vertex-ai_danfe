FROM ubuntu:22.04
LABEL maintainer="lgmferras@gmail.com"

# Essa variável de ambiente é usada para controlar se o Python deve 
# gravar arquivos de bytecode (.pyc) no disco. 1 = Não, 0 = Sim
ENV PYTHONDONTWRITEBYTECODE 1

# Define que a saída do Python será exibida imediatamente no console ou em 
# outros dispositivos de saída, sem ser armazenada em buffer.
# Em resumo, você verá os outputs do Python em tempo real.
ENV PYTHONUNBUFFERED 1

# Copia a pasta "danfeapp" e "scripts" para dentro do container.
COPY danfeapp /danfeapp
COPY scripts /scripts

# Entra na pasta danfeapp no container
WORKDIR /danfeapp

# A porta 8000 estará disponível para conexões externas ao container
# É a porta que vamos usar para o Django.
EXPOSE 8000

# Define a variável de ambiente DEBIAN_FRONTEND para noninteractive.
ENV DEBIAN_FRONTEND=noninteractive
# Define a variável de ambiente TZ para America/Sao_Paulo.
ENV TZ=America/Sao_Paulo

# RUN executa comandos em um shell dentro do container para construir a imagem. 
# O resultado da execução do comando é armazenado no sistema de arquivos da 
# imagem como uma nova camada.
# Agrupar os comandos em um único RUN pode reduzir a quantidade de camadas da 
# imagem e torná-la mais eficiente.
RUN apt-get update && apt-get install -y \
  python3 \
  python3-pip \
  python3-venv \
  build-essential \
  netcat \
  tzdata \
  sudo \
  && rm -rf /var/lib/apt/lists/* && \ 
  python3 -m venv /venv && \
  /venv/bin/pip install --upgrade pip && \
  /venv/bin/pip install -r /danfeapp/requirements.txt && \
  adduser --disabled-password --gecos "" duser && \
  usermod -aG sudo duser && \
  echo "duser ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers && \
  mkdir -p /data/web/static && \
  mkdir -p /data/web/media && \
  sudo chown -R duser:duser /venv && \
  sudo chown -R duser:duser /data && \
  sudo chown -R duser:duser /data/web/static && \
  sudo chown -R duser:duser /data/web/media && \
  sudo chmod -R 755 /data && \
  chmod -R +x /scripts
ENV PATH="/scripts:/venv/bin:$PATH"
USER duser
CMD ["commands.sh"]