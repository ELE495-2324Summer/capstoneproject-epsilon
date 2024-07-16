from flask import Flask, request, jsonify
import json
import os
from threading import Thread, Event, Timer
from werkzeug.serving import make_server
#from example import example_func
from main_final import main_function
#from renk_son import color_start

app = Flask(__name__)

# Global variable for controlling the server
server = None
should_update_ip = Event()

# Sabit port numarası
port = 8765

# Global variable for storing the IP address
server_ip = '0.0.0.0'  # Initial IP address

# Endpoint to update server config
@app.route('/update_server_config', methods=['POST'])
def update_server_config():
    data = request.json
    new_ip = data.get('server_ip')

    if new_ip:
        global server_ip
        server_ip = new_ip
        should_update_ip.set()  # Signal to update IP
        return jsonify({"message": "Server configuration updated"}), 200
    return jsonify({"message": "Invalid data"}), 400

# Başlangıçta varsayılan kaybedilen puan
losing_point = [0]

# Kullanıcının girdiği plaka numarasını global bir değişkende saklayın
user_plate_number = None
detected_plate_number = [0] # None olacak deneme yapıyorum

isParkFound = [True]
is_park_stage = [True] #park etme işlemi bitti diyen



@app.route('/update_plate', methods=['POST'])
def update_plate():
    data = request.get_json()
    global user_plate_number
    user_plate_number = data.get('plate_number')
    if user_plate_number:
        print(f'Received plate number: {user_plate_number}')
        #example_func()
        #thread_1 = Thread(target=color_start, args=(losing_point,))
        #thread_1.start()
    
        thread_2 = Thread(target=main_function, args=(user_plate_number, is_park_stage, detected_plate_number, isParkFound,))
        thread_2.start()
        #main_function(user_plate_number, is_park_stage, detected_plate_number, isParkFound)
        return jsonify({'status': 'success', 'message': 'Plate number received'}), 200
    else:
        return jsonify({'status': 'error', 'message': 'Plate number not provided'}), 400

@app.route('/get_losing_point', methods=['GET'])
def get_losing_point():
    global losing_point
    return jsonify({'losing_point': int(losing_point[0])}), 200

@app.route('/check_plate', methods=['POST'])
def check_plate():
    data = request.get_json()
    global detected_plate_number
    detected_plate_number = data.get('detected_plate_number')
    global user_plate_number
    if detected_plate_number:
        if detected_plate_number == user_plate_number:
            return jsonify({'status': 'found', 'message': f'Plate number matched: {detected_plate_number}'}), 200
        else:
            return jsonify({'status': 'not_found', 'message': f'Detected plate number: {detected_plate_number}, but no match found'}), 200
    else:
        return jsonify({'status': 'error', 'message': 'Detected plate number not provided'}), 400

@app.route('/get_external_plate', methods=['GET'])
def get_external_plate():
    global detected_plate_number
    return jsonify({'detected_plate_number': int(detected_plate_number[-1])}), 200

@app.route('/get_park_status', methods=['GET'])
def get_park_status():
    global isParkFound
    return jsonify({'is_park_found': isParkFound[0]}), 200

@app.route('/get_is_park_stage', methods=['GET'])
def get_is_park_stage():
    global is_park_stage
    return jsonify({'is_park_stage': is_park_stage[-1]}), 200

# def increase_losing_point():
#     global losing_point
#     losing_point += 1
#     print(f'Losing point updated: {losing_point}')
#     Timer(10, increase_losing_point).start()
    
# def increase_detected_plate():
#     global detected_plate_number
#     detected_plate_number += 1
#     print(f'Detected plate updated: {detected_plate_number}')
#     Timer(10, increase_detected_plate).start()

# def update_park_status():
#     global isParkFound
#     isParkFound = not isParkFound
#     print(f'Park Status: {isParkFound}')
#     Timer(10, update_park_status).start()
    
# def update_park_stage():
#     global is_park_stage
#     is_park_stage = not is_park_stage
#     print(f'Park Stage: {is_park_stage}')
#     Timer(10, update_park_stage).start()
    
def run_flask():
    global server_ip, server
    print(f"Sunucu başlatılıyor: {server_ip}:{port}")
    server = make_server(server_ip, port, app)
    server.serve_forever()

if __name__ == '__main__':
    def update_ip():
        global server
        while True:
            should_update_ip.wait()  # Wait for signal to update IP
            should_update_ip.clear()
            if server:
                server.shutdown()
            print(f"Updating server IP to {server_ip}...")
            server = make_server(server_ip, port, app)
            thread = Thread(target=server.serve_forever)
            thread.start()

    # Flask sunucusunu arka planda başlat
    thread = Thread(target=run_flask)
    thread.start()

    # Monitor for IP update signals
    update_thread = Thread(target=update_ip)
    update_thread.start()

#     # Kaybedilen puanı artırma işlemini başlat
#     increase_losing_point()

#     # Algılanan plakayı artırma işlemini başlat
#     increase_detected_plate()
    
#     # Plaka durumunu güncelleme
#     update_park_status()
    
#     #Park durumunu güncelleme
#     update_park_stage()