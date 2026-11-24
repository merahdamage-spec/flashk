from flask import Blueprint, request, jsonify
from datetime import datetime, timezone
from database.connection import db

pesanan_bp = Blueprint('pesanan', __name__)
collection_produk = db["produk_smartphone"]
collection_pesanan = db["pesanan"]

@pesanan_bp.route("/", methods=["POST"])
def buat_pesanan():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"pesan": "JSON tidak valid"}), 400

    sku = data.get("sku")
    jumlah = data.get("jumlah")
    user_id = data.get("user_id", "GUEST")

    if not isinstance(sku, str) or not sku.strip():
        return jsonify({"pesan": "SKU wajib diisi"}), 400
    if not isinstance(jumlah, int) or isinstance(jumlah, bool) or jumlah <= 0:
        return jsonify({"pesan": "Jumlah harus bilangan bulat positif"}), 400

    # 1. Cek dan Kurangi Stok secara Atomik (Sesuai PDF Hal 14)
    hasil_update = collection_produk.update_one(
        {"sku": sku, "aktif": True, "stok": {"$gte": jumlah}},
        {"$inc": {"stok": -jumlah}}
    )

    if hasil_update.modified_count == 0:
        return jsonify({"pesan": "Stok tidak mencukupi atau produk tidak ditemukan"}), 409

    # 2. Ambil data produk untuk snapshot harga
    produk = collection_produk.find_one({"sku": sku})
    
    # 3. Buat Dokumen Pesanan
    dokumen_pesanan = {
        "nomor_pesanan": f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "user_id": user_id,
        "tanggal": datetime.now(timezone.utc).isoformat(),
        "items": [
            {
                "sku": sku,
                "nama_produk": produk["model"],
                "harga": produk["harga_idr"],
                "jumlah": jumlah,
                "subtotal": produk["harga_idr"] * jumlah
            }
        ],
        "total_harga": produk["harga_idr"] * jumlah,
        "status": "DIPROSES"
    }

    try:
        collection_pesanan.insert_one(dokumen_pesanan)
        return jsonify({"pesan": "Pesanan berhasil dibuat", "data": dokumen_pesanan}), 201
    except Exception as e:
        # Catatan: Idealnya gunakan transaksi (session) untuk rollback stok jika insert gagal.
        # Sesuai arahan PDF hal 14, ini adalah operasi atomik sederhana.
        return jsonify({"pesan": "Gagal membuat pesanan", "error": str(e)}), 500