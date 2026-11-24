from flask import Blueprint, request, jsonify
from bson import ObjectId
from pymongo.errors import DuplicateKeyError
from database.connection import db

produk_bp = Blueprint('produk', __name__)
collection = db["produk_smartphone"]

# Membuat indeks unik untuk SKU
collection.create_index("sku", unique=True)

def ubah_object_id(data):
    if data and "_id" in data:
        data["_id"] = str(data["_id"])
    return data

@produk_bp.route("/", methods=["GET"])
def tampil_produk():
    data = list(collection.find({"aktif": True}))
    for item in data:
        ubah_object_id(item)
    return jsonify(data), 200

@produk_bp.route("/<id>", methods=["GET"])
def detail_produk(id):
    if not ObjectId.is_valid(id):
        return jsonify({"pesan": "ID produk tidak valid"}), 400
    data = collection.find_one({"_id": ObjectId(id), "aktif": True})
    if not data:
        return jsonify({"pesan": "Produk tidak ditemukan"}), 404
    return jsonify(ubah_object_id(data)), 200

@produk_bp.route("/", methods=["POST"])
def tambah_produk():
    data = request.get_json(silent=True)
    if not data or "sku" not in data:
        return jsonify({"pesan": "Produk tidak lengkap"}), 400
    try:
        hasil = collection.insert_one(data)
        return jsonify({"id": str(hasil.inserted_id), "pesan": "Produk berhasil ditambahkan"}), 201
    except DuplicateKeyError:
        return jsonify({"pesan": "SKU sudah terdaftar"}), 409

@produk_bp.route("/<id>", methods=["PUT"])
def ubah_produk(id):
    if not ObjectId.is_valid(id):
        return jsonify({"pesan": "ID produk tidak valid"}), 400
    data = request.get_json(silent=True)
    hasil = collection.update_one({"_id": ObjectId(id)}, {"$set": data})
    if hasil.matched_count == 0:
        return jsonify({"pesan": "Produk tidak ditemukan"}), 404
    return jsonify({"pesan": "Produk berhasil diperbarui"}), 200

@produk_bp.route("/<id>", methods=["DELETE"])
def hapus_produk(id):
    if not ObjectId.is_valid(id):
        return jsonify({"pesan": "ID produk tidak valid"}), 400
    hasil = collection.delete_one({"_id": ObjectId(id)})
    if hasil.deleted_count == 0:
        return jsonify({"pesan": "Produk tidak ditemukan"}), 404
    return jsonify({"pesan": "Produk berhasil dihapus"}), 200