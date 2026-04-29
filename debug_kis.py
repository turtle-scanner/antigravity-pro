import os
import sys
import importlib.util

file_path = "g:/내 드라이브/ANTI GRAVITY/자동매매설정/full_terminal_app_v5.5_Integrated_Final.py"
module_name = "app"

spec = importlib.util.spec_from_file_location(module_name, file_path)
app = importlib.util.module_from_spec(spec)
sys.modules[module_name] = app
try:
    spec.loader.exec_module(app)
except Exception as e:
    pass

print("--- DEBUG INFO ---")
print("KEY:", repr(app.KIS_APP_KEY))
print("SECRET (first 10):", repr(app.KIS_APP_SECRET[:10]) if app.KIS_APP_SECRET else None)
print("MOCK:", app.KIS_MOCK_TRADING)

import requests
url = "https://openapi.koreainvestment.com:9443/oauth2/tokenP" if not app.KIS_MOCK_TRADING else "https://openapivts.koreainvestment.com:29443/oauth2/tokenP"
headers = {"content-type": "application/json"}
body = {
    "grant_type": "client_credentials",
    "appkey": app.KIS_APP_KEY,
    "appsecret": app.KIS_APP_SECRET
}
res = requests.post(url, headers=headers, json=body, timeout=5)
print("HTTP STATUS:", res.status_code)
print("RESPONSE TEXT:", res.text)
print("TOKEN FUNC CALL:", app.get_kis_access_token())
