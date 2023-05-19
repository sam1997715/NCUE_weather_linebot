from flask import Flask, request, abort
from linebot.models import TextSendMessage
from linebot import LineBotApi
import configparser
import requests
import json
import base64
import hashlib, hmac


app = Flask(__name__)

@app.route('/line_webhook', methods=['POST'])
def webhook():
    config = configparser.ConfigParser()
    config.read('config.ini')

    channel_secret = config.get("API", "secret")
    cwbtoken = config.get("API", "cwbtoken")
    linebot = LineBotApi(config.get("API", "bottoken"))

    body = request.get_data(as_text=True)
    hash = hmac.new(channel_secret.encode('utf-8'), body.encode('utf-8'), hashlib.sha256).digest()
    signature = base64.b64encode(hash)


    # LINE 平台篩選
    if request.headers.get('X-Line-Signature').encode('utf-8') != signature:
        abort(400)

    # 取得body (type==dict)
    payload = request.get_json()

    # 事件處理
    for event in payload['events']:
        # 依照事件型態做處理
        if event['type'] == 'message':
            handle_message_event(event, linebot, cwbtoken)
        elif event['type'] == 'follow':
            handle_follow_event(event, linebot)
        elif event['type'] == 'unfollow':
            handle_unfollow_event(event, linebot)


    return 'OK'

def handle_message_event(event, linebot, cwbtoken):
    # 處理收到訊息
    message = event["message"]["text"]

    if message == "今天彰師大天氣如何":
        result = query_weather(cwbtoken)
        texts = "現在溫度: {} \n天氣狀態: {} \n濕度: {} \n風速: {} \n風向: {}".format(result[0], result[1], result[2], result[3], result[4])
        linebot.reply_message(event["replyToken"],TextSendMessage(text=texts))
    elif message == "雷達回波圖":
        picurl = "https://cwbopendata.s3.ap-northeast-1.amazonaws.com/MSC/O-A0058-003.png"
        linebot.reply_message(event["replyToken"],TextSendMessage(text=texts))
    else:
        linebot.reply_message(event["replyToken"],TextSendMessage(text=message))

def handle_follow_event(event, linebot):
    # 處理開始關注
    pass

def handle_unfollow_event(event, linebot):
    # 處理取消關注
    pass

def query_weather(token):
    params = {"Authorization" : token,
              "locationName" : "彰師大"	# 彰師大
             }
    response = requests.get("https://opendata.cwb.gov.tw/api/v1/rest/datastore/O-A0003-001", params = params)
    datas = json.loads(response.text)
    print(datas)
    for data in datas["records"]["location"][0]["weatherElement"]:
        if data["elementName"] == "TEMP":
            # 溫度 (°C)
            temp = (lambda b:"氣象測站維護中" if b=="-99" else b + " °C")(data["elementValue"])
        elif data["elementName"] == "Weather":
            # 天氣現象 (晴/陰/雨)
            stat = (lambda b:"氣象測站維護中" if b=="-99" else b)(data["elementValue"])
        elif data["elementName"] == "HUMD":
            # 濕度 (%)
            humd = (lambda b:"氣象測站維護中" if b=="-99" else b + " %")(data["elementValue"][-2:])
        elif data["elementName"] == "WDSD":
            # 風速 (m/s)
            wspd = (lambda b:"氣象測站維護中" if b=="-99" else b + " m/s")(data["elementValue"])
        elif data["elementName"] == "WDIR":
            # 風向 (m/s)
            wdir = convert_winddir(data["elementValue"])

    return (temp, stat, humd, wspd, wdir)

def convert_winddir(angle):
    '''
    0~22.5		:北
    22.5~67.5 		:東北
    67.5~112.5		:東
    112.5~157.5		:東南
    157.5~202.5		:南
    202.5~247.5		:西南
    247.5~292.5		:西
    292.5~337.5		:西北
    337.5~360		:北
    '''
    angle = float(angle)
    if (angle >= 0 and angle <= 22.5) or (angle > 337.5 and angle <= 360):
        return "北"
    elif angle > 22.5 and angle <= 67.5:
        return "東北"
    elif angle > 67.5 and angle <= 112.5:
        return "東"
    elif angle > 112.5 and angle <= 157.5:
        return "東南"
    elif angle > 157.5 and angle <= 202.5:
        return "南"
    elif angle > 202.5 and angle <= 247.5:
        return "西南"
    elif angle > 247.5 and angle <= 292.5:
        return "西"
    elif angle > 292.5 and angle <= 337.5:
        return "西北"
    elif angle < 0:
        return "氣象測站維護中"
    else:
        return "未知"

if __name__ == '__main__':
    app.run(port=8443,
            debug=True)
