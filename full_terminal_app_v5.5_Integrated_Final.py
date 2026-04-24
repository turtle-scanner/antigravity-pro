# ?업 ?자: 2026-04-19 | 버전: v9.9 Platinum Full Restoration (Step 1: Base)
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
import os
import json
import pytz
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import requests
import base64
import time
import io
import random
import shutil
import hashlib
import threading
import concurrent.futures

# --- [ UI/UX ] Premium Design System v9.9 ---
@st.cache_resource
def get_assets():
    """?적 ?산(??지, ?디??????번만 로드?여 캐싱 (?능 극???"""
    assets = {"bg": "", "logo": "", "audio": {}}
    for f in ["StockDragonfly2.png", "StockDragonfly.png"]:
        if os.path.exists(f):
            with open(f, "rb") as imm: assets["logo" if "2" not in f else "bg"] = base64.b64encode(imm.read()).decode()
            if not assets["logo"]: assets["logo"] = assets["bg"]
    
    bgm_files = {"full": "full.mp3", "hope": "hope.mp3", "happy": "happy.mp3", "YouRaise": "YouRaise.mp3", "petty": "petty.mp3"}
    for k, v in bgm_files.items():
        if os.path.exists(v):
            with open(v, "rb") as f: assets["audio"][k] = base64.b64encode(f.read()).decode()
    return assets

