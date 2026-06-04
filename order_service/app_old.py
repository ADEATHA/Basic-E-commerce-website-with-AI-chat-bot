from flask import Flask, jsonify, request
import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from threading import Timer
import pika

app = Flask(__name__)
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')
EXCHANGE_NAME = 'ecommerce_events'

# DB Settings
DB_HOST = os.getenv('DB_HOST', 'postgres-db')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
DB_NAME = os.getenv('DB_NAME', 'ms_order')

def get_conn():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        dbname=DB_NAME
    )

def init_db():
    # Ensure database exists
    try:
        temp_conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            dbname='postgres'
        )
        temp_conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        with temp_conn.cursor() as cur:
            cur.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{DB_NAME}'")
            if not cur.fetchone():
                cur.execute(f"CREATE DATABASE {DB_NAME}")
        temp_conn.close()
    except Exception as e:
        print(f"Postgres DB check/create failed: {e}")

    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(
            '''
            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                tracking_id TEXT UNIQUE,
                user_id INTEGER,
                full_name TEXT,
                address TEXT,
                phone TEXT,
                items_json TEXT,
                total DOUBLE PRECISION,
                status TEXT,
                created_at TEXT,
                completed_at TEXT
            )
            '''
        )
    conn.commit()
    conn.close()

def row_to_order(row):
    if not row:
        return None
    return {
        'id': row['id'],
        'tracking_id': row['tracking_id'],
        'user_id': row['user_id'],
        'full_name': row['full_name'],
        'address': row['address'],
        'phone': row['phone'],
        'items': json.loads(row['items_json'] or '[]'),
        'total': row['total'] or 0,
        'status': row['status'] or 'PENDING',
        'created_at': row['created_at'],
        'completed_at': row['completed_at']
    }

def publish_event(routing_key: str, payload: dict):
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBITMQ_HOST, heartbeat=30)
        )
        channel = connection.channel()
        channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type='topic', durable=True)
        channel.basic_publish(
            exchange=EXCHANGE_NAME,
            routing_key=routing_key,
            body=json.dumps(payload),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        connection.close()
        return True
    except Exception as e:
        print(f"RabbitMQ publish failed ({routing_key}): {e}")
        return False

@app.put('/<int:order_id>')
def update_order_status(order_id: int):
    data = request.get_json(force=True)
    new_status = data.get('status')
    if not new_status:
        return jsonify({'error': 'Status is required'}), 400

    conn = get_conn()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            'UPDATE orders SET status = %s WHERE id = %s RETURNING *',
            (new_status, order_id)
        )
        row = cur.fetchone()
        conn.commit()
    conn.close()

    if not row:
        return jsonify({'error': 'Order not found'}), 404

    order = row_to_order(row)
    publish_event('order.updated', order)
    return jsonify(order)

@app.get('/health')
def health():
    return jsonify({'service': 'order_service', 'status': 'ok'})

@app.post('/')
def create_order():
    data = request.get_json(force=True)
    created_at = datetime.utcnow().isoformat()
    items_json = json.dumps(data.get('items', []))

    conn = get_conn()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            '''
            INSERT INTO orders (tracking_id, user_id, full_name, address, phone, items_json, total, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            ''',
            (
                None,
                data.get('user_id'),
                data.get('full_name'),
                data.get('address'),
                data.get('phone'),
                items_json,
                float(data.get('total', 0) or 0),
                'PENDING',
                created_at
            )
        )
        order_id = cur.fetchone()['id']
        tracking_id = data.get('tracking_id') or f'ORD-{order_id + 1000}'
        cur.execute('UPDATE orders SET tracking_id = %s WHERE id = %s', (tracking_id, order_id))
        cur.execute('SELECT * FROM orders WHERE id = %s', (order_id,))
        row = cur.fetchone()
        conn.commit()

    order = row_to_order(row)
    conn.close()
    
    publish_event('order.created', order)
    return jsonify(order), 201

@app.get('/')
def list_orders():
    conn = get_conn()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute('SELECT * FROM orders ORDER BY id DESC')
        rows = cur.fetchall()
    conn.close()
    return jsonify([row_to_order(r) for r in rows])

@app.get('/<int:order_id>')
def get_order(order_id: int):
    conn = get_conn()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute('SELECT * FROM orders WHERE id = %s', (order_id,))
        row = cur.fetchone()
    conn.close()
    order = row_to_order(row)
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    return jsonify(order)

init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)

