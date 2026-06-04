from flask import Flask, jsonify, request
import json
import os
import pymysql
import threading
from datetime import datetime
from threading import Timer
import pika

app = Flask(__name__)
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')
EXCHANGE_NAME = 'ecommerce_events'
QUEUE_NAME = 'shipping_payment_success'

# DB Settings
DB_HOST = os.getenv('DB_HOST', 'mysql-db')
DB_PORT = int(os.getenv('DB_PORT', '3306'))
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'root')
DB_NAME = os.getenv('DB_NAME', 'ms_shipping')

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
            CREATE TABLE IF NOT EXISTS shipments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                order_id INT UNIQUE,
                carrier VARCHAR(255),
                status VARCHAR(50),
                created_at VARCHAR(100),
                delivered_at VARCHAR(100),
                source VARCHAR(50)
            )
            '''
        )
    conn.commit()
    conn.close()

def row_to_shipment(row):
    if not row:
        return None
    return {
        'id': row['id'],
        'order_id': row['order_id'],
        'carrier': row['carrier'],
        'status': row['status'],
        'created_at': row['created_at'],
        'delivered_at': row['delivered_at'],
        'source': row['source']
    }

def mark_shipment_delivered(order_id: int):
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute('SELECT id, status FROM shipments WHERE order_id = %s', (order_id,))
        row = cur.fetchone()
        if not row:
            conn.close()
            return
        if row['status'] == 'PREPARING':
            cur.execute(
                'UPDATE shipments SET status = %s, delivered_at = %s WHERE order_id = %s',
                ('DELIVERED', datetime.utcnow().isoformat(), order_id)
            )
            conn.commit()
    conn.close()

def schedule_delivery(order_id: int, delay_seconds: int = 30):
    timer = Timer(delay_seconds, mark_shipment_delivered, args=[order_id])
    timer.daemon = True
    timer.start()

def upsert_shipment(order_id: int, carrier: str, source: str):
    created_at = datetime.utcnow().isoformat()
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(
            '''
            INSERT INTO shipments (order_id, carrier, status, created_at, delivered_at, source)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
              carrier = %s,
              source = %s
            ''',
            (order_id, carrier, 'PREPARING', created_at, None, source, carrier, source)
        )
        conn.commit()
        cur.execute('SELECT * FROM shipments WHERE order_id = %s', (order_id,))
        row = cur.fetchone()
    conn.close()

    shipment = row_to_shipment(row)
    if shipment and shipment.get('status') == 'PREPARING':
        schedule_delivery(order_id, 30)
    return shipment

def consume_payment_success():
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, heartbeat=30))
            channel = connection.channel()
            channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type='topic', durable=True)
            channel.queue_declare(queue=QUEUE_NAME, durable=True)
            channel.queue_bind(exchange=EXCHANGE_NAME, queue=QUEUE_NAME, routing_key='payment.success')

            def callback(ch, method, properties, body):
                try:
                    payload = json.loads(body.decode('utf-8'))
                    order_id = int(payload.get('order_id'))
                    upsert_shipment(order_id, 'Standard Express', 'event')
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                except Exception as cb_err:
                    print(f"shipping consumer error: {cb_err}")
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)
            channel.start_consuming()
        except Exception as e:
            print(f"shipping consumer reconnecting: {e}")
            import time
            time.sleep(5)

@app.get('/health')
def health():
    return jsonify({'service': 'shipping_service', 'status': 'ok'})

@app.post('/')
def create_shipment():
    data = request.get_json(force=True)
    order_id = int(data.get('order_id'))
    carrier = data.get('carrier', 'Standard Express')
    shipment = upsert_shipment(order_id, carrier, 'api')
    return jsonify(shipment), 201

@app.get('/')
def list_shipments():
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute('SELECT * FROM shipments ORDER BY id DESC')
        rows = cur.fetchall()
    conn.close()
    return jsonify([row_to_shipment(r) for r in rows])

@app.get('/order/<int:order_id>')
def get_shipment_by_order(order_id: int):
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute('SELECT * FROM shipments WHERE order_id = %s', (order_id,))
        row = cur.fetchone()
    conn.close()
    shipment = row_to_shipment(row)
    if not shipment:
        return jsonify({'error': 'Shipment not found'}), 404
    return jsonify(shipment)

init_db()
consumer_thread = threading.Thread(target=consume_payment_success, daemon=True)
consumer_thread.start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
