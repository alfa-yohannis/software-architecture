from flask import Flask, jsonify, request
import json

app = Flask(__name__)

@app.route('/verifikasiumur', methods=['POST'])
def verifikasiumur():
    data_pribadi = json.loads(request.data)
    if(data_pribadi["age"] >= 17):
        hasil_verifikasi = {'age': data_pribadi["age"], 'status': 'You are old enough'}
    else:
        hasil_verifikasi = {'age': data_pribadi["age"], 'status': 'Sorry not old enough :('}
    with open('hasil_verifikasi.json', 'w') as file_validasi:
        json.dump(hasil_verifikasi, file_validasi)
    return jsonify(hasil_verifikasi)

if __name__ == '__main__':
    app.run(port=5002)