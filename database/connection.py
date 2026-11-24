from pymongo import MongoClient
from config import Config

client = MongoClient(Config.MONGO_URI, serverSelectionTimeoutMS=5000)
db = client[Config.DB_NAME]

def cek_koneksi():
    try:
        client.admin.command("ping")
        print("Koneksi MongoDB berhasil!")
        return True
    except Exception as error:
        print("Koneksi MongoDB gagal:", error)
        return False