from flask import Flask, request, jsonify
from confluent_kafka import Producer
import json

app = Flask(__name__)

producer = Producer({
    'bootstrap.servers': 'broker:9092',  # Kafka 브로커 주소
    'security.protocol': 'PLAINTEXT'
})

def send_to_kafka(topic, message):
    """Kafka로 메시지 전송"""
    try:
        producer.produce(topic, json.dumps(message).encode('utf-8'))
        producer.flush()
        print(f"Sent to Kafka: {message}")
    except Exception as e:
        print(f"Error sending to Kafka: {e}")

# 전송된 데이터를 저장할 리스트 (선택적, 로그용)
received_data = []

# 대역 가중치
weight_theta = 1.0
weight_alpha = 0.5
weight_beta = 0.7

# 졸음 판정 기준
D_THRESHOLD = 0.4

@app.route('/muse2', methods=['POST'])
def receive_brainwave_data():
    """EEG 데이터 수신 및 졸음 판정"""
    try:
        # 요청에서 JSON 데이터 가져오기
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No JSON data received"}), 400

        # 데이터 로그 (선택적)
        received_data.append(data)

        # JSON 데이터를 보기 좋게 출력
        formatted_data = json.dumps(data, indent=4)
        print(f"Received Data:\n{formatted_data}")

        # Theta, Alpha, Beta 값 추출
        theta = data.get("Theta", 0)
        alpha = data.get("Alpha", 0)
        beta = data.get("Beta", 0)

        # 전체 진폭 계산
        total_amplitude = theta + alpha + beta
        if total_amplitude == 0:
            return jsonify({"status": "error", "message": "Invalid amplitude values"}), 400

        # 대역 비율 계산
        rate_theta = theta / total_amplitude
        rate_alpha = alpha / total_amplitude
        rate_beta = beta / total_amplitude

        # 졸음지수 D 계산
        D = weight_theta * rate_theta + weight_alpha * rate_alpha - weight_beta * rate_beta
        print(f"Calculated D: {D}")

        # 졸음 판정
        if D > D_THRESHOLD:
            print("drowsy")
            result = "drowsy"
            kafka_message = {"drowsy": "1"}
            send_to_kafka('drowsy-topic', kafka_message)
        else:
            print("not drowsy")
            result = "not drowsy"

        # 결과 반환
        return jsonify({"status": "success", "drowsiness": result, "D": D}), 200

    except Exception as e:
        print(f"Error while receiving data: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # Flask 서버 실행
    app.run(host='0.0.0.0', port=5001, debug=True)
