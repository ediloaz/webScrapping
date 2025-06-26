from pymongo import MongoClient, errors
from config.settings import MONGO_URI, MONGO_DB_NAME, MONGO_COLLECTION_NAME

def check_mongo_connection():
    print()
    print("Verificando conexión con MongoDB Atlas...")
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)  # Timeout rápido
        client.admin.command('ping')  # Comando ligero para verificar conexión

        db = client[MONGO_DB_NAME]
        if MONGO_COLLECTION_NAME not in db.list_collection_names():
            print(f"⚠️  La colección '{MONGO_COLLECTION_NAME}' no existe aún. Será creada al insertar documentos.")
        else:
            print(f"✅ Conectado exitosamente a MongoDB Atlas. Base de datos: '{MONGO_DB_NAME}'")

    except errors.ServerSelectionTimeoutError as err:
        print("❌ Error al conectar con MongoDB Atlas:")
        print(f"   {err}")
        print("   Verifica que el clúster esté activo y tu IP esté autorizada.")
        exit(1)  # Terminar el programa si no hay conexión

    except Exception as e:
        print("❌ Se produjo un error inesperado al verificar MongoDB:")
        print(f"   {e}")
        exit(1)
