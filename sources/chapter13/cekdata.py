from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/cekdata')
def cekdata():
    data = {'name': 'Yefta Tanuwijaya', 'age': 20}
    return jsonify(data)

if __name__ == '__main__':
    app.run(port=5000)