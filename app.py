import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import pymysql

app = Flask(__name__)
CORS(app)

def get_conn():
    ssl_ca = os.environ.get("DB_SSL_CA", "/etc/ssl/certs/ca-certificates.crt")
    kwargs = {
        "host": os.environ["DB_HOST"],
        "port": int(os.environ.get("DB_PORT", 4000)),
        "user": os.environ["DB_USER"],
        "password": os.environ["DB_PASS"],
        "database": os.environ.get("DB_NAME", "clothing_db"),
        "cursorclass": pymysql.cursors.DictCursor,
    }
    if ssl_ca and os.path.exists(ssl_ca):
        kwargs["ssl"] = {"ca": ssl_ca}
    else:
        kwargs["ssl"] = {}
    return pymysql.connect(**kwargs)

@app.get("/")
def health():
    return jsonify({"status": "ok"})

@app.get("/api/products")
def get_products():
    category = request.args.get("category", "").strip()
    q = request.args.get("q", "").strip()

    sql = "SELECT id, sku, name, category, color, price, size, image_url FROM clothing_products WHERE 1=1"
    params = []

    if category and category != "全部":
        sql += " AND category = %s"
        params.append(category)

    if q:
        sql += " AND (name LIKE %s OR sku LIKE %s OR color LIKE %s)"
        like_q = f"%{q}%"
        params.extend([like_q, like_q, like_q])

    sql += " ORDER BY id ASC"

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return jsonify(cur.fetchall())
    finally:
        conn.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
