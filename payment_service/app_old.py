from flask import Flask, jsonify, request
import os
import json
import pymysql
import threading
from datetime import datetime
import pika

app = Flask(__name__)
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')
EXCHANGE_NAME = 'ecommerce_events'
QUEUE_NAME = 'payment_order_created'

# DB Settings
DB_HOST = os.getenv('DB_HOST', 'mysql-db')
DB_PORT = int(os.getenv('DB_PORT', '3306'))
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'root')
DB_NAME = os.getenv('DB_NAME', 'ms_payment')

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
            CREATE TABLE IF NOT EXISTS payments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                order_id INT UNIQUE,
                amount DOUBLE,
                method VARCHAR(100),
                status VARCHAR(50),
                created_at VARCHAR(100),
                source VARCHAR(50)
            )
            '''
        )
    conn.commit()
    conn.close()

def row_to_payment(row):
    if not row:
        return None
    return {
        'id': row['id'],
        'order_id': row['order_id'],
        'amount': row['amount'],
        'method': row['method'],
        'status': row['status'],
        'created_at': row['created_at'],
        'source': row['source']
    }

def publish_event(routing_key: str, payload: dict):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, heartbeat=30))
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

def upsert_payment(order_id: int, amount: float, method: str, source: str):
    created_at = datetime.utcnow().isoformat()
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(
            '''
            INSERT INTO payments (order_id, amount, method, status, created_at, source)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
              amount = %s,
              method = %s,
              status = %s,
              source = %s
            ''',
            (order_id, amount, method, 'PAID', created_at, source, amount, method, 'PAID', source)
        )
        conn.commit()
        cur.execute('SELECT * FROM payments WHERE order_id = %s', (order_id,))
        row = cur.fetchone()
    conn.close()

    payment = row_to_payment(row)
    publish_event('payment.success', payment)
    return payment

def consume_order_created():
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, heartbeat=30))
            channel = connection.channel()
            channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type='topic', durable=True)
            channel.queue_declare(queue=QUEUE_NAME, durable=True)
            channel.queue_bind(exchange=EXCHANGE_NAME, queue=QUEUE_NAME, routing_key='order.created')

            def callback(ch, method, properties, body):
                try:
                    payload = json.loads(body.decode('utf-8'))
                    order_id = int(payload.get('id'))
                    amount = float(payload.get('total', 0) or 0)
                    upsert_payment(order_id, amount, 'COD', 'event')
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                except Exception as cb_err:
                    print(f"payment consumer error: {cb_err}")
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)
            channel.start_consuming()
        except Exception as e:
            print(f"payment consumer reconnecting: {e}")
            import time
            time.sleep(5)

@app.get('/health')
def health():
    return jsonify({'service': 'payment_service', 'status': 'ok'})

@app.post('/')
def create_payment():
    data = request.get_json(force=True)
    order_id = int(data.get('order_id'))
    amount = float(data.get('amount', 0) or 0)
    method = data.get('method', 'COD')
    payment = upsert_payment(order_id, amount, method, 'api')
    return jsonify(payment), 201

@app.get('/')
def list_payments():
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute('SELECT * FROM payments ORDER BY id DESC')
        rows = cur.fetchall()
    conn.close()
    return jsonify([row_to_payment(r) for r in rows])

@app.get('/order/<int:order_id>')
def get_payment_by_order(order_id: int):
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute('SELECT * FROM payments WHERE order_id = %s', (order_id,))
        row = cur.fetchone()
    conn.close()
    payment = row_to_payment(row)
    if not payment:
        return jsonify({'error': 'Payment not found'}), 404
    return jsonify(payment)

init_db()
consumer_thread = threading.Thread(target=consume_order_created, daemon=True)
consumer_thread.start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)