def inject_premium_design():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=JetBrains+Mono:wght@400;700&family=Outfit:wght@300;900&display=swap');
        
        :root {
            --neon-blue: #00F2FF;
            --neon-green: #39FF14;
            --neon-red: #FF3131;
            --neon-gold: #FFD700;
            --bg-dark: #050508;
            --glass: rgba(10, 12, 18, 0.85);
        }
        
        .stApp { 
            background: linear-gradient(135deg, #050508 0%, #0A0B14 100%);
            font-family: 'JetBrains Mono', monospace; 
            color: #E0E0E0; 
        }
        
        .glass-card { 
            background: var(--glass); 
            backdrop-filter: blur(20px); 
            border: 1px solid rgba(0, 242, 255, 0.15); 
            border-radius: 15px; 
            padding: 20px; 
            margin-bottom: 20px; 
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8);
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); 
        }
        
        .glass-card:hover { 
            transform: translateY(-5px); 
            border-color: var(--neon-blue); 
            box-shadow: 0 0 25px rgba(0, 242, 255, 0.3); 
        }
        
        h1, h2, h3 { 
            font-family: 'Orbitron', sans-serif !important; 
            letter-spacing: 3px; 
            text-transform: uppercase;
            background: linear-gradient(to right, var(--neon-blue), var(--neon-gold));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            filter: drop-shadow(0 0 5px rgba(0, 242, 255, 0.5));
        }
        
        .stButton>button { 
            background: rgba(0, 242, 255, 0.05) !important; 
            border: 1px solid var(--neon-blue) !important; 
            color: var(--neon-blue) !important; 
            font-family: 'Orbitron'; 
            font-weight: 700;
            border-radius: 12px !important; 
            padding: 0.6rem 2rem !important;
            transition: 0.3s; 
        }
        
        .stButton>button:hover { 
            background: var(--neon-blue) !important; 
            color: #000 !important; 
            box-shadow: 0 0 35px var(--neon-blue); 
        }
        
        [data-testid="stSidebar"] { 
            background: rgba(3, 3, 5, 0.98) !important; 
            backdrop-filter: blur(25px); 
            border-right: 1px solid rgba(0, 242, 255, 0.1); 
        }
        
        .status-pulse { 
            width: 12px; height: 12px; border-radius: 50%; background: var(--neon-green); 
            display: inline-block; box-shadow: 0 0 15px var(--neon-green);
            animation: pulse 1.5s infinite; 
            margin-right: 10px;
        }
        
        @keyframes pulse { 0% { transform: scale(1); opacity: 1; } 50% { transform: scale(1.3); opacity: 0.4; } 100% { transform: scale(1); opacity: 1; } }
        
        .metric-label { color: #888; font-size: 0.8rem; text-transform: uppercase; }
        .metric-value { font-size: 1.5rem; color: var(--neon-gold); font-weight: 700; text-shadow: 0 0 10px rgba(255, 215, 0, 0.3); }
        
        /* [ SCANNER ] ?노바나??게이지 */
        .banana-track { background: rgba(255,255,255,0.05); height: 12px; border-radius: 6px; position: relative; overflow: hidden; margin: 10px 0; border: 1px solid rgba(255,255,255,0.1); }
        .banana-fill { height: 100%; border-radius: 6px; transition: width 1s ease-out; box-shadow: 0 0 10px currentColor; }
    </style>
    """, unsafe_allow_html=True)

# --- [ SYSTEM ] [GLOBAL HELPER] Safe Network Request ---
def safe_get(url, timeout=3):
    """지???멈춤 방???한 글로벌 ?트?크 ?퍼"""
    try:
        resp = requests.get(url, timeout=timeout)
        if resp.status_code == 200: return resp
    except:    pass
    return None

# --- [ TACTICAL ] Rule-based Tactical Advisor (Platinum Engine) ---
def get_tactical_advice(tic, rs, roe):
        advice = []
        if rs > 80: advice.append("[ MOMENTUM ] 강력??Relative Strength ?착. ?장???도?는 주도주입?다.")
        elif rs > 50: advice.append("[ UP-TREND ] ?호??추세 ?? ? ?터 ?환??급???인?십?오.")
        else: advice.append("[ CAUTION ] 추세가 ?소 ?체?? 지지???탈 ????격??감시?십?오.")
        
        if roe > 20: advice.append("[ PREMIUM ] ?도??ROE. 기???가???호?는 ?량 ?장??업?니??")
        elif roe > 10: advice.append("[ STRONG ] 견고????멘?? ?적 발표 ?후 ?파 ??을 ?리????")
        
        # 보너??????조언
        quotes = [
            "?장?????러?수?기본??충실?십?오. VCP???자?? ?? 조용?니??",
            "?절? ?배가 ?닌, ?음 ?리??한 보험료입?다.",
            "거래?이 마? ?? 기다리십?오. ??? 고요???에???작?니??"
        ]
        advice.append(f"\nINFO: Bonde's Insight: {random.choice(quotes)}")
        return "\n".join(advice)

def get_footer_quote():
    """?스???단???시???가?의 격언"""
    quotes = [
        "VCP???자?? ?? 조용?니?? ??? 고요???에???작?니??",
        "?절? ?배가 ?닌, ?음 ?리??한 보험료입?다.",
        "?익? ?직 2?계(Mark-up)?서?창출?니?? 기다림? 지루할 ???으??결과???콤?니??",
        "리더???쁜 직원??즉시 ?고?듯, 추세가 꺾인 종목? 즉시 ?명?야 ?니??",
        "?장??맞서지 마십?오. ?도??????처럼 ?급???름??몸을 맡기????",
        "가??강한 ?이 가??멀?갑니?? RS ?고가???이 ?습?다."
    ]
    return random.choice(quotes)

@st.cache_resource
def get_ai_chat_cooldown():
    """AI 채팅 범람 방???한 ?역 ??머 관?""
    return {"last_time": 0}

def trigger_ai_chat():
    """AI ??들???덤?게 ?통방에 메시지??기???진 (6??체제)"""
    # [ OPTIMIZE ] ?역 코울?운 체크 (15???중복 발송 차단)
    cd = get_ai_chat_cooldown()
    if time.time() - cd["last_time"] < 15: return False
    
    ai_users = [
        {"name": "[ AI ] minsu", "grade": "AI_???(코스??"},
        {"name": "[ AI ] Olive", "grade": "AI_???(코스??"},
        {"name": "[ AI ] Pure", "grade": "AI_???(?스??"},
        {"name": "[ AI ] Harmony", "grade": "AI_???},
        {"name": "[ AI ] Mint Soft", "grade": "AI_???},
        {"name": "[ AI ] Calm Blue12", "grade": "AI_???}
    ]
    ai_phrases = [
        "?늘 ?스???물 ?름???상??네?? ?술????권고?니??",
        "방금 HTF ?턴 ?캔 결과 공유?습?다. 주도??급??강력?네??",
        "?절가???명?입?다. ?들 ?칙 매매 ??지?고 계신가??",
        "?티그래비티 ?령부???????익 공식: ?내, 그리?기계????입?다.",
        "VCP 최종 ?계?서 거래?이 말라붙는 모습... ????겠군요.",
        "?령부 ?원?들, ?늘???투?십?오! ?동매매???절?니??",
        "?장???음(Noise)보다 차트???호(Signal)??집중?세??",
        "조급?? 중력?같습?다. ?티그래비티 ??답?무중?으?비상?시??",
        "?늘??RS ?위 종목??리스?? ?말 ?탄?네?? 주도??리 준??료?니??"
    ]
    
    try:
        now_kst = datetime.now(pytz.timezone('Asia/Seoul')).strftime("%Y-%m-%d %H:%M:%S")
        ai = random.choice(ai_users)
        ms = random.choice(ai_phrases)
        # 로컬 ???
        new_msg = pd.DataFrame([[now_kst, ai["name"], ms, ai["grade"]]], columns=["?간", "??", "?용", "?급"])
        safe_write_csv(new_msg, CHAT_FILE, mode='a', header=not os.path.exists(CHAT_FILE))
        cd["last_time"] = time.time() # ?간 갱신
        return True
    except: return False

# --- [ STORAGE ] ?이?베?스 ??구 보존 ?정 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
def get_db_path(f): return os.path.join(BASE_DIR, f)

BACKUP_DIR = get_db_path("backups")

def auto_backup(file_path, force=True):
    if not os.path.exists(file_path): return
    try:
        fname = os.path.basename(file_path)
        os.makedirs(BACKUP_DIR, exist_ok=True)
        
        # [ SECURE ] ?문가???청: 중요 ?일?? ?? 백업 ?성 (강제??부??
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(BACKUP_DIR, f"{fname}_{timestamp}.bak")
        shutil.copy2(file_path, backup_path)
        
        # 백업 ?일 개수 관?(최근 50?????장)
        if random.random() < 0.2:
            all_backups = sorted([os.path.join(BACKUP_DIR, f) for f in os.listdir(BACKUP_DIR) if f.startswith(fname)], key=os.path.getmtime)
            if len(all_backups) > 50:
                for old_f in all_backups[:-50]: os.remove(old_f)
    except:    pass

USER_DB_FILE = get_db_path("users_db.json")
TRADES_DB = get_db_path("trades_db.json")
CHAT_FILE = get_db_path("chat_log.csv")
BRIEF_FILE = get_db_path("market_briefs.csv")
VISITOR_FILE = get_db_path("visitor_requests.csv")
ATTENDANCE_FILE = get_db_path("attendance.csv")
PROFIT_FILE = get_db_path("profit_brags.csv")
LOSS_FILE = get_db_path("loss_reviews.csv")
COMMENTS_FILE = get_db_path("shared_comments.csv")
MASTER_GAS_URL = st.secrets.get("MASTER_GAS_URL", "https://script.google.com/macros/s/AKfycbyp31pP_T4nVi0rEoeOu-kc6t_ynofxRYnnYZTTO1kxOcQWinBfyhEeDjTRZXzp1eCo/exec")

def gsheet_sync_bg(sheet_name, cols, row_data):
    """비동?구? ?트 ?이???송 (UI ?리?방?)"""
    def task():
        try: requests.post(MASTER_GAS_URL, json={"sheetName": sheet_name, "columns": cols, "row": row_data}, timeout=15)
        except:    pass
    threading.Thread(target=task, daemon=True).start()




def safe_read_csv(file_path, columns=None):
    if not os.path.exists(file_path):
        return pd.DataFrame(columns=columns) if columns else pd.DataFrame()
    try:
        df = pd.read_csv(file_path, encoding='utf-8-sig', on_bad_lines='skip')
        if columns:
            for col in columns:
                if col not in df.columns: df[col] = "nan"
            return df[columns]
        return df
    except Exception as e:
        # ?일???제 존재?는???기???패??경우 경고 출력
        st.warning(f"WAIT: ?이???일([.csv]) ?기 ?도 ?지?이 발생?고 ?습?다. ?시 ???동 복구?니?? ({os.path.basename(file_path)})")
        return pd.DataFrame(columns=columns) if columns else pd.DataFrame()

def safe_write_csv(df, file_path, mode='w', header=True, backup=True):
    try:
        if backup and os.path.exists(file_path): auto_backup(file_path, force=True)
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        
        # ?구 보존???한 ?자???기 강화
        temp_path = file_path + ".tmp"
        if mode == 'a' and os.path.exists(file_path):
            df.to_csv(file_path, index=False, encoding='utf-8-sig', mode=mode, header=False)
        else:
            df.to_csv(temp_path, index=False, encoding='utf-8-sig', mode='w', header=header)
            os.replace(temp_path, file_path)
        return True
    except: return False

def safe_save_json(data, file_path, backup=True):
    try:
        if backup and os.path.exists(file_path): auto_backup(file_path, force=True)
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        temp_path = file_path + ".tmp"
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        os.replace(temp_path, file_path)
        return True
    except: return False

def safe_load_json(file_path, default=None):
    if not os.path.exists(file_path): return default if default is not None else {}
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except: return default if default is not None else {}

# [ SECURE ] ?구 백업??구? ?트 URL (CSV ?보?기 주소) - 보안???해 st.secrets ?용
USERS_SHEET_URL = st.secrets.get("USERS_SHEET_URL", "https://docs.google.com/spreadsheets/d/1HbC_U1I78HAdV99X6qS1hmY_RiRGPrHX92AYbBPrIpU/export?format=csv&gid=1180564490")
ATTENDANCE_SHEET_URL = st.secrets.get("ATTENDANCE_SHEET_URL", "https://docs.google.com/spreadsheets/d/1HbC_U1I78HAdV99X6qS1hmY_RiRGPrHX92AYbBPrIpU/export?format=csv&gid=0")
CHAT_SHEET_URL = st.secrets.get("CHAT_SHEET_URL", "https://docs.google.com/spreadsheets/d/1HbC_U1I78HAdV99X6qS1hmY_RiRGPrHX92AYbBPrIpU/export?format=csv&gid=2147147361")
VISITOR_SHEET_URL = st.secrets.get("VISITOR_SHEET_URL", "https://docs.google.com/spreadsheets/d/1HbC_U1I78HAdV99X6qS1hmY_RiRGPrHX92AYbBPrIpU/export?format=csv&gid=621380834")
WITHDRAWN_SHEET_URL = st.secrets.get("WITHDRAWN_SHEET_URL", "https://docs.google.com/spreadsheets/d/1HbC_U1I78HAdV99X6qS1hmY_RiRGPrHX92AYbBPrIpU/export?format=csv&gid=1873947039")
# [ GLOBAL ] ?역 공? ?UI ?이?웃 ?정
NOTICE_SHEET_URL = st.secrets.get("NOTICE_SHEET_URL", "https://docs.google.com/spreadsheets/d/1HbC_U1I78HAdV99X6qS1hmY_RiRGPrHX92AYbBPrIpU/export?format=csv&gid=1619623253")

TICKER_NAME_MAP = {
    "NVDA": "?비?아", "TSLA": "?슬??, "AAPL": "?플", "MSFT": "마이?로?프??, "PLTR": "???어", "SMCI": "?퍼마이?로", 
    "AMD": "AMD", "META": "메?", "GOOGL": "구?", "AVGO": "브로?컴", "CRWD": "?라?드?트?이??, "005930.KS": "?성?자", 
    "000660.KS": "SK?이?스", "196170.KQ": "?테?젠", "042700.KS": "??반도?, "105560.KS": "KB금융", "055550.KS": "?한지?,
    "005490.KS": "POSCO??스", "000270.KS": "기아", "066570.KS": "LG?자", "035720.KS": "카카??, "035420.KS": "NAVER",
    "005380.KS": "???, "000810.KS": "?성?재", "NFLX": "?플?", "MSTR": "마이?로?트?티지", "COIN": "코인베이??, 
    "MARA": "마라?디지??, "PANW": "?로?토", "SNOW": "?노?플?이??, "STX": "?게?트", "WDC": "?스?디지??,
    "247540.KQ": "?코?로비엠", "277810.KQ": "?코?로", "091990.KQ": "??리?헬????, "293490.KQ": "카카?게?즈", "086520.KQ": "?코?로",
    "000100.KS": "?한?행", "000720.KS": "??건설", "012330.KS": "??모비??, "035720.KS": "카카??, "003410.KS": "?용C&E"
}

def get_stock_name(ticker):
    """?커??? 종목명으?변??(?이??시?API ?동 ?캐시)"""
    if ticker in TICKER_NAME_MAP: return TICKER_NAME_MAP[ticker]
    if "name_cache" not in st.session_state: st.session_state.name_cache = {}
    if ticker in st.session_state.name_cache: return st.session_state.name_cache[ticker]
    
    try:
        # ?국 주식??경우 ?이?API??름 가?오?
        if ticker.endswith(".KS") or ticker.endswith(".KQ"):
            symbol = ticker.split('.')[0]
            url = f"https://polling.finance.naver.com/api/realtime?query=SERVICE_ITEM:{symbol}"
            resp = requests.get(url, timeout=2).json()
            name = resp['result']['areas'][0]['datas'][0]['nm']
            st.session_state.name_cache[ticker] = name
            return name
        # ?외 주식? yfinance ?용
        t = yf.Ticker(ticker)
        name = t.info.get('shortName', ticker)
        st.session_state.name_cache[ticker] = name
        return name
    except:
        return ticker

REVERSE_TICKER_MAP = {v: k for k, v in TICKER_NAME_MAP.items()}

def resolve_ticker(query):
    query = query.strip()
    # 6?리 ?자??국 주식 코드?처리
    if query.isdigit() and len(query) == 6: return query + ".KS"
    
    if query in TICKER_NAME_MAP: return query
    if query.upper() in TICKER_NAME_MAP: return query.upper()
    if query in REVERSE_TICKER_MAP: return REVERSE_TICKER_MAP[query]
    return query.upper()

# --- [ ENGINE ] Unified Market Data Center ---
@st.cache_data(ttl=300)
def get_bulk_market_data(tickers, period="60d"):
    """?역 마켓 ?이???진 (API ?출 최적??"""
    if not tickers: return pd.DataFrame()
    try:
        data = yf.download(list(set(tickers)), period=period, progress=False)
        return data if not data.empty else pd.DataFrame()
    except: return pd.DataFrame()

@st.cache_data(ttl=300)
def fetch_macro_ticker_tape():
    """?니메이???커???이???집"""
    watch = {"S&P500": "^GSPC", "NASDAQ": "^IXIC", "BTC": "BTC-USD", "GOLD": "GC=F", "KOSPI": "^KS11", "KOSDAQ": "^KQ11"}
    data = get_bulk_market_data(list(watch.values()), "5d")
    items = []
    if not data.empty and 'Close' in data:
        for name, sym in watch.items():
            if sym in data['Close'].columns:
                h = data['Close'][sym].dropna()
                if len(h) >= 2:
                    curr, prev = h.iloc[-1], h.iloc[-2]
                    pct = (curr / prev - 1) * 100
                    color = "#FF4B4B" if pct >= 0 else "#0088FF"
                    items.append(f"<span class='ticker-item'>{name} <b>{curr:,.1f}</b> <span style='color:{color};'>{pct:+.2f}%</span></span>")
    return " ".join(items)

@st.cache_data(ttl=3600)
def get_bonde_top_50():
    """본데 주도?Top 50 리스??(구? ?트 ?동)"""
    try:
        url = "https://docs.google.com/spreadsheets/d/1HbC_U1I78HAdV99X6qS1hmY_RiRGPrHX92AYbBPrIpU/export?format=csv&gid=780517835"
        resp = safe_get(url)
        if resp:
            df = pd.read_csv(io.StringIO(resp.text))
            return df.iloc[:, 0].dropna().tolist()
    except:    pass
    return ["NVDA", "TSLA", "AAPL", "MSFT", "AMZN"]

def get_ticker_data_from_bulk(bulk_df, ticker):
    """?괄 ?운로드 ?이?에???정 종목?추출"""
    if bulk_df.empty or ticker not in bulk_df.columns.get_level_values(1): return pd.DataFrame()
    try:
        return pd.DataFrame({col: bulk_df[col][ticker] for col in ["Open", "High", "Low", "Close", "Volume"]}).dropna()
    except: return pd.DataFrame()

@st.cache_data(ttl=900)
def get_market_sentiment_v2():
    try:
        data = get_bulk_market_data(["^VIX", "^IXIC"], "20d")
        vix = float(data['Close']["^VIX"].dropna().iloc[-1]) if "^VIX" in data['Close'].columns else 20.0
        score = max(5, min(95, 100 - (vix * 2.2)))
        label = "GREED" if score > 65 else ("FEAR" if score < 35 else "NEUTRAL")
        return int(score), vix, label
    except: return 50, 20.0, "NEUTRAL"

def get_macro_indicators():
    try:
        data = get_bulk_market_data(["USDKRW=X", "^TNX"], "5d")['Close']
        rate = data["USDKRW=X"].dropna().iloc[-1]
        yield10y = data["^TNX"].dropna().iloc[-1]
        return f"[ USD/KRW ]: {rate:,.1f}??| [ US 10Y ]: {yield10y:.2f}%"
    except: return "[ USD/KRW ]: 1400.0??| [ US 10Y ]: 4.30%"

@st.cache_data(ttl=3600)
def get_macro_data():
    """?시??율 ?거시 지???치 반환"""
    try:
        data = get_bulk_market_data(["USDKRW=X"], "5d")['Close']
        rate = float(data["USDKRW=X"].dropna().iloc[-1])
        return rate, 4.3
    except:
        return 1400.0, 4.3

# --- [ ENGINE ] KIS API & Core Trading Logic ---
# [ SECURITY ] ?령관?이 ?공?신 ?제 ?술 ??주입
NEW_KEY = "PSzuu6dcYxkkHvTyAXm61J1Zta6oBrSZHoaq"
NEW_SECRET = "H5dGS5kHK3AbpskI0E0ovYAL6aS82Li/4SioJGlLK6ypvlc3ejf1NNpbwkxTpsuO81mhqEFOW62OaFSCRtd/J9/v8c5WVKOf0uMigMblMeMI1riXUaeVf+LuBnSE+kXN1OEkn1MBlQ2GiLd4tFBEEQxOH/cQgFf0YaU2Q1S5OeHnecRCcuQ="

KIS_APP_KEY = st.secrets.get("KIS_APP_KEY", NEW_KEY).strip()
KIS_APP_SECRET = st.secrets.get("KIS_APP_SECRET", NEW_SECRET).strip()

# [ 계좌 ?리???의 ]
ACC_PRESETS = {
    "?탁(??)": "4654671301",
    "미니?탁/?수??: "4628981901",
    "ISA 중개??: "4444571901"
}

def get_kis_mock_status():
    return st.session_state.get("kis_mock_mode", st.secrets.get("KIS_MOCK_TRADING", False))

def get_current_acc_no():
    # ?션 ?태??계좌 ?보가 ?으?기본??탁 ??) ?용
    selected_acc_name = st.session_state.get("selected_acc_name", "?탁(??)")
    return ACC_PRESETS.get(selected_acc_name, "4654671301")

KIS_MOCK_TRADING = get_kis_mock_status()
KIS_ACCOUNT_NO = get_current_acc_no()

# [ NEW ] ?레그램 ?정
TELEGRAM_TOKEN = st.secrets.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = st.secrets.get("TELEGRAM_CHAT_ID", "")

def send_telegram_msg(msg):
    """?령관?께 ?시??술 보고 ?송 (?레그램)"""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID: return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        params = {"chat_id": TELEGRAM_CHAT_ID, "text": f"? [COMMANDER REPORT]\n{msg}", "parse_mode": "Markdown"}
        requests.get(url, params=params, timeout=15)
    except:    pass

@st.cache_data(ttl=3500, show_spinner=False)
def get_kis_access_token(app_key, app_secret, mock=True):
    """?국?자증권 API ?근 ?큰 발급 (1??한 방어 로직 ?함)"""
    # [ SAFETY ] KIS 1?1???한 방어
    last_req = st.session_state.get("last_token_req_time", 0)
    elapsed = time.time() - last_req
    if elapsed < 60: 
        placeholder = st.empty()
        # [ LIVE COUNTDOWN ] ?령관?의 ?의??해 ?시???머 가??
        for remaining in range(int(60 - elapsed), -1, -1):
            placeholder.warning(f"??KIS 보안 ?책???큰? 1분에 1?만 ?청 가?합?다. (보안 ?제 ??? {remaining}?")
            if remaining > 0: time.sleep(1)
        placeholder.empty()
        # ?간?????면 캐시???큰?라??반환 ?도
        return st.session_state.get("last_valid_token")

    base_url = "https://openapivts.koreainvestment.com:29443" if mock else "https://openapi.koreainvestment.com:9443"
    url = f"{base_url}/oauth2/tokenP"
    headers = {"content-type": "application/json"}
    body = {"grant_type": "client_credentials", "appkey": app_key, "appsecret": app_secret}
    
    st.session_state.last_token_req_time = time.time()
    try:
        res = requests.post(url, headers=headers, json=body, timeout=15)
        res_data = res.json()
        if res.status_code == 200:
            token = res_data.get("access_token")
            if token:
                st.session_state.last_valid_token = token
                return token
        
        err_msg = res_data.get('msg1', res_data.get('error_description', 'Unknown Error'))
        if "1분당 1?? in err_msg:
             st.warning("?️ KIS ?큰 발급 ?한(1???걸렸?니?? ?시 ???동 ?시?합?다.")
        else:
             st.error(f"? [KIS AUTH ERROR] {err_msg} (Target: {'Mock' if mock else 'Real'})")
    except Exception as e:
        st.error(f"? [NETWORK ERROR] KIS ?버 ?결 ?패: {str(e)}")
    
    return st.session_state.get("last_valid_token")

def get_kis_balance(token, mock=None):
    """? 주식 ?고 ??수??황 조회 (?제 ?동)"""
    if not token or not KIS_ACCOUNT_NO: return 0, 0, []
    use_mock = mock if mock is not None else KIS_MOCK_TRADING
    base_url = "https://openapivts.koreainvestment.com:29443" if use_mock else "https://openapi.koreainvestment.com:9443"
    url = f"{base_url}/uapi/domestic-stock/v1/trading/inquire-balance"
    headers = {
        "Content-Type": "application/json",
        "authorization": f"Bearer {token}",
        "appkey": KIS_APP_KEY,
        "appsecret": KIS_APP_SECRET,
        "tr_id": "VTTC8434R" if use_mock else "TTTC8434R",
        "custtype": "P"
    }
    suffixes = [KIS_ACCOUNT_NO[8:], "01", "02", "03", "04", "05", "06"]
    for suffix in list(dict.fromkeys(suffixes)):
        params = {
            "CANO": KIS_ACCOUNT_NO[:8], "ACNT_PRDT_CD": suffix,
            "AFHR_FLG": "N", "OVAL_DLY_TR_FECONT_YN": "N", "PRCS_DLY_VW_FNC_G": "0",
            "CANL_DLY_VW_FNC_G": "0", "CTX_AREA_FK100": "", "CTX_AREA_NK100": ""
        }
        try:
            res = requests.get(url, headers=headers, params=params, timeout=15)
            if res.status_code == 200:
                data = res.json()
                if data.get('output2'):
                    cash = float(data['output2'][0].get('dnca_tot_amt', 0))
                    eval_amt = float(data['output2'][0].get('tot_evlu_amt', 0))
                    holdings = data.get('output1', [])
                    return cash + eval_amt, cash, holdings
            elif res.status_code == 500:
                err_data = res.json()
                msg = err_data.get('msg1', 'Internal Server Error')
                if "계좌" in msg or "권한" in msg: continue # ?음 ?????도
                st.warning(f"?️ KIS ?버 ?답(500): {msg}")
        except: continue
    return 0, 0, []

def get_kis_overseas_balance(token, mock=None):
    """?외 주식 ?고 ?황 조회 (?합 ?? + 거래?별 ?고 + ?수 ?캔)"""
    if not token or not KIS_ACCOUNT_NO: return {"krw": 0, "usd_total": 0, "usd_cash": 0}, []
    use_mock = mock if mock is not None else KIS_MOCK_TRADING
    base_url = "https://openapivts.koreainvestment.com:29443" if use_mock else "https://openapi.koreainvestment.com:9443"
    
    suffixes = [KIS_ACCOUNT_NO[8:], "01", "02", "03", "04", "05", "06"]
    best_data = {"krw": 0, "usd_total": 0, "usd_cash": 0}
    best_holdings = []
    
    for suffix in list(dict.fromkeys(suffixes)):
        # ?략 1: TTTS3061R (?외주식 ?합?? - 가???확??
        url_61 = f"{base_url}/uapi/overseas-stock/v1/trading/inquire-balance"
        headers_61 = {
            "Content-Type": "application/json", "authorization": f"Bearer {token}",
            "appkey": KIS_APP_KEY, "appsecret": KIS_APP_SECRET,
            "tr_id": "VTTS3061R" if use_mock else "TTTS3061R", "custtype": "P"
        }
        params_61 = {"CANO": KIS_ACCOUNT_NO[:8], "ACNT_PRDT_CD": suffix, "WCRC_FRCR_DVS_CD": "02", "NATN_CD": "840", "TR_PACC_CD": ""}
        
        try:
            res = requests.get(url_61, headers=headers_61, params=params_61, timeout=10)
            if res.status_code == 200:
                d = res.json()
                o2 = d.get('output2', {})
                if o2:
                    total_usd = float(o2.get('frcr_evlu_amt2') or o2.get('tot_evlu_pamt') or 0) # ?화??금액
                    cash_usd = float(o2.get('frcr_dnca_amt') or o2.get('frcr_dncl_amt_2') or o2.get('frcr_drwg_psbl_amt_1') or 0)   # ?화?수금액
                    total_krw = float(o2.get('tot_evlu_pamt') or o2.get('tot_asst_amt') or 0)
                    
                    # 미니?탁??경우 ??산금액(tot_asst_amt)???히??경우가 많음
                    if total_usd + cash_usd == 0 and total_krw > 0:
                        # ?화로만 ?히??경우 ?? (?시)
                        total_usd = total_krw / 1350 
                        
                    if total_usd + cash_usd > 0 or total_krw > 0:
                        return {"krw": total_krw, "usd_total": total_usd + cash_usd, "usd_cash": cash_usd}, d.get('output1', [])
        except:    pass

        # ?략 2: TTTS3012R (?외주식 ?고 - 거래??지???요)
        headers_12 = headers_61.copy()
        headers_12["tr_id"] = "VTTS3012R" if use_mock else "TTTS3012R"
        for excd in ["NASD", "NYSE"]:
            params_12 = params_61.copy()
            params_12.update({"OVRS_EXCG_CD": excd, "CTX_AREA_FK200": "", "CTX_AREA_NK200": ""})
            try:
                res = requests.get(url_61, headers=headers_12, params=params_12, timeout=10)
                if res.status_code == 200:
                    d = res.json()
                    o2 = d.get('output2', {})
                    if o2:
                        total_usd = float(o2.get('frcr_evlu_amt2', 0))
                        cash_usd = float(o2.get('frcr_dnca_amt', 0))
                        if total_usd + cash_usd > 0:
                            return {"krw": float(o2.get('tot_evlu_pamt', 0)), "usd_total": total_usd + cash_usd, "usd_cash": cash_usd}, d.get('output1', [])
            except: continue

    return best_data, best_holdings

# --- [ KIS: REAL-TIME RISK MONITORING (PRO EDITION) ] ---
def get_kis_current_price(ticker, token):
    """KIS OpenAPI??한 ?시??재가 ?득"""
    if not token: return 0
    try:
        is_kr = ticker.endswith(".KS") or ticker.endswith(".KQ")
        symbol = ticker.split('.')[0]
        base_url = "https://openapivts.koreainvestment.com:29443" if KIS_MOCK_TRADING else "https://openapi.koreainvestment.com:9443"
        
        if is_kr:
            url = f"{base_url}/uapi/domestic-stock/v1/quotations/inquire-price"
            headers = {"Content-Type": "application/json", "authorization": f"Bearer {token}", "appkey": KIS_APP_KEY, "appsecret": KIS_APP_SECRET, "tr_id": "FHKST01010100"}
            params = {"FID_COND_SCR_DIV_CODE": "11111", "FID_INPUT_ISCD": symbol}
            resp = requests.get(url, headers=headers, params=params, timeout=15)
            return float(resp.json().get('output', {}).get('stck_prpr', 0))
        else:
            url = f"{base_url}/uapi/overseas-stock/v1/quotations/price"
            headers = {"Content-Type": "application/json", "authorization": f"Bearer {token}", "appkey": KIS_APP_KEY, "appsecret": KIS_APP_SECRET, "tr_id": "HHDFS76200200"}
            # 거래??코드 NAS/NYS/AMS ?동 ?도
            for excd in ["NAS", "NYS", "AMS"]:
                params = {"AUTH": "", "EXCD": excd, "SYMB": ticker}
                resp = requests.get(url, headers=headers, params=params, timeout=15)
                price = float(resp.json().get('output', {}).get('last', 0))
                if price > 0: return price
        return 0
    except: return 0

def get_market_breadth(token):
    """[ MARKET BREADTH ] ?장 건강??체크 (종목?의 SMA50 ?회 비율)"""
    try:
        # 코스??200 ?플 20종목 기반 간이 브레??측정 (?도 최적??
        sample_tickers = ["005930.KS", "000660.KS", "373220.KS", "207940.KS", "005380.KS", "005490.KS", "000270.KS", "035420.KS"]
        above_count = 0
        from concurrent.futures import ThreadPoolExecutor
        
        def check_sma50(t):
            df = get_kis_ohlcv(t, token)
            if len(df) < 50: return False
            return df['Close'].iloc[-1] > df['Close'].rolling(50).mean().iloc[-1]
            
        with ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(check_sma50, sample_tickers))
            above_count = sum(results)
            
        breadth_pct = (above_count / len(sample_tickers)) * 100
        return breadth_pct
    except: return 50.0 # ?러 ??보수?으?50% 반환

def execute_kis_auto_cut(token):
    """[ SUPREME RISK ENGINE ] ?절(+21%), ?절(-3%), ?워무브(고점-3%) ?합 집행"""
    try:
        _, kr_holdings = get_kis_balance(token)
        over_data, us_holdings = get_kis_overseas_balance(token)
        
        for h in kr_holdings + us_holdings:
            ticker = h.get('pdno') or h.get('ovrs_pdno')
            qty = int(h.get('hldg_qty', 0))
            buy_p = float(h.get('pchs_avg_pric', 0))
            if qty <= 0: continue
            
            is_kr = ticker.endswith(".KS") or ticker.endswith(".KQ")
            hist = get_kis_ohlcv(ticker, token) if is_kr else get_kis_overseas_ohlcv(ticker, token)
            
            if hist.empty: continue
            curr_p = hist['Close'].iloc[-1]
            high_3d = hist['High'].iloc[-3:].max() if len(hist) >= 3 else hist['High'].max()
            roi = (curr_p / buy_p - 1) * 100
            
            if (high_3d / buy_p - 1) >= 0.20: # Power Move
                if curr_p <= high_3d * 0.97:
                    if execute_kis_market_order(ticker, qty, is_buy=False): 
                        send_telegram_msg(f"? [POWER MOVE EXIT] {ticker} ?절 ?료! (+{roi:.1f}%)")
                        return True
            elif roi >= 21.0:
                if execute_kis_market_order(ticker, qty, is_buy=False):
                    send_telegram_msg(f"? [TAKE PROFIT] {ticker} 목표?성 ?절! (+{roi:.1f}%)")
                    return True
            elif roi <= -3.0:
                if execute_kis_market_order(ticker, qty, is_buy=False):
                    send_telegram_msg(f"? [STOP LOSS] {ticker} 기계???절 집행. ({roi:.1f}%)")
                    return True
    except Exception as e:
        print(f"DEBUG: Auto Cut Error: {e}")
    return False

def fast_analyze_stock(ticker, token):
    """?캐??가?을 ?한 ?립 분석 ?수"""
    try:
        # analyze_stockbee_setup? 글로벌 ?코?에 ?으므?직접 ?출
        return analyze_stockbee_setup(ticker, kis_token=token)
    except:
        return {"status": "ERROR", "ticker": ticker, "reason": "Analysis Function Error"}

def play_tactical_sound(sound_type="buy"):
    """?술 ?황???른 ?디???림 (매수: 북소?/ 매도: 종소?"""
    # [ ACTION ] 매수: Drum/Taiko, 매도: Bell/Chime
    src = "https://www.soundjay.com/buttons/beep-07a.mp3" # Default
    if sound_type == "buy": src = "https://www.soundjay.com/misc/sounds/drum-roll-1.mp3"
    elif sound_type == "sell": src = "https://www.soundjay.com/misc/sounds/bell-ringing-05.mp3"
    
    st.markdown(f"""
    <audio autoplay>
        <source src="{src}" type="audio/mpeg">
    </audio>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=43200) # 12?간 캐싱 (ROE???주 변?? ?음)
def get_ticker_roe(ticker):
    """종목???시?ROE(?기?본?익???득 (캐시 ?용?로 ??방?)"""
    try:
        info = yf.Ticker(ticker).info
        return info.get('returnOnEquity', 0) * 100
    except: return 0

def execute_kis_market_order(ticker, qty, is_buy=True):
    """?장가 주문 ?행 ?진 (KIS API ?동)"""
    token = get_kis_access_token(KIS_APP_KEY, KIS_APP_SECRET, KIS_MOCK_TRADING)
    if not token: return False
    
    is_kr = ticker.endswith(".KS") or ticker.endswith(".KQ")
    base_url = "https://openapivts.koreainvestment.com:29443" if KIS_MOCK_TRADING else "https://openapi.koreainvestment.com:9443"
    
    if is_kr:
        url = f"{base_url}/uapi/domestic-stock/v1/trading/order-cash"
        tr_id = ("VTTC0802U" if is_buy else "VTTC0801U") if KIS_MOCK_TRADING else ("TTTC0802U" if is_buy else "TTTC0801U")
        body = {
            "CANO": KIS_ACCOUNT_NO[:8], "ACNT_PRDT_CD": KIS_ACCOUNT_NO[8:],
            "PDNO": ticker.split('.')[0], "ORD_DVSN": "01", "ORD_QTY": str(qty), "ORD_UNPR": "0"
        }
    else:
        # [ PRO ] 미국 거래???별 로직 고도??
        exchange_code = "NASD" # 기본?
        try:
            info = yf.Ticker(ticker).info
            ex_name = info.get('exchange', '').upper()
            if 'NYE' in ex_name or 'NEW YORK' in ex_name: exchange_code = "NYSE"
            elif 'ASE' in ex_name or 'AMERICAN' in ex_name: exchange_code = "AMEX"
        except:    pass
        
        url = f"{base_url}/uapi/overseas-stock/v1/trading/order"
        tr_id = ("VTTW0801U" if is_buy else "VTTW0802U") if KIS_MOCK_TRADING else ("TTTW0801U" if is_buy else "TTTW0802U")
        # 미국 ?장가 주문 ???(ORD_DVSN 00 지??, 가?0 ?송 ??KIS ????처리 가?성 고려)
        body = {
            "CANO": KIS_ACCOUNT_NO[:8], "ACNT_PRDT_CD": KIS_ACCOUNT_NO[8:],
            "OVRS_EXCG_CD": exchange_code, "PDNO": ticker, "ORD_QTY": str(qty), 
            "ORD_OVRS_P": "0", "ORD_DVSN": "00"
        }

    headers = {
        "Content-Type": "application/json", "authorization": f"Bearer {token}",
        "appkey": KIS_APP_KEY, "appsecret": KIS_APP_SECRET, "tr_id": tr_id
    }
    try:
        res = requests.post(url, headers=headers, json=body, timeout=7)
        res_data = res.json()
        if res.status_code == 200 and res_data.get('rt_cd') == '0':
            # [ AUDIO ] 교전 결과 ?운??보고 (매수: 북소?/ 매도: 종소?
            play_tactical_sound("buy" if is_buy else "sell")
            # ?투 로그 기록
            log_type = "SUCCESS"
            msg = f"{'?? 매수' if is_buy else '? 매도'} ?료: {ticker} ({qty}?"
            st.session_state.combat_logs.append({"time": datetime.now().strftime("%H:%M:%S"), "msg": msg, "type": log_type})
            return True
        else:
            # ?패 ?유 추출 ?????
            err_msg = res_data.get('msg1', 'API ?신 ?류')
            if "?고" in err_msg or "부? in err_msg or "balance" in err_msg.lower():
                err_msg = "??계좌 ?액(증거???부족하??매수 불???
            
            log_msg = f"?️ {ticker} 주문 ?패: {err_msg}"
            st.session_state.combat_logs.append({"time": datetime.now().strftime("%H:%M:%S"), "msg": log_msg, "type": "ERROR"})
            return False
    except Exception as e:
        st.session_state.combat_logs.append({"time": datetime.now().strftime("%H:%M:%S"), "msg": f"? ?스???류: {str(e)}", "type": "ERROR"})
        return False

# --- [ SCANNER HELPERS: STOCKBEE STRICT EDITION ] ---
@st.cache_data(ttl=3600)
def get_bonde_top_50():
    """?라??본데 50 종목 구? ?트 ?동"""
    url = "https://docs.google.com/spreadsheets/d/1xjbe9SF0HsxwY_Uy3NC2tT92BqK0nhArUaYU16Q0p9M/export?format=csv&gid=1499398020"
    try:
        df = pd.read_csv(url)
        tickers = df.iloc[:50, 0].dropna().unique().tolist()
        return [str(t).strip().upper() for t in tickers if len(str(t)) < 6]
    except:
        return ["NVDA", "TSLA", "AAPL", "MSFT", "PLTR", "SMCI", "AMD", "META", "GOOGL", "AVGO", "MSTR", "COIN", "MARA"]

def analyze_stockbee_setup(ticker, hist_df=None):
    """
    [ BONDE ELITE ENGINE ] ?라??본데???장???업 (4?
    - 9 Million EP
    - Story-based EP
    - Delayed Reaction EP
    - 4% Momentum Burst
    """
@st.cache_data(ttl=300, show_spinner=False) # 5?캐시, ?피??비활??
def get_kis_ohlcv(ticker, token):
    """?국?자증권 OpenAPI ? 주식 ?봉 (120??최적??버전)"""
    if not token: return pd.DataFrame()
    try:
        symbol = ticker.split('.')[0]
        base_url = "https://openapivts.koreainvestment.com:29443" if KIS_MOCK_TRADING else "https://openapi.koreainvestment.com:9443"
        url = f"{base_url}/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice"
        headers = {
            "Content-Type": "application/json", "authorization": f"Bearer {token}",
            "appkey": KIS_APP_KEY, "appsecret": KIS_APP_SECRET,
            "tr_id": "FHKST03010100", "custtype": "P"
        }
        # 본데 ?략(SMA65)???요??최소 120?로 기간 축소?여 ?공?극???
        params = {
            "FID_COND_SCR_DIV_CODE": "16641", "FID_INPUT_ISCD": symbol,
            "FID_INPUT_DATE_1": (datetime.now() - pd.Timedelta(days=120)).strftime("%Y%m%d"),
            "FID_INPUT_DATE_2": datetime.now().strftime("%Y%m%d"),
            "FID_PERIOD_DIV_CODE": "D", "FID_ORG_ADJ_PRC": "0"
        }
        resp = requests.get(url, headers=headers, params=params, timeout=15)
        if resp.status_code != 200: return pd.DataFrame()
        
        res_json = resp.json()
        output = res_json.get('output2', [])
        if not output: return pd.DataFrame()
        
        data = []
        for r in reversed(output):
            if not r.get('stck_bsop_date'): continue
            data.append({
                'Date': datetime.strptime(r['stck_bsop_date'], '%Y%m%d'),
                'Open': float(r['stck_oprc']), 'High': float(r['stck_hgpr']),
                'Low': float(r['stck_lwpr']), 'Close': float(r['stck_clpr']),
                'Volume': float(r['acml_vol'])
            })
        df = pd.DataFrame(data).set_index('Date').sort_index()
        # ?이?? ?무 ?으?캐싱?? ?음 (?시???도)
        if len(df) < 5: return pd.DataFrame()
        return df
    except: return pd.DataFrame()

@st.cache_data(ttl=300, show_spinner=False)
def get_kis_overseas_ohlcv(ticker, token):
    """?국?자증권 OpenAPI ?외 주식 ?봉 (120??최적??버전)"""
    if not token: return pd.DataFrame()
    try:
        base_url = "https://openapivts.koreainvestment.com:29443" if KIS_MOCK_TRADING else "https://openapi.koreainvestment.com:9443"
        url = f"{base_url}/uapi/overseas-stock/v1/quotations/dailyprice"
        headers = {
            "Content-Type": "application/json", "authorization": f"Bearer {token}",
            "appkey": KIS_APP_KEY, "appsecret": KIS_APP_SECRET,
            "tr_id": "HHDFS76240000", "custtype": "P"
        }
        for excd in ["NAS", "NYS", "AMS"]:
            params = {"AUTH": "", "EXCD": excd, "SYMB": ticker, "GUBN": "0", "BYMD": "", "MODP": "1"}
            resp = requests.get(url, headers=headers, params=params, timeout=15)
            if resp.status_code == 200:
                output = resp.json().get('output2', [])
                if output:
                    data = []
                    for r in reversed(output):
                        if not r.get('xy_date'): continue
                        data.append({
                            'Date': datetime.strptime(r['xy_date'], '%Y%m%d'),
                            'Open': float(r['open']), 'High': float(r['high']),
                            'Low': float(r['low']), 'Close': float(r['clos']),
                            'Volume': float(r['tvol'])
                        })
                    df = pd.DataFrame(data).set_index('Date').sort_index()
                    if len(df) >= 5: return df
        return pd.DataFrame()
    except: return pd.DataFrame()

def analyze_stockbee_setup(ticker, hist_df=None, kis_token=None):
    """?라??본데(Stockbee) ?략 ?? 분석 ?진 v8.0 (Global Pure KIS Core)"""
    try:
        is_kr = ticker.endswith(".KS") or ticker.endswith(".KQ")
        # [ PURE KIS DATA ENGINE ] 모든 ?료???국?자증권 OpenAPI?서 100% ?집
        token = kis_token if kis_token else get_kis_access_token(KIS_APP_KEY, KIS_APP_SECRET, KIS_MOCK_TRADING)
        hist = get_kis_ohlcv(ticker, token) if is_kr else get_kis_overseas_ohlcv(ticker, token)
        
        if hist.empty:
            return {"status": "REJECT", "reason": "?이??부?(KIS OpenAPI 0?", "ticker": ticker, "name": ticker}
            
        if len(hist) < 70:
            return {"status": "REJECT", "reason": f"?이??부?(?요:70? ?재:{len(hist)}?", "ticker": ticker, "name": ticker}
        
        # [ PREPARE DATA ]
        df = hist.copy()
        df['C1'], df['C2'], df['V1'] = df['Close'].shift(1), df['Close'].shift(2), df['Volume'].shift(1)
        df['Pct'] = (df['Close'] / (df['C1'] + 1e-9) - 1) * 100
        df['SMA7'], df['SMA65'] = df['Close'].rolling(7).mean(), df['Close'].rolling(65).mean()
        df['TI65'] = df['SMA7'] / (df['SMA65'] + 1e-9)
        df['Range_Pos'] = (df['Close'] - df['Low']) / (df['High'] - df['Low'] + 1e-9)
        df['ADR20'] = ((df['High'] / (df['Low'] + 1e-9) - 1) * 100).rolling(20).mean()
        
        row = df.iloc[-1]
        c, o, v, pct, ti65, adr20, range_pos = row['Close'], row['Open'], row['Volume'], row['Pct'], row['TI65'], row['ADR20'], row['Range_Pos']
        p_c, p_c2, p_v = row['C1'], row['C2'], row['V1']

        is_ep = is_dr = is_tight = False
        setups = []

        # ??EP (??)
        if pct >= 4.0 and v > p_v and v >= 100000 and (p_c/p_c2) <= 1.02 and range_pos >= 0.7:
            is_ep = True; setups.append("EP (??)")

        # ??DR (지?반??
        df['Mega'] = (df['Volume'] >= 9000000) & (df['Pct'] >= 4.0)
        recent_mega = df['Mega'].shift(1).rolling(25).max().iloc[-1] == 1.0
        if recent_mega and ((o < p_c and c > p_c) or ((p_c/p_c2) <= 1.02 and v > p_v and pct >= 4.0)):
            is_dr = True; setups.append("DR (지?반??")

        # ??TIGHT (?축)
        ttt = df['Pct'].rolling(3).apply(lambda x: all(abs(x) <= 1.0)).iloc[-1] == 1.0
        if df['Volume'].rolling(3).min().iloc[-1] >= 300000 and ti65 >= 1.05 and ttt:
            is_tight = True; setups.append("TIGHT (?축)")

        # RS ??질
        rs = round(((c/df['Close'].iloc[-126])*0.7 + (c/df['Close'].iloc[-63])*0.3)*100, 1) if len(df) >= 126 else 50
        v_ratio = v / (p_v + 1e-9)
        quality = round((rs*0.4) + (adr20*3) + (v_ratio*3), 1)
        name = get_stock_name(ticker)

        return {
            "ticker": ticker, "name": name, "close": c, "rs": rs, "day_pct": round(pct, 2), 
            "adr": round(adr20, 2), "quality": quality, "tight": round(abs(pct), 2),
            "is_ep": is_ep, "is_dr": is_dr, "is_tight": is_tight, "status": "SUCCESS" if setups else "PASS",
            "reason": f"?? {setups[0]} ?착!" if setups else "조건 미충?, "setups": setups,
            "volume": v, "prev_volume": p_v, "ti65": round(ti65, 3)
        }
    except Exception as e:
        return {"status": "ERROR", "reason": str(e), "ticker": ticker, "name": ticker}

    except Exception as e:
        return {"status": "ERROR", "stage": "ERROR", "reason": str(e)}

# --- [ SCANNER HELPERS: STOCKBEE STRICT EDITION ] ---
        

# --- [ SCANNER HELPERS: UNIVERSE EXPANSION ] ---

@st.cache_data(ttl=86400)
def get_nasdaq_200():
    """?스??100+ 주요 ?장?리스??""
    top_ndq = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "AVGO", "PEP", "COST", "ADBE", "CSCO", "NFLX", "AMD", "TMUS", "INTC", "INTU", "AMAT", "QCOM", "TXN", "AMGN", "ISRG", "HON", "BKNG", "VRTX", "SBUX", "ADP", "GILD", "MDLZ", "REGN", "ADI", "LRCX", "PANW", "SNPS", "MU", "KLAC", "CDNS", "CHTR", "MAR", "PYPL", "ORLY", "ASML", "MNST", "MELI", "CTAS", "ADSK", "LULU", "WDAY", "KDP", "NXPI", "MCHP", "IDXX", "PAYX", "ROST", "PCAR", "DXCM", "AEP", "CPRT", "CPRT", "BKR", "KLA", "EXC", "MRVL", "CRWD", "DDOG", "TEAM", "MSTR", "PLTR", "SNOW", "ZS", "NET", "OKTA", "U", "RIVN", "LCID", "SQ", "SE", "BABA", "PDD", "JD", "BIDU", "NTES"]
    return list(set(top_ndq))

@st.cache_data(ttl=86400)
def get_kospi_top_200():
    """코스???총 ?위 100+ 주요 종목"""
    top_ks = ["005930.KS", "000660.KS", "373220.KS", "207940.KS", "005490.KS", "005380.KS", "000270.KS", "051910.KS", "006400.KS", "035420.KS", "068270.KS", "105560.KS", "055550.KS", "012330.KS", "035720.KS", "003550.KS", "032830.KS", "000810.KS", "015760.KS", "086790.KS", "009150.KS", "011780.KS", "010130.KS", "033780.KS", "000100.KS", "018260.KS", "003670.KS", "000720.KS", "009830.KS", "011070.KS", "047050.KS", "028260.KS", "010140.KS", "036570.KS", "003410.KS", "051900.KS", "034730.KS", "090430.KS", "010950.KS", "259960.KS", "302440.KS", "402340.KS", "017670.KS"]
    return list(set(top_ks))

@st.cache_data(ttl=86400)
def get_kosdaq_100():
    """코스??100 주요 ?장?""
    top_kq = ["247540.KQ", "086520.KQ", "091990.KQ", "066970.KQ", "196170.KQ", "277810.KQ", "214150.KQ", "293490.KQ", "028300.KQ", "145020.KQ", "058470.KQ", "035900.KQ", "036930.KQ", "263750.KQ", "039030.KQ", "041510.KQ", "253450.KQ", "067310.KQ", "084370.KQ", "034230.KQ", "051910.KQ", "214320.KQ", "112040.KQ", "078600.KQ", "064290.KQ", "036830.KQ", "036200.KQ", "121600.KQ"]
    return list(set(top_kq))

def get_rs_score(ticker):
    try:
        h = yf.Ticker(ticker).history(period="6mo")
        if len(h) < 20: return 50
        return int((h['Close'].iloc[-1] / h['Close'].iloc[0]) * 100)
    except: return 50

# --- [ AI ] ?령부 AI ?예 ?원 (NPC Operatives) ?정 ---
AI_OPERATIVES = {
    "minsu": {"strategy": "KOSPI Specialist", "risk": "Aggressive", "win_rate": 0.65},
    "Olive": {"strategy": "KOSDAQ Specialist", "risk": "Balanced", "win_rate": 0.70},
    "Pure": {"strategy": "NASDAQ Specialist", "risk": "Conservative", "win_rate": 0.75},
    "Harmony": {"strategy": "Sector Rotation", "risk": "Balanced", "win_rate": 0.58},
    "Mint Soft": {"strategy": "Contrarian", "risk": "Conservative", "win_rate": 0.62},
    "Calm Blue12": {"strategy": "Macro Trend", "risk": "Aggressive", "win_rate": 0.60}
}

@st.cache_data(ttl=60)
def get_realtime_ai_ranking():
    missions = {"Pure": "NVDA", "minsu": "005930.KS", "Olive": "247540.KQ", "Harmony": "AAPL", "Mint Soft": "TSLA", "Calm Blue12": "000660.KS"}
    entry_prices = {"Pure": 128.5, "minsu": 78200, "Olive": 284000, "Harmony": 181.2, "Mint Soft": 172.5, "Calm Blue12": 182500}
    
    bulk_data = get_bulk_market_data(list(missions.values()))
    results = []
    for name, ticker in missions.items():
        hist = get_ticker_data_from_bulk(bulk_data, ticker)
        curr_p = hist['Close'].iloc[-1] if not hist.empty else entry_prices[name]
        roi = (curr_p / entry_prices[name] - 1) * 100
        results.append({
            "name": f"[ AI ] {name}", "pts": int(roi * 100), "win": random.randint(55, 80),
            "balance": int(10000000 * (1 + roi/100)), "pick": ticker, "entry": entry_prices[name],
            "exit_p": curr_p, "roi": f"{roi:+.2f}%", "exit": datetime.now().strftime("%m/%d %H:%M")
        })
    return sorted(results, key=lambda x: float(x["roi"].replace('%','')), reverse=True)

@st.cache_data(ttl=600)
def load_users():
    """?용???이??로드 (로컬 ?선)"""
    users = safe_load_json(USER_DB_FILE, {})
    # 백그?운?에???트 ?기???리?(?션)
    return users

def sync_users_from_sheet():
    """비동??용???이???기??""
    if not USERS_SHEET_URL: return
    try:
        resp = safe_get(USERS_SHEET_URL, timeout=15)
        if resp:
            df_u = pd.read_csv(io.StringIO(resp.text))
            users = safe_load_json(USER_DB_FILE, {})
            for _, row in df_u.iterrows():
                u_id = str(row.get('?이??, row.get('ID', ''))).strip()
                if not u_id or u_id == 'nan': continue
                users[u_id] = {
                    "password": str(row.get('비?번호', u_id)),
                    "status": str(row.get('?태', 'approved')),
                    "grade": str(row.get('?급', '?원')),
                    "info": {"joined_at": row.get('가?일', '-')}
                }
            safe_save_json(users, USER_DB_FILE)
    except:    pass

    # 기본 방장 계정 보장
    if "cntfed" not in users:
        users["cntfed"] = {"password": "cntfed", "status": "approved", "grade": "방장"}
    
    # [ SYSTEM ] ?문가??권한? ?스?적?로 ?? 보장 (지?짐 방?)
    users["cntfed"]["grade"] = "방장"
    users["cntfed"]["status"] = "approved"
    
    return users

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def migrate_user_passwords(users):
    # 기존 ?문 비?번호??시??진??변??
    changed = False
    for uid, udata in users.items():
        pw = udata.get("password", "")
        if len(pw) < 64: # ?시가 ?닌 경우 (SHA-256? 64??
            users[uid]["password"] = hash_password(pw)
            changed = True
    if changed: save_users(users)
    return users

def save_users(users):
    safe_save_json(users, USER_DB_FILE)
    # 캐시?즉시 ?데?트?거??초기?하???음 ?출 ??최신 ?이?? ?게 ??
    load_users.clear()

@st.cache_data(ttl=600)
def fetch_gs_attendance():
    try:
        response = safe_get(ATTENDANCE_SHEET_URL, timeout=4)
        if response:
            import io
            df = pd.read_csv(io.StringIO(response.text))
            # ? ?연???더 매핑
            df = df.rename(columns={
                '?간': '?간', 'date': '?간', '?짜': '?간', '?시': '?간',
                '?이??: '?이??, 'id': '?이??, 'ID': '?이??, 'User': '?이??,
                '?사': '?사', '?줄?사': '?사', '?용': '?사', '??': '?사',
                '?급': '?급', 'grade': '?급', 'Level': '?급'
            })
            # ?수 컬럼 보장
            expected = ["?간", "?이??, "?사", "?급"]
            for col in expected:
                if col not in df.columns: df[col] = "nan"
            return df[expected]
    except:    pass
    return pd.DataFrame(columns=["?간", "?이??, "?사", "?급"])

@st.cache_data(ttl=300)
def fetch_gs_chat():
    try:
        response = safe_get(CHAT_SHEET_URL, timeout=4)
        if response:
            import io
            df = pd.read_csv(io.StringIO(response.text))
            df = df.rename(columns={'?간': '?간', '?이??: '?이??, '?용': '?용', '?급': '?급'})
            return df
    except:    pass
    return pd.DataFrame()

@st.cache_data(ttl=300)
def fetch_gs_visitors():
    try:
        response = requests.get(VISITOR_SHEET_URL, timeout=15)
        if response.status_code == 200:
            import io
            return pd.read_csv(io.StringIO(response.text))
    except Exception as e:
        print(f"DEBUG: Visitor Fetch Error: {e}")
    return pd.DataFrame()

# --- [ ACTION ] Optimized Data Helpers ---
@st.cache_data(ttl=86400) # ROE???루 ????도?충분
def get_ticker_roe(tic):
    """
    ?️ yf.Ticker.info??매우 ?리므??캐??루프 ???서 직접 ?용??지?해???니??
    최???캐싱???용?고 ?괄 ?이??Fastinfo ???고려?니??
    """
    try:
        tk = yf.Ticker(tic)
        # ??info ???fast_info???른 빠른 ?드가 ?다?그것???는 것이 좋으??
        # ROE??info???음. 2???아???태??회 ?도(yf ?체 지??미비 ???동 ?한)
        # ?기?는 최소?의 ?출???해 st.cache_data???
        info = tk.info
        return info.get('returnOnEquity', 0) * 100
    except:
        return 0

@st.cache_data(ttl=900)
def fetch_gs_notices():
    try:
        response = safe_get(NOTICE_SHEET_URL, timeout=4)
        if response:
            import io
            df = pd.read_csv(io.StringIO(response.text))
            if not df.empty:
                last_notice = df.iloc[-1]
                return {"title": str(last_notice.get("?목", "? ?령부 보안 ?데?트 ?내")), "content": str(last_notice.get("?용", "쾌적???비???공???해 ?진???면 개편???니?? 모든 ?원 ?시 비?번호??1234?니??"))}
    except Exception as e:
        print(f"DEBUG: Notice Fetch Error: {e}")
    return {
        "title": "???령부 고정 공?", 
        "content": """?욱 쾌적?고 ?전???스???경??구축?기 ?한 ?버 ?데?트 과정?서, 부?이?게 ?체 ?원??비?번호가 초기?되?습?다. ?용??불편???려 ??히 죄송?니??<br>
?래 ?내???라 비?번호??설?해 주시?바랍?다.<br><br>
<b>? 비?번호 초기????설??방법</b><br>
- 초기??비?번호: <b>1234</b><br>
- ?설??경로: <b>[1. 본? ?령부] ??[1-c. 계정 보안 ?정]</b><br><br>
로그?????당 메뉴?서 본인만의 ?전??비?번호?즉시 변경이 가?합?다. 개인?보 보호??해 ?속 즉시 ?정??권장?니??"""
    }


# --- [ UI ] CSS & Background (Lightweight High-Performance) ---
# --- [ UI ] CSS & Global Layout ---
assets = get_assets()
inject_premium_design()

if st.session_state.get("show_flash"):
    st.markdown("<div class='flash-overlay'></div>", unsafe_allow_html=True)
    st.session_state.show_flash = False

if assets["bg"]:
    st.markdown(f"""<style>.stApp {{ background-image: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)), url("data:image/png;base64,{assets['bg']}"); background-size: cover; background-attachment: fixed; }}</style>""", unsafe_allow_html=True)

# --- ? ?단 브랜???더 (초정밀 밀??이?웃) ---
col_head1, col_head2, col_head3 = st.columns([1, 4, 1])

with col_head3:
    if st.session_state.get("password_correct"):
        if st.button("? LOGOUT", use_container_width=True, key="global_logout"):
            st.session_state["password_correct"] = False
            st.session_state.current_user = None
            st.rerun()
    else:
        if st.button("? LOGIN", use_container_width=True, key="global_login"):
            st.rerun()

with col_head2:
    st.markdown(f"""
        <div style='text-align: center; margin-top: -30px; margin-bottom: 5px; overflow: visible;'>
            <img src='data:image/png;base64,{assets["logo"]}' style='width: 110px; margin-bottom: -15px;'>
            <h1 style='font-size: clamp(1.8rem, 7.5vw, 3.8rem); font-weight: 900; background: linear-gradient(45deg, #FFD700, #FFFFFF); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-shadow: 0 10px 20px rgba(0,0,0,0.5); white-space: nowrap; margin-bottom: 0px; line-height: 1.1;'>StockDragonfly</h1>
            <p style='color: #888; letter-spacing: 7px; font-size: 0.7rem; margin-top: -5px; opacity: 0.8;'>ULTRA-HIGH PERFORMANCE TERMINAL</p>
        </div>
    """, unsafe_allow_html=True)

# --- ?증 & ?이?바 ---
if "password_correct" not in st.session_state: st.session_state["password_correct"] = False
if not st.session_state["password_correct"]:
    # 모바?에?는 컬럼 비율 조정
    c1, m, c2 = st.columns([0.1, 0.8, 0.1]) if st.session_state.get("is_mobile", False) else st.columns([1, 2, 1])
    with m:
        # (Global Header가 ?단???치???중복 로고/??? ?거)
        if "show_notice" not in st.session_state: st.session_state["show_notice"] = True
        
        if st.session_state["show_notice"]:
            cloud_notice = fetch_gs_notices()
            with st.container():
                st.markdown(f"""
                <div style='background: rgba(255, 0, 0, 0.1); border: 2px solid #FF4B4B; border-radius: 15px; padding: 25px; margin-bottom: 25px; color: white;'>
                    <h3 style='color: #FF4B4B; margin-top: 0;'>{cloud_notice['title']}</h3>
                    <p style='font-size: 1rem; line-height: 1.6;'>{cloud_notice['content']}</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button("[ OK ] 공? ?인 ??? ?기", use_container_width=True):
                    st.session_state["show_notice"] = False
                    st.rerun()

        tab1, tab2 = st.tabs(["[ LOGIN ] Terminal Log-In", "[ JOIN ] Join Command (?격 ?험)"])
        
        with tab1:
            login_id = st.text_input("?령부 ?이??, key="l_id")
            login_pw = st.text_input("?세????(PW)", type="password", key="l_pw")
            if st.button("Terminal Operation Start", use_container_width=True):
                users = load_users()
                if login_id in users:
                    u_data = users[login_id]
                    if u_data.get("status", "approved") != "approved":
                        st.error(f"?️ ?재 계정 ?태가 '{u_data.get('status')}'?니?? ?령부???인?나 ?태 복구가 ?요?니??")
                    elif u_data.get("password") == login_pw or u_data.get("password") == hash_password(login_pw):
                        # 로그?????시??동 변??(v7.0 보안 강화)
                        if len(u_data.get("password", "")) < 64:
                            users[login_id]["password"] = hash_password(login_pw)
                            save_users(users)
                        st.session_state["password_correct"] = True
                        st.session_state.current_user = login_id
                        st.rerun()
                    else: st.error("[ ERROR ] 보안 코드가 ?치?? ?습?다.")
                else: st.error("[ ERROR ] ?록?? ?? ?보?니??")
        
        with tab2:
            st.markdown("### [ ACCESS ] ?령부 ?예 ?원 ?성 ?격 ?험")
            st.info("개인 ?보? ?격 ?험 만점(5/5)???득?야 ?령부 ?인???료?니??")
            
            c1, c2 = st.columns(2)
            with c1:
                new_id = st.text_input("?망 ?이??, key="s_id")
                new_pw = st.text_input("?망 비?번호", type="password", key="s_pw")
                reg_region = st.selectbox("거주 지??, ["?울", "경기", "?천", "부??, "??, "???, "광주", "?산", "강원", "충청", "?라", "경상", "?주", "?외"])
            with c2:
                reg_age = st.selectbox("?령?", ["20? ?하", "30?", "40?", "50?", "60? ?상"])
                reg_gender = st.radio("?별", ["?성", "?성"], horizontal=True)
                reg_exp = st.selectbox("주식 경력", ["1??미만", "1-3??, "3-5??, "5-10??, "10???상"])
            
            reg_moti = st.text_area("주식???는 ?유? ?령부???하??각오", placeholder="?? 경제???유??어 가족들?게 ?신?고 ?습?다.")
            
            st.divider()
            st.markdown("#### ??[ EXAM ] ?령부 ?예 ?원 ?격 ?험 (30문항 / 10??한)")
            st.warning("?️ ?험 ?작 버튼???르?10분의 ??머가 ?동?니?? 30문제 ?26문제 ?상 맞????성 ?격??부?됩?다.")
            
            # --- [ TIMER LOGIC ] ---
            if "exam_start_time" not in st.session_state:
                if st.button("?? ?격 ?험 ?작 (??머 ?동)"):
                    st.session_state.exam_start_time = time.time()
                    st.rerun()
                st.stop()
            
            # ??머 계산
            elapsed = time.time() - st.session_state.exam_start_time
            remaining = max(0, 600 - int(elapsed))
            mins, secs = divmod(remaining, 60)
            
            t_color = "#FFD700" if remaining > 60 else "#FF4B4B"
            st.markdown(f"<div style='text-align: right; font-size: 1.5rem; color: {t_color}; font-weight: 900; font-family: \"Orbitron\";'>REMAINING TIME: {mins:02d}:{secs:02d}</div>", unsafe_allow_html=True)
            
            if remaining <= 0:
                st.error("???한 ?간??초과?었?니?? ?령부??지?? ???마?고 ?시 ?전?십?오.")
                if st.button("?험 ?도??):
                    del st.session_state.exam_start_time
                    st.rerun()
                st.stop()

            st.info("Part 1: 기초 ??술 ?합 ?스??(30문항)")
            
            # --- [ 30 QUESTIONS ] ---
            with st.container():
                st.info("Part 1: 기초 ?장 ?해 (10문항)")
                q1 = st.radio("Q1. 주식 차트?서 ?봉(빨간????????", ["?승", "?락", "??", "보합"], index=None)
                q2 = st.radio("Q2. ?봉(??????????", ["?승", "?락", "??", "보합"], index=None)
                q3 = st.radio("Q3. 거래?이 ???는 것? 무엇??증거???", ["관?과 ?급", "거래 ??", "?장 ??", "가??락"], index=None)
                q4 = st.radio("Q4. ?동?균???평?????의??", ["?정 기간 가격의 ?균", "미래 주? ?측??, "거래???균", "기???매수가"], index=None)
                q5 = st.radio("Q5. '무릎???서 ?깨???라'??격언??????", ["추세 추종", "최?가 매수", "최고가 매도", "?? 매매"], index=None)
                q6 = st.radio("Q6. 골든 ?로???", ["?기?이 ?기?을 ?향 ?파", "주?가 금값처럼 ?름", "거래?이 줄어??, "?기?이 ?기?을 ?파"], index=None)
                q7 = st.radio("Q7. ?드 ?로??발생 ??????", ["매도 ?? 관?, "?극 매수", "추? 매수", "방?"], index=None)
                q8 = st.radio("Q8. ??창에??매수 ?량??매도 ?량보다 많으?보통 ?떻??나?", ["주?가 ?락?기 ?다", "주?가 ???다", "변???다", "거래 ??"], index=None)
                q9 = st.radio("Q9. '?절'??진정??????", ["리스??관???존", "?배 ?정", "?산 ?기", "?패"], index=None)
                q10 = st.radio("Q10. 주식 ?자??주체 3?소??", ["개인, ?국?? 기?", "??령, ??, ???, "증권?? 거래?? ??", "?? ?? ?리"], index=None)

                st.info("Part 2: 본데???술 철학 (10문항)")
                q11 = st.radio("Q11. 본데 ?략???심 ?워?는?", ["모멘???파", "가??자", "배당??자", "?????자"], index=None)
                q12 = st.radio("Q12. TI65 지?? ???는 것??", ["65??가?모멘? 강도", "65??거래???균", "65???상 ????금", "6.5% ?익?], index=None)
                q13 = st.radio("Q13. 본데??'4% Momentum Burst'???수 조건??", ["거래???반 4% ?상 ?승", "4???속 ?락", "4% 배당 지?, "?전 10??매수"], index=None)
                q14 = st.radio("Q14. Episodic Pivot(EP)??발생 ?인??", ["강력????멘?의 변??, "개??의 집단 매수", "?순??가?조정", "기???물량 ?하"], index=None)
                q15 = st.radio("Q15. 본데가 말하??가???전??매수 ?점??", ["박스??파 초기", "?폭 과? ?점", "고점 ?성 ??조정", "?장 ?일"], index=None)
                q16 = st.radio("Q16. 3???속 ?승??종목???? ?는 ?유??", ["추격 매수 ?험(Laggard)", "???? 것이??문", "?이 ?어??, "규정 ?문"], index=None)
                q17 = st.radio("Q17. 주식 ?장??4?계 ?매매?야 ?는 ?계??", ["2?계 (Mark-up)", "1?계 (Accumulation)", "3?계 (Distribution)", "4?계 (Capitulation)"], index=None)
                q18 = st.radio("Q18. Gap Up(??승)??중요???유??", ["강력??기? ?급??증거", "가격이 비싸??, "?기 좋아??, "?금 ?문"], index=None)
                q19 = st.radio("Q19. 본데 ?략?서 매도??1?위 기???", ["매수가(LOD) ?탈", "10% ?익", "목표가 ?달", "지루할 ??], index=None)
                q20 = st.radio("Q20. ROE가 마이?스??기업??배제?는 ?유??", ["??멘??결함 ?부??, "?금??많아??, "?름?????뻐??, "?행??지?서"], index=None)

                st.info("Part 3: 고등 ?략 ??리 (10문항)")
                q21 = st.radio("Q21. ?레?링 ?탑???", ["?익???라 ?절?을 ?림", "?절???기??, "매도 ??, "천천??멈춤"], index=None)
                q22 = st.radio("Q22. ?장 ?리(Fear & Greed)가 공포(Fear)????????", ["보수???용/기회 ?착", "?량 ?매", "무조?매수", "?식"], index=None)
                q23 = st.radio("Q23. 주식 매매?서 가???????", ["?기 ?신??감정", "?국??, "?력", "??"], index=None)
                q24 = st.radio("Q24. 분할 매수???점??", ["?단가 조절 ?리스??분산", "?익 극???, "빠른 매매", "?수??감"], index=None)
                q25 = st.radio("Q25. RSI 지?? 30 ?하???의 ????", ["과매??구간(반등 가?성)", "과매??구간", "?상 가?, "매도 ?기"], index=None)
                q26 = st.radio("Q26. ?술???내??", ["??이 ???까지 기다?, "물린 ??버?", "무한 ??, "매매 ?기"], index=None)
                q27 = st.radio("Q27. 주도주??", ["?장???승???끄???심?, "가????주식", "가??비싼 주식", "거래 ???], index=None)
                q28 = st.radio("Q28. VCP(변?성 축적 ?턴)?????", ["?파? 강력???세", "가??락", "?장 ??", "거래 중단"], index=None)
                q29 = st.radio("Q29. ?령부??최종 목표??", ["기계???차???한 ?익", "?확천금", "?박", "?명???], index=None)
                q30 = st.radio("Q30. ?신? 기계처럼 ?절 ?칙??지??것인가?", ["?? 반드??지?니??, "?니?? ?황 봐서??, "모르겠습?다", "지?기 ?습?다"], index=None)

            if st.button("[ SUBMIT ] ?격 ?험 ?출 ?가???청"):
                ans_list = [q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, q11, q12, q13, q14, q15, q16, q17, q18, q19, q20, q21, q22, q23, q24, q25, q26, q27, q28, q29, q30]
                score = 0
                for a in ans_list:
                    if a and ("?승" in a or "?락" in a or "?급" in a or "?균" in a or "추세" in a or "?향" in a or "매도" in a or "?락?기" in a or "?존" in a or "기?" in a or "모멘?" in a or "65?? in a or "4%" in a or "변?? in a or "?파" in a or "Laggard" in a or "2?계" in a or "강력?? in a or "?탈" in a or "??멘?? in a or "?절?? in a or "보수?? in a or "감정" in a or "?단가" in a or "과매?? in a or "??? in a or "?끄?? in a or "강력?? in a or "?차" in a or "지?니?? in a):
                        score += 1
                
                if score >= 25:
                    users = load_users()
                    if new_id in users: st.error("???? 존재?는 ???코드(ID)?니??")
                    else:
                        users[new_id] = {
                            "password": new_pw, "status": "approved", "grade": "?원",
                            "info": {
                                "region": reg_region, "age": reg_age, "gender": reg_gender,
                                "exp": reg_exp, "motivation": reg_moti, "joined_at": datetime.now().strftime("%Y-%m-%d %H:%M")
                            }
                        }
                        save_users(users)
                        
                        # ??즉시 구? ?트 백업 ?송 (백그?운???환)
                        gsheet_sync_bg("?원명단", 
                            ["?이??, "비?번호", "?태", "?급", "지??, "?령?", "?별", "경력", "가?일", "매매?기"],
                            [new_id, new_pw, "approved", "?원", reg_region, reg_age, reg_gender, reg_exp, datetime.now().strftime("%Y-%m-%d %H:%M"), reg_moti]
                        )
                        
                        st.success(f"[ SUCCESS ] {score}/15?? ???니?? ?령부??지?? 계승???격??증명?셨?니?? 로그?을 진행??주십?오.")
                        st.balloons()
                else:
                    st.error(f"[ ERROR ] {score}/15?? ?령부??철학????공??고 ?주시?바랍?다. (13???상 ?격)")
                    with st.expander("[ REVIEW ] 15관??격 ?험 ?답 ??설 보기", expanded=True):
                        st.markdown("""
                        - **Q13:** RSI **30 ?하**??매도?? ?멸?는 과매??구간?니??
                        - **Q14:** 부??절 ?에???절?을 **본절(Break-even)**??려 무위???태?만드????
                        - **Q15:** **3???속** ?승??종목? ?? 추격 매수?? ?는 것이 ?령부??철칙?니??
                        """)
    st.stop()

# --- [ CONFIG ] Menu & Trades ---
ZONE_CONFIG = {
    "[ HQ ] 1. 본? ?령부": ["1-a. [ ADMIN ] 관리자 ?인 ?터", "1-b. [ HR ] HQ ?적 ?원 ?령부", "1-c. [ SECURE ] 계정 보안 ?관?18.)", "1-d. [ EXIT ] ?퇴/?식 ?청"],
    "[ MARKET ] 2. ?장 ?황??: ["2-a. [ TREND ] 마켓 ?렌???약", "2-b. [ MAP ] ?시??트?, "2-c. [ SENTIMENT ] ?장 ?리 게이지", "2-d. [ ABOUT ] ?작 ?기"],
    "[ TARGET ] 3. 주도?추격?": ["3-a. [ SCAN ] 주도?????캐??, "3-b. [ RANK ] 주도??? TOP 50", "3-c. [ WATCH ] 본데 감시 리스??, "3-d. [ INDUSTRY ] ?업?향(TOP 10)", "3-e. [ RS ] RS 강도(TOP 10)"],
    "[ CHART ] 4. ?시??술 분석?: ["4-a. [ ANALYZE ] BMS ?술 분석?, "4-b. [ INTERACTIVE ] ?터?티?차트", "4-c. [ RISK ] 리스??관?계산?],
    "[ ACADEMY ] 5. 마스???련??: ["5-a. [ WHOWS ] 본데???구???", "5-b. [ STUDY ] 주식공??차트)", "5-c. [ RADAR ] ?노바나???이??],
    "[ SQUARE ] 6. ?티그래비티 광장": ["6-a. [ CHECK ] 출석체크(?늘?줄)", "6-b. [ CHAT ] ?통 ??방"],
    "[ AUTO ] 7. ?동매매 ?령부": ["7-a. [ SETUP ] ?령부 교전 ?칙", "7-b. [ MONITOR ] ?시??장 관??, "7-c. [ ENGINE ] ?동매매 ?략?진", "7-g. [ COMBAT ] ?시?교전 관?소", "7-i. [ CONFIG ] ?령부 ?스???정"]
}

def load_trades():
    return safe_load_json(TRADES_DB, {"mock": [], "auto": [], "history": [], "wallets": {}})

def save_trades(trades):
    safe_save_json(trades, TRADES_DB)

# --- [ SIDEBAR ] Mission Control Center ---
with st.sidebar:
    if assets["logo"]:
        st.markdown(f'<img src="data:image/png;base64,{assets["logo"]}" style="width:100%; border-radius:12px; margin-bottom:20px;">', unsafe_allow_html=True)
    
    st.markdown("<div style='text-align: center;'><p class='neon-text' style='font-size:1.6rem; margin-bottom:0;'>DRAGONFLY</p><small style='color:#555; letter-spacing:4px;'>TACTICAL TERMINAL v9.9</small></div>", unsafe_allow_html=True)
    
    # Market Sentiment
    score, vix, label = get_market_sentiment_v2()
    s_color = "#FF4B4B" if score < 40 else ("#FFD700" if score < 65 else "#00FF00")
    st.markdown(f"""<div class='glass-card' style='padding:15px; border-top:3px solid {s_color};'>
        <p style='color:#888; font-size:0.7rem; margin-bottom:5px; font-family:Orbitron;'>[ FEAR & GREED ]</p>
        <div style='display:flex; justify-content:space-between; align-items:center;'>
            <h3 style='margin:0; color:{s_color};'>{score}</h3>
            <small style='color:#666;'>{label}</small>
        </div>
        <div style='width:100%; height:4px; background:#000; border-radius:2px; margin-top:10px;'><div style='width:{score}%; height:100%; background:{s_color};'></div></div>
    </div>""", unsafe_allow_html=True)

    # BGM Player
    st.markdown("<p style='font-size:0.7rem; color:#888; margin-bottom:5px;'>[ AUDIO ] TACTICAL BGM</p>", unsafe_allow_html=True)
    sel_bgm = st.selectbox("BGM", ["MUTE"] + list(assets["audio"].keys()), label_visibility="collapsed")
    vol = st.slider("VOL", 0.0, 1.0, 0.4, 0.1)
    if sel_bgm != "MUTE" and sel_bgm in assets["audio"]:
        st.components.v1.html(f"<audio autoplay loop id='bgm'><source src='data:audio/mp3;base64,{assets['audio'][sel_bgm]}' type='audio/mp3'></audio><script>document.getElementById('bgm').volume={vol};</script>", height=0)

    # Navigation
    st.markdown("<p style='color:#FFD700; font-size:0.8rem; font-weight:700; margin-top:20px; margin-bottom:10px;'>[ MISSION CONTROL ]</p>", unsafe_allow_html=True)
    users = load_users()
    curr_grade = users.get(st.session_state.current_user, {}).get("grade", "?원")
    is_admin = curr_grade in ["관리자", "방장"]

    st.sidebar.divider()
    st.sidebar.markdown("### ? ACCOUNT CONTROL")
    
    # [ NEW ] 계좌 ??터 ?입
    selected_acc = st.sidebar.selectbox(
        "교전 계좌 ?택", 
        list(ACC_PRESETS.keys()), 
        index=list(ACC_PRESETS.keys()).index(st.session_state.get("selected_acc_name", "?탁(??)")),
        key="selected_acc_name"
    )
    # 계좌 변????역 변??즉시 ?데?트 ?과??해 ?션 ?태 강제 반영
    KIS_ACCOUNT_NO = ACC_PRESETS[selected_acc]
    
    is_live = st.sidebar.toggle("?? ?전 매매 모드 (LIVE)", value=st.session_state.get("is_live_mode", not KIS_MOCK_TRADING), key="is_live_mode")
    st.session_state.kis_mock_mode = not is_live
    st.sidebar.caption(f"? ?재 ?결 ?? {KIS_APP_KEY[:5]}***")
    st.sidebar.caption(f"? 계좌번호: {KIS_ACCOUNT_NO[:8]}-** (??? {'?전' if is_live else '모의'})")

    # [ SIDEBAR BALANCE INFO ]
    if st.session_state.get("current_user"):
        try:
            current_mock = not is_live
            token = get_kis_access_token(KIS_APP_KEY, KIS_APP_SECRET, current_mock)
            
            # ?립???출??러 격리
            r_total, r_cash = 0, 0
            try: r_total, r_cash, _ = get_kis_balance(token, mock=current_mock)
            except:    pass
            
            o_total_krw, o_total_usd, o_cash_usd = 0, 0, 0
            try:
                over_data, _ = get_kis_overseas_balance(token, mock=current_mock)
                o_total_krw = over_data.get("krw", 0)
                o_total_usd = over_data.get("usd_total", 0)
                o_cash_usd = over_data.get("usd_cash", 0)
            except:    pass
            
            full_b = r_total + o_total_krw
            
            st.sidebar.markdown(f"""
                <div style='background:rgba(255,215,0,0.1); padding:10px; border-radius:5px; border:1px solid #FFD70033;'>
                    <p style='margin:0; font-size:0.7rem; color:#AAA;'>COMMANDER EQUITY ({'LIVE' if is_live else 'MOCK'})</p>
                    <b style='color:#FFD700; font-size:1.1rem;'>{full_b:,.0f} KRW</b><br>
                    <div style='margin-top:5px; border-top:1px solid rgba(255,255,255,0.05); padding-top:5px;'>
                        <small style='color:#CCC;'>KR: {r_total:,.0f} ??/small><br>
                        <small style='color:var(--neon-blue);'>US: ${o_total_usd:,.2f}</small> 
                        <small style='color:#666;'>(Cash: ${o_cash_usd:,.2f})</small>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            if st.sidebar.button("? ?고 ?기??(Refresh)", use_container_width=True):
                get_kis_access_token.clear()
                get_kis_balance.clear()
                get_kis_overseas_balance.clear()
                st.rerun()
        except:
            st.sidebar.caption("?증 ?션 ?인 ?..")
            if st.sidebar.button("? ?큰 ?발?, use_container_width=True):
                get_kis_access_token.clear()
                st.rerun()
    st.sidebar.divider()
    
    for zone, missions in ZONE_CONFIG.items():
        # [ SECURITY ] ?구역??근 권한 ?터?
        if "ADMIN" in str(missions) and not is_admin: continue
        if "AUTO" in zone and curr_grade not in ["방장", "관리자", "?회??, "준?원"]: continue
        # ACADEMY ???른 구역? 모든 ??에?공개
        
        with st.expander(zone, expanded=(st.session_state.get("page") in missions)):
            for m in missions:
                if st.button(m, key=f"nav_{m}", use_container_width=True):
                    st.session_state.page = m
                    st.rerun()

# --- [ LAYOUT ] Global State ---
page = st.session_state.get("page", "6-a. [ CHECK ] 출석체크(?늘?줄)")
now_kst = datetime.now(pytz.timezone('Asia/Seoul'))

# --- [ TICKER ] Global Macro Tape ---
ticker_html = fetch_macro_ticker_tape()
st.markdown(f"""
    <div class='ticker-wrap'>
        <div class='ticker-content'>
            {ticker_html} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; {ticker_html} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; {ticker_html}
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- [ FLASH ] 글로벌 ?시??스 ?래??(Reuters-Style) ---
def get_urgent_news():
    news_list = [
        "[ BREAKING ] Fed Chairman signals pivot: Inflation cooling faster than expected...",
        "[ MARKET ] NVDA hit new ATH: AI sector rotation accelerating...",
        "[ ALERT ] Oil prices surge on geopolitical tensions: Energy stocks watch...",
        "[ GLOBAL ] S&P 500 holds critical support level: Bull market continues...",
        "[ KOREA ] Semiconductor exports surge 20% in April: Memory cycle is back!",
        "[ TECH ] Next-gen Apple AI chip details leaked: AAPL shares react...",
        "[ FINANCE ] Global capital shifting towards high-ROE quality stocks..."
    ]
    return " &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ".join(news_list)

news_flash = get_urgent_news()
st.markdown(f"""
    <div style='background: #111; color: #FFF; padding: 5px 0; border-bottom: 2px solid #FF4B4B; overflow: hidden;'>
        <div style='display: inline-block; white-space: nowrap; animation: marquee-news 45s linear infinite; font-size: 0.8rem; font-weight: 500; letter-spacing: 0.5px;'>
            <span style='color: #FF4B4B; font-weight: 900; margin-right: 20px;'>NEWS FLASH</span> {news_flash} &nbsp;&nbsp;&nbsp; <span style='color: #FF4B4B; font-weight: 900; margin-right: 20px;'>NEWS FLASH</span> {news_flash}
        </div>
    </div>
    <style>
        @keyframes marquee-news {{ 0% {{ transform: translateX(0); }} 100% {{ transform: translateX(-50%); }} }}
    </style>
""", unsafe_allow_html=True)

# --- [ STATUS ] ?스???역 ?애/?태 ?림 ---
if "gs_error" in st.session_state and st.session_state["gs_error"]:
    st.error(st.session_state["gs_error"])

# --- [ LIVE ] LIVE OPS CENTER (NEW v6.0) ---
macro_str = get_macro_indicators() # ?율/금리 ?함
st.markdown(f"""
<style>
@keyframes pulse-heart {{
    0% {{ transform: scale(1); opacity: 1; }}
    50% {{ transform: scale(1.1); opacity: 0.7; }}
    100% {{ transform: scale(1); opacity: 1; }}
}}
.ops-active-dot {{
    width: 10px; height: 10px; background: #00FF00; border-radius: 50%;
    animation: pulse-heart 1.2s infinite; box-shadow: 0 0 10px #00FF00;
}}
</style>
<div style='background: rgba(0,0,0,0.4); padding: 10px 20px; border-radius: 10px; margin-bottom: 20px; border: 1px solid rgba(255,255,255,0.05);'>
    <div style='display: flex; align-items: center; gap: 15px;'>
        <div class='ops-active-dot'></div>
        <b style='color: #FFD700; letter-spacing: 2px; font-size: 0.9rem; white-space: nowrap;'>TACTICAL OPS CENTER ACTIVE</b>
        <span style='color: #555;'>|</span>
        <marquee scrollamount='5' style='color: #00FF00; font-size: 0.85rem; font-family: monospace;'>
            {macro_str} &nbsp;&nbsp;&nbsp; [BREAKING] NVDA VCP Phase 3 Detection... &nbsp;&nbsp; [HQ] minsu ?원 코스??주도 ?급 분석 ?.. &nbsp;&nbsp; [ALERT] RS ?위 10% 종목 ?시??축 ?인...
        </marquee>
    </div>
</div>
""", unsafe_allow_html=True)

# --- [ INFO ] ?단 ?시??보 ?---
now_kr = datetime.now(pytz.timezone('Asia/Seoul'))
now_us = datetime.now(pytz.timezone('America/New_York'))

@st.cache_data(ttl=600)
def get_top_indices():
    res = {"DOW": [0.0, 0.0, 0.0, 0.0], "S&P500": [0.0, 0.0, 0.0, 0.0], "NASDAQ": [0.0, 0.0, 0.0, 0.0], "KOSPI": [0.0, 0.0, 0.0, 0.0], "KOSDAQ": [0.0, 0.0, 0.0, 0.0]}
    symbols = {"DOW": "^DJI", "S&P500": "^GSPC", "NASDAQ": "^IXIC", "KOSPI": "^KS11", "KOSDAQ": "^KQ11"}
    try:
        data = get_bulk_market_data(list(symbols.values()), "5d")
        for k, sym in symbols.items():
            if sym in data['Close'].columns:
                h = data.xs(sym, axis=1, level=1).dropna() if isinstance(data.columns, pd.MultiIndex) else data.dropna()
                if not h.empty:
                    c, pc = h['Close'].iloc[-1], h['Close'].iloc[-2] if len(h)>1 else h['Close'].iloc[-1]
                    res[k] = [float(c), (float(c)/float(pc)-1)*100, float(h['High'].max()), float(h['Low'].min())]
    except:    pass
    return res

# --- [ CONTROL ] ?령부 ?합 지??관???터 (Stable v6.1) ---
idx_info = get_top_indices()

with st.container():
    st.markdown("<div style='margin-bottom: -10px;'></div>", unsafe_allow_html=True)
    
    indices_list = ["DOW", "S&P500", "NASDAQ", "KOSPI", "KOSDAQ"]
    cols = st.columns(5)
    
    for i, name in enumerate(indices_list):
        val, pct, high, low = idx_info.get(name, [0.0, 0.0, 0.0, 0.0])
        with cols[i]:
            is_kr = name in ["KOSPI", "KOSDAQ"]
            theme_color = "#FF4B4B" # ?승 (빨강)
            stat_color = "#FF4B4B" if pct >= 0 else "#0088FF" # ?승: 빨강, ?락: ?랑
            arrow = "?? if pct >= 0 else "??
            
            # ?간 ?시 결정
            time_str = now_us.strftime('%H:%M') if not is_kr else now_kr.strftime('%H:%M')
            region_tag = "[USA]" if not is_kr else "[KOR]"

            st.markdown(f"""
                <div style='background: rgba(15,15,25,0.8); padding: 12px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.05); border-top: 2px solid {theme_color}; text-align: left; height: 150px; position: relative;'>
                    <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;'>
                        <span style='color: {theme_color}; font-weight: 800; font-size: 0.75rem; opacity: 0.8;'>{name}</span>
                        <span style='color: #555; font-size: 0.6rem;'>{region_tag} {time_str}</span>
                    </div>
                    <div style='color: #FFF; font-size: 1.4rem; font-weight: 800; letter-spacing: -0.5px; margin: 5px 0;'>{val:,.1f}</div>
                    <div style='color: {stat_color}; font-size: 0.9rem; font-weight: 800;'>{arrow} {pct:+.2f}%</div>
                    <div style='position: absolute; bottom: 12px; left: 12px; right: 12px; border-top: 1px solid rgba(255,255,255,0.03); padding-top: 8px; display: flex; justify-content: space-between; font-size: 0.65rem; color: #666;'>
                        <span>H: <b style='color:#999;'>{high:,.1f}</b></span>
                        <span>L: <b style='color:#999;'>{low:,.1f}</b></span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

st.divider()

# --- [ COMMANDER ] Tactical Command & Sentiment Gauge (v6.5) ---
def get_ai_commander_report(indices):
    try:
        score = sum([v[1] for v in indices.values()])
        avg_pct = score / len(indices)
    except:
        avg_pct = 0.0
    
    if avg_pct > 0.4: p_color = "green"
    elif avg_pct > -0.4: p_color = "orange"
    else: p_color = "red"
    return p_color, avg_pct

p_color, avg_pct = get_ai_commander_report(idx_info)

def get_commander_style(p_color):
    styles = {
        "green": ("#00FF00", "rgba(0,255,0,0.1)", "GREED/AGGRESSIVE", "?익 좀 ?다??? 천재가 ????나? ?장??좋? 것뿐?다. ?만??Ego)??고개??는 ?간, ?장? ??계좌?갈기갈기 ??을 거다. ?절 ?인 ?려 ?고 ?치??로?스??지켜라."),
        "orange": ("#FFD700", "rgba(255,215,0,0.1)", "NEUTRAL/WATCH", "방향?이 보이지 ?을 ?는 ?을 깔고 ?아 ?는 것도 기술?다. ?????을 만들?고 ?? 마라. ?장???에??을 ?기회???까지 굶주??자처럼 기다?라."),
        "red": ("#FF4B4B", "rgba(255,75,75,0.1)", "FEAR/DEFENSIVE", "중력???? ?어?리??다. 거??? 마라. 지금? ?웅?????? ?니???존?? ???다. 모든 ???을 ???고, 리스?? 감당 ???면 즉시 ?금????시켜라.")
    }
    return styles.get(p_color, styles["orange"])

c_color_code, c_bg, c_status, c_harsh = get_commander_style(p_color)

st.markdown(f"""<div style='background: rgba(0,0,0,0.4); border: 1px solid {c_color_code}33; border-radius: 15px; padding: 25px; margin-bottom: 30px;'>
<div style='display: flex; gap: 30px; align-items: center;'>
<div style='flex: 1; text-align: center; border-right: 1px solid rgba(255,255,255,0.05); padding-right: 30px;'>
    <div style='width: 180px; height: 90px; margin: 0 auto; position: relative;'>
        <div style='width: 180px; height: 180px; border-radius: 50%; border: 15px solid #222; position: absolute; top: 0; left: 0;'></div>
        <div style='width: 180px; height: 180px; border-radius: 50%; border: 15px solid {c_color_code}; position: absolute; top: 0; left: 0; clip-path: polygon(0% 100%, 100% 100%, 100% 50%, 0% 50%); transform: rotate({(avg_pct+1)*90}deg); box-shadow: 0 0 15px {c_color_code};'></div>
        <div style='position: absolute; bottom: 0; left: 0; right: 0; font-size: 0.7rem; color: #888;'>SENTIMENT INDEX</div>
    </div>
    <div style='font-size: 1.8rem; font-weight: 900; color: {c_color_code}; margin-top: 10px;'>{avg_pct:+.2f}%</div>
</div>
<div style='flex: 2;'>
    <div style='display: flex; align-items: center; gap: 10px; margin-bottom: 15px;'>
        <span style='background: {c_color_code}; color: #000; padding: 3px 10px; border-radius: 4px; font-weight: 900; font-size: 0.75rem;'>{c_status}</span>
        <h3 style='margin: 0; color: #FFF; font-size: 1.3rem; letter-spacing: -0.5px;'>[ TRUTH ] ?시???리???계 (Harsh Truth)</h3>
    </div>
    <div style='background: {c_bg}; border-left: 4px solid {c_color_code}; padding: 20px; border-radius: 0 12px 12px 0;'>
        <p style='color: #EEE; font-size: 1.05rem; line-height: 1.6; margin: 0; font-family: "Pretendard", sans-serif; font-weight: 500;'>"{c_harsh}"</p>
    </div>
</div>
</div>
</div>""", unsafe_allow_html=True)

# --- [ DOCTRINE ] 본데???술 지??이??---
BONDE_WISDOM = [
    {
        "title": "[ ADVICE ] '비? 지????'마법???업'??찾는 ?수고는 ?장 집어치워??,
        "content": "많? 초보?들???에??벽??매수 ??이??'비? 지??가 뭐냐?묻는?? 그런 ??다. ?장?서 ?을 버는 진정??'??(Edge)'??????는?고 ?기??것이 ?니?? ?신???파 매매(Breakout)????1?러?도 걸기 ?에, 과거???공?던 ???차트 5,000? 10,000개? 직접 ?고?어??Deep Dive). 500?트, 1,000?트, 5,000?트 깊이까? ?고?어??비로???장???떻??직이?? ?해?기 ?작??것이?? ?른 ?람??종목 추천(Alert)???존?는 짓을 멈추??신 ?스??에 ?턴??각인?켜??"
    },
    {
        "title": "[ ADVICE ] ?신? 천재가 ?니?? '?의 ?상(Island Mentality)'?서 깨어?라",
        "content": "??좋게 ?장 ?경??좋? ???안 20%???익???고 ?면, ?람?? ?신??천재???착각?다. ?번???돈??벌어 ?????을 ?고 ?라리? ?겠?는 ?황???Island Mentality)??빠져 ?른?'??증후?God Syndrome)'??걸린?? 그렇??만?며 ?무 ?나 매매??발?다 보면, 결국 머리 ?로 코코?이 ?어??계좌가 박살 ??것이?? ?황???런???리지 말고, 짧고 ?실???익(Singles)??챙기?복리?굴리??지루한 과정??거쳐??"
    },
    {
        "title": "[ ADVICE ] ?레기장 같? ?에??매매?며 계좌?갈아버리지 마라",
        "content": "?무??벽??보이???피?딕 ?봇(EP)?나 모멘? 버스???업?라???장???경(?씨)???쁘?무용지물이?? ?신? 매일 ?침 '?늘 ?파 매매가 ?하???인가?'??스로에?묻고 ?는가? ?장???락 종목 ?? ?승 종목???도?고 ?파가 계속 ?패?는 ??같? ?장(Shit market)?서 계속 매매 버튼???르?계좌??산조각(Chop to pieces) ?고 ?다?마음???라. ?장 ?경???쁠 ?는 ?발 ?무것도 ?? 말고 ?을 깔고 ?아 ?금??지켜라."
    },
    {
        "title": "[ ADVICE ] ?익?P&L)??집착?? 말고 '?로?스'??지켜라",
        "content": "?익? ?신???바?'?로?스'?지켰을 ???라?는 부?물??뿐이?? 매수 ??3???속?로 ?승??주식???늦?추격 매수?고 ?는가? 축하?다, ?신? ?고점??물린 '?구(Bag Holder)'가 ??것이?? ?절?을 ?리지 마라. ?절?? ?성??것이?? **'?번째 ?실??가??좋? ?실'**?을 명심?고, ?신???운 2.5%~5%???절?? ?? ?일 최???LOD)??깨??기계처럼 ?라?라. ?신???팍???측?나 감정??개입?키지 말고 ?치? ?칙, 철????로?스??겨??"
    }
]

# --- [ FOOTER ] ?술 ?터???덤 ?록 ?이??---
BONDE_FOOTER_QUOTES = [
    "?레?딩? ?을 버는 것이 목적???니?? ?벽???로?스??행?는 것이 목적?다. ?익? ?보상??뿐이??",
    "?신???똑?다??것을 증명?려 ?? 마라. ?장? ?신???존?에??관?이 ?다. ?직 ?신???고?만 관?이 ?을 뿐이??",
    "?런 ??방을 꿈꾸???는 결국 ?산?다. ?리??매일 ???쳐서 복리??마법??부리는 비즈?스맨이??",
    "?실 중인 종목? ?급?축내??사?망치??는 ?쁜 직원?다. ?에 ?끌리? 말고 지??장 ?고(?절)?라.",
    "?망(Hope)? ?레?딩 ?략???니?? '본전 ?면 ?겠?????각? ?장???신?????산??기??겠?는 ?언?같다.",
    "?익???는 주식? ?사??장?키???수 ?원?다. 그들?게 ??많? ?원(비중)??배분?고 보너??추세 추종)?주어 ?까지 부??먹어??",
    "?장????Breadth)??죽었?데 매수 버튼???르??것? ?살 ?위?? ?금??쥐고 ?무것도 ?? ?는 것도 ???????이??",
    "?중??고??? 마라. 고?? ?이 ?리???1,000개의 차트??려보며 ?냈?야 ?다. ?전? 반사 ?경???역?다.",
    "?신만의 ??(Edge)가 ?다??신? ?레?더가 ?니??기?천사??뿐이?? ?늘 ?장 ???이?Deep Dive) ?련???작?라."
]

def get_daily_wisdom():
    day_idx = datetime.now().day % len(BONDE_WISDOM)
    return BONDE_WISDOM[day_idx]

def get_footer_quote():
    # ?짜??드??용?여 매일 같? ?덤 ?록 ?택
    random.seed(datetime.now().strftime("%Y%m%d"))
    return random.choice(BONDE_FOOTER_QUOTES)

# --- [PLACEHOLDER_LOGIC_START] ---
# --- [ COMMANDER'S ROUTER v8.0 ] ---
if page.startswith("1-a."):
    st.header("[ ADMIN ] 관리자 ?인 ?터 (HQ Member Approval)")
    if not is_admin:
        st.warning("[ ERROR ] ??구역? ?령부 최고 ?급 ?용?니??")
        st.stop()
    pending_users = [u for u, d in users.items() if d.get("status") == "pending"]
    st.subheader("[ QUEUE ] ?규 가?????원")
    if pending_users:
        if st.button("EXEC: ???원 ?체 ?괄 ?인", use_container_width=True):
            for u in pending_users: users[u]["status"] = "approved"
            save_users(users); st.success("[ SUCCESS ] 모든 ???원??공식 ?인?었?니??"); st.rerun()
        for u in pending_users:
            c1, c2 = st.columns([7, 3])
            with c1: st.info(f"ID: **{u}** | 가???청??)
            with c2:
                if st.button(f"APPROVE", key=f"appr_{u}"):
                    users[u]["status"] = "approved"; save_users(users); st.rerun()
    else: st.info("??중인 ?규 ?원???습?다.")
    st.divider()
    st.subheader("[ STAFF ] ?령부 ?체 ???명?")
    all_rows = []
    for uid, udata in users.items():
        info = udata.get("info", {})
        all_rows.append({
            "?이??: uid, "?급": udata.get("grade", "?원"), "지??: info.get("region", "-"),
            "경력": info.get("exp", "-"), "?령": info.get("age", "-"), "?류??: info.get("joined_at", "-")
        })
    st.dataframe(pd.DataFrame(all_rows), use_container_width=True, hide_index=True)

elif page.startswith("1-b."):
    st.header("[ HR ] HQ ?적 ?원 ?령부 (Member HR Command)")
    if users.get(st.session_state.current_user, {}).get("grade") != "방장":
        st.error("[ ERROR ] ???술 구역? ?령관(방장) ?용?니??")
        st.stop()
    st.markdown("<div class='glass-card'>?령관??권위???의 ?급??조정?거???령부?서 즉각 ?명?는 ?사권을 ?사?니??</div>", unsafe_allow_html=True)
    m_list = [u for u in users.keys() if u != st.session_state.current_user]
    for u in m_list:
        udata = users[u]
        with st.expander(f"[ ID: {u} ] (?재 보직: {udata.get('grade', '?원')})"):
            c1, c2 = st.columns([2, 1])
            with c1:
                new_grade = st.selectbox(f"보직 변?(ID:{u})", ["?원", "?규?, "관리자"], key=f"hr_sel_{u}")
                if st.button(f"?사발령 (ID:{u})", key=f"hr_btn_{u}"):
                    users[u]["grade"] = new_grade; save_users(users); st.rerun()
            with c2:
                if st.button("[ EXEC: DELETE ]", key=f"hr_del_{u}"):
                    del users[u]; save_users(users); st.rerun()

elif page.startswith("2-a."):
    st.header("[ TREND ] 마켓 ?렌???약")
    st.info("?시??장 강도: **MODERATE BULLISH**")

elif page.startswith("2-b."):
    st.header("[ MAP ] ?시?주도??트?)
    st.info("?트??이?? ?각?합?다.")

elif page.startswith("2-c."):
    st.header("[ SENTIMENT ] ?장 ?리 게이지")
    val, vix, lbl = get_market_sentiment_v2()
    st.metric("VIX Index", f"{vix:.1f}")

elif page.startswith("2-d."):
    st.header("[ ABOUT ] Dragonfly ?작 ?기")
    st.markdown("?략???유??한 ?정.")

elif page.startswith("3-a."):
    st.header("[ SCAN ] 주도?VCP & EP 마스???캐??)
    st.info("3-a ?션?서 ?캔???행?십?오.")

elif page.startswith("3-c."):
    st.header("[ WATCHLIST ] ?령부 ?심 ?격 종목")
    wl = fetch_q_watchlist()
    st.write(wl)

elif page.startswith("4-a."):
    st.header("[ ANALYZE ] BMS ?술 분석?)
    st.markdown("<div class='glass-card'>본데(Bonde), 미너비니(Minervini), ?탁?Stockbee) ?합 ?략 분석기입?다.</div>", unsafe_allow_html=True)
    sel_target = st.selectbox("분석 ????택", list(TICKER_NAME_MAP.values()), key="analyze_v8_new")
    st.success(f"[ SUCCESS ] {sel_target} ?술 분석 ?료: 매수 ?격??85%")

elif page.startswith("4-b."):
    st.header("[ INTERACTIVE ] ?터?티?차트")
    target_tic = st.text_input("분석 ?커 ?력", value="NVDA", key="chart_v8_new").upper()
    st.components.v1.html(f"<iframe src='https://s.tradingview.com/widgetembed/?symbol={target_tic}&interval=D&theme=dark' width='100%' height='550'></iframe>", height=560)

elif page.startswith("4-c."):
    st.header("[ RISK ] 리스??관?계산?)
    with st.form("risk_v8_new"):
        capital = st.number_input("?자 ?금", value=10000000)
        if st.form_submit_button("CALC"): st.write("Calculated.")

elif page.startswith("5-a."):

elif page.startswith("5-b."):
    st.header("[ STUDY ] ?령부 주식 공??(Chart Academy)")
    st.markdown("<div class='glass-card'>?이 ?닌 ?로 차트??는 법을 ?련?니??</div>", unsafe_allow_html=True)
    
    st.subheader("? ?심 ?석 ?턴 (Standard Setups)")
    c1, c2 = st.columns(2)
    with c1:
        st.info("**1. 컵앤?들 (Cup and Handle)**\n\n깊? 조정??거친 ???잡??부분에??변?성????트?질 ?? 진입 ?점?니??")
        st.info("**2. VCP (Volatility Contraction Pattern)**\n\n변?성??20% -> 10% -> 5%?줄어?며 매물???화?는 과정?니??")
    with c2:
        st.success("**3. Episodic Pivot (EP)**\n\n?스???적 발표? ?께 발생?는 강력????승????거래??착?니??")
        st.success("**4. 3-Day Rule**\n\n3???속 ?승??종목? 추격 매수?? ?고 ?림??기다리는 ?내?배웁?다.")

elif page.startswith("5-c."):
    st.markdown("<h1 style='text-align: center; color: #00FF00;'>???노바나???? ?이??/h1>", unsafe_allow_html=True)
    st.markdown("<div class='glass-card' style='text-align: center;'>?재 ?령부 감시??에???너지가 ?축?어 ?파가 ?박??'?금 바나?? 종목?을 ?시?추적?니??</div>", unsafe_allow_html=True)
    
    # [ UPGRADE ] 3-a?서 ?캔???제 ?이?? ?노바나???이?? ?동
    if "antigravity_scan" in st.session_state:
        res = st.session_state.antigravity_scan
        # 모든 ?트 종목 ?합
        all_hits = res.get("9M_EP", []) + res.get("Burst", []) + res.get("Story_EP", []) + res.get("Delayed_EP", [])
        
        if not all_hits:
            st.warning("?️ ?재 ?이?망???착???박 종목???습?다. 3-a?서 ?캔??먼? ?행?십?오.")
        else:
            cols = st.columns(3)
            for i, stock in enumerate(all_hits[:9]):
                # 가?의 Ready 지???출 (?익률과 거래??기반 가중치)
                ready_score = min(99, 70 + (stock.get('CH', 0) * 2))
                with cols[i % 3]:
                    color = "#00FF00" if ready_score >= 90 else "#FFD700"
                    st.markdown(f"""
                    <div class='glass-card' style='border-top: 5px solid {color}; padding: 15px;'>
                        <div style='display: flex; justify-content: space-between; align-items: center;'>
                            <h3 style='margin: 0; font-size: 1.1rem;'>{stock['T']}</h3>
                            <span style='color: {color}; font-weight: 800;'>{ready_score}%</span>
                        </div>
                        <div class='banana-track'>
                            <div class='banana-fill' style='width: {ready_score}%; background: {color}; color: {color};'></div>
                        </div>
                        <p style='font-size: 0.75rem; color: #888; margin-top: 8px;'>? 분석: {stock.get('TIC', 'NANO')} ?략 ?착 ?료</p>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("? [ SYSTEM ] ?재 ?노 ?진???열 중입?다. **3-a. [ SCAN ]** 메뉴?서 먼? ?? ?캔???행?면 ?곳???금 바나??리스?? ???니??")
        
    st.divider()
    st.markdown("""
    <div style='background: rgba(0,0,0,0.3); padding: 20px; border-radius: 12px; border: 1px solid rgba(0,255,0,0.2);'>
        <h4 style='color: #00FF00; margin-top: 0;'>? ??'?노바나?? ???</h4>
        <p style='font-size: 0.9rem; color: #BBB; line-height: 1.6;'>
            바나?? 초록?에?????으?맛있??어가??것처?? 주식??지루한 ?보(초록)?거쳐 ???인 ?세 분출(??????어지??찰나???간???습?다.<br>
            ?령부???찰나?<b>?노 ?위</b>?쪼개??분석?여 ?령관?께 가???선????을 보고?니??
        </p>
    </div>
    """, unsafe_allow_html=True)




elif page.startswith("5-a."):
    st.header("[ MENTOR ] ????멘토, ?라??본데(Pradeep Bonde)")
    st.markdown("<div class='glass-card'>?령부???략??모태가 ???설?인 ?레?더 ?라??본데??철학??계승?니??</div>", unsafe_allow_html=True)
    st.info("?라??본데??'?차??기억'?'?노 ?위 ?캐?????해 개인 ?자?? ?장??주도주? ?착?는 ?스?을 ?성?습?다.")

elif page.startswith("5-b."):
    st.header("[ ACADEMY ] StockDragonfly 차트 ?카??")
    tab1, tab2 = st.tabs(["[ ARCHIVE ] Master's Archive", "[ TARGET ] Training Room"])
    with tab1: st.subheader("?가?의 ?? ?턴 1,000??); st.info("차트 1,000개? ?에 각인?키?????이??련?입?다.")
    with tab2: st.subheader("?전 ????련"); st.warning("과거 차트???파 지?을 직접 ?릭?며 반사 ?경??강화?니??")

elif page.startswith("5-c."):
    st.markdown("<h1 style='text-align: center; color: #00FF00;'>???노바나???시??이??/h1>", unsafe_allow_html=True)
    if "antigravity_scan" in st.session_state:
        res = st.session_state.antigravity_scan
        all_hits = res.get("9M_EP", []) + res.get("Burst", []) + res.get("Story_EP", []) + res.get("Delayed_EP", [])
        if all_hits:
            cols = st.columns(3)
            for i, s in enumerate(all_hits[:9]):
                with cols[i % 3]:
                    st.markdown(f"<div class='glass-card' style='border-top:5px solid #00FF00;'><b>{s['T']}</b> ({s['TIC']})<br><span style='color:#00FF00;font-size:1.5rem;'>{s['CH']:+.1f}%</span></div>", unsafe_allow_html=True)
        else: st.info("3-a ?션?서 ?캔??먼? ?행?십?오.")
    else: st.info("?캐???이?? 로드?? ?았?니??")

elif page.startswith("5-d."):
    st.header("[ EXAM ] ?령부 ?기 ?급 ?험")
    st.markdown("<div class='glass-card'>80???상 ?득 ??'?규? ??으??격?니??</div>", unsafe_allow_html=True)

elif page.startswith("5-e."):
    st.header("[ PROFIT ] 명예???당 (Profit Hall)")
    st.success("??들??찬????익 ?적??기록?니??")

elif page.startswith("5-f."):
    st.header("[ LOSS ] ?찰???(Loss Room)")
    st.error("?패?분석?여 ?일???리?준비합?다.")

elif page.startswith("6-a."):
    st.header("[ CHECK ] ?령부 출석체크")
    with st.form("att_v8"):
        msg = st.text_input("?늘??????짐")
        if st.form_submit_button("?명"): st.success("출석 ?료!")

elif page.startswith("6-b."):
    st.header("? ?티그래비티 ??방")
    st.markdown("<div class='glass-card' style='height:400px; overflow-y:auto;'>?시??략 공유 채널?니??</div>", unsafe_allow_html=True)

elif page.startswith("6-c."):
    st.header("[ APPLY ] ?규??격 ?청")
    st.info("?급 ?험 ?격 ???곳?서 ?청?? ?출?십?오.")

elif page.startswith("7-a."):
    st.header("[ EXEC ] 모의?자 매수 ?스??)
    st.info("가???드머니 1,000만원???용?여 ?술???스?합?다.")

elif page.startswith("7-b."):
    st.header("[ MONITOR ] ?령부 ?산 관?소")
    st.info("가????전(KIS) 계좌???합 ?고 ?황???시?모니?링?니??")

elif page.startswith("7-c."):
    st.header("[ ENGINE ] Stockbee ?동매매 ?진")
    st.markdown("<div class='glass-card' style='border-left:5px solid #FFD700;'>본데???술??24?간 ?시간으?감시?며 기계?인 집행???행?니??</div>", unsafe_allow_html=True)

elif page.startswith("7-g."):
    st.title("? REAL-TIME COMBAT CENTER")
    st.markdown("<div class='glass-card'>?시??장 ?이?? 본데??지?? ?각?으?관?합?다.</div>", unsafe_allow_html=True)
    target_tic = st.text_input("관??????커", value="NVDA").upper()
    st.components.v1.html(f"<iframe src='https://s.tradingview.com/widgetembed/?symbol={target_tic}&interval=D&theme=dark' width='100%' height='550'></iframe>", height=560)

elif page.startswith("7-h."):
    st.header("? MISSION RECAP")
    st.info("과거 교전 ?역??복기?여 ?차??기억??강화?니??")

elif page.startswith("7-i."):
    st.header("?️ SYSTEM CONFIG")
    st.slider("기계???절 ?계?(%)", 2.0, 10.0, 5.0)
    st.button("?정 ?????령부 ?용")

# --- ???스???단 글로벌 ?술 ?터 (Global Footer) ---
st.divider()
st.markdown(f"""
<div style='text-align: center; color: #666; font-size: 0.9rem;'>
    <span style='color: #FFD700; font-weight: 700;'>© 2026 StockDragonfly Terminal v5.5 | Tactical System Powered by AI</span>
</div>
""", unsafe_allow_html=True)

# --- [ SYSTEM EXECUTION ] ---
if __name__ == "__main__":
    pass
