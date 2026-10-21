import json
import requests

# Service A: Reads data from file and returns it as a JSON response
def cekdata():
    with open('data_pribadi.json', 'r') as file_data:
        data_pribadi = json.load(file_data)
    return json.dumps(data_pribadi)

# Service B: Reads data from file, performs some transformation, and writes it to another file
def validasidata():
    with open('data_pribadi.json', 'r') as file_data:
        data_pribadi = json.load(file_data)
    hasil_validasi = {'name': data_pribadi['name'], 'greeting': 'Hello, ' + data_pribadi['name'], 'status': 'verified'}
    with open('hasil_validasi.json', 'w') as file_validasi:
        json.dump(hasil_validasi, file_validasi)
        
def verifikasiumur():
    with open('data_pribadi.json', 'r') as file_data:
        data_pribadi = json.load(file_data)
    if(data_pribadi["age"] >= 17):
        hasil_verifikasi = {'age': data_pribadi["age"], 'status': 'You are old enough'}
    else:
        hasil_verifikasi = {'age': data_pribadi["age"], 'status': 'Sorry not old enough :('}
    with open('hasil_verifikasi.json', 'w') as file_validasi:
        json.dump(hasil_verifikasi, file_validasi)

# Orchestration layer: Calls Service A, sends its response to Service B, and returns the response from Service B
def verifikasidata():
    cek_respon = cekdata()
    headers = {'Content-Type': 'application/json'}
    cek_validasi = requests.post('http://localhost:5001/validasidata', data=cek_respon, headers=headers)
    return cek_validasi.text

def verifikasiumur():
    cek_respon = cekdata()
    headers = {'Content-Type': 'application/json'}
    cek_verifikasi = requests.post('http://localhost:5002/verifikasiumur', data=cek_respon, headers=headers)
    return cek_verifikasi.text

if __name__ == '__main__':
    verifikasidata()
    verifikasiumur()