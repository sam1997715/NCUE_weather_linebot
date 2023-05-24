from flask import Flask, request, abort
from linebot.models import TextSendMessage, ImageSendMessage
from linebot import LineBotApi
import configparser
import requests
import json
import base64
import hashlib, hmac
import datetime


app = Flask(__name__)

@app.route('/line_webhook', methods=['POST'])
def webhook():
    config = configparser.ConfigParser()
    config.read('config.ini')

    channel_secret = config.get("API", "secret")
    tokens = [config.get("API", "cwbtoken"),
              config.get("API", "epatoken")]


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
            handle_message_event(event, linebot, tokens)
        elif event['type'] == 'follow':
            handle_follow_event(event, linebot)
        elif event['type'] == 'unfollow':
            handle_unfollow_event(event, linebot)


    return 'OK'

def handle_message_event(event, linebot, tokens):
    # 處理收到訊息
    message = event["message"]["text"]

    if message == "現在彰師大天氣":
        results = query_weather(tokens[0])
        texts = "現在溫度: {} \n天氣狀態: {} \n濕度: {}\n風速: {} \n風向: {}".format(results[0], results[1], results[2], results[3], results[4])
        linebot.reply_message(event["replyToken"],TextSendMessage(text=texts))
    elif message == "彰師大天氣預報":
        results = query_forecast(tokens[0])
        # {時間:描述}
        texts = ""
        for index in results:
            texts += "{}: {}\n".format(index, results[index])
        texts = texts[:-1]  # 去除最後換行符號
        linebot.reply_message(event["replyToken"], TextSendMessage(text=texts))
    elif message == "雷達回波圖":
        linebot.reply_message(event["replyToken"],ImageSendMessage(original_content_url = "https://cwbopendata.s3.ap-northeast-1.amazonaws.com/MSC/O-A0058-003.png",
                                                                   preview_image_url = "https://cwbopendata.s3.ap-northeast-1.amazonaws.com/MSC/O-A0058-003.png"
                                                                   )
                             )
    elif message == "現在彰師大空氣":
        results = query_airquality(tokens[1])
        texts = "觀測時間: {} \n空氣品質指標(AQI): {} \n空氣{} \nPM2.5: {} \nPM10: {}".format(results[0], results[1], results[2], results[3], results[4])
        linebot.reply_message(event["replyToken"],TextSendMessage(text=texts))
    else:
        linebot.reply_message(event["replyToken"],TextSendMessage(text="無法處理您的訊息: " + message))

def handle_follow_event(event, linebot):
    # 處理開始關注
    pass

def handle_unfollow_event(event, linebot):
    # 處理取消關注
    pass

def query_weather(token):
    params = {"Authorization" : token,
              "locationName" : "彰師大"	# 直接輸入中文測站名稱
             }
    response = requests.get("https://opendata.cwb.gov.tw/api/v1/rest/datastore/O-A0003-001", params = params)
    datas = json.loads(response.text)

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

def query_airquality(token):
    params = {"api_key": token,
              "offset": "31",   # 彰化市是第31個
              "limit": "1"}     # 只顯示1筆
    response = requests.get("https://data.epa.gov.tw/api/v2/aqx_p_432", params = params)
    queryResult = json.loads(response.text)

    time = queryResult["records"][0]["publishtime"]                  # 觀測時刻
    aqi = queryResult["records"][0]["aqi"]                           # AQI指數
    pm25 = queryResult["records"][0]["pm2.5"] + " μg/m^3"           # PM2.5
    pm10 = queryResult["records"][0]["pm10"] + " μg/m^3"            # PM10

    if int(aqi) <= 50:
        comment = "良好(綠色)"
    elif int(aqi) <= 100:
        comment = "普通(黃色)"
    elif int(aqi) <= 150:
        comment = "對敏感族群不良(橘色)"
    elif int(aqi) <= 200:
        comment = "對所有族群不良(紅色)"
    elif int(aqi) <= 300:
        comment = "非常不良(紫色)"
    elif int(aqi) <= 500:
        comment = "有害(褐紅)"

    return [time, aqi, comment, pm25, pm10]

def query_forecast(token):
    params = {"Authorization": token,
              "offset": "6",        # 彰化市是第31個
              "limit": "1",         # 只顯示1個
              "elementName": "WeatherDescription",  # 直接回傳預報描述
              "sort": "time"}
    response = requests.get("https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-D0047-017", params=params)
    datas = json.loads(response.text)
    forecasts = datas["records"]["locations"][0]["location"][0]["weatherElement"][0]["time"]
    casts = {}
    for cast in forecasts:
        timestamp = convert_dayformat(cast["startTime"])
        casts.update({timestamp:cast["elementValue"][0]["value"]})

    return casts

def convert_dayformat(time):
    datetimeObj = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
    wday = datetimeObj.weekday()
    if wday == 0:
        weekday = "一"
    elif wday == 1:
        weekday = "二"
    elif wday == 2:
        weekday = "三"
    elif wday == 3:
        weekday = "四"
    elif wday == 4:
        weekday = "五"
    elif wday == 5:
        weekday = "六"
    elif wday == 6:
        weekday = "日"

    return "{}/{}({}) {}時".format(datetimeObj.month, datetimeObj.day, wday, datetimeObj.hour)

if __name__ == '__main__':
    app.run(port=8443,
            debug=True)
