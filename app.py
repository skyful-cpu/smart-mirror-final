from flask import Flask, render_template, request, jsonify, make_response
import json
import ssl

import static.assets.py.IoT as IoT
import static.assets.py.Recognizer as Recognizer

app = Flask(__name__)
#__name__ 인자는 정적파일과 템플릿을 찾는 데 쓰임 
import crawling
iot = IoT.IoT()

@app.route('/')
def hello():
    news_list, href, img = crawling.news_crawling()
    img_list = crawling.img_src(news_list)
    sum_list = crawling.summary(news_list)

    return render_template('index.html', news_list = news_list, href = href, img = img, img_list=img_list, len = len(news_list), sum = sum_list )
    #return "Hello world"

@app.route('/update_iot', methods=['GET'])
def update_iot_status():
    iot_update_result = iot.get_initial_state()
    # iot_update_result = {'light': 'on', 'boiler': 'on', 'fan': 'on'}

    response = app.response_class(
        response = json.dumps(iot_update_result),
        status = 200,
        mimetype = 'application/json'
    )

    return response

@app.route('/speech_recog', methods=['POST'])
def speech_recognition():
    speech_recog_result = request.get_json()
    user_said = speech_recog_result['speech_recog_result'][0]
    
    response_dict = {}

    recognizer = Recognizer.Recognizer(threshold=0.6)
    command = recognizer.what_user_said(user_said)
    print(command)

    if command != 'no match':
        iot.command = command
        iot.socket.close()
        control_result = iot.control_iot()
        print(control_result)

        response_dict = app.response_class(
            response = json.dumps(control_result),
            status = 200,
            mimetype = 'application/json'
        )

    print('-'*30)
    return response_dict

if __name__ == '__main__':
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    ssl_context.load_cert_chain(certfile='ssl/server.crt', keyfile='ssl/server.key', password='3680')
    
    app.run(debug=True, host='0.0.0.0', port=3680, ssl_context=ssl_context)