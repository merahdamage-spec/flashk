from flask import Blueprint, request, jsonify
from database.connection import db
import hashlib # Contoh sederhana untuk hash password

users_bp = Blueprint('users', __name__)
collection = db["users"]

@users_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data or "email" not in data or "password" not in data:
        return jsonify({"pesan": "Data tidak lengkap"}), 400
    
    # Hash password sederhana (Untuk produksi gunakan bcrypt/werkzeug)
    hashed_pw = hashlib.sha256(data["password"].encode()).hexdigest()
    
    user_data = {
        "email": data["email"],
        "password": hashed_pw,
        "role": data.get("role", "pelanggan") # default pelanggan
    }
    
    try:
        hasil = collection.insert_one(user_data)
        return jsonify({"id": str(hasil.inserted_id), "pesan": "User berhasil didaftarkan"}), 201
    except Exception as e:
        return jsonify({"pesan": "Gagal mendaftar", "error": str(e)}), 500