## NCUE_weather_linebot
LINE機器人透過中央氣象局資料，回報彰師大當地天氣
 + 2020年5月 1.0版
   > 查詢天氣基本資訊(氣溫、濕度、風向)
 + 2023年5月 2.0版
   > 新增:
     1. 查詢氣象局天氣預報功能
     2. 查看雷達回波圖
---
## 前置準備
1. 需事先架設好 LINE Bot
2. 中央氣象局-開放資料平台 API 授權碼
   > [由此申請](https://opendata.cwb.gov.tw/index)
3. 環保署開放資料 API key
   > [由此申請](https://data.epa.gov.tw/)
4. 能夠持續執行該程式的後端伺服器
5. 將專案<code>git clone</code>在後端伺服器上，並且在同一個資料夾內建立<code>config.ini</code>文字檔
6. 在此文字檔放入已經申請好的 LINE Bot 、中央氣象局開放資料平台 與 環保署開放資料 的 API keys，項目有：
    + **secret**: LINE Bot 的 Channel Secret
    + **bottoken**: LINE Bot 的 Channel Access Token
    + **cwbtoken**: 中央氣象局開放資料平台的授權碼
    + **epatoken**: 環保署開放資料的API金鑰
   將以上資訊寫成config.ini檔案，文字檔內容如下
