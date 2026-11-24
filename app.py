from flask import Flask
from database.connection import cek_koneksi

app = Flask(__name__)

# Import routes
from routes.produk import produk_bp
from routes.users import users_bp
from routes.pesanan import pesanan_bp

# Register blueprint
app.register_blueprint(produk_bp, url_prefix='/api/produk')
app.register_blueprint(users_bp, url_prefix='/api/users')
app.register_blueprint(pesanan_bp, url_prefix='/api/pesanan')

@app.route("/", methods=["GET"])
def home():
    return {"pesan": "API Jaya Phone Cell aktif", "status": "success"}, 200

if __name__ == "__main__":
    if cek_koneksi():
        app.run(debug=True)