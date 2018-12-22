#! conding:utf-8

from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/buy_main')
def buy_main():
    return render_template('buy_main.html')
'''
@app.route('/buy_nfc', methods=["GET"])
def buy_nfc():
    try:
        value = request.args.get("value")
    except:
        print("ERROR! Can't GET value\n")
    
    return render_template('buy_nfc.html', value=value)
'''
if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8080)