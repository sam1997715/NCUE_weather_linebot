## NCUE_weather_linebot
LINE機器人透過中央氣象局資料，回報彰師大當地天氣
 + 2020年5月 1.0版
   > 查詢天氣基本資訊(氣溫、濕度、風向)
 + 2023年5月 2.0版
   > 新增查詢氣象局天氣預報功能、查看雷達回波圖
---
## 前置準備
1. 需事先安裝 [Python](https://www.python.org/)，並透過 <code>pip install -r requirements.txt</code> 安裝所需的套件。
2. 需事先申請與架設好 LINE Bot 操作功能。
    + 需要事先設定好 **Webhook** ，以接受使用者傳送的資訊(需使用HTTPS協定)。
    + 需要事先設定好 **圖文選單**，並在對應的區域設定傳送文字。
      可以在[LINE Official Account](https://manager.line.biz)找到，於 主頁>聊天室相關>圖文選單，建立以下功能
      1. 文字 - 雷達回波圖
      2. 文字 - 彰師大兩天天氣預報
      3. 文字 - 現在彰師大空氣
      4. 文字 - 雷達回波圖
      5. 文字 - 彰師大一週天氣預報
      6. 文字 - 現在彰師大天氣
3. 中央氣象局-開放資料平台 API 授權碼。
   > [由此申請](https://opendata.cwb.gov.tw/index)
4. 環保署開放資料 API key。
   > [由此申請](https://data.epa.gov.tw/)
7. 能夠持續執行該程式的後端伺服器。
8. 將專案<code>git clone</code>在後端伺服器上，並且在同一個資料夾內建立<code>config.ini</code>文字檔。
9. 在此文字檔放入已經申請好的 LINE Bot 、中央氣象局開放資料平台 與 環保署開放資料 的 API keys，項目有：
    + **secret**: LINE Bot 的 Channel Secret
    + **bottoken**: LINE Bot 的 Channel Access Token
    + **cwbtoken**: 中央氣象局開放資料平台的授權碼
    + **epatoken**: 環保署開放資料的API金鑰
   
   將以上資訊寫成config.ini檔案，文字檔內容如下：
   
   <img decoding="async" src="https://github.com/sam1997715/NCUE_weather_linebot/blob/main/%E8%AA%AA%E6%98%8E/config%E8%AA%AA%E6%98%8E%E5%9C%96%E7%89%87.png?raw=true" height="50%"></img>
   
8. 在 Terminal 或 cmd 中，將路徑轉移至此專案後，執行
   <pre><code>python app.py</code></pre>
   > 需視安裝環境，指令可能為 <pre><code>python3 app.py</code></pre>

   順利執行後即為完成部署LINE機器人。

---
## 功能介紹


  使用者可以透過功能表快速傳遞訊息給機器人，共有五個功能：
  
   + 現在天氣: 回傳中央氣象局測站彙整資訊 － 溫度、天氣狀態、相對濕度、紫外線指數、風速、風向。
   + 現在空氣: 回傳環保署測站彙整資訊 － AQI、空氣級數、PM2.5、PM10。
   + 逐三小時預報: 回傳中央氣象局未來三天天氣預報，並逐3小時分段預報當下天氣 － 溫度、降雨機率、風向風速、相對濕度。
   + 一週預報: 回傳中央氣象局未來七天天氣預報，並逐12小時分段預報當下天氣 － 溫度、降雨機率、風向風速、相對濕度。
   + 雷達回波圖: 回傳中央氣象局白底台灣附近地區的地圖，並由藍至紅表示降雨強度。

<img decoding="async" src="https://github.com/sam1997715/NCUE_weather_linebot/blob/main/design/LINE%E5%B0%8D%E8%A9%B1%E6%A1%86.png?raw=true" height="20%"></img>

---
## 補充說明
### 雷達回波
  以中央氣象局的雷達回波色階標示來說，當你看到要去的目的地顯示是沒有任何顏色的，恭喜你，非常適合出門，完全不會下雨；如果是藍色，可能要注意空氣會有點潮濕；看到綠色的話，就要準備雨具了，會有小小降雨情形；看到呈現黃色的區域，是一般降雨的程度，可以多安排室內活動；若是紅色或紫色的區域，雨勢加劇，還是乖乖待在家，才不用淋成落湯雞。
  
  提醒你，雷達回波圖的色階標示可能不同，請以各圖所標之色階或dBZ數值為準。
  
  <img decoding="async" src="https://github-production-user-asset-6210df.s3.amazonaws.com/69688053/240967042-883ef4b5-d86d-4739-8002-5793c129332b.png" height="20%"></img>
  
  > 以上說明引用自[中央氣象局官方說明](https://south.cwb.gov.tw/inner/wbIg1572340584AuPg)
