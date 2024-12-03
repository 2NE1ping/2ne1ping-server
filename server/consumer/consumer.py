from flask import Flask, jsonify
from confluent_kafka import Consumer, KafkaError
import threading
import json

app = Flask(__name__)

# Kafka Consumer 설정
kafka_config = {
    'bootstrap.servers': 'broker:9092',
    'group.id': 'settings-group',
    'auto.offset.reset': 'latest',
    'enable.auto.commit': True,
    'security.protocol': 'PLAINTEXT'
}
consumer = Consumer(kafka_config)
consumer.subscribe(['drowsy-topic'])

# 메시지 상태 저장 (전역 변수)
messages = []

def consume_kafka_messages():
    """Kafka 메시지 실시간 소비"""
    global messages
    while True:
        msg = consumer.poll(1.0)  # 1초 대기하며 메시지 수신
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() != KafkaError._PARTITION_EOF:
                print(f"Consumer error: {msg.error()}")
            continue

        # Kafka 메시지 처리
        try:
            data = json.loads(msg.value().decode('utf-8'))
            print(f"Received message: {data}")
            messages.append(data)
        except Exception as e:
            print(f"Error processing message: {e}")

@app.route('/consume', methods=['GET'])
def get_messages():
    """저장된 메시지 반환"""
    global messages

    if messages:
        # 가장 최근 메시지를 가져옴
        latest_message = messages.pop(0)  # FIFO 방식으로 처리
        status = "drowsy" if latest_message.get("drowsy") == "1" else "not drowsy"

        response = {
            "data": latest_message,
            "status": status
        }
        print(f"Returning response: {response}")
        return jsonify(response), 200
    else:
        print("No messages available")
        return jsonify({"status": "no_data", "message": "No messages available"}), 200


if __name__ == '__main__':
    # Kafka Consumer를 별도의 스레드로 실행
    threading.Thread(target=consume_kafka_messages, daemon=True).start()
    app.run(host='0.0.0.0', port=5001, debug=True)

