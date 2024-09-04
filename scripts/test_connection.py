from pymongo import MongoClient

try:
    client = MongoClient('mongodb_danfeapp', 27017)
    # Testa a conexão
    client.server_info()  # Isso fará uma solicitação para o servidor
    print("Conexão com MongoDB bem-sucedida!")
except Exception as e:
    print(f"Erro ao conectar ao MongoDB: {e}")
