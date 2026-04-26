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
    print("Module load error:", e)

token = app.get_kis_access_token(app.KIS_APP_KEY, app.KIS_APP_SECRET, app.KIS_MOCK_TRADING)
print("TOKEN_RESULT:", token)
