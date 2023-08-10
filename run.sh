#!/bin/bash

# 執行 LINE bot 主程式 (先使用 port 4040)
python3 app.py


if pgrep -x "ngrok" > /dev/null; then
# 如果 ngrok 已經在執行
	echo "ngrok 已經於先前啟動了"
else
	ngrok_start_command="ngrok http 4040"
	tmux send-keys -t "linebotweather":2 "$ngrok_start_command" C-m
	sleep 10
fi

# 讀取公開 url 以設置 webhook
public_url=$(curl -s localhost:4041/api/tunnels | jq -r '.tunnels[0].public_url')
public_url+="/line_webhook"
# 讀取 linebot 的 Channel_Acess_Token
source "config.ini" > /dev/null
channel_token="$bottoken"

# 設定 webhook
curl -X PUT \
-H "Authorization: Bearer $channel_token" \
-H "Content-Type: application/json" \
-d "{\"endpoint\":\"$public_url\"}" \
https://api.line.me/v2/bot/channel/webhook/endpoint
# echo "exit curl by $?"
