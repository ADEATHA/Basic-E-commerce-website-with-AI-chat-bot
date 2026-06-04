from flask import Flask, jsonify, request
import os
import pymysql
from datetime import datetime

app = Flask(__name__)

# DB Settings
DB_HOST = os.getenv('DB_HOST', 'mysql-db')
DB_PORT = int(os.getenv('DB_PORT', '3306'))
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'root')
DB_NAME = os.getenv('DB_NAME', 'ms_cart')

def get_conn():
    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )

def init_db():
    # Ensure database exists
    try:
        temp_conn = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD
        )
        with temp_conn.cursor() as cur:
            cur.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        temp_conn.commit()
        temp_conn.close()
    except Exception as e:
        print(f"MySQL DB check/create failed ({DB_NAME}): {e}")

    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(
            '''
            CREATE TABLE IF NOT EXISTS cart_items (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                product_id VARCHAR(255),
                quantity INT,
                updated_at VARCHAR(255),
                UNIQUE(user_id, product_id)
            )
            '''
        )
    conn.commit()
    conn.close()

@app.get('/health')
def health():
    return jsonify({'service': 'cart_service', 'status': 'ok'})

@app.get('/<int:user_id>')
def get_cart(user_id: int):
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(
            'SELECT product_id, quantity FROM cart_items WHERE user_id = %s ORDER BY id DESC',
            (user_id,)
        )
        rows = cur.fetchall()
    conn.close()
    return jsonify({'user_id': user_id, 'items': rows})

@app.post('/add')
def add_item():
    data = request.get_json(force=True)
    user_id = int(data.get('user_id', 0))
    product_id = str(data.get('product_id', '')).strip()
    quantity = int(data.get('quantity', 1))

    if not user_id or not product_id:
        return jsonify({'error': 'user_id and product_id are required'}), 400
    if quantity <= 0:
        quantity = 1

    now = datetime.utcnow().isoformat()
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(
            '''
            INSERT INTO cart_items (user_id, product_id, quantity, updated_at)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
              quantity = quantity + %s,
              updated_at = %s
            ''',
            (user_id, product_id, quantity, now, quantity, now)
        )
        conn.commit()
        cur.execute(
            'SELECT product_id, quantity FROM cart_items WHERE user_id = %s ORDER BY id DESC',
            (user_id,)
        )
        rows = cur.fetchall()
    conn.close()
    return jsonify({'message': 'Item added', 'cart': rows})

@app.post('/remove')
def remove_item():
    data = request.get_json(force=True)
    user_id = int(data.get('user_id', 0))
    product_id = str(data.get('product_id', '')).strip()

    if not user_id or not product_id:
        return jsonify({'error': 'user_id and product_id are required'}), 400

    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(
            'DELETE FROM cart_items WHERE user_id = %s AND product_id = %s',
            (user_id, product_id)
        )
        conn.commit()
        cur.execute(
            'SELECT product_id, quantity FROM cart_items WHERE user_id = %s ORDER BY id DESC',
            (user_id,)
        )
        rows = cur.fetchall()
    conn.close()
    return jsonify({'message': 'Item removed', 'cart': rows})

init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)

