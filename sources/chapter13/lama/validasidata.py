from flask import Flask, jsonify, request
import json

app = Flask(__name__)

@app.route('/validasidata', methods=['POST'])
def validasidata():
    data_pribadi = json.loads(request.data)
    hasil_validasi = {'name': data_pribadi['name'], 'greeting': 'Hello, ' + data_pribadi['name'], 'status': 'verified'}
    with open('hasil_validasi.json', 'w') as file_validasi:
        json.dump(hasil_validasi, file_validasi)
    return jsonify(hasil_validasi)

if __name__ == '__main__':
    app.run(port=5001)
