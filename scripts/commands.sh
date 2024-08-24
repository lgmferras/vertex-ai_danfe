#!/bin/sh

# O shell irá encerrar a execução do script quando um comando falhar
set -e

# Aguarda a inicialização do PostgreSQL
while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
  echo "🟡 Waiting for PostgreSQL Database Startup ($POSTGRES_HOST:$POSTGRES_PORT)..."
  sleep 2
done

echo "✅ PostgreSQL Database Started Successfully ($POSTGRES_HOST:$POSTGRES_PORT)"
sleep 1

# Aguarda a inicialização do MongoDB
while ! nc -z $MONGODB_HOST $MONGODB_PORT; do
  echo "🟡 Waiting for MongoDB Database Startup ($MONGODB_HOST:$MONGODB_PORT)..."
  sleep 2
done

echo "✅ MongoDB Database Started Successfully ($MONGODB_HOST:$MONGODB_PORT)"
sleep 1

# Executa os comandos Django
echo 'Executando Collect Static'
python manage.py collectstatic --noinput
echo 'Executando Migrations'
python manage.py makemigrations --noinput
echo 'Aplicando Migrations'
python manage.py migrate --noinput
echo 'Executando Runserver'
python manage.py runserver 0.0.0.0:8000