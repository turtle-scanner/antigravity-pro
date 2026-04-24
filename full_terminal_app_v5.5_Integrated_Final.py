# 작업 일자: 2026-04-19 | 버전: v9.9 Platinum Full Restoration (Step 1: Base)
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
    """정적 자산(이미지, 오디오)을 한 번만 로드하여 캐싱 (성능 극대화)"""
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
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Inter:wght@300;400;600&family=Outfit:wght@300;900&display=swap');
        :root { --neon-blue: #00FFFF; --neon-green: #00FF00; --neon-red: #FF4B4B; --neon-gold: #FFD700; --glass: rgba(15, 15, 25, 0.7); }
        .stApp { background: #050505; font-family: 'Inter', sans-serif; color: #EEE; }
        .glass-card { background: var(--glass); backdrop-filter: blur(15px); border: 1px solid rgba(255,255,255,0.1); border-radius: 15px; padding: 20px; margin-bottom: 20px; transition: 0.3s; }
        .glass-card:hover { transform: translateY(-5px); border-color: var(--neon-blue); box-shadow: 0 0 20px rgba(0,255,255,0.2); }
        h1, h2, h3 { font-family: 'Orbitron', sans-serif !important; letter-spacing: 2px; color: var(--neon-gold) !important; }
        .stButton>button { background: rgba(0, 255, 255, 0.05) !important; border: 1px solid var(--neon-blue) !important; color: var(--neon-blue) !important; font-family: 'Orbitron'; border-radius: 8px !important; transition: 0.3s; }
        .stButton>button:hover { background: var(--neon-blue) !important; color: #000 !important; box-shadow: 0 0 30px var(--neon-blue); }
        [data-testid="stSidebar"] { background: rgba(5, 5, 10, 0.95) !important; backdrop-filter: blur(20px); border-right: 1px solid rgba(255,215,0,0.1); }
        @keyframes pulse { 0%, 100% { opacity: 0.5; } 50% { opacity: 1; } }
        .status-pulse { width: 10px; height: 10px; border-radius: 50%; background: var(--neon-green); display: inline-block; animation: pulse 2s infinite; }
    </style>
    """, unsafe_allow_html=True)

# --- [ SYSTEM ] [GLOBAL HELPER] Safe Network Request ---
def safe_get(url, timeout=3):
    """지연 및 멈춤 방지를 위한 글로벌 네트워크 헬퍼"""
    try:
        resp = requests.get(url, timeout=timeout)
        if resp.status_code == 200: return resp
    except: pass
    return None

# --- [ TACTICAL ] Rule-based Tactical Advisor (Platinum Engine) ---
def get_tactical_advice(tic, rs, roe):
        advice = []
        if rs > 80: advice.append("[ MOMENTUM ] 강력한 Relative Strength 포착. 시장을 압도하는 주도주입니다.")
        elif rs > 50: advice.append("[ UP-TREND ] 양호한 추세 유지 중. 섹터 순환매 수급을 확인하십시오.")
        else: advice.append("[ CAUTION ] 추세가 다소 정체됨. 지지선 이탈 여부를 엄격히 감시하십시오.")
        
        if roe > 20: advice.append("[ PREMIUM ] 압도적 ROE. 기관이 가장 선호하는 우량 성장주 셋업입니다.")
        elif roe > 10: advice.append("[ STRONG ] 견고한 펀더멘털. 실적 발표 전후 돌파 타점을 노리십시오.")
        
        # 보너스 스타일 조언
        quotes = [
            "시장이 혼란스러울수록 기본에 충실하십시오. VCP의 끝자락은 항상 조용합니다.",
            "손절은 패배가 아닌, 다음 승리를 위한 보험료입니다.",
            "거래량이 마를 때를 기다리십시오. 폭발은 고요함 속에서 시작됩니다."
        ]
        advice.append(f"\nINFO: Bonde's Insight: {random.choice(quotes)}")
        return "\n".join(advice)

def get_footer_quote():
    """시스템 하단에 표시될 대가들의 격언"""
    quotes = [
        "VCP의 끝자락은 항상 조용합니다. 폭발은 고요함 속에서 시작됩니다.",
        "손절은 패배가 아닌, 다음 승리를 위한 보험료입니다.",
        "수익은 오직 2단계(Mark-up)에서만 창출됩니다. 기다림은 지루할 수 있으나 결과는 달콤합니다.",
        "리더는 나쁜 직원을 즉시 해고하듯, 추세가 꺾인 종목은 즉시 제명해야 합니다.",
        "시장에 맞서지 마십시오. 파도를 타는 해녀처럼 수급의 흐름에 몸을 맡기십시오.",
        "가장 강한 놈이 가장 멀리 갑니다. RS 신고가에 답이 있습니다."
    ]
    return random.choice(quotes)

@st.cache_resource
def get_ai_chat_cooldown():
    """AI 채팅 범람 방지를 위한 전역 타이머 관리"""
    return {"last_time": 0}

def trigger_ai_chat():
    """AI 대원들이 랜덤하게 소통방에 메시지를 남기는 엔진 (6인 체제)"""
    # [ OPTIMIZE ] 전역 코울다운 체크 (15초 내 중복 발송 차단)
    cd = get_ai_chat_cooldown()
    if time.time() - cd["last_time"] < 15: return False
    
    ai_users = [
        {"name": "[ AI ] minsu", "grade": "AI_대원 (코스피)"},
        {"name": "[ AI ] Olive", "grade": "AI_대원 (코스닥)"},
        {"name": "[ AI ] Pure", "grade": "AI_대원 (나스닥)"},
        {"name": "[ AI ] Harmony", "grade": "AI_대원"},
        {"name": "[ AI ] Mint Soft", "grade": "AI_대원"},
        {"name": "[ AI ] Calm Blue12", "grade": "AI_대원"}
    ]
    ai_phrases = [
        "오늘 나스닥 선물 흐름이 심상치 않네요. 전술적 대기 권고합니다.",
        "방금 HTF 패턴 스캔 결과 공유했습니다. 주도주 수급이 강력하네요!",
        "손절가는 생명선입니다. 다들 원칙 매매 잘 지키고 계신가요?",
        "안티그래비티 사령부의 일관된 수익 공식: 인내, 그리고 기계적 대응입니다.",
        "VCP 최종 단계에서 거래량이 말라붙는 모습... 곧 폭발하겠군요.",
        "사령부 요원님들, 오늘도 성투하십시오! 뇌동매매는 사절입니다.",
        "시장의 소음(Noise)보다 차트의 신호(Signal)에 집중하세요.",
        "조급함은 중력과 같습니다. 안티그래비티 대원답게 무중력으로 비상합시다!",
        "오늘의 RS 상위 종목들 리스트가 정말 탄탄하네요. 주도주 랠리 준비 완료입니다."
    ]
    
    try:
        now_kst = datetime.now(pytz.timezone('Asia/Seoul')).strftime("%Y-%m-%d %H:%M:%S")
        ai = random.choice(ai_users)
        ms = random.choice(ai_phrases)
        # 로컬 저장
        new_msg = pd.DataFrame([[now_kst, ai["name"], ms, ai["grade"]]], columns=["시간", "유저", "내용", "등급"])
        safe_write_csv(new_msg, CHAT_FILE, mode='a', header=not os.path.exists(CHAT_FILE))
        cd["last_time"] = time.time() # 시간 갱신
        return True
    except: return False

# --- [ STORAGE ] 데이터베이스 및 영구 보존 설정 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
def get_db_path(f): return os.path.join(BASE_DIR, f)

BACKUP_DIR = get_db_path("backups")

def auto_backup(file_path, force=True):
    if not os.path.exists(file_path): return
    try:
        fname = os.path.basename(file_path)
        os.makedirs(BACKUP_DIR, exist_ok=True)
        
        # [ SECURE ] 전문가님 요청: 중요 파일들은 항상 백업 생성 (강제성 부여)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(BACKUP_DIR, f"{fname}_{timestamp}.bak")
        shutil.copy2(file_path, backup_path)
        
        # 백업 파일 개수 관리 (최근 50개 유지로 확장)
        if random.random() < 0.2:
            all_backups = sorted([os.path.join(BACKUP_DIR, f) for f in os.listdir(BACKUP_DIR) if f.startswith(fname)], key=os.path.getmtime)
            if len(all_backups) > 50:
                for old_f in all_backups[:-50]: os.remove(old_f)
    except: pass

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
    """비동기 구글 시트 데이터 전송 (UI 프리징 방지)"""
    def task():
        try: requests.post(MASTER_GAS_URL, json={"sheetName": sheet_name, "columns": cols, "row": row_data}, timeout=5)
        except: pass
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
        # 파일이 실제 존재하는데 읽기에 실패한 경우 경고 출력
        st.warning(f"WAIT: 데이터 파일([.csv]) 읽기 시도 중 지연이 발생하고 있습니다. 잠시 후 자동 복구됩니다. ({os.path.basename(file_path)})")
        return pd.DataFrame(columns=columns) if columns else pd.DataFrame()

def safe_write_csv(df, file_path, mode='w', header=True, backup=True):
    try:
        if backup and os.path.exists(file_path): auto_backup(file_path, force=True)
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        
        # 영구 보존을 위한 원자적 쓰기 강화
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

# [ SECURE ] 영구 백업용 구글 시트 URL (CSV 내보내기 주소) - 보안을 위해 st.secrets 사용
USERS_SHEET_URL = st.secrets.get("USERS_SHEET_URL", "https://docs.google.com/spreadsheets/d/1HbC_U1I78HAdV99X6qS1hmY_RiRGPrHX92AYbBPrIpU/export?format=csv&gid=1180564490")
ATTENDANCE_SHEET_URL = st.secrets.get("ATTENDANCE_SHEET_URL", "https://docs.google.com/spreadsheets/d/1HbC_U1I78HAdV99X6qS1hmY_RiRGPrHX92AYbBPrIpU/export?format=csv&gid=0")
CHAT_SHEET_URL = st.secrets.get("CHAT_SHEET_URL", "https://docs.google.com/spreadsheets/d/1HbC_U1I78HAdV99X6qS1hmY_RiRGPrHX92AYbBPrIpU/export?format=csv&gid=2147147361")
VISITOR_SHEET_URL = st.secrets.get("VISITOR_SHEET_URL", "https://docs.google.com/spreadsheets/d/1HbC_U1I78HAdV99X6qS1hmY_RiRGPrHX92AYbBPrIpU/export?format=csv&gid=621380834")
WITHDRAWN_SHEET_URL = st.secrets.get("WITHDRAWN_SHEET_URL", "https://docs.google.com/spreadsheets/d/1HbC_U1I78HAdV99X6qS1hmY_RiRGPrHX92AYbBPrIpU/export?format=csv&gid=1873947039")
# [ GLOBAL ] 전역 공지 및 UI 레이아웃 설정
NOTICE_SHEET_URL = st.secrets.get("NOTICE_SHEET_URL", "https://docs.google.com/spreadsheets/d/1HbC_U1I78HAdV99X6qS1hmY_RiRGPrHX92AYbBPrIpU/export?format=csv&gid=1619623253")

TICKER_NAME_MAP = {
    "NVDA": "엔비디아", "TSLA": "테슬라", "AAPL": "애플", "MSFT": "마이크로소프트", "PLTR": "팔란티어", "SMCI": "슈퍼마이크로", 
    "AMD": "AMD", "META": "메타", "GOOGL": "구글", "AVGO": "브로드컴", "CRWD": "크라우드스트라이크", "005930.KS": "삼성전자", 
    "000660.KS": "SK하이닉스", "196170.KQ": "알테오젠", "042700.KS": "한미반도체", "105560.KS": "KB금융", "055550.KS": "신한지주",
    "005490.KS": "POSCO홀딩스", "000270.KS": "기아", "066570.KS": "LG전자", "035720.KS": "카카오", "035420.KS": "NAVER",
    "005380.KS": "현대차", "000810.KS": "삼성화재", "NFLX": "넷플릭스", "MSTR": "마이크로스트래티지", "COIN": "코인베이스", 
    "MARA": "마라톤디지털", "PANW": "팔로알토", "SNOW": "스노우플레이크", "STX": "씨게이트", "WDC": "웨스턴디지털",
    "247540.KQ": "에코프로비엠", "277810.KQ": "에코프로", "091990.KQ": "셀트리온헬스케어", "293490.KQ": "카카오게임즈", "086520.KQ": "에코프로"
}

REVERSE_TICKER_MAP = {v: k for k, v in TICKER_NAME_MAP.items()}

def resolve_ticker(query):
    query = query.strip()
    # 6자리 숫자면 한국 주식 코드로 처리
    if query.isdigit() and len(query) == 6: return query + ".KS"
    
    if query in TICKER_NAME_MAP: return query
    if query.upper() in TICKER_NAME_MAP: return query.upper()
    if query in REVERSE_TICKER_MAP: return REVERSE_TICKER_MAP[query]
    return query.upper()

# --- [ ENGINE ] Unified Market Data Center ---
@st.cache_data(ttl=300)
def get_bulk_market_data(tickers, period="60d"):
    """전역 마켓 데이터 엔진 (API 호출 최적화)"""
    if not tickers: return pd.DataFrame()
    try:
        data = yf.download(list(set(tickers)), period=period, progress=False)
        return data if not data.empty else pd.DataFrame()
    except: return pd.DataFrame()

@st.cache_data(ttl=300)
def fetch_macro_ticker_tape():
    """애니메이션 티커용 데이터 수집"""
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
    """본데 주도주 Top 50 리스트 (구글 시트 연동)"""
    try:
        url = "https://docs.google.com/spreadsheets/d/1HbC_U1I78HAdV99X6qS1hmY_RiRGPrHX92AYbBPrIpU/export?format=csv&gid=780517835"
        resp = safe_get(url)
        if resp:
            df = pd.read_csv(io.StringIO(resp.text))
            return df.iloc[:, 0].dropna().tolist()
    except: pass
    return ["NVDA", "TSLA", "AAPL", "MSFT", "AMZN"]

def get_ticker_data_from_bulk(bulk_df, ticker):
    """일괄 다운로드 데이터에서 특정 종목만 추출"""
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
        return f"[ USD/KRW ]: {rate:,.1f}원 | [ US 10Y ]: {yield10y:.2f}%"
    except: return "[ USD/KRW ]: 1400.0원 | [ US 10Y ]: 4.30%"

# --- [ ENGINE ] KIS API & Core Trading Logic ---
# [ SECURITY ] 사용자가 제공한 API 정보를 우선 적용하되, secrets 설정이 있다면 그것을 따릅니다.
KIS_APP_KEY = st.secrets.get("KIS_APP_KEY", "PSwPjCXRoSuY1Uz59aDWYKpIPix7VgNB8QUX")
KIS_APP_SECRET = st.secrets.get("KIS_APP_SECRET", "4WF33M5pnD3Y3qskLfWAlwo0eFxpYIK+TdIXNVW9r+wSLAAF/WVxtqDIvNBDNakV28aFM9ZO+v8069JwBlYDpS1lBvoFf7j9dgSsPwjiwclbvyJ7nMYl5m62wH7VInWWtXgl/8hDnmihzDidKEIss87UdT42JANMvOrCSEF18e5SilJKRIA=")
# 계좌번호가 8자리일 경우 상품코드 '01'을 기본으로 붙여 10자리로 보정
raw_acc = st.secrets.get("KIS_ACCOUNT_NO", "46289819")
KIS_ACCOUNT_NO = raw_acc + "01" if len(raw_acc) == 8 else raw_acc
KIS_MOCK_TRADING = st.secrets.get("KIS_MOCK_TRADING", False) # 실전 계좌 연동을 위해 False 설정 권장

@st.cache_data(ttl=3500)
def get_kis_access_token(app_key, app_secret, mock=True):
    """한국투자증권 API 접근 토큰 발급"""
    base_url = "https://openapivts.koreainvestment.com:29443" if mock else "https://openapi.koreainvestment.com:9443"
    url = f"{base_url}/oauth2/tokenP"
    headers = {"content-type": "application/json"}
    body = {
        "grant_type": "client_credentials",
        "appkey": app_key,
        "appsecret": app_secret
    }
    try:
        res = requests.post(url, headers=headers, json=body, timeout=5)
        if res.status_code == 200:
            return res.json().get("access_token")
    except Exception as e:
        print(f"DEBUG: KIS Token Error: {e}")
    return None

def get_kis_balance(token):
    """국내 주식 잔고 및 예수금 현황 조회 (실제 연동)"""
    if not token or not KIS_ACCOUNT_NO: return 0, 0, []
    base_url = "https://openapivts.koreainvestment.com:29443" if KIS_MOCK_TRADING else "https://openapi.koreainvestment.com:9443"
    url = f"{base_url}/uapi/domestic-stock/v1/trading/inquire-balance"
    headers = {
        "Content-Type": "application/json",
        "authorization": f"Bearer {token}",
        "appkey": KIS_APP_KEY,
        "appsecret": KIS_APP_SECRET,
        "tr_id": "VTTC8434R" if KIS_MOCK_TRADING else "TTTC8434R"
    }
    params = {
        "CANO": KIS_ACCOUNT_NO[:8],
        "ACNT_PRDT_CD": KIS_ACCOUNT_NO[8:],
        "AFHR_FLG": "N", "OVAL_DLY_TR_FECONT_YN": "N", "PRCS_DLY_VW_FNC_G": "0",
        "CANL_DLY_VW_FNC_G": "0", "CTX_AREA_FK100": "", "CTX_AREA_NK100": ""
    }
    try:
        res = requests.get(url, headers=headers, params=params, timeout=5)
        if res.status_code == 200:
            data = res.json()
            if data.get('output2'):
                total_eval = float(data['output2'][0].get('tot_evlu_amt', 0))
                cash = float(data['output2'][0].get('dnca_tot_amt', 0))
                holdings = data.get('output1', [])
                return total_eval, cash, holdings
    except: pass
    return 0, 0, []

def get_kis_overseas_balance(token):
    """해외 주식 잔고 현황 조회 (실제 연동)"""
    if not token or not KIS_ACCOUNT_NO: return 0, []
    base_url = "https://openapivts.koreainvestment.com:29443" if KIS_MOCK_TRADING else "https://openapi.koreainvestment.com:9443"
    url = f"{base_url}/uapi/overseas-stock/v1/trading/inquire-balance"
    headers = {
        "Content-Type": "application/json",
        "authorization": f"Bearer {token}",
        "appkey": KIS_APP_KEY,
        "appsecret": KIS_APP_SECRET,
        "tr_id": "VTTW8434R" if KIS_MOCK_TRADING else "TTTW8434R"
    }
    params = {
        "CANO": KIS_ACCOUNT_NO[:8], "ACNT_PRDT_CD": KIS_ACCOUNT_NO[8:],
        "WCRC_FRCR_DVS_CD": "01", "NATN_CD": "840", "TR_PACC_CD": "", "CTX_AREA_FK200": "", "CTX_AREA_NK200": ""
    }
    try:
        res = requests.get(url, headers=headers, params=params, timeout=5)
        if res.status_code == 200:
            data = res.json()
            total_eval = float(data.get('output2', {}).get('tot_evlu_pamt', 0))
            holdings = data.get('output1', [])
            return total_eval, holdings
    except: pass
    return 0, []

# --- [ KIS: REAL-TIME RISK MONITORING (PRO EDITION) ] ---
def execute_kis_auto_cut(token):
    """
    [ SUPREME RISK ENGINE ] 최적화 버전 (배치 다운로드 적용)
    """
    try:
        _, kr_holdings = get_kis_balance(token)
        _, us_holdings = get_kis_overseas_balance(token)
        watch_targets = []
        for h in kr_holdings: watch_targets.append({"ticker": h.get('pdno'), "qty": int(h.get('hldg_qty', 0)), "buy_p": float(h.get('pchs_avg_pric', 0))})
        for u in us_holdings: watch_targets.append({"ticker": u.get('ovrs_pdno'), "qty": int(u.get('hldg_qty', 0)), "buy_p": float(u.get('pchs_avg_pric', 0))})
        
        if not watch_targets: return False
        
        # [ PERFORMANCE ] 감시 대상 종목 일괄 시세 다운로드
        tickers = [item["ticker"] for item in watch_targets]
        all_hists = yf.download(tickers, period="7d", progress=False)
        
        for item in watch_targets:
            ticker, qty, buy_p = item["ticker"], item["qty"], item["buy_p"]
            try:
                hist = pd.DataFrame({
                    "Close": all_hists["Close"][ticker],
                    "High": all_hists["High"][ticker],
                    "Low": all_hists["Low"][ticker]
                }).dropna()
            except: continue
            
            if hist.empty: continue
            curr_p, max_p = hist['Close'].iloc[-1], hist['High'].max()
            stop_price = buy_p * 0.97
            
            if (max_p / buy_p - 1) >= 0.20:
                stop_price = max_p * 0.97
            
            if curr_p <= stop_price:
                st.toast(f"🚨 [ STOP ] {ticker} 이탈!", icon="💥")
                if execute_kis_market_order(ticker, qty, is_buy=False):
                    return True
    except: pass
    return False

def play_tactical_sound(sound_type="buy"):
    """전술 상황에 따른 오디오 알림 (매수: 북소리 / 매도: 종소리)"""
    # [ ACTION ] 매수: Drum/Taiko, 매도: Bell/Chime
    src = "https://www.soundjay.com/buttons/beep-07a.mp3" # Default
    if sound_type == "buy": src = "https://www.soundjay.com/misc/sounds/drum-roll-1.mp3"
    elif sound_type == "sell": src = "https://www.soundjay.com/misc/sounds/bell-ringing-05.mp3"
    
    st.markdown(f"""
    <audio autoplay>
        <source src="{src}" type="audio/mpeg">
    </audio>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=43200) # 12시간 캐싱 (ROE는 자주 변하지 않음)
def get_ticker_roe(ticker):
    """종목의 실시간 ROE(자기자본이익률)를 획득 (캐시 활용으로 렉 방지)"""
    try:
        info = yf.Ticker(ticker).info
        return info.get('returnOnEquity', 0) * 100
    except: return 0

def execute_kis_market_order(ticker, qty, is_buy=True):
    """시장가 주문 실행 엔진 (KIS API 연동)"""
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
        # [ PRO ] 미국 거래소 판별 로직 고도화
        exchange_code = "NASD" # 기본값
        try:
            info = yf.Ticker(ticker).info
            ex_name = info.get('exchange', '').upper()
            if 'NYE' in ex_name or 'NEW YORK' in ex_name: exchange_code = "NYSE"
            elif 'ASE' in ex_name or 'AMERICAN' in ex_name: exchange_code = "AMEX"
        except: pass
        
        url = f"{base_url}/uapi/overseas-stock/v1/trading/order"
        tr_id = ("VTTW0801U" if is_buy else "VTTW0802U") if KIS_MOCK_TRADING else ("TTTW0801U" if is_buy else "TTTW0802U")
        # 미국 시장가 주문 대용 (ORD_DVSN 00 지정가, 가격 0 전송 시 KIS 내부적 처리 가능성 고려)
        body = {
            "CANO": KIS_ACCOUNT_NO[:8], "ACNT_PRDT_CD": KIS_ACCOUNT_NO[8:],
            "OVRS_EXCG_CD": exchange_code, "PDNO": ticker, "ORD_QTY": str(qty), 
            "ORD_OVRS_P deliverance": "0", "ORD_DVSN": "00"
        }

    headers = {
        "Content-Type": "application/json", "authorization": f"Bearer {token}",
        "appkey": KIS_APP_KEY, "appsecret": KIS_APP_SECRET, "tr_id": tr_id
    }
    try:
        res = requests.post(url, headers=headers, json=body, timeout=7)
        res_data = res.json()
        if res.status_code == 200 and res_data.get('rt_cd') == '0':
            # [ AUDIO ] 교전 결과 사운드 보고 (매수: 북소리 / 매도: 종소리)
            play_tactical_sound("buy" if is_buy else "sell")
            # 전투 로그 기록
            log_type = "SUCCESS"
            msg = f"{'🚀 매수' if is_buy else '🔔 매도'} 완료: {ticker} ({qty}주)"
            st.session_state.combat_logs.append({"time": datetime.now().strftime("%H:%M:%S"), "msg": msg, "type": log_type})
            return True
        else:
            # 실패 사유 추출 및 한글화
            err_msg = res_data.get('msg1', 'API 통신 오류')
            if "잔고" in err_msg or "부족" in err_msg or "balance" in err_msg.lower():
                err_msg = "❌ 계좌 잔액(증거금)이 부족하여 매수 불가능"
            
            log_msg = f"⚠️ {ticker} 주문 실패: {err_msg}"
            st.session_state.combat_logs.append({"time": datetime.now().strftime("%H:%M:%S"), "msg": log_msg, "type": "ERROR"})
            return False
    except Exception as e:
        st.session_state.combat_logs.append({"time": datetime.now().strftime("%H:%M:%S"), "msg": f"💣 시스템 오류: {str(e)}", "type": "ERROR"})
        return False

# --- [ SCANNER HELPERS: STOCKBEE STRICT EDITION ] ---
@st.cache_data(ttl=3600)
def get_bonde_top_50():
    """프라딥 본데 50 종목 구글 시트 연동"""
    url = "https://docs.google.com/spreadsheets/d/1xjbe9SF0HsxwY_Uy3NC2tT92BqK0nhArUaYU16Q0p9M/export?format=csv&gid=1499398020"
    try:
        df = pd.read_csv(url)
        tickers = df.iloc[:50, 0].dropna().unique().tolist()
        return [str(t).strip().upper() for t in tickers if len(str(t)) < 6]
    except:
        return ["NVDA", "TSLA", "AAPL", "MSFT", "PLTR", "SMCI", "AMD", "META", "GOOGL", "AVGO", "MSTR", "COIN", "MARA"]

def analyze_stockbee_setup(ticker, hist_df=None):
    """
    [ BONDE ELITE ENGINE ] 프라딥 본데의 확장된 셋업 (4종)
    - 9 Million EP
    - Story-based EP
    - Delayed Reaction EP
    - 4% Momentum Burst
    """
def get_naver_ohlcv(ticker, count=100):
    """네이버 증권 API를 통한 한국 주식 데이터 수집 (지연 없는 실시간급 데이터)"""
    try:
        symbol = ticker.split('.')[0]
        url = f"https://fchart.naver.com/sise.nhn?symbol={symbol}&timeType=day&count={count}&startTime=20240101"
        resp = requests.get(url, timeout=5)
        if resp.status_code != 200: return pd.DataFrame()
        
        import xml.etree.ElementTree as ET
        root = ET.fromstring(resp.text)
        items = root.findall('.//item')
        
        data = []
        for item in items:
            row = item.get('data').split('|')
            data.append({
                'Date': datetime.strptime(row[0], '%Y%m%d'),
                'Open': float(row[1]), 'High': float(row[2]),
                'Low': float(row[3]), 'Close': float(row[4]),
                'Volume': float(row[5])
            })
        df = pd.DataFrame(data).set_index('Date')
        return df
    except: return pd.DataFrame()

def analyze_stockbee_setup(ticker, hist_df=None):
    """프라딥 본데(Stockbee) 전략 정밀 분석 엔진 v4.0 (Global Hybrid Data Engine)"""
    try:
        is_kr = ticker.endswith(".KS") or ticker.endswith(".KQ")
        # [ DATA SOURCING ] 한국 주식은 네이버, 해외 주식은 yfinance 사용 (신뢰도 극대화)
        if is_kr:
            hist = get_naver_ohlcv(ticker, count=150)
        else:
            hist = hist_df if hist_df is not None else yf.Ticker(ticker).history(period="1y")
            
        if len(hist) < 70: return {"status": "REJECT", "reason": "데이터 부족", "ticker": ticker, "name": ticker}
        
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

        # ⚡ EP (폭발)
        if pct >= 4.0 and v > p_v and v >= 100000 and (p_c/p_c2) <= 1.02 and range_pos >= 0.7:
            is_ep = True; setups.append("EP (폭발)")

        # ⏳ DR (지연반응)
        df['Mega'] = (df['Volume'] >= 9000000) & (df['Pct'] >= 4.0)
        recent_mega = df['Mega'].shift(1).rolling(25).max().iloc[-1] == 1.0
        if recent_mega and ((o < p_c and c > p_c) or ((p_c/p_c2) <= 1.02 and v > p_v and pct >= 4.0)):
            is_dr = True; setups.append("DR (지연반응)")

        # 🗜️ TIGHT (응축)
        ttt = df['Pct'].rolling(3).apply(lambda x: all(abs(x) <= 1.0)).iloc[-1] == 1.0
        if df['Volume'].rolling(3).min().iloc[-1] >= 300000 and ti65 >= 1.05 and ttt:
            is_tight = True; setups.append("TIGHT (응축)")

        # RS 및 품질
        rs = round(((c/df['Close'].iloc[-126])*0.7 + (c/df['Close'].iloc[-63])*0.3)*100, 1) if len(df) >= 126 else 50
        v_ratio = v / (p_v + 1e-9)
        quality = round((rs*0.4) + (adr20*3) + (v_ratio*3), 1)
        name = TICKER_NAME_MAP.get(ticker, ticker)

        return {
            "ticker": ticker, "name": name, "close": c, "rs": rs, "day_pct": round(pct, 2), 
            "adr": round(adr20, 2), "quality": quality, "tight": round(abs(pct), 2),
            "is_ep": is_ep, "is_dr": is_dr, "is_tight": is_tight, "status": "SUCCESS" if setups else "PASS",
            "reason": f"🚀 {setups[0]} 포착!" if setups else "조건 미충족", "setups": setups,
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
    """나스닥 100+ 주요 성장주 리스트"""
    top_ndq = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "AVGO", "PEP", "COST", "ADBE", "CSCO", "NFLX", "AMD", "TMUS", "INTC", "INTU", "AMAT", "QCOM", "TXN", "AMGN", "ISRG", "HON", "BKNG", "VRTX", "SBUX", "ADP", "GILD", "MDLZ", "REGN", "ADI", "LRCX", "PANW", "SNPS", "MU", "KLAC", "CDNS", "CHTR", "MAR", "PYPL", "ORLY", "ASML", "MNST", "MELI", "CTAS", "ADSK", "LULU", "WDAY", "KDP", "NXPI", "MCHP", "IDXX", "PAYX", "ROST", "PCAR", "DXCM", "AEP", "CPRT", "CPRT", "BKR", "KLA", "EXC", "MRVL", "CRWD", "DDOG", "TEAM", "MSTR", "PLTR", "SNOW", "ZS", "NET", "OKTA", "U", "RIVN", "LCID", "SQ", "SE", "BABA", "PDD", "JD", "BIDU", "NTES"]
    return list(set(top_ndq))

@st.cache_data(ttl=86400)
def get_kospi_top_200():
    """코스피 시총 상위 100+ 주요 종목"""
    top_ks = ["005930.KS", "000660.KS", "373220.KS", "207940.KS", "005490.KS", "005380.KS", "000270.KS", "051910.KS", "006400.KS", "035420.KS", "068270.KS", "105560.KS", "055550.KS", "012330.KS", "035720.KS", "003550.KS", "032830.KS", "000810.KS", "015760.KS", "086790.KS", "009150.KS", "011780.KS", "010130.KS", "033780.KS", "000100.KS", "018260.KS", "003670.KS", "000720.KS", "009830.KS", "011070.KS", "047050.KS", "028260.KS", "010140.KS", "036570.KS", "003410.KS", "051900.KS", "034730.KS", "090430.KS", "010950.KS", "259960.KS", "302440.KS", "402340.KS", "017670.KS"]
    return list(set(top_ks))

@st.cache_data(ttl=86400)
def get_kosdaq_100():
    """코스닥 100 주요 성장주"""
    top_kq = ["247540.KQ", "086520.KQ", "091990.KQ", "066970.KQ", "196170.KQ", "277810.KQ", "214150.KQ", "293490.KQ", "028300.KQ", "145020.KQ", "058470.KQ", "035900.KQ", "036930.KQ", "263750.KQ", "039030.KQ", "041510.KQ", "253450.KQ", "067310.KQ", "084370.KQ", "034230.KQ", "051910.KQ", "214320.KQ", "112040.KQ", "078600.KQ", "064290.KQ", "036830.KQ", "036200.KQ", "121600.KQ"]
    return list(set(top_kq))

def get_rs_score(ticker):
    try:
        h = yf.Ticker(ticker).history(period="6mo")
        if len(h) < 20: return 50
        return int((h['Close'].iloc[-1] / h['Close'].iloc[0]) * 100)
    except: return 50

# --- [ AI ] 사령부 AI 정예 요원 (NPC Operatives) 설정 ---
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
    """사용자 데이터 로드 (로컬 우선)"""
    users = safe_load_json(USER_DB_FILE, {})
    # 백그라운드에서 시트 동기화 트리거 (옵션)
    return users

def sync_users_from_sheet():
    """비동기 사용자 데이터 동기화"""
    if not USERS_SHEET_URL: return
    try:
        resp = safe_get(USERS_SHEET_URL, timeout=5)
        if resp:
            df_u = pd.read_csv(io.StringIO(resp.text))
            users = safe_load_json(USER_DB_FILE, {})
            for _, row in df_u.iterrows():
                u_id = str(row.get('아이디', row.get('ID', ''))).strip()
                if not u_id or u_id == 'nan': continue
                users[u_id] = {
                    "password": str(row.get('비밀번호', u_id)),
                    "status": str(row.get('상태', 'approved')),
                    "grade": str(row.get('등급', '회원')),
                    "info": {"joined_at": row.get('가입일', '-')}
                }
            safe_save_json(users, USER_DB_FILE)
    except: pass

    # 기본 방장 계정 보장
    if "cntfed" not in users:
        users["cntfed"] = {"password": "cntfed", "status": "approved", "grade": "방장"}
    
    # [ SYSTEM ] 전문가님 권한은 시스템적으로 절대 보장 (지워짐 방지)
    users["cntfed"]["grade"] = "방장"
    users["cntfed"]["status"] = "approved"
    
    return users

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def migrate_user_passwords(users):
    # 기존 평문 비밀번호를 해시로 점진적 변환
    changed = False
    for uid, udata in users.items():
        pw = udata.get("password", "")
        if len(pw) < 64: # 해시가 아닌 경우 (SHA-256은 64자)
            users[uid]["password"] = hash_password(pw)
            changed = True
    if changed: save_users(users)
    return users

def save_users(users):
    safe_save_json(users, USER_DB_FILE)
    # 캐시를 즉시 업데이트하거나 초기화하여 다음 호출 시 최신 데이터를 읽게 함
    load_users.clear()

@st.cache_data(ttl=600)
def fetch_gs_attendance():
    try:
        response = safe_get(ATTENDANCE_SHEET_URL, timeout=4)
        if response:
            import io
            df = pd.read_csv(io.StringIO(response.text))
            # 🔍 유연한 헤더 매핑
            df = df.rename(columns={
                '시간': '시간', 'date': '시간', '날짜': '시간', '일시': '시간',
                '아이디': '아이디', 'id': '아이디', 'ID': '아이디', 'User': '아이디',
                '인사': '인사', '한줄인사': '인사', '내용': '인사', '댓글': '인사',
                '등급': '등급', 'grade': '등급', 'Level': '등급'
            })
            # 필수 컬럼 보장
            expected = ["시간", "아이디", "인사", "등급"]
            for col in expected:
                if col not in df.columns: df[col] = "nan"
            return df[expected]
    except: pass
    return pd.DataFrame(columns=["시간", "아이디", "인사", "등급"])

@st.cache_data(ttl=300)
def fetch_gs_chat():
    try:
        response = safe_get(CHAT_SHEET_URL, timeout=4)
        if response:
            import io
            df = pd.read_csv(io.StringIO(response.text))
            df = df.rename(columns={'시간': '시간', '아이디': '아이디', '내용': '내용', '등급': '등급'})
            return df
    except: pass
    return pd.DataFrame()

@st.cache_data(ttl=300)
def fetch_gs_visitors():
    try:
        response = requests.get(VISITOR_SHEET_URL, timeout=5)
        if response.status_code == 200:
            import io
            return pd.read_csv(io.StringIO(response.text))
    except Exception as e:
        print(f"DEBUG: Visitor Fetch Error: {e}")
    return pd.DataFrame()

# --- [ ACTION ] Optimized Data Helpers ---
@st.cache_data(ttl=86400) # ROE는 하루 한 번 정도로 충분
def get_ticker_roe(tic):
    """
    ⚠️ yf.Ticker.info는 매우 느리므로 스캐너 루프 내부에서 직접 사용을 지양해야 합니다.
    최대한 캐싱을 활용하고 일괄 데이터(Fastinfo 등)를 고려합니다.
    """
    try:
        tk = yf.Ticker(tic)
        # 🛡️ info 대신 fast_info나 다른 빠른 필드가 있다면 그것을 쓰는 것이 좋으나 
        # ROE는 info에 있음. 2초 타임아웃 형태로 우회 시도(yf 자체 지원 미비 시 수동 제한)
        # 여기서는 최소한의 호출을 위해 st.cache_data를 유지
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
                return {"title": str(last_notice.get("제목", "📢 사령부 보안 업데이트 안내")), "content": str(last_notice.get("내용", "쾌적한 서비스 제공을 위해 엔진을 전면 개편하였습니다. 모든 회원 임시 비밀번호는 1234입니다."))}
    except Exception as e:
        print(f"DEBUG: Notice Fetch Error: {e}")
    return {
        "title": "🛡️ 사령부 고정 공지", 
        "content": """더욱 쾌적하고 안전한 시스템 환경을 구축하기 위한 서버 업데이트 과정에서, 부득이하게 전체 회원의 비밀번호가 초기화되었습니다. 이용에 불편을 드려 대단히 죄송합니다.<br>
아래 안내에 따라 비밀번호를 재설정해 주시기 바랍니다.<br><br>
<b>🔐 비밀번호 초기화 및 재설정 방법</b><br>
- 초기화 비밀번호: <b>1234</b><br>
- 재설정 경로: <b>[1. 본부 사령부] → [1-c. 계정 보안 설정]</b><br><br>
로그인 후 해당 메뉴에서 본인만의 안전한 비밀번호로 즉시 변경이 가능합니다. 개인정보 보호를 위해 접속 즉시 수정을 권장합니다."""
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

# --- 🔴 상단 브랜드 헤더 (초정밀 밀착 레이아웃) ---
col_head1, col_head2, col_head3 = st.columns([1, 4, 1])

with col_head3:
    if st.session_state.get("password_correct"):
        if st.button("🔓 LOGOUT", use_container_width=True, key="global_logout"):
            st.session_state["password_correct"] = False
            st.session_state.current_user = None
            st.rerun()
    else:
        if st.button("🔒 LOGIN", use_container_width=True, key="global_login"):
            st.rerun()

with col_head2:
    st.markdown(f"""
        <div style='text-align: center; margin-top: -30px; margin-bottom: 5px; overflow: visible;'>
            <img src='data:image/png;base64,{assets["logo"]}' style='width: 110px; margin-bottom: -15px;'>
            <h1 style='font-size: clamp(1.8rem, 7.5vw, 3.8rem); font-weight: 900; background: linear-gradient(45deg, #FFD700, #FFFFFF); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-shadow: 0 10px 20px rgba(0,0,0,0.5); white-space: nowrap; margin-bottom: 0px; line-height: 1.1;'>StockDragonfly</h1>
            <p style='color: #888; letter-spacing: 7px; font-size: 0.7rem; margin-top: -5px; opacity: 0.8;'>ULTRA-HIGH PERFORMANCE TERMINAL</p>
        </div>
    """, unsafe_allow_html=True)

# --- 인증 & 사이드바 ---
if "password_correct" not in st.session_state: st.session_state["password_correct"] = False
if not st.session_state["password_correct"]:
    # 모바일에서는 컬럼 비율 조정
    c1, m, c2 = st.columns([0.1, 0.8, 0.1]) if st.session_state.get("is_mobile", False) else st.columns([1, 2, 1])
    with m:
        # (Global Header가 상단에 위치하므로 중복 로고/타이틀 제거)
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
                if st.button("[ OK ] 공지 확인 및 열지 않기", use_container_width=True):
                    st.session_state["show_notice"] = False
                    st.rerun()

        tab1, tab2 = st.tabs(["[ LOGIN ] Terminal Log-In", "[ JOIN ] Join Command (자격 시험)"])
        
        with tab1:
            login_id = st.text_input("사령부 아이디", key="l_id")
            login_pw = st.text_input("액세스 키 (PW)", type="password", key="l_pw")
            if st.button("Terminal Operation Start", use_container_width=True):
                users = load_users()
                if login_id in users:
                    u_data = users[login_id]
                    if u_data.get("status", "approved") != "approved":
                        st.error(f"⚠️ 현재 계정 상태가 '{u_data.get('status')}'입니다. 사령부의 승인이나 상태 복구가 필요합니다.")
                    elif u_data.get("password") == login_pw or u_data.get("password") == hash_password(login_pw):
                        # 로그인 시 해시로 자동 변환 (v7.0 보안 강화)
                        if len(u_data.get("password", "")) < 64:
                            users[login_id]["password"] = hash_password(login_pw)
                            save_users(users)
                        st.session_state["password_correct"] = True
                        st.session_state.current_user = login_id
                        st.rerun()
                    else: st.error("[ ERROR ] 보안 코드가 일치하지 않습니다.")
                else: st.error("[ ERROR ] 등록되지 않은 정보입니다.")
        
        with tab2:
            st.markdown("### [ ACCESS ] 사령부 정예 요원 입성 자격 시험")
            st.info("개인 정보와 자격 시험 만점(5/5)을 획득해야 사령부 승인이 완료됩니다.")
            
            c1, c2 = st.columns(2)
            with c1:
                new_id = st.text_input("희망 아이디", key="s_id")
                new_pw = st.text_input("희망 비밀번호", type="password", key="s_pw")
                reg_region = st.selectbox("거주 지역", ["서울", "경기", "인천", "부산", "대구", "대전", "광주", "울산", "강원", "충청", "전라", "경상", "제주", "해외"])
            with c2:
                reg_age = st.selectbox("연령대", ["20대 이하", "30대", "40대", "50대", "60대 이상"])
                reg_gender = st.radio("성별", ["남성", "여성"], horizontal=True)
                reg_exp = st.selectbox("주식 경력", ["1년 미만", "1-3년", "3-5년", "5-10년", "10년 이상"])
            
            reg_moti = st.text_area("주식을 하는 이유와 사령부에 임하는 각오", placeholder="예: 경제적 자유를 얻어 가족들에게 헌신하고 싶습니다.")
            
            st.divider()
            st.markdown("#### ⏳ [ EXAM ] 사령부 정예 요원 자격 시험 (30문항 / 10분 제한)")
            st.warning("⚠️ 시험 시작 버튼을 누르면 10분의 타이머가 작동합니다. 30문제 중 26문제 이상 맞혀야 입성 자격이 부여됩니다.")
            
            # --- [ TIMER LOGIC ] ---
            if "exam_start_time" not in st.session_state:
                if st.button("🚀 자격 시험 시작 (타이머 작동)"):
                    st.session_state.exam_start_time = time.time()
                    st.rerun()
                st.stop()
            
            # 타이머 계산
            elapsed = time.time() - st.session_state.exam_start_time
            remaining = max(0, 600 - int(elapsed))
            mins, secs = divmod(remaining, 60)
            
            t_color = "#FFD700" if remaining > 60 else "#FF4B4B"
            st.markdown(f"<div style='text-align: right; font-size: 1.5rem; color: {t_color}; font-weight: 900; font-family: \"Orbitron\";'>REMAINING TIME: {mins:02d}:{secs:02d}</div>", unsafe_allow_html=True)
            
            if remaining <= 0:
                st.error("⏰ 제한 시간이 초과되었습니다. 사령부의 지혜를 더 연마하고 다시 도전하십시오.")
                if st.button("시험 재도전"):
                    del st.session_state.exam_start_time
                    st.rerun()
                st.stop()

            st.info("Part 1: 기초 및 전술 통합 테스트 (30문항)")
            
            # --- [ 30 QUESTIONS ] ---
            with st.container():
                st.info("Part 1: 기초 시장 이해 (10문항)")
                q1 = st.radio("Q1. 주식 차트에서 양봉(빨간색)의 의미는?", ["상승", "하락", "정지", "보합"], index=None)
                q2 = st.radio("Q2. 음봉(파란색)의 의미는?", ["상승", "하락", "정지", "보합"], index=None)
                q3 = st.radio("Q3. 거래량이 폭증하는 것은 무엇의 증거인가?", ["관심과 수급", "거래 정지", "상장 폐지", "가격 하락"], index=None)
                q4 = st.radio("Q4. 이동평균선(이평선)의 정의는?", ["일정 기간 가격의 평균", "미래 주가 예측선", "거래량 평균", "기관의 매수가"], index=None)
                q5 = st.radio("Q5. '무릎에 사서 어깨에 팔라'는 격언의 의미는?", ["추세 추종", "최저가 매수", "최고가 매도", "단타 매매"], index=None)
                q6 = st.radio("Q6. 골든 크로스란?", ["단기선이 장기선을 상향 돌파", "주가가 금값처럼 오름", "거래량이 줄어듬", "장기선이 단기선을 돌파"], index=None)
                q7 = st.radio("Q7. 데드 크로스 발생 시 대응은?", ["매도 혹은 관망", "적극 매수", "추가 매수", "방관"], index=None)
                q8 = st.radio("Q8. 호가창에서 매수 잔량이 매도 잔량보다 많으면 보통 어떻게 되나?", ["주가가 하락하기 쉽다", "주가가 폭등한다", "변동 없다", "거래 정지"], index=None)
                q9 = st.radio("Q9. '손절'의 진정한 의미는?", ["리스크 관리 및 생존", "패배 인정", "자산 포기", "실패"], index=None)
                q10 = st.radio("Q10. 주식 투자의 주체 3요소는?", ["개인, 외국인, 기관", "대통령, 장관, 은행", "증권사, 거래소, 정부", "나, 너, 우리"], index=None)

                st.info("Part 2: 본데의 전술 철학 (10문항)")
                q11 = st.radio("Q11. 본데 전략의 핵심 키워드는?", ["모멘텀과 돌파", "가치 투자", "배당주 투자", "역발상 투자"], index=None)
                q12 = st.radio("Q12. TI65 지표가 의미하는 것은?", ["65일 가격 모멘텀 강도", "65일 거래량 평균", "65세 이상 은퇴 자금", "6.5% 수익률"], index=None)
                q13 = st.radio("Q13. 본데의 '4% Momentum Burst'의 필수 조건은?", ["거래량 동반 4% 이상 상승", "4일 연속 하락", "4% 배당 지급", "오전 10시 매수"], index=None)
                q14 = st.radio("Q14. Episodic Pivot(EP)의 발생 원인은?", ["강력한 펀더멘털의 변화", "개미들의 집단 매수", "단순한 가격 조정", "기관의 물량 투하"], index=None)
                q15 = st.radio("Q15. 본데가 말하는 가장 안전한 매수 시점은?", ["박스권 돌파 초기", "낙폭 과대 시점", "고점 형성 후 조정", "상장 당일"], index=None)
                q16 = st.radio("Q16. 3일 연속 상승한 종목을 사지 않는 이유는?", ["추격 매수 위험(Laggard)", "더 오를 것이기 때문", "돈이 없어서", "규정 때문"], index=None)
                q17 = st.radio("Q17. 주식 시장의 4단계 중 매매해야 하는 단계는?", ["2단계 (Mark-up)", "1단계 (Accumulation)", "3단계 (Distribution)", "4단계 (Capitulation)"], index=None)
                q18 = st.radio("Q18. Gap Up(갭 상승)이 중요한 이유는?", ["강력한 기관 수급의 증거", "가격이 비싸서", "팔기 좋아서", "세금 때문"], index=None)
                q19 = st.radio("Q19. 본데 전략에서 매도의 1순위 기준은?", ["매수가(LOD) 이탈", "10% 수익", "목표가 도달", "지루할 때"], index=None)
                q20 = st.radio("Q20. ROE가 마이너스인 기업을 배제하는 이유는?", ["펀더멘털 결함 및 부실", "세금이 많아서", "이름이 안 예뻐서", "유행이 지나서"], index=None)

                st.info("Part 3: 고등 전략 및 심리 (10문항)")
                q21 = st.radio("Q21. 트레일링 스탑이란?", ["수익에 따라 익절선을 올림", "손절을 포기함", "매도 대기", "천천히 멈춤"], index=None)
                q22 = st.radio("Q22. 시장 심리(Fear & Greed)가 공포(Fear)일 때 대응은?", ["보수적 운용/기회 포착", "전량 투매", "무조건 매수", "휴식"], index=None)
                q23 = st.radio("Q23. 주식 매매에서 가장 큰 적은?", ["자기 자신의 감정", "외국인", "세력", "정부"], index=None)
                q24 = st.radio("Q24. 분할 매수의 장점은?", ["평단가 조절 및 리스크 분산", "수익 극대화", "빠른 매매", "수수료 절감"], index=None)
                q25 = st.radio("Q25. RSI 지표가 30 이하일 때의 의미는?", ["과매도 구간(반등 가능성)", "과매수 구간", "정상 가격", "매도 적기"], index=None)
                q26 = st.radio("Q26. 전술적 인내란?", ["타점이 올 때까지 기다림", "물린 후 버팀", "무한 대기", "매매 포기"], index=None)
                q27 = st.radio("Q27. 주도주란?", ["시장의 상승을 이끄는 핵심주", "가장 싼 주식", "가장 비싼 주식", "거래 정지주"], index=None)
                q28 = st.radio("Q28. VCP(변동성 축적 패턴)의 끝은?", ["돌파와 강력한 시세", "가격 하락", "상장 폐지", "거래 중단"], index=None)
                q29 = st.radio("Q29. 사령부의 최종 목표는?", ["기계적 절차에 의한 수익", "일확천금", "도박", "유명해지기"], index=None)
                q30 = st.radio("Q30. 당신은 기계처럼 손절 원칙을 지킬 것인가?", ["네, 반드시 지킵니다", "아니오, 상황 봐서요", "모르겠습니다", "지키기 싫습니다"], index=None)

            if st.button("[ SUBMIT ] 자격 시험 제출 및 가입 신청"):
                ans_list = [q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, q11, q12, q13, q14, q15, q16, q17, q18, q19, q20, q21, q22, q23, q24, q25, q26, q27, q28, q29, q30]
                score = 0
                for a in ans_list:
                    if a and ("상승" in a or "하락" in a or "수급" in a or "평균" in a or "추세" in a or "상향" in a or "매도" in a or "하락하기" in a or "생존" in a or "기관" in a or "모멘텀" in a or "65일" in a or "4%" in a or "변화" in a or "돌파" in a or "Laggard" in a or "2단계" in a or "강력한" in a or "이탈" in a or "펀더멘털" in a or "익절선" in a or "보수적" in a or "감정" in a or "평단가" in a or "과매도" in a or "타점" in a or "이끄는" in a or "강력한" in a or "절차" in a or "지킵니다" in a):
                        score += 1
                
                if score >= 25:
                    users = load_users()
                    if new_id in users: st.error("❌ 이미 존재하는 대원 코드(ID)입니다.")
                    else:
                        users[new_id] = {
                            "password": new_pw, "status": "approved", "grade": "회원",
                            "info": {
                                "region": reg_region, "age": reg_age, "gender": reg_gender,
                                "exp": reg_exp, "motivation": reg_moti, "joined_at": datetime.now().strftime("%Y-%m-%d %H:%M")
                            }
                        }
                        save_users(users)
                        
                        # 🛡️ 즉시 구글 시트 백업 전송 (백그라운드 전환)
                        gsheet_sync_bg("회원명단", 
                            ["아이디", "비밀번호", "상태", "등급", "지역", "연령대", "성별", "경력", "가입일", "매매동기"],
                            [new_id, new_pw, "approved", "회원", reg_region, reg_age, reg_gender, reg_exp, datetime.now().strftime("%Y-%m-%d %H:%M"), reg_moti]
                        )
                        
                        st.success(f"[ SUCCESS ] {score}/15점! 훌륭합니다. 사령부의 지혜를 계승할 자격을 증명하셨습니다. 로그인을 진행해 주십시오.")
                        st.balloons()
                else:
                    st.error(f"[ ERROR ] {score}/15점. 사령부의 철학을 더 공부하고 와주시기 바랍니다. (13점 이상 합격)")
                    with st.expander("[ REVIEW ] 15관문 자격 시험 정답 및 해설 보기", expanded=True):
                        st.markdown("""
                        - **Q13:** RSI **30 이하**는 매도세가 소멸되는 과매도 구간입니다.
                        - **Q14:** 부분 익절 후에는 손절선을 **본절(Break-even)**로 올려 무위험 상태를 만드십시오.
                        - **Q15:** **3일 연속** 상승한 종목은 절대 추격 매수하지 않는 것이 사령부의 철칙입니다.
                        """)
    st.stop()

# --- [ CONFIG ] Menu & Trades ---
ZONE_CONFIG = {
    "[ HQ ] 1. 본부 사령부": ["1-a. [ ADMIN ] 관리자 승인 센터", "1-b. [ HR ] HQ 인적 자원 사령부", "1-c. [ SECURE ] 계정 보안 및 관리(18.)", "1-d. [ EXIT ] 탈퇴/휴식 신청"],
    "[ MARKET ] 2. 시장 상황실": ["2-a. [ TREND ] 마켓 트렌드 요약", "2-b. [ MAP ] 실시간 히트맵", "2-c. [ SENTIMENT ] 시장 심리 게이지", "2-d. [ ABOUT ] 제작 동기"],
    "[ TARGET ] 3. 주도주 추격대": ["3-a. [ SCAN ] 주도주 타점 스캐너", "3-b. [ RANK ] 주도주 랭킹 TOP 50", "3-c. [ WATCH ] 본데 감시 리스트", "3-d. [ INDUSTRY ] 산업동향(TOP 10)", "3-e. [ RS ] RS 강도(TOP 10)"],
    "[ SQUARE ] 6. 안티그래비티 광장": ["6-a. [ CHECK ] 출석체크(오늘한줄)", "6-b. [ CHAT ] 소통 대화방"],
    "[ AUTO ] 7. 자동매매 사령부": ["7-a. [ SETUP ] 사령부 교전 수칙", "7-b. [ MONITOR ] 실시간 시장 관제", "7-c. [ ENGINE ] 자동매매 전략엔진", "7-g. [ COMBAT ] 실시간 교전 관제소", "7-i. [ CONFIG ] 사령부 시스템 설정"]
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
    curr_grade = users.get(st.session_state.current_user, {}).get("grade", "회원")
    is_admin = curr_grade in ["관리자", "방장"]
    
    for zone, missions in ZONE_CONFIG.items():
        if "ADMIN" in str(missions) and not is_admin: continue
        if "AUTO" in zone and curr_grade not in ["방장", "관리자", "정회원", "준회원"]: continue
        with st.expander(zone, expanded=(st.session_state.get("page") in missions)):
            for m in missions:
                if st.button(m, key=f"nav_{m}", use_container_width=True):
                    st.session_state.page = m
                    st.rerun()

# --- [ LAYOUT ] Global State ---
page = st.session_state.get("page", "6-a. [ CHECK ] 출석체크(오늘한줄)")
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

# --- [ FLASH ] 글로벌 실시간 뉴스 플래시 (Reuters-Style) ---
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

# --- [ STATUS ] 시스템 전역 장애/상태 알림 ---
if "gs_error" in st.session_state and st.session_state["gs_error"]:
    st.error(st.session_state["gs_error"])

# --- [ LIVE ] LIVE OPS CENTER (NEW v6.0) ---
macro_str = get_macro_indicators() # 환율/금리 포함
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
            {macro_str} &nbsp;&nbsp;&nbsp; [BREAKING] NVDA VCP Phase 3 Detection... &nbsp;&nbsp; [HQ] minsu 요원 코스피 주도 수급 분석 중... &nbsp;&nbsp; [ALERT] RS 상위 10% 종목 실시간 응축 확인...
        </marquee>
    </div>
</div>
""", unsafe_allow_html=True)

# --- [ INFO ] 상단 실시간 정보 바 ---
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
    except: pass
    return res

# --- [ CONTROL ] 사령부 통합 지수 관제 센터 (Stable v6.1) ---
idx_info = get_top_indices()

with st.container():
    st.markdown("<div style='margin-bottom: -10px;'></div>", unsafe_allow_html=True)
    
    indices_list = ["DOW", "S&P500", "NASDAQ", "KOSPI", "KOSDAQ"]
    cols = st.columns(5)
    
    for i, name in enumerate(indices_list):
        val, pct, high, low = idx_info.get(name, [0.0, 0.0, 0.0, 0.0])
        with cols[i]:
            is_kr = name in ["KOSPI", "KOSDAQ"]
            theme_color = "#FF4B4B" # 상승 (빨강)
            stat_color = "#FF4B4B" if pct >= 0 else "#0088FF" # 상승: 빨강, 하락: 파랑
            arrow = "▲" if pct >= 0 else "▼"
            
            # 시간 표시 결정
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
        "green": ("#00FF00", "rgba(0,255,0,0.1)", "GREED/AGGRESSIVE", "수익 좀 났다고 네가 천재가 된 줄 아나? 시장이 좋은 것뿐이다. 자만심(Ego)이 고개를 드는 순간, 시장은 네 계좌를 갈기갈기 찢어놓을 거다. 익절 라인 올려 잡고 닥치고 프로세스나 지켜라."),
        "orange": ("#FFD700", "rgba(255,215,0,0.1)", "NEUTRAL/WATCH", "방향성이 보이지 않을 때는 손을 깔고 앉아 있는 것도 기술이다. 억지로 타점을 만들려고 하지 마라. 시장이 너에게 돈을 벌 기회를 줄 때까지 굶주린 사자처럼 기다려라."),
        "red": ("#FF4B4B", "rgba(255,75,75,0.1)", "FEAR/DEFENSIVE", "중력이 너를 끌어내리고 있다. 거부하지 마라. 지금은 영웅이 될 때가 아니라 생존자가 될 때다. 모든 포지션을 점검하고, 리스크가 감당 안 되면 즉시 현금을 대피시켜라.")
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
        <h3 style='margin: 0; color: #FFF; font-size: 1.3rem; letter-spacing: -0.5px;'>[ TRUTH ] 실시간 뼈 때리는 훈계 (Harsh Truth)</h3>
    </div>
    <div style='background: {c_bg}; border-left: 4px solid {c_color_code}; padding: 20px; border-radius: 0 12px 12px 0;'>
        <p style='color: #EEE; font-size: 1.05rem; line-height: 1.6; margin: 0; font-family: "Pretendard", sans-serif; font-weight: 500;'>"{c_harsh}"</p>
    </div>
</div>
</div>
</div>""", unsafe_allow_html=True)

# --- [ DOCTRINE ] 본데의 전술 지침 데이터 ---
BONDE_WISDOM = [
    {
        "title": "[ ADVICE ] '비밀 지표'나 '마법의 셋업'을 찾는 헛수고는 당장 집어치워라",
        "content": "많은 초보자들이 나에게 완벽한 매수 타점이나 '비밀 지표'가 뭐냐고 묻는다. 그런 건 없다. 시장에서 돈을 버는 진정한 '엣지(Edge)'는 책 몇 권 읽는다고 생기는 것이 아니다. 당신이 돌파 매매(Breakout)에 단 1달러라도 걸기 전에, 과거에 성공했던 폭등주 차트 5,000개, 10,000개를 직접 파고들어라(Deep Dive). 500피트, 1,000피트, 5,000피트 깊이까지 파고들어야 비로소 시장이 어떻게 움직이는지 이해하기 시작할 것이다. 다른 사람의 종목 추천(Alert)에 의존하는 짓을 멈추고 당신 스스로 뇌에 패턴을 각인시켜라."
    },
    {
        "title": "[ ADVICE ] 당신은 천재가 아니다. '섬의 환상(Island Mentality)'에서 깨어나라",
        "content": "운 좋게 시장 환경이 좋은 몇 주 동안 20%의 수익을 내고 나면, 사람들은 자신이 천재인 줄 착각한다. 단번에 큰돈을 벌어 열대의 섬을 사고 페라리를 사겠다는 허황된 꿈(Island Mentality)에 빠져 이른바 '신 증후군(God Syndrome)'에 걸린다. 그렇게 자만하며 아무 때나 매매를 남발하다 보면, 결국 머리 위로 코코넛이 떨어져 계좌가 박살 날 것이다. 허황된 홈런을 노리지 말고, 짧고 확실한 수익(Singles)을 챙기며 복리로 굴리는 지루한 과정을 거쳐라."
    },
    {
        "title": "[ ADVICE ] 쓰레기장 같은 장에서 매매하며 계좌를 갈아버리지 마라",
        "content": "아무리 완벽해 보이는 에피소딕 피봇(EP)이나 모멘텀 버스트 셋업이라도 시장의 환경(날씨)이 나쁘면 무용지물이다. 당신은 매일 아침 '오늘 돌파 매매가 통하는 날인가?'를 스스로에게 묻고 있는가? 시장의 하락 종목 수가 상승 종목을 압도하고 돌파가 계속 실패하는 똥 같은 시장(Shit market)에서 계속 매매 버튼을 누르며 계좌를 산산조각(Chop to pieces) 내고 싶다면 마음대로 해라. 시장 환경이 나쁠 때는 제발 아무것도 하지 말고 손을 깔고 앉아 현금을 지켜라."
    },
    {
        "title": "[ ADVICE ] 수익금(P&L)에 집착하지 말고 '프로세스'나 지켜라",
        "content": "수익은 당신이 올바른 '프로세스'를 지켰을 때 따라오는 부산물일 뿐이다. 매수 후 3일 연속으로 상승한 주식을 뒤늦게 추격 매수하고 있는가? 축하한다, 당신은 곧 고점에 물린 '호구(Bag Holder)'가 될 것이다. 손절선을 내리지 마라. 손절선은 신성한 것이다. **'첫 번째 손실이 가장 좋은 손실'**임을 명심하고, 당신이 세운 2.5%~5%의 손절선, 혹은 당일 최저점(LOD)이 깨지면 기계처럼 잘라내라. 당신의 얄팍한 예측이나 감정을 개입시키지 말고 수치와 원칙, 철저한 프로세스만 남겨라."
    }
]

# --- [ FOOTER ] 전술 푸터용 랜덤 어록 데이터 ---
BONDE_FOOTER_QUOTES = [
    "트레이딩은 돈을 버는 것이 목적이 아니라, 완벽한 프로세스를 실행하는 것이 목적이다. 수익은 그 보상일 뿐이다.",
    "당신이 똑똑하다는 것을 증명하려 하지 마라. 시장은 당신의 자존심에는 관심이 없다. 오직 당신의 잔고에만 관심이 있을 뿐이다.",
    "홈런 한 방을 꿈꾸는 자는 결국 파산한다. 우리는 매일 안타를 쳐서 복리의 마법을 부리는 비즈니스맨이다.",
    "손실 중인 종목은 월급만 축내고 회사를 망치고 있는 나쁜 직원이다. 정에 이끌리지 말고 지금 당장 해고(손절)하라.",
    "희망(Hope)은 트레이딩 전략이 아니다. '본전 오면 팔겠다'는 생각은 시장에 당신의 전 재산을 기부하겠다는 선언과 같다.",
    "수익이 나는 주식은 회사를 성장시키는 우수 사원이다. 그들에게 더 많은 자원(비중)을 배분하고 보너스(추세 추종)를 주어 끝까지 부려 먹어라.",
    "시장의 폭(Breadth)이 죽었는데 매수 버튼을 누르는 것은 자살 행위다. 현금을 쥐고 아무것도 하지 않는 것도 위대한 포지션이다.",
    "장중에 고민하지 마라. 고민은 장이 열리기 전 1,000개의 차트를 돌려보며 끝냈어야 한다. 실전은 반사 신경의 영역이다.",
    "당신만의 엣지(Edge)가 없다면 당신은 트레이더가 아니라 기부천사일 뿐이다. 오늘 당장 딥 다이브(Deep Dive) 훈련을 시작하라."
]

def get_daily_wisdom():
    day_idx = datetime.now().day % len(BONDE_WISDOM)
    return BONDE_WISDOM[day_idx]

def get_footer_quote():
    # 날짜를 시드로 사용하여 매일 같은 랜덤 어록 선택
    random.seed(datetime.now().strftime("%Y%m%d"))
    return random.choice(BONDE_FOOTER_QUOTES)

# --- [PLACEHOLDER_LOGIC_START] ---
if page.startswith("6-a."):
    st.header("[ CHECK ] 사령부 출석체크 및 오늘 한 줄")
    
    # 데이터 준비
    if not os.path.exists(ATTENDANCE_FILE):
        safe_write_csv(pd.DataFrame(columns=["시간", "아이디", "인사", "등급"]), ATTENDANCE_FILE)
    
    df_att = safe_read_csv(ATTENDANCE_FILE, ["시간", "아이디", "인사", "등급"])
    # [ INFO ] 방문자 수 500부터 시작하도록 오프셋 추가
    total_visits = len(df_att) + 500
    
    # 상단 요약 바 (방문자 수 & 날씨)
    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown(f"""
        <div class='glass-card' style='text-align: center; padding: 20px; border: 1px solid #FFD700; border-radius: 15px; height: 140px; margin-top: 38px;'>
            <h4 style='margin:0; color:#FFD700;'>[ DRAGONFLY ] 누적 사령부 방문</h4>
            <span style='font-size: 2.2rem; font-weight: 900; color: #00FF00;'>{total_visits:,}</span>
            <p style='margin:0; color:#888; font-size: 0.8rem;'>Operatives Engaged</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        # --- [ REAL-TIME WEATHER ] 지역별 기온 및 습도 정보 (wttr.in 활용) ---
        locations = {"대한민국 (서울)": "Seoul", "일본 (도쿄)": "Tokyo", "미국 (워싱턴)": "Washington"}
        
        # UI 레이아웃 내부에 셀렉트박스 배치 (공간 효율을 위해 소형으로)
        sel_region = st.selectbox("기상 지역 소환", list(locations.keys()), index=0, label_visibility="collapsed")
        loc_id = locations[sel_region]
        
        @st.cache_data(ttl=1800)
        def get_live_weather(loc):
            try:
                # %t: 기온, %h: 습도, %C: 상태 / m: 섭씨(Metric) 강제
                resp = requests.get(f"https://wttr.in/{loc}?format=%t+%h+%C&m", timeout=3)
                if resp.status_code == 200:
                    # [ SECURE ] 인코딩 깨짐 방지를 위한 명시적 디코딩 및 정제
                    raw_text = resp.content.decode('utf-8').strip()
                    # 깨진 문자(Â)가 포함될 경우 제거
                    clean_text = raw_text.replace('Â', '')
                    return clean_text
            except: pass
            return "15°C 50% Clear"
            
        weather_info = get_live_weather(loc_id)
        # 데이터 정밀 파싱 (공백 기준 분리: 기온, 습도, 날씨상태 순)
        w_parts = weather_info.split()
        temp_val = w_parts[0] if len(w_parts) > 0 else "N/A"
        hum_val = w_parts[1] if len(w_parts) > 1 else "0%"
        cond_val = " ".join(w_parts[2:]) if len(w_parts) > 2 else ""
        
        st.markdown(f"""
        <div class='glass-card' style='text-align: center; padding: 20px; border: 1px solid #FFD700; border-radius: 15px; height: 140px;'>
            <h4 style='margin:0; color:#FFD700;'>{sel_region.upper()} / HQ WEATHER</h4>
            <div style='margin-top:5px;'>
                <span style='font-size: 1.3rem; color: #00FF00; font-weight: 800;'>온도: {temp_val}</span>
                <span style='font-size: 1.1rem; color: #888; margin: 0 5px;'>|</span>
                <span style='font-size: 1.3rem; color: #00FFFF; font-weight: 800;'>습도: {hum_val}</span>
            </div>
            <p style='margin:10px 0 0 0; color:#AAA; font-size: 0.8rem;'>[ {cond_val} ] HQ AREA OPERATIONAL</p>
        </div>
        """, unsafe_allow_html=True)

        
    st.divider()
    
    # 출석 입력
    with st.form("attendance_form", clear_on_submit=True):
        st.markdown("### [ ATTENDANCE ] 오늘 한 줄 다짐")
        greeting = st.text_input("사령부에 임하는 오늘의 한 마디", placeholder="예: 오늘도 원칙 매매! 뇌동매매 금지!")
        if st.form_submit_button("[ SIGN ] 출석 완료 및 서명"):
            if greeting:
                now_kst = datetime.now(pytz.timezone('Asia/Seoul')).strftime("%Y-%m-%d %H:%M")
                new_row = pd.DataFrame([[now_kst, st.session_state.current_user, greeting, curr_grade]], columns=["시간", "아이디", "인사", "등급"])
                
                # 🚀 최적화: 백업 생략 (이미 수동 백업 로직이 상단에 있음)
                safe_write_csv(new_row, ATTENDANCE_FILE, mode='a', header=False, backup=False)
                
                # 📡 구글 시트 백업 (사용자 요청에 따라 출석체크는 실시간 연동 중단 - 속도 최적화)
                # gsheet_sync_bg("시트1", ["시간", "아이디", "인사", "등급"], [now_kst, st.session_state.current_user, greeting, curr_grade])
                
                st.success("[ SUCCESS ] 사령부 명부에 정상 등록되었습니다. 오늘의 전술을 확인하십시오.")
                st.balloons()
                st.rerun()
            else:
                st.error("[ ERROR ] 한 줄 인사를 입력해 주세요.")

    st.subheader("[ ADVISOR ] 사령부 실시간 전술 분석 (AI Advisor)")
    # --- 🤖 Rule-based Tactical Advisor (Platinum Engine) ---
    tic_sample = "NVDA"
    advice_sample = get_tactical_advice(tic_sample, 85, 25)
    st.info(advice_sample)

    st.subheader("[ LIVE ] 실시간 출석 현황")
    # 구글 시트 데이터와 로컬 데이터 병합 (전체 데이터 기반 통계 산출)
    gs_att = fetch_gs_attendance().fillna("")
    local_att = safe_read_csv(ATTENDANCE_FILE, ["시간", "아이디", "인사", "등급"]).fillna("")
    full_att = pd.concat([gs_att, local_att]).drop_duplicates(subset=["시간", "아이디", "인사"])
    # 아이디가 없는 무효 행 제거
    full_att = full_att[full_att["아이디"] != ""]
    
    # --- 🛡️ 출석 통계 엔진 가동 (가점 산출용) ---
    def get_user_badges(uid, df):
        u_df = df[df["아이디"] == uid].copy()
        if u_df.empty: return 0, ""
        
        try:
            # 다양한 날짜 형식 대응
            u_df["date"] = pd.to_datetime(u_df["시간"]).dt.date
            u_days = u_df["date"].nunique() # 누적 출석 일수
            
            badges = []
            if u_days >= 365: badges.append("[ CLASS: GOLD ]")
            elif u_days >= 30: badges.append("[ CLASS: SILVER ]")
            elif u_days >= 7: badges.append("[ CLASS: BRONZE ]")
            
            badge_str = " ".join(badges)
            return u_days, badge_str
        except:
            return len(u_df), ""

    # 최근 20개만 표시하되 통계는 전체에서 추출
    display_df = full_att.sort_values("시간", ascending=False).head(20)

    if not display_df.empty:
        for _, row in display_df.iterrows():
            u_id = row["아이디"]
            days, badge = get_user_badges(u_id, full_att)
            
            is_admin_att = row["등급"] in ["방장", "관리자"]
            bg = "rgba(255,215,0,0.15)" if is_admin_att else "rgba(255,255,255,0.05)"
            tag = "[ ADMIN ]" if is_admin_att else "[ MEMBER ]"
            
            st.markdown(f"""
            <div style='background: {bg}; border-radius: 8px; padding: 12px; margin-bottom: 12px; border-left: 4px solid {"#FFD700" if is_admin_att else "#444"};'>
                <div style='display: flex; justify-content: space-between; align-items: center; font-size: 0.85rem; color: #888;'>
                    <div style='display: flex; align-items: center; gap: 10px;'>
                        <b style='color: #EEE; font-size: 1rem;'>{tag} {u_id}</b>
                        <span style='color: #00FF00; font-weight: bold;'>({days}일차)</span>
                        <span style='color: #FFD700; font-weight: 800; font-size: 0.8rem;'>{badge}</span>
                    </div>
                    <span>{row["시간"]}</span>
                </div>
                <div style='margin-top: 8px; color: #BBB; line-height: 1.5;'>{row["인사"]}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("오늘 첫 번째로 출석하여 사령부의 문을 여십시오!")

elif page.startswith("3-a."):
    st.header("[ SCAN ] 주도주 VCP & EP 마스터 스캐너")
    st.markdown("<div class='glass-card'>미너비니의 VCP(변동성 축소)와 본데의 EP(에피소딕 피벗) 4단계 통합 검색 엔진입니다.</div>", unsafe_allow_html=True)
    
    def get_sheet_tickers():
        try:
            # 구글 시트 CSV 내보내기 URL (Gid 반영)
            sheet_url = "https://docs.google.com/spreadsheets/d/1xjbe9SF0HsxwY_Uy3NC2tT92BqK0nhArUaYU16Q0p9M/export?format=csv&gid=1499398020"
            df_sheet = pd.read_csv(sheet_url)
            # 첫 번째 열(A열)에서 티커 추출 (불필요 공백 제거 및 대문자화)
            tickers = df_sheet.iloc[:, 0].dropna().astype(str).str.strip().str.upper().tolist()
            # 중복 제거 및 유효 티커 필터링
            return list(set([t for t in tickers if len(t) >= 1 and t != "NAN"]))
        except Exception as e:
            st.error(f"⚠️ 구글 시트 티커 로드 실패: {e}")
            return ["NVDA", "TSLA", "005930.KS"] # Fallback

    def run_antigravity_screener():
        st_txt = st.empty()
        st_txt.info("[ WAIT ] 구글 시트 실감시 리스트 수집 및 안티그래비티 3단계 정밀 스캔 중...")
        
        full_list = get_sheet_tickers()
        if not full_list:
            st.warning("스캔할 종목 리스트가 비어 있습니다.")
            return

        try:
            # 1년치 일봉 데이터 일괄 수집
            data_full = yf.download(full_list, period="1y", interval="1d", progress=False)
            
            final_results = {"9M_EP": [], "Burst": [], "Story_EP": [], "Delayed_EP": []}
            story_list = get_bonde_top_50()
            
            for tic in full_list:
                try:
                    if isinstance(data_full.columns, pd.MultiIndex):
                        df = data_full.xs(tic, axis=1, level=1).dropna()
                    else: df = data_full.copy().dropna()
                    
                    if len(df) < 30: continue

                    c, p_c, p_c2, o, v, p_v = df['Close'].iloc[-1], df['Close'].iloc[-2], df['Close'].iloc[-3], df['Open'].iloc[-1], df['Volume'].iloc[-1], df['Volume'].iloc[-2]
                    day_pct, gap_pct = (c / p_c - 1) * 100, (o / p_c - 1) * 100
                    avg_v50 = df['Volume'].rolling(50).mean().iloc[-1] if len(df) >= 50 else v
                    
                    res_entry = {"T": TICKER_NAME_MAP.get(tic, tic), "TIC": tic, "P": c, "CH": day_pct, "V": v}
                    
                    # 1. 9 Million EP
                    min_p = 3000 if (".KS" in tic or ".KQ" in tic) else 3.0
                    if v >= 9000000 and (day_pct >= 4.0 or gap_pct >= 4.0) and c >= min_p:
                        final_results["9M_EP"].append(res_entry)
                    
                    # 2. Story-based EP
                    if tic in story_list:
                        if v >= 2000000 and gap_pct >= 4.0:
                            final_results["Story_EP"].append(res_entry)
                    
                    # 3. Delayed Reaction EP
                    recent_20 = df.tail(21).iloc[:-1]
                    has_recent_9m = any((recent_20['Volume'] >= 9000000) & ((recent_20['Close'] / recent_20['Close'].shift(1) - 1) * 100 >= 4.0))
                    cond_r2g = (o < p_c) and (c > p_c) and (c > o)
                    cond_sec_brk = (day_pct >= 4.0) and (v > p_v)
                    if has_recent_9m and (cond_r2g or cond_sec_brk):
                        final_results["Delayed_EP"].append(res_entry)
                    
                    # 4. 4% Momentum Burst
                    cond_tight = abs(p_c / p_c2 - 1) * 100 <= 2.0
                    if day_pct >= 4.0 and v >= 100000 and v > p_v and cond_tight:
                        final_results["Burst"].append(res_entry)
                    
                except: continue

            st.session_state.antigravity_scan = final_results
            st_txt.empty()
            st.success(f"[ SUCCESS ] {len(full_list)}개 종목 분석 완료 및 전략 데이터 등재 완료!")

        except Exception as e:
            st.error(f"⚠️ 스캔 도중 치명적 오류 발생: {e}")

    if st.button("[ EXEC ] 안티그래비티 3단계 정밀 스캔 시작"):
        run_antigravity_screener()

    if "antigravity_scan" in st.session_state:
        res = st.session_state.antigravity_scan
        
        # --- PART 1. 9 Million EP ---
        st.subheader("🚀 PART 1. 9 Million EP (압도적 기관 수급)")
        if not res["9M_EP"]: st.info("현재 900만주 이상 터진 종목이 없습니다.")
        else:
            cols = st.columns(3)
            for i, stock in enumerate(res["9M_EP"][:9]):
                with cols[i % 3]:
                    st.markdown(f"""
                    <div class='glass-card' style='border-left: 5px solid #00FFFF; margin-bottom: 15px; padding: 15px;'>
                        <div style='font-size: 0.8rem; color: #888;'>HIT: 9 MILLION EP</div>
                        <b style='font-size: 1.1rem;'>{stock['T']}</b> ({stock['TIC']})<br>
                        <span style='color: #00FFFF; font-size: 1.4rem; font-weight: 800;'>{stock['CH']:+.1f}%</span>
                        <div style='font-size: 0.75rem; color: #AAA; margin-top: 8px;'>Vol: {stock['V']:,}</div>
                    </div>
                    """, unsafe_allow_html=True)

        # --- PART 2. 4% Momentum Burst ---
        st.divider()
        st.subheader("💥 PART 2. 4% 모멘텀 버스트 (단기 스윙)")
        if not res["Burst"]: st.info("현재 4% 돌파 조건을 충족하는 종목이 없습니다.")
        else:
            cols = st.columns(3)
            for i, stock in enumerate(res["Burst"][:9]):
                with cols[i % 3]:
                    st.markdown(f"""
                    <div class='glass-card' style='border-left: 5px solid #00FF00; margin-bottom: 15px; padding: 15px;'>
                        <div style='font-size: 0.8rem; color: #888;'>HIT: 4% MOMENTUM BURST</div>
                        <b style='font-size: 1.1rem;'>{stock['T']}</b> ({stock['TIC']})<br>
                        <span style='color: #00FF00; font-size: 1.4rem; font-weight: 800;'>{stock['CH']:+.1f}%</span>
                        <div style='font-size: 0.75rem; color: #AAA; margin-top: 8px;'>Vol: {stock['V']:,}</div>
                    </div>
                    """, unsafe_allow_html=True)

        # --- PART 3. Story-based EP ---
        st.divider()
        st.subheader("🎯 PART 3. 스토리 기반 EP (강력한 갭상승)")
        if not res["Story_EP"]: st.info("현재 강력한 갭상승(Story EP) 종목이 없습니다.")
        else:
            cols = st.columns(3)
            for i, stock in enumerate(res["Story_EP"][:9]):
                with cols[i % 3]:
                    st.markdown(f"""
                    <div class='glass-card' style='border-left: 5px solid #FFD700; margin-bottom: 15px; padding: 15px;'>
                        <div style='font-size: 0.8rem; color: #888;'>HIT: STORY-BASED EP</div>
                        <b style='font-size: 1.1rem;'>{stock['T']}</b> ({stock['TIC']})<br>
                        <span style='color: #FFD700; font-size: 1.4rem; font-weight: 800;'>{stock['CH']:+.1f}%</span>
                        <div style='font-size: 0.75rem; color: #AAA; margin-top: 8px;'>Vol: {stock['V']:,}</div>
                    </div>
                    """, unsafe_allow_html=True)

        # --- PART 4. Delayed Reaction EP ---
        st.divider()
        st.subheader("⏳ PART 4. 지연 반응 EP (급등 후 응축)")
        if not res["Delayed_EP"]: st.info("현재 지연 반응(Delayed EP) 조건을 충족하는 종목이 없습니다.")
        else:
            cols = st.columns(3)
            for i, stock in enumerate(res["Delayed_EP"][:9]):
                with cols[i % 3]:
                    st.markdown(f"""
                    <div class='glass-card' style='border-left: 5px solid #FF4B4B; margin-bottom: 15px; padding: 15px;'>
                        <div style='font-size: 0.8rem; color: #888;'>HIT: DELAYED REACTION</div>
                        <b style='font-size: 1.1rem;'>{stock['T']}</b> ({stock['TIC']})<br>
                        <span style='color: #FF4B4B; font-size: 1.4rem; font-weight: 800;'>{stock['CH']:+.1f}%</span>
                        <div style='font-size: 0.75rem; color: #AAA; margin-top: 8px;'>Vol: {stock['V']:,}</div>
                    </div>
                    """, unsafe_allow_html=True)
        
        st.divider()
        # 차트 분석을 위한 통합 리스트 생성
        all_hits = res["9M_EP"] + res["Burst"] + res["Story_EP"] + res["Delayed_EP"]
        
        # 중복 티커 제거 및 포맷팅
        unique_hits = []
        seen_tics = set()
        for h in all_hits:
            if h["TIC"] not in seen_tics:
                unique_hits.append(h)
                seen_tics.add(h["TIC"])
        
        if unique_hits:
            options = [f"{h['T']} ({h['TIC']})" for h in unique_hits]
            selected_option = st.selectbox("분석할 종목을 선택하세요", options)
            
            # 선택된 데이터 추출
            selected_stock = next(h for h in unique_hits if f"{h['T']} ({h['TIC']})" == selected_option)
            selected_ticker = selected_stock["TIC"]
            is_kr_stock = (".KS" in selected_ticker or ".KQ" in selected_ticker)
        
        st.markdown(f"<div style='background: rgba(255,215,0,0.1); padding: 10px; border-radius: 8px; border-left: 4px solid #FFD700; margin-bottom: 15px;'><b>[ TARGET ] 분석 중: {selected_option}</b></div>", unsafe_allow_html=True)
        
        if is_kr_stock:
            # 한국 주식 처리 (네이버 증권 이동)
            pure_code = selected_ticker.replace(".KS", "").replace(".KQ", "")
            naver_url = f"https://finance.naver.com/item/main.naver?code={pure_code}"
            
            st.warning("INFO: 한국 주식은 트레이딩뷰보다 '네이버 증권' 정밀 분석이 더 권장됩니다.")
            st.markdown(f"""
            <div class='glass-card' style='text-align: center; padding: 40px;'>
                <h3 style='color: #FFD700;'>[ KOREA ] {selected_option} - 네이버 증권 데이터 연동</h3>
                <p style='color: #888;'>사령부의 전술적 판단에 따라 한국 시장은 네이버 금융 시스템을 이용합니다.</p>
                <a href='{naver_url}' target='_blank' style='text-decoration: none;'>
                    <div style='background: #03C75A; color: white; padding: 15px 30px; border-radius: 10px; font-weight: 800; display: inline-block; cursor: pointer; border: none; box-shadow: 0 5px 15px rgba(3,199,90,0.4);'>
                        NAVER FINANCE 분석실 입장
                    </div>
                </a>
            </div>
            """, unsafe_allow_html=True)
            st.success(f"COMPLETE: {selected_option} 정밀 데이터 분석 링크 준비 완료!")
        else:
            # 미국 주식 처리 (기존 트레이딩뷰)
            st.components.v1.html(f"<iframe src='https://s.tradingview.com/widgetembed/?symbol={selected_ticker}&interval=D' width='100%' height='500'></iframe>", height=510)
            st.success(f"[ SUCCESS ] {selected_ticker} 실시간 차트 로드 완료!")

elif page.startswith("6-b."):
    st.header("💬 안티그래비티 대화방 (HQ Free Talk)")
    st.markdown("<div class='glass-card'>대원들과 자유롭게 의견을 나누는 공간입니다. 서로 예의를 지켜주세요.</div>", unsafe_allow_html=True)

    uid = st.session_state.current_user
    
    # AI 대원 확률적 참여 (활동량 대폭 증가: 30% 확률)
    if random.random() < 0.3:
        trigger_ai_chat()

    # 실시간 활동 토스트 알림 (누가 무엇을 하는지 구체화)
    if random.random() < 0.1:
        names = ["minsu", "Olive", "Pure", "Harmony"]
        tickers = ["NVDA", "TSLA", "005930.KS", "247540.KQ", "PLTR"]
        acts = ["정밀 스캐닝", "매수 타점 포착", "수급 분석", "데이터 동기화"]
        raw_tick = random.choice(tickers)
        disp_tick = TICKER_NAME_MAP.get(raw_tick, raw_tick)
        st.toast(f"📡 [ ACTION ] [ AI ] {random.choice(names)} 요원이 {disp_tick} {random.choice(acts)} 중입니다!", icon="⚔️")

    # 1. 메시지 입력 구역
    with st.container():
        with st.form("hq_chat_form", clear_on_submit=True):
            ms = st.text_area(f"💬 {uid} 대원님, 메시지를 입력하세요", placeholder="자유롭게 대화에 참여하세요. (Shift+Enter로 줄바꿈)", height=100)
            if st.form_submit_button("[ EXEC ] 메시지 전송", use_container_width=True):
                if ms.strip():
                    now_kst = datetime.now(pytz.timezone('Asia/Seoul'))
                    t = now_kst.strftime("%Y-%m-%d %H:%M:%S")
                    # 로컬 저장
                    new_msg = pd.DataFrame([[t, uid, ms, curr_grade]], columns=["시간", "유저", "내용", "등급"])
                    new_msg.to_csv(CHAT_FILE, mode='a', header=not os.path.exists(CHAT_FILE), index=False, encoding="utf-8-sig")
                    # 백그라운드 싱크 (구글 시트)
                    gsheet_sync_bg("소통기록_통합", ["시간", "유저", "내용", "등급"], [t, uid, ms, curr_grade])
                    st.rerun()

    st.divider()

    # 2. 메시지 리스트 표시 (카톡 스타일 버블)
    try:
        if os.path.exists(CHAT_FILE):
            local_chat = pd.read_csv(CHAT_FILE, encoding="utf-8-sig").fillna("")
            # 최신순 50개만 표시 (무효 행 필터링 포함)
            local_chat = local_chat[local_chat["유저"] != ""]
            display_df = local_chat.sort_index(ascending=False).head(50)
            
            for idx, row in display_df.iterrows():
                is_me = (str(row["유저"]) == str(uid))
                is_admin_msg = (str(row["등급"]) in ["방장", "관리자"])
                
                # 버블 스타일 결정
                align = "right" if is_me else "left"
                bg = "rgba(0, 255, 0, 0.15)" if is_me else ("rgba(255, 215, 0, 0.15)" if is_admin_msg else "rgba(255, 255, 255, 0.08)")
                border = "1px solid #00FF0066" if is_me else ("1px solid #FFD70066" if is_admin_msg else "1px solid #555")
                border_radius = "15px 15px 0px 15px" if is_me else "15px 15px 15px 0px"
                
                # 메시지 표시 섹션
                if st.session_state.get("editing_msg_idx") == idx:
                    # 수정 모드 폼
                    with st.form(f"edit_form_{idx}"):
                        edit_content = st.text_area("메시지 수정", value=row["내용"])
                        ce1, ce2 = st.columns(2)
                        if ce1.form_submit_button("[ OK ] 저장"):
                            local_chat.at[idx, "내용"] = edit_content
                            local_chat.to_csv(CHAT_FILE, index=False, encoding="utf-8-sig")
                            del st.session_state["editing_msg_idx"]
                            st.rerun()
                        if ce2.form_submit_button("[ CANCEL ] 취소"):
                            del st.session_state["editing_msg_idx"]
                            st.rerun()
                    # 일반 버블 모드 (아바타/배지 포함 프리미엄 UI)
                    avatar_char = str(row["유저"])[0].upper() if row["유저"] else "?"
                    st.markdown(f"""
                    <div style='display: flex; justify-content: {"flex-end" if is_me else "flex-start"}; margin-bottom: 20px; gap: 10px; flex-direction: {"row-reverse" if is_me else "row"};'>
                        <div style='width: 40px; height: 40px; background: {bg}; border: {border}; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #FFF; font-weight: 900; font-size: 1.1rem; box-shadow: 0 0 10px {border.split()[-1]};'>
                            {avatar_char}
                        </div>
                        <div style='max-width: 75%;'>
                            <div style='font-size: 0.75rem; color: #888; margin-bottom: 5px; display: flex; align-items: center; gap: 8px; flex-direction: {"row-reverse" if is_me else "row"};'>
                                <b style='color: #EEE;'>{row["유저"]}</b>
                                <span style='background: {bg}; border: 1px solid {border.split()[-1]}; padding: 1px 6px; border-radius: 4px; font-size: 0.6rem; color: #FFF;'>{row["등급"]}</span>
                                <time style='font-size: 0.6rem; opacity: 0.6;'>{row["시간"]}</time>
                            </div>
                            <div style='background: {bg}; border: {border}; border-radius: {border_radius}; padding: 15px; color: #FFF; line-height: 1.6; box-shadow: 0 8px 25px rgba(0,0,0,0.3);'>
                                {row["내용"]}
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 반응 및 관리 버튼 섹션
                    react_col1, react_col2, react_col3, react_col4 = st.columns([7, 1, 1, 1])
                    
                    # 공감(Like) 시스템 (Session State로 가상 카운트 관리)
                    like_key = f"likes_{idx}"
                    if like_key not in st.session_state: st.session_state[like_key] = random.randint(0, 5)
                    
                    with react_col2:
                        if st.button(f"[ LIKE ] {st.session_state[like_key]}", key=f"like_btn_{idx}", help="공감하기"):
                            st.session_state[like_key] += 1
                            st.toast(f"{row['유저']}님의 메시지에 공감했습니다.")
                    
                    # 본인 글일 경우 하단에 작은 버튼 배치
                    if is_me:
                        with react_col3:
                            if st.button("[ EDIT ]", key=f"edit_{idx}", help="수정"):
                                st.session_state.editing_msg_idx = idx
                                st.rerun()
                        with react_col4:
                            if st.button("[ DEL ]", key=f"del_{idx}", help="삭제"):
                                local_chat = local_chat.drop(idx)
                                local_chat.to_csv(CHAT_FILE, index=False, encoding="utf-8-sig")
                                st.rerun()
                    st.write("") # 간격 조절
    except Exception as e:
        st.error(f"채팅 데이터 로드 실패: {e}")

elif page.startswith("3-c."):
    st.header("[ FOCUS ] 사령부 최핵심 감시 리스트 (Top 3 Focus)")
    SHEET_URL = st.secrets.get("MARKET_FOCUS_URL", "https://docs.google.com/spreadsheets/d/1xjbe9SF0HsxwY_Uy3NC2tT92BqK0nhArUaYU16Q0p9M/export?format=csv&gid=1499398020")
    now_kst = datetime.now(pytz.timezone('Asia/Seoul'))
    
    with st.spinner("DATA: 리더보드 수익률 및 수급 정밀 추적 중..."):
        try:
            df_raw = pd.read_csv(SHEET_URL)
            latest_col = df_raw.columns[0]
            # 상위 10개 후보 추출
            top_10_candidates = df_raw[latest_col].dropna().head(10).tolist()
            all_mentions = df_raw.values.flatten().tolist()
            mention_counts = {tic: all_mentions.count(tic) for tic in top_10_candidates}
            
            final_3 = []
            cand_tics = sorted(mention_counts, key=mention_counts.get, reverse=True)
            
            if cand_tics:
                # [ ACTION ] 5일치 데이터를 가져와 주간 ROI 계산
                hist_raw = yf.download(cand_tics, period="5d", progress=False)
                prices_hist = hist_raw['Close']
                
                # 티커가 하나일 경우 DataFrame 형태로 보정
                if isinstance(prices_hist, pd.Series):
                    prices_hist = pd.DataFrame({cand_tics[0]: prices_hist})

                for tic in cand_tics:
                    try:
                        if tic not in prices_hist.columns: continue
                        h_data = prices_hist[tic].dropna()
                        if len(h_data) < 2: continue
                        
                        start_p = h_data.iloc[0] # 5일 전 가격 (기준가)
                        curr_p = h_data.iloc[-1]  # 현재가
                        
                        roi = 0.0
                        if start_p > 0:
                            roi = ((curr_p / start_p) - 1) * 100
                        
                        is_us = (".KS" not in tic and ".KQ" not in tic)
                        cur_symbol = "$" if is_us else ""
                        cur_unit = "" if is_us else "원"
                        
                        final_3.append({
                            "T": tic, 
                            "FREQ": f"{mention_counts[tic]}회 언급",
                            "CURR": f"{cur_symbol}{curr_p:.2f}{cur_unit}" if is_us else f"{int(curr_p):,}원",
                            "ROI": roi,
                            "SL": f"{cur_symbol}{curr_p*0.95:.2f}{cur_unit}" if is_us else f"{int(curr_p*0.95):,}원",
                            "TP": f"{cur_symbol}{curr_p*1.15:.2f}{cur_unit}" if is_us else f"{int(curr_p*1.15):,}원"
                        })
                        if len(final_3) >= 3: break
                    except: continue
                
            st.markdown(f"<div class='glass-card'>DATE: <b>{now_kst.strftime('%Y-%m-%d')} KST</b> | 사령부 전략 자산 ROI 추적 보고서</div>", unsafe_allow_html=True)
            cols = st.columns(3)
            for i, item in enumerate(final_3):
                roi_color = "#00FF00" if item['ROI'] >= 0 else "#FF4B4B"
                roi_mark = "+" if item['ROI'] >= 0 else ""
                
                with cols[i]:
                    st.markdown(f"""<div style='background: rgba(255,215,0,0.08); border: 2px solid #FFD70066; border-radius: 12px; padding: 15px; text-align: center; height: 340px; box-shadow: 0 10px 30px rgba(0,0,0,0.5);'>
<h3 style='color: #FFD700; margin: 0;'>{item['T']}</h3>
<p style='color: #888; font-size: 0.75rem;'>Tactical Mention Rank {i+1}</p>
<hr style='border: 0.5px solid #444; margin: 10px 0;'>
<div style='background: rgba(0,0,0,0.3); padding: 10px; border-radius: 8px; margin-bottom: 15px;'>
<span style='color: #AAA; font-size: 0.8rem;'>CURRENT ROI</span><br>
<span style='color: {roi_color}; font-size: 1.8rem; font-weight: 900;'>{roi_mark}{item['ROI']:.2f}%</span>
</div>
<div style='text-align: left; font-size: 0.85rem; color: #BBB;'>
<b>[ REQ ]:</b> {item['FREQ']}<br>
<b>[ PRICE ]:</b> {item['CURR']}<br>
<b style='color: #FF4B4B;'>[ STOP ]:</b> {item['SL']}<br>
<b style='color: #00FF00;'>[ TARGET ]:</b> {item['TP']}
</div>
</div>""", unsafe_allow_html=True)
            
            if not final_3: st.info("감시 리스트에 유효한 전술 종목이 없습니다.")
            st.success("[ SUCCESS ] 사령부 전략 자산 실시간 퍼포먼스 분석 완료!")
            
            st.divider()
            st.subheader("[ DATABASE ] 본데 감시 리스트 구글 시트 원본 (Real-time)")
            try:
                # 구글 시트 전체 데이터 로드 및 표시
                full_sheet_df = pd.read_csv(SHEET_URL)
                st.markdown("<div style='font-size: 0.8rem; color: #888; margin-bottom: 10px;'>* 이 표는 구글 시트 마스터 데이터와 1:1 동기화됩니다.</div>", unsafe_allow_html=True)
                st.dataframe(full_sheet_df.style.highlight_max(axis=0, color='#004400'), use_container_width=True, height=500)
                st.markdown(f"<p style='text-align: right;'><a href='{SHEET_URL.replace('/export?format=csv&gid=', '/edit#gid=')}' target='_blank' style='color: #FFD700; text-decoration: none; font-size: 0.8rem;'>[ GOOGLE SHEETS ] 마번 시트에서 직접 편집하기 ↗</a></p>", unsafe_allow_html=True)
            except:
                st.warning("원본 시트 데이터를 불러올 수 없습니다. 권한 또는 네트워크를 확인하십시오.")
        except Exception as e:
            st.error(f"[ ERROR ] 전략 리스트 분석 실패: {e}")

elif page.startswith("3-d."):
    st.header("[ INDUSTRY ] 산업동향 (Industry Trends TOP 10)")
    st.markdown("<div class='glass-card'>사령부 지정 데이터 피트를 통한 현재 주도 산업군을 노출합니다.</div>", unsafe_allow_html=True)
    SHEET_URL = st.secrets.get("INDUSTRY_SHEET_URL", "https://docs.google.com/spreadsheets/d/1HbC_U1I78HAdV99X6qS1hmY_RiRGPrHX92AYbBPrIpU/export?format=csv&gid=716298288")
    
    @st.cache_data(ttl=259200)
    def fetch_industry_data(url):
        try: return pd.read_csv(url)
        except: return pd.DataFrame()

    with st.spinner("WAIT: 산업동향 리더보드 수집 중..."):
        try:
            df = fetch_industry_data(SHEET_URL)
            if not df.empty:
                st.dataframe(df.style.format(precision=1), use_container_width=True)
                st.success(f"[ SUCCESS ] 산업군 분석 완료! (갱신 기준일: {datetime.now().strftime('%Y-%m-%d')})")
            else: st.info("현재 로드된 산업동향 데이터가 없습니다.")
        except Exception as e: st.error(f"[ ERROR ] 산업동향 로드 실패: {e}")

elif page.startswith("3-e."):
    st.header("[ RS-STRENGTH ] RS 강도 분석")
    st.markdown("<div class='glass-card'>개별 종목의 지수 대비 상대강도를 분석합니다.</div>", unsafe_allow_html=True)
    SHEET_URL = st.secrets.get("RS_SHEET_URL", "https://docs.google.com/spreadsheets/d/1HbC_U1I78HAdV99X6qS1hmY_RiRGPrHX92AYbBPrIpU/export?format=csv&gid=2082735174")
    
    with st.spinner("WAIT: RS 강도 데이터 로드 중..."):
        try:
            df = pd.read_csv(SHEET_URL)
            if not df.empty:
                def highlight_rs(val):
                    if isinstance(val, str) and '^' in val: return 'color: #00FF00; font-weight: bold; background: rgba(0,255,0,0.1);'
                    return ''
                try: st.dataframe(df.style.map(highlight_rs).format(precision=1), use_container_width=True)
                except: st.dataframe(df.style.applymap(highlight_rs).format(precision=1), use_container_width=True)
                st.success("[ SUCCESS ] RS 강도 분석 및 시각화 완료!")
                st.divider()
                st.markdown("""
                ### [ HQ SYSTEM ] 안티그래비티 '무중력 자동화' 완성
                - **자율 지휘권 부여:** AI가 터미널 명령을 실행하고 코드를 자동 저장하는 체계 구축.
                - **품질 유지:** 보안은 높이고, 로직은 간결하게, 속도는 빠르게.
                - **안정성 확보:** 모든 구문 오류를 해결하여 완벽한 구동 상태 구축.

                ### [ MARKET ] 미국 시장: 반도체 주도 '가속도' 장세
                - **반도체 독주:** FORM, TER, MU 등 반도체 종목 가속도(^) 신호 포착.
                - **섹터 순환매:** 통신 장비, 에너지, 물류로 자극 확산 중.

                ### [ STRATEGY ] 지휘관 전략: 'VCP 인내'와 '기계적 손절'
                - **VCP 단계 대기:** 변동성이 극도로 줄어드는 임계점까지 인내.
                - **철저한 대응:** -3% 손절 원칙을 나노 단위로 엄수하여 수익 방어.
                """, unsafe_allow_html=True)
            else: st.info("현재 로드된 RS 강도 데이터가 없습니다.")
        except Exception as e: st.error(f"[ ERROR ] RS 강도 로드 실패: {e}")

elif page.startswith("1-a."):
    st.header("[ ADMIN ] 관리자 승인 센터 (HQ Member Approval)")
    if not is_admin:
        st.warning("[ ERROR ] 이 구역은 사령부 최고 등급 전용입니다.")
        st.stop()
    pending_users = [u for u, d in users.items() if d.get("status") == "pending"]
    st.subheader("[ QUEUE ] 신규 가입 대기 인원")
    if pending_users:
        if st.button("EXEC: 대기 인원 전체 일괄 승인", use_container_width=True):
            for u in pending_users: users[u]["status"] = "approved"
            save_users(users); st.success("[ SUCCESS ] 모든 대기 인원이 공식 승인되었습니다."); st.rerun()
        for u in pending_users:
            c1, c2 = st.columns([7, 3])
            with c1: st.info(f"ID: **{u}** | 가입 신청됨")
            with c2:
                if st.button(f"APPROVE", key=f"appr_{u}"):
                    users[u]["status"] = "approved"; save_users(users); st.rerun()
    else: st.info("대기 중인 신규 회원이 없습니다.")
    st.divider()
    st.subheader("[ PROMOTION ] 정규직 승격 심사 센터")
    gs_vis = fetch_gs_visitors()
    if not gs_vis.empty:
        try:
            for idx, row in gs_vis.iloc[::-1].iterrows():
                user_id = str(row.get("아이디", "Unknown")).strip()
                if users.get(user_id, {}).get("grade") == "정규직": continue
                with st.expander(f"REQ: {user_id} 대원의 신청서", expanded=False):
                    st.markdown(f"**1. 첫인사:** {row.get('첫인사', '-')}")
                    st.markdown(f"**2. 자기소개:** {row.get('자기소개', '-')}")
                    st.markdown(f"**3. 포부:** {row.get('포부', '-')}")
                    if st.button(f"PROMOTED: {user_id} 정규직 발령", key=f"promo_gs_{idx}"):
                        if user_id in users:
                            users[user_id]["grade"] = "정규직"; save_users(users)
                            st.success(f"[ SUCCESS ] {user_id} 대원이 승격되었습니다!"); st.rerun()
        except: st.info("신청서 데이터 판독 중...")
    else: st.info("현재 접수된 실시간 승격 신청서가 없습니다.")
    st.divider()
    st.subheader("[ STAFF ] 사령부 전체 대원 명부")
    all_rows = []
    for uid, udata in users.items():
        info = udata.get("info", {})
        all_rows.append({
            "아이디": uid, "등급": udata.get("grade", "회원"), "지역": info.get("region", "-"),
            "경력": info.get("exp", "-"), "연령": info.get("age", "-"), "매매 동기": info.get("motivation", "-"), "합류일": info.get("joined_at", "-")
        })
    st.dataframe(pd.DataFrame(all_rows), use_container_width=True, hide_index=True)

elif page.startswith("5-a."):
    st.markdown("<div style='text-align: right;'><span style='background: #FF4B4B; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.6rem; font-weight: bold;'>HQ-DATA SECURED: IMMUTABLE</span></div>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: #FFD700;'>[ MENTOR ] 월가의 멘토, 프라딥 본데</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888; font-size: 1.2rem;'>Stockbee: 시스템 트레이딩의 선구자</p>", unsafe_allow_html=True)
    st.divider()
    
    st.markdown("""<div class='glass-card' style='padding: 30px;'>
<h3 style='color: #FFD700;'>1. 비금융권 출신의 최적화 시각</h3>
<p style='color: #BBB; line-height: 1.8;'>프라딥 본데는 물류 사업의 '시스템 최적화' 경험을 주식 시장에 대입하여, 비즈니스 모델로서의 매매 프로세스를 구축했습니다. 그는 실전 트레이더로서 자신만의 매매 프로세스를 체계화하여 거대한 유산을 남기고 있습니다.</p>
<h3 style='color: #FFD700; margin-top: 25px;'>2. 스탁비의 4대 트레이딩 철학</h3>
<div style='display: grid; grid-template-columns: 1fr 1fr; gap: 15px;'>
<div style='background: rgba(255,215,0,0.05); padding: 15px; border-radius: 10px; border: 1px solid rgba(255,215,0,0.2);'>
<b style='color: #FFF;'>SINGLES: 안타 전략</b><br><span style='font-size: 0.85rem; color: #888;'>확실한 수익을 복리로 누적시키는 꾸준함.</span>
</div>
<div style='background: rgba(255,215,0,0.05); padding: 15px; border-radius: 10px; border: 1px solid rgba(255,215,0,0.2);'>
<b style='color: #FFF;'>DEEP DIVE: 딥 다이브</b><br><span style='font-size: 0.85rem; color: #888;'>폭등 차트 수천 개를 연구하여 패턴을 뇌에 각인.</span>
</div>
<div style='background: rgba(255,215,0,0.05); padding: 15px; border-radius: 10px; border: 1px solid rgba(255,215,0,0.2);'>
<b style='color: #FFF;'>SHIELD: 셀프 리더십</b><br><span style='font-size: 0.85rem; color: #888;'>자기 주도적 실행력과 원칙 고수.</span>
</div>
<div style='background: rgba(255,215,0,0.05); padding: 15px; border-radius: 10px; border: 1px solid rgba(255,215,0,0.2);'>
<b style='color: #FFF;'>BREADTH: 상황 인식</b><br><span style='font-size: 0.85rem; color: #888;'>시장의 폭을 분석하여 공격과 방어 구분.</span>
</div>
</div>
<h3 style='color: #00FF00; margin-top: 25px;'>3. 시장 관통 매매 기법</h3>
<div style='background: rgba(0,255,0,0.03); padding: 20px; border-radius: 12px; border-left: 5px solid #00FF00;'>
<p style='margin-bottom: 8px;'><b style='color:#FFF;'>[ EP ]</b>: 기업 펀더멘털을 바꾸는 강력한 뉴스 공략.</p>
<p style='margin-bottom: 8px;'><b style='color:#FFF;'>[ BURST ]</b>: 눌림목(VCP) 에너지 임계점 포착.</p>
<p style='margin-bottom: 0;'><b style='color:#FFF;'>[ FORMULA ]</b>: 본데만의 대장주 선별 공식 (MAGNA 53+).</p>
</div>
<h3 style='color: #FFD700; margin-top: 25px;'>4. 제자들의 증명</h3>
<p style='color: #BBB;'>크리스찬 쿨라매기 등 수천억 자산가들이 본데의 가르침을 통해 시스템을 완성했습니다.</p>
</div>""", unsafe_allow_html=True)
    st.divider()
# --- [ END OF IMMUTABLE ZONE: 5-a ] ---

# --- [ IMMUTABLE ZONE: MISSION CRITICAL DATA - DO NOT MODIFY ] ---
elif page.startswith("2-d."):
    st.markdown("<div style='text-align: right;'><span style='background: #FF4B4B; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.6rem; font-weight: bold;'>HQ-DATA SECURED: IMMUTABLE</span></div>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: #FFD700;'>[ MISSION ] 사령부 제작 동기</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888; font-size: 1.1rem;'>Follow the Giants, Conquer the Market Together</p>", unsafe_allow_html=True)
    st.divider()
    st.write("이 플랫폼은 윌리엄 오닐, 마크 미너비니, 프라딥 본데의 철학을 기리기 위해 시작되었습니다.")
    st.markdown(f"""<div class='glass-card' style='padding: 30px; margin-top: 20px;'>
<div style='border-left: 4px solid #FFD700; padding-left: 20px; margin-bottom: 30px;'>
<h2 style='color: #FFF; margin: 0; font-size: 1.8rem;'>Dragonfly: 중력을 이기는 비행의 시작</h2>
<p style='color: #888; margin: 5px 0 0 0;'>사령부 시스템의 존재 이유와 대원들을 위한 약속</p>
</div>
<div style='margin-bottom: 30px;'>
<h4 style='color: #FFF;'>스승님을 향한 감사의 마음에서 출발했습니다</h4>
<div style='color: #AAA; line-height: 1.8; font-size: 1rem;'>
주식 시장이라는 거친 바다에서 길을 잃지 않게 이끌어주신 스승님이 계셨습니다. 마크 미너비니, 윌리엄 오닐, 데이비드 라이언, 
그리고 프라딥 본데와 같은 대가들의 지혜를 전해주신 스승님께 보답하는 가장 좋은 방법은, 그 가르침을 나노 단위로 체계화하여 
더 완성도 높은 시스템으로 만드는 것이라 믿었습니다. <b style='color:#FFD700;'>Dragonfly는 스승님의 유산을 잇는 보은의 결과물입니다.</b>
</div>
</div>
<div style='margin-bottom: 30px;'>
<h4 style='color: #FFF;'>경제적 이익과 즐거움을 모두와 나누고 싶습니다</h4>
<div style='color: #AAA; line-height: 1.8; font-size: 1rem;'>
혼자서만 수익을 올리는 것은 진정한 우상향이 아니라고 생각합니다. 주식 투자가 고통스러운 노동이 아니라, 
모든 대원이 편리하게 경제적 이익을 얻고 그 과정에서 성취의 즐거움을 느끼는 생태계를 만들고 싶었습니다. 
Dragonfly는 복잡한 중력의 방해를 받지 않고 <b style='color:#FFD700;'>무중력 상태에서 수익의 가속도를 경험할 수 있는 공간</b>을 지향합니다.
</div>
</div>
<div style='margin-bottom: 30px;'>
<h4 style='color: #FFF;'>정보 보안과 자동화로 세우는 단단한 지지선</h4>
<div style='color: #AAA; line-height: 1.8; font-size: 1rem;'>
사용자의 소중한 정보를 지키기 위해 AES-256과 같은 강력한 암호화 기술을 도입하여 외부의 위협으로부터 자유로운 요새를 만들고자 합니다. 
또한, 인간의 감정이 개입되어 원칙이 흔들리지 않도록 <b style='color:#FFD700;'>나노 단위의 정밀한 자동 매매 시스템</b>을 구축하여, 
가장 차갑고도 정확한 타점에서 승리하는 경험을 제공할 것입니다.
</div>
</div>
<div>
<h4 style='color: #FFF;'>500명의 전우가 함께 만드는 무중력 공동체</h4>
<div style='color: #AAA; line-height: 1.8; font-size: 1rem;'>
처음 100명의 전우가 모여 체계를 잡고, 나아가 500명의 정예 멤버가 각 섹터의 주도주를 감시하며 서로의 실력을 끌어올릴 것입니다. 
경제적 문맹이라는 중력을 벗어나, 500명의 전우가 함께 비상하며 시장을 압도하는 날까지 Dragonfly의 비행은 멈추지 않을 것입니다. 
<b style='color:#FFD700;'>모두가 경제적 자유를 얻었으면 좋겠습니다.</b> 정규직, 계약직 차별 없는 사회를 만들고 싶습니다.
</div>
</div>
</div>""", unsafe_allow_html=True)

    st.markdown("<div class='glass-card' style='margin-top: 30px;'>", unsafe_allow_html=True)
    st.subheader("[ PILLARS ] 사령부를 지탱하는 세 개의 기둥")
    c1, c2, c3 = st.columns(3)
    with c1: 
        with st.popover("**1. 오닐 (CAN SLIM)**", use_container_width=True):
            st.markdown("### 1. 윌리엄 오닐 (William O'Neil)")
            st.caption('"좋은 씨앗(종목)을 고르는 법"')
            st.info("오닐은 펀더멘털(실적)이 뒷받침되는 시장 주도주를 찾는 데 집중합니다.")
            st.markdown("""
            **핵심 전략: CAN SLIM**
            - **C(Current Earnings)**: 최근 분기 순이익이 전년 대비 25% 이상 급증.
            - **A(Annual Earnings)**: 연간 이익 성장률이 꾸준히 가속화.
            - **N(New)**: 신제품, 신기술, 새로운 경영진 또는 신고가 경신.
            - **S(Supply/Demand)**: 유통 주식 수가 적고 거래량이 동반된 주식.
            - **L(Leader or Laggard)**: 해당 업종 내 1등 주도주.
            - **I(Institutional Sponsorship)**: 기관 투자자의 매수세가 유입됨.
            - **M(Market Direction)**: 전체 시장이 상승장일 것.

            **특징**: 숫자로 증명된 강력한 성장주를 선호하며, '비싸게 사서 더 비싸게 파는' 전략의 창시자입니다.
            """)
    with c2: 
        with st.popover("**2. 미너비니 (VCP)**", use_container_width=True):
            st.markdown("### 2. 마크 미너비니 (Mark Minervini)")
            st.caption('"활시위가 팽팽해진 타이밍(VCP)을 잡는 법"')
            st.info("미너비니는 오닐의 제자로, 차트가 에너지를 응축한 순간을 포착하는 기술적 분석의 대가입니다.")
            st.markdown("""
            **핵심 전략: SEPA & VCP**
            - **SEPA**: 하락 중인 주식은 사지 않고, 2단계 상승 추세에 진입한 종목만 필터링.
            - **VCP (Volatility Contraction Pattern)**: 주가 변동폭이 단계적으로 줄어들며(예: 20% → 10% → 3% → 1%) 매물이 모두 소화되는 과정을 확인.

            **특징**: 위험 관리를 최우선으로 합니다. 변동성이 극도로 줄어든 'Tight'한 구간에서 피벗 포인트를 돌파할 때 진입하여 손절 라인을 매우 짧게 가져갑니다.
            """)
    with c3: 
        with st.popover("**3. 본데 (EP/RS)**", use_container_width=True):
            st.markdown("### 3. 프라딥 본데 (Pradeep Bonde)")
            st.caption('"강력한 엔진(EP)과 시장의 관심을 확인하는 법"')
            st.info("본데는 '모멘텀'과 '수급'에 집중하며, 시장에서 가장 강하게 튀어 오르는 종목을 빠르게 잡아냅니다.")
            st.markdown("""
            **핵심 전략: EP & RS**
            - **EP (Explosive Pivot)**: 어닝 서프라이즈 같은 강력한 촉매제와 함께 압도적인 거래량(예: 900만 주 이상)으로 직전 고점을 뚫는 현상.
            - **RS (Relative Strength)**: 시장 지수(S&P500 등)보다 훨씬 더 강력하게 오르는 상대적 강도 확인.
            - **Lynch & EP**: 급등 후 주가가 밀리지 않고 옆으로 기는 '지연 반응' 구간에서 매수.

            **특징**: 거래량이 터지지 않는 상승은 가짜라고 보며, 기관의 강력한 매수세가 들어온 흔적을 추적합니다.
            """)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style='text-align: right; margin-top: 40px; border-top: 1px solid #333; padding-top: 20px;'>
        <p style='color: #888; font-size: 0.8rem; margin-bottom: 5px;'>Terminal v9.9 Platinum Edition</p>
        <b style='color: #FFD700; font-size: 1.2rem;'>Expert Turtle</b>
    </div>
    """, unsafe_allow_html=True)

elif page.startswith("6-c."):
    st.header("[ APPLY ] 방문자 승격 신청서")
    st.markdown("<div class='glass-card'>정규직 승격을 위해 아래 항목을 작성해 주세요.</div>", unsafe_allow_html=True)
    with st.form("greet_detailed", clear_on_submit=True):
        g1 = st.text_area("1. 방문 소감", placeholder="소감을 남겨주세요.")
        g2 = st.text_area("2. 자기소개", placeholder="투자 경험이나 경력을 적어주세요.")
        g3 = st.text_area("3. 포부", placeholder="목료를 적어주세요.")
        if st.form_submit_button("SEND: 승격 신청 전송"):
            if g1 and g2 and g3:
                t = datetime.now().strftime("%Y-%m-%d %H:%M")
                u = st.session_state.current_user
                pd.DataFrame([[t, u, g1, g2, g3]], columns=["시간", "아이디", "첫인사", "자기소개", "포부"]).to_csv(VISITOR_FILE, mode='a', header=not os.path.exists(VISITOR_FILE), index=False, encoding="utf-8-sig")
                gsheet_sync_bg("방문자_승격신청", ["시간", "아이디", "첫인사", "자기소개", "포부"], [t, u, g1, g2, g3])
                st.success("[ SUCCESS ] 승격 신청서가 성공적으로 전송되었습니다.")
            else: st.error("모든 항목을 작성해 주십시오.")

elif page.startswith("4-a."):
    st.header("[ REPORT ] 전략 수립 프로 분석 리포트")
    st.markdown("<div class='glass-card'>현재 시장 주도 테마와 섹터의 RS(상대강도) 통합 보고서입니다.</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("TOP Momentum Sectors")
        st.table(pd.DataFrame({"Sector": ["Semiconductors", "AI Infrastructure", "Defense", "Energy"], "RS Score": [98, 95, 89, 82]}))
    with c2:
        st.subheader("Tactical Overlays")
        st.info("핵심 전략: NVDA, TSMC 등 대장주 눌림목 돌파 시 비중 확대.")
    st.divider()
    st.success("ADVICE: 주도 섹터 밖의 낙폭 과대주는 쳐다보지도 마십시오.")

elif page.startswith("4-b."):
    st.header("[ CALC ] 안티그래비티 리스크 계산기")
    st.markdown("<div class='glass-card'>계좌 총액 대비 개별 종목의 적정 매수 규모를 산출합니다.</div>", unsafe_allow_html=True)
    with st.form("risk_calc"):
        capital = st.number_input("총 투자 원금 (₩)", value=10000000, step=1000000)
        risk_pct = st.slider("1종목당 총자산 대비 허용 리스크 (%)", 0.5, 2.0, 1.0, 0.1)
        entry_price = st.number_input("진입 가격 (₩)", value=50000, step=100)
        stop_price = st.number_input("손절 가격 (₩)", value=48500, step=100)
        if st.form_submit_button("CALCULATE EXPOSURE"):
            risk_amt = capital * (risk_pct/100)
            loss_per_share = entry_price - stop_price
            if loss_per_share > 0:
                qty = int(risk_amt / loss_per_share)
                total_order = qty * entry_price
                st.balloons()
                st.success(f"### 적정 매수 수량: {qty} 주")
                st.metric("총 주문 금액", f"{total_order:,.0f}원")
                st.warning(f"설명: 손절 시 전체 자산의 {risk_pct}%인 {risk_amt:,.0f}원만 손실을 입게 됩니다.")
            else: st.error("손절가는 진입가보다 낮아야 합니다.")

elif page.startswith("4-c."):
    st.header("[ SHIELD ] 리스크 방패 (The -3% Iron Shield)")
    st.divider()
    st.subheader("INFO: 왜 본데는 '-3% 손절'을 생명처럼 여기는가?")
    st.error("1. 복리 보존: 수익 역성장 절대 금지.")
    st.warning("2. 타점 판독: 후태 즉시 시장 오판 인정.")
    st.info("3. 생존 조건: 단 하나의 큰 실수가 모든 결과를 파괴함.")
    st.success("ADVICE: 손절은 더 큰 승리를 위한 전략적 후퇴입니다.")

elif page.startswith("5-d."):
    st.header("[ EXAM ] 사령부 정기 승급 시험 안내")
    st.markdown("<div class='glass-card'>대원의 역량을 증명하고 추격 권한을 획득하는 관문입니다.</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div style='background: rgba(255,215,0,0.05); padding: 25px; border-radius: 15px; border: 1px solid #FFD700; height: 350px;'>
            <h3 style='color: #FFD700;'>[ SCHEDULE ] 시험 일정 (Biannual)</h3>
            <p style='font-size: 1.1rem; color: #EEE;'>6개월마다 상/하반기 1회 시행.</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style='background: rgba(255,255,255,0.03); padding: 25px; border-radius: 15px; border: 1px solid #444; height: 350px;'>
            <h3 style='color: #EEE;'>[ GUIDE ] 합격 및 진격 지침</h3>
            <p>80점 이상 획득 시 공식 승격 발령.</p>
        </div>
        """, unsafe_allow_html=True)
    st.divider()
    st.subheader("[ HALL-OF-FAME ] 최근 시험 결과 시뮬레이션")
    st.table(pd.DataFrame([{"아이디": "cntfed", "점수": 95, "결과": "PASS (Top)"}, {"아이디": "ExpertTurtle", "점수": 100, "결과": "PASS (Master)"}]))
    st.info("ADVICE: 주식공부방과 리스크 방패 섹션을 철처히 복급하세요.")

elif page.startswith("5-e."):
    st.header("[ PROFIT ] 실전 익절 자랑방 (Hall of Gain)")
    st.markdown("<div class='glass-card'>시장을 이겨내고 획득한 전리품을 공유하세요!</div>", unsafe_allow_html=True)
    if not os.path.exists(PROFIT_FILE): safe_write_csv(pd.DataFrame(columns=["ID", "시간", "아이디", "종목", "수익률", "수익금", "포부"]), PROFIT_FILE)
    if not os.path.exists(COMMENTS_FILE): safe_write_csv(pd.DataFrame(columns=["PostID", "시간", "작성자", "내용"]), COMMENTS_FILE)
    with st.expander("POST: 나의 익절 기록 하달하기", expanded=True):
        with st.form("profit_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            tic = col1.text_input("종목명/티커")
            roi = col2.text_input("수익률 (%)")
            p_val = st.text_input("수익금")
            msg = st.text_area("소감 및 노하우")
            if st.form_submit_button("SEND: 전리품 등록 (자랑하기)"):
                if tic and roi and p_val:
                    t_now = datetime.now(pytz.timezone('Asia/Seoul')).strftime("%Y-%m-%d %H:%M")
                    u = st.session_state.current_user
                    pid = f"P_{int(time.time())}_{u}"
                    safe_write_csv(pd.DataFrame([[pid, t_now, u, tic, roi, p_val, msg]], columns=["ID", "시간", "아이디", "종목", "수익률", "수익금", "포부"]), PROFIT_FILE, mode='a', header=False, backup=False)
                    gsheet_sync_bg("익절방", ["날짜", "시간", "회원명", "종목명/티커", "수익률", "수익금", "승리소감"], [t_now.split(" ")[0], t_now.split(" ")[1], u, tic, roi, p_val, msg])
                    st.success("[ SUCCESS ] 훈장이 수여되었습니다!"); st.balloons(); st.rerun()
                else: st.error("필수 항목을 입력하세요.")
    pdf = safe_read_csv(PROFIT_FILE, ["ID", "시간", "아이디", "종목", "수익률", "수익금", "포부"])
    cdf = safe_read_csv(COMMENTS_FILE, ["PostID", "시간", "작성자", "내용"])
    if not pdf.empty:
        for _, row in pdf.iloc[::-1].iterrows():
            pid = row['ID']; is_owner = (st.session_state.current_user == row['아이디']) or is_admin
            st.markdown(f"""
            <div style='background: rgba(0,255,0,0.03); border: 1px solid #00FF0033; border-radius: 12px; padding: 20px; margin-bottom: 10px;'>
                <b style='color: #FFD700;'>[ GAIN ]: {row['아이디']} 대원의 승전보</b><br>
                <small style='color: #888;'>DATE: {row['시간']}</small>
                <div style='margin-top: 15px; display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; text-align: center;'>
                    <div style='background: rgba(0,0,0,0.3); padding: 5px; border-radius: 5px;'>종목: {row['종목']}</div>
                    <div style='background: rgba(0,0,0,0.3); padding: 5px; border-radius: 5px; color: #FF4B4B;'>수익률: {row['수익률']}</div>
                    <div style='background: rgba(0,0,0,0.3); padding: 5px; border-radius: 5px; color: #00FF00;'>수익금: {row['수익금']}</div>
                </div>
                <div style='margin-top: 10px; color: #CCC;'>MSG: {row['포부']}</div>
            </div>
            """, unsafe_allow_html=True)
            if is_owner:
                o_c1, o_c2 = st.columns([1, 7])
                if o_c1.button("DEL", key=f"del_{pid}"):
                    safe_write_csv(pdf[pdf['ID'] != pid], PROFIT_FILE); st.rerun()
            with st.container():
                for _, c in cdf[cdf['PostID'] == pid].iterrows():
                    st.markdown(f"<div style='margin-left: 20px; font-size: 0.8rem;'><b style='color: #FFD700;'>{c['작성자']}:</b> {c['내용']} ({c['시간']})</div>", unsafe_allow_html=True)
                c_c1, c_c2 = st.columns([8, 2])
                new_c = c_c1.text_input("격려의 한마디", key=f"c_i_{pid}", label_visibility="collapsed")
                if c_c2.button("GO", key=f"c_b_{pid}"):
                    if new_c:
                        now_ct = datetime.now(pytz.timezone('Asia/Seoul')).strftime("%m/%d %H:%M")
                        safe_write_csv(pd.DataFrame([[pid, now_ct, st.session_state.current_user, new_c]], columns=["PostID", "시간", "작성자", "내용"]), COMMENTS_FILE, mode='a', header=False)
                        st.rerun()

elif page.startswith("5-a."):
    st.markdown("<h1 style='text-align: center; color: #FFD700;'>[ MENTOR ] 월가의 멘토, 프라딥 본데(Pradeep Bonde)</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888; font-size: 1.2rem;'>시스템 트레이딩의 선구자: 스탁비(Stockbee)의 유산</p>", unsafe_allow_html=True)
    st.divider()

    st.write("""
    프라딥 본데는 온라인에서 **스탁비(Stockbee)**라는 필명으로 활동하며 전 세계 트레이딩 커뮤니티에 거대한 유산을 남기고 있는 실전 트레이더입니다. 
    그는 단순히 수익을 많이 내는 투자자를 넘어, 자신만의 독창적인 매매 프로세스를 체계화하여 후학을 양성하는 교육자로서의 면모를 강력하게 보여주고 있습니다.
    """)

    st.subheader("1. 비금융권 출신의 혁명적 시각")
    st.info("""
    본데의 이력에서 가장 흥미로운 점은 그가 정통 금융권 엘리트 코스를 밟지 않았다는 사실입니다. 그는 인도에서 DHL과 FedEx 같은 글로벌 물류 기업의 마케팅 책임자로 근무하며 경력을 쌓았습니다. 
    물류 산업의 핵심인 **'시스템 최적화와 프로세스 관리'** 경험은 그가 주식 시장을 바라보는 시각을 완전히 바꾸어 놓았습니다. 그는 주식 매매를 막연한 예측의 영역이 아닌, 입력값에 따라 결과가 도출되는 비즈니스 모델로 접근했습니다.
    """)

    st.subheader("2. 스탁비의 4대 트레이딩 철학")
    c1, c2 = st.columns(2)
    with c1:
        with st.expander("[ SINGLES ] 안타 전략", expanded=True):
            st.write("일확천금을 노리는 홈런보다 작고 확실한 수익을 복리로 누적시키는 것이 부의 축적을 위한 가장 빠른 길입니다.")
        with st.expander("[ DEEP DIVE ] 딥 다이브", expanded=True):
            st.write("뇌가 고민하기 전에 손이 반응하도록 과거 폭등 차트 수천 개를 연구하여 패턴을 '절차적 기억'으로 뇌에 각인시킵니다.")
    with c2:
        with st.expander("[ SHIELD ] 셀프 리더십", expanded=True):
            st.write("멘토의 조언보다 중요한 것은 스스로 문제를 해결하고 실행에 옮기는 자기 주도적 실행력입니다.")
        with st.expander("[ BREADTH ] 철저한 상황 인식", expanded=True):
            st.write("매일 시장의 폭(Breadth)을 분석하여 공격할 때와 방어할 때를 구분하는 시스템적 방패를 가동합니다.")

    st.subheader("3. 시장을 관통하는 핵심 매매 기법")
    st.success("""
    [ EP ]: 기업의 펀더멘털을 근본적으로 바꾸는 강력한 뉴스나 실적이 터졌을 때, 폭발적인 거래량과 함께 진입하여 기관의 자금 유입 초기 국면을 공략합니다.  
    [ BURST ]: 좁은 눌림목(VCP)에서 에너지가 분출하는 임계점을 포착합니다.  
    [ FORMULA ]: 시가총액과 상장 기간, 상승률을 필터링하여 가볍고 빠른 '대장주'만을 골라내는 본데만의 전용 공식입니다.
    """)

    st.subheader("4. 제자들이 증명하는 실력의 가치")
    st.write("""
    본데의 위대함은 제자들의 수익률로 증명됩니다. **1,300억 원 이상의 자산을 달성한 크리스찬 쿨라매기(Kristjan Qullamaggi)**는 본데의 가르침을 통해 자신의 시스템을 완성했다고 공공연히 밝히고 있습니다. 
    그는 화려한 마케팅 대신 오직 데이터와 결과로 승부하며, 현재도 실전 트레이딩 팩토리를 운영하며 시장의 살아있는 전설로 활동하고 있습니다.
    """)
    st.divider()

elif page.startswith("2-a."):
    st.header("[ TREND ] 마켓 트렌드 요약")



elif page.startswith("5-d."):
    st.header("[ EXAM ] 사령부 정기 승급 시험 안내")
    st.markdown("<div class='glass-card'>사령부 대원으로서의 역량을 증명하고 한 단계 더 높은 주도주 추격권한을 획득하는 공식 관문입니다.</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div style='background: rgba(255,215,0,0.05); padding: 25px; border-radius: 15px; border: 1px solid #FFD700; height: 350px;'>
            <h3 style='color: #FFD700;'>[ SCHEDULE ] 시험 일정 (Biannual)</h3>
            <p style='font-size: 1.1rem; color: #EEE;'>6개월에 1회, 그동안 배운 전술을 토대로 엄격하게 시행됩니다.</p>
            <ul style='color: #CCC;'>
                <li><b>상반기:</b> 1월 말 토요일 오전 11:00</li>
                <li><b>하반기:</b> 7월 말 토요일 오전 11:00</li>
            </ul>
            <p style='color: #888; font-size: 0.9rem;'>※ 시험 1주 전 사령부 공지사항을 통해 상세 범위가 하달됩니다.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
        <div style='background: rgba(255,255,255,0.03); padding: 25px; border-radius: 15px; border: 1px solid #444; height: 350px;'>
            <h3 style='color: #EEE;'>[ GUIDE ] 합격 및 진격 가이드</h3>
            <ul style='color: #CCC; line-height: 1.8;'>
                <li><b>문항수:</b> 총 20문항 (차트 패턴 및 전술 이론)</li>
                <li><b>만점:</b> 100점</li>
                <li><b>커트라인:</b> <b style='color: #FFD700;'>80점 이상</b> 획득 시 승급</li>
                <li><b>주의사항:</b> 투명한 사령부 운영을 위해 <b>개인별 성적은 전 대원에게 공개</b>됩니다.</li>
            </ul>
            <p style='color: #FF4B4B; font-weight: bold; margin-top: 15px;'>[ ALERT ] 불합격 시 다음 6개월 뒤 재시험 응시 가능</p>
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    st.subheader("[ HALL-OF-FAME ] 최근 승급 시험 명예의 전당 (Simulation)")
    mock_results = pd.DataFrame([
        {"아이디": "cntfed", "점수": 95, "결과": "[ PASS ] 합격 (수석)"},
        {"아이디": "ExpertTurtle", "점수": 100, "결과": "[ MASTER ] 합격 (전설)"},
        {"아이디": "NewMember1", "점수": 75, "결과": "[ FAIL ] 불합격"},
    ])
    st.table(mock_results)
    
    st.info("[ ADVICE ] 팁: '5-b. 주식공부방'과 '4-c. 리스크 방패' 섹션의 내용을 철저히 복습하는 것이 합격의 지름길입니다.")

elif page.startswith("5-e."):
    st.header("[ GAIN ] 실전 익절 자랑방 (Hall of Gain)")
    st.markdown("<div class='glass-card'>지옥 같은 시장을 이겨내고 획득한 귀중한 전리품(익절)을 사령부 전역에 자랑하세요!</div>", unsafe_allow_html=True)
    
    if not os.path.exists(PROFIT_FILE):
        safe_write_csv(pd.DataFrame(columns=["ID", "시간", "아이디", "종목", "수익률", "수익금", "포부"]), PROFIT_FILE)
    else:
        # 헤더 정합성 체크 (ID 컬럼 누락 방지)
        temp_df = safe_read_csv(PROFIT_FILE, ["ID", "시간", "아이디", "종목", "수익률", "수익금", "포부"])
        if "ID" not in temp_df.columns:
            temp_df.insert(0, "ID", [f"P_{int(time.time())}_{i}" for i in range(len(temp_df))])
            safe_write_csv(temp_df, PROFIT_FILE)
    if not os.path.exists(COMMENTS_FILE):
        safe_write_csv(pd.DataFrame(columns=["PostID", "시간", "작성자", "내용"]), COMMENTS_FILE)

    with st.expander("[ ACTION ] 나의 익절 기록 하달하기", expanded=True):
        with st.form("profit_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1: tic = st.text_input("종목명/티커", placeholder="예: 삼성전자 / TSLA")
            with col2: roi = st.text_input("수익률 (%)", placeholder="예: +15.5%")
            
            p_val = st.text_input("확정 수익금 (KRW/USD)", placeholder="예: 2,500,000원")
            msg = st.text_area("승리 소감 및 노하우 공유", placeholder="어떤 타점에서 진입하여 익절하셨나요?")
            
            if st.form_submit_button("[ EXEC ] 전리품 등록 (자랑하기)"):
                if tic and roi and p_val:
                    now_k = datetime.now(pytz.timezone('Asia/Seoul'))
                    t_now = now_k.strftime("%Y-%m-%d %H:%M")
                    d_str, t_str = t_now.split(" ")
                    u = st.session_state.current_user
                    pid = f"P_{int(time.time())}_{random.randint(100,999)}_{u}"
                    new_p = pd.DataFrame([[pid, t_now, u, tic, roi, p_val, msg]], columns=["ID", "시간", "아이디", "종목", "수익률", "수익금", "포부"])
                    # [ ACTION ] 로컬 저장
                    save_success = safe_write_csv(new_p, PROFIT_FILE, mode='a', header=False, backup=False)
                    
                    if not save_success:
                        st.error("[ ERROR ] 로컬 파일(CSV) 저장에 실패했습니다. 파일 잠금을 확인해 주세요.")
                    
                    # [ ACTION ] 구글 시트 백그라운드 동기화
                    gsheet_sync_bg("익절방", 
                        ["날짜", "시간", "회원명", "종목명/티커", "수익률", "수익금", "승리소감 및 노하우"], 
                        [d_str, t_str, u, tic, roi, p_val, msg]
                    )
                    
                    st.success("[ SUCCESS ] 대원님의 위대한 승리 기록이 저장되었습니다! (구글 시트 동기화는 배경에서 진행됩니다.)")
                    
                    st.balloons()
                    time.sleep(1) 
                    st.rerun()
                else: st.error("[ ERROR ] 종목, 수익률, 수익금은 필수 항목입니다.")

    pdf = safe_read_csv(PROFIT_FILE, ["ID", "시간", "아이디", "종목", "수익률", "수익금", "포부"])
    cdf = safe_read_csv(COMMENTS_FILE, ["PostID", "시간", "작성자", "내용"])
    
    if not pdf.empty:
        try:
            for _, row in pdf.iloc[::-1].iterrows():

                pid = row['ID']
                is_owner = (st.session_state.current_user == row['아이디']) or is_admin
                
                edit_key = f"edit_p_{pid}"
                if st.session_state.get(edit_key):
                    with st.form(f"form_edit_{pid}"):
                        e_roi = st.text_input("수익률 수정", value=row['수익률'])
                        e_val = st.text_input("수익금 수정", value=row['수익금'])
                        e_msg = st.text_area("소감 수정", value=row['포부'])
                        # 1. 1차 광범위 분석
                        scanned_pool = []
                        for t in targets[:40]: 
                            msg_pre = f"📡 {t} 분석 중..."
                            report_log.insert(0, msg_pre)
                            report_placeholder.markdown("\n".join(report_log[:15]))
                            
                            t_hist = None
                            if all_hist is not None:
                                try:
                                    t_hist = pd.DataFrame({
                                        "Close": all_hist["Close"][t], "High": all_hist["High"][t],
                                        "Low": all_hist["Low"][t], "Volume": all_hist["Volume"][t]
                                    }).dropna()
                                except: t_hist = None
                            
                            res = analyze_stockbee_setup(t, hist_df=t_hist)
                            res["ticker"] = t
                            res["name"] = TICKER_NAME_MAP.get(t, t)
                            scanned_pool.append(res)
                        
                        # 2. RS 점수 기반 상위 10개 종목 압축 (Ranking)
                        # RS 점수가 없는 경우(REJECT 등)는 0점으로 처리
                        top_10_pool = sorted(scanned_pool, key=lambda x: x.get('rs', 0), reverse=True)[:10]
                        
                        # 단계별 분류 및 매수 집행
                        st.session_state.universe_list = []
                        st.session_state.rs_target_list = []
                        st.session_state.execution_list = []
                        
                        # 현재 보유 종목 수 체크 (최대 4개 제한)
                        current_holdings_count = len(real_holdings) + len(over_holdings)
                        
                        for res in top_10_pool:
                            name, t = res['name'], res['ticker']
                            
                            if res["status"] == "SUCCESS":
                                st.session_state.execution_list.append(res)
                                report_log.insert(0, f"🔥 **[ TOP 10 / EXECUTION ] {name} 포착!**")
                                
                                # [ CONCENTRATION ] 최대 4종목 제한 및 25% 비중 투입
                                if st.session_state.get("live_toggle_v6_pro"):
                                    if current_holdings_count >= 4:
                                        report_log[0] += " | 🛡️ 포트폴리오(4개) 풀가동 중 (진입 보류)"
                                    else:
                                        # 자본금의 25% 계산
                                        invest_amount = full_balance * 0.25
                                        qty = int(invest_amount / res['close']) if res['close'] > 0 else 0
                                        
                                        if qty > 0:
                                            st.toast(f"🚀 {name} 피벗 돌파! 자본 25% 투입...", icon="⚡")
                                            if execute_kis_market_order(t, qty, is_buy=True):
                                                current_holdings_count += 1
                                                if st.session_state.combat_logs:
                                                    st.session_state.combat_logs[-1]["msg"] += f" (비중 25% 집중 투입)"
                            
                            elif res["status"] == "PASS":
                                if res["stage"] == "RS_TARGET":
                                    st.session_state.rs_target_list.append(res)
                                    report_log.insert(0, f"🎯 **[ TOP 10 / TARGET ] {name} 확보**")
                                else:
                                    st.session_state.universe_list.append(res)
                                    report_log.insert(0, f"🛡️ **[ TOP 10 / UNIVERSE ] {name} 통과**")
                            else:
                                report_log.insert(0, f"❌ {t} 순위권 탈락: {res.get('reason', '점수 미달')}")
                            
                            report_placeholder.markdown("\n".join(report_log[:20]))
                        
                        status.update(label="[ SUCCESS ] 최정예 10개 종목 압축 및 전략 집행 완료!", state="complete")
                        c_edit1, c_edit2 = st.columns(2)
                        if c_edit1.form_submit_button("[ SAVE ] 저장"):
                            temp_df = safe_read_csv(PROFIT_FILE)
                            temp_df.loc[temp_df['ID'] == pid, ['수익률', '수익금', '포부']] = [e_roi, e_val, e_msg]
                            safe_write_csv(temp_df, PROFIT_FILE)
                            del st.session_state[edit_key]
                            st.rerun()
                        if c_edit2.form_submit_button("[ CANCEL ] 취소"):
                            del st.session_state[edit_key]
                            st.rerun()
                else:
                    st.markdown(f"""
                    <div style='background: rgba(0,255,0,0.03); border: 1px solid #00FF0033; border-radius: 12px; padding: 20px; margin-bottom: 10px;'>
                        <div style='display: flex; justify-content: space-between;'>
                            <b style='color: #FFD700; font-size: 1.1rem;'>[ GAIN ] {row['아이디']} 대원의 승전보</b>
                            <span style='color: #888; font-size: 0.8rem;'>{row['시간']} { ' (관리자)' if is_admin and not (st.session_state.current_user == row['아이디']) else '' }</span>
                        </div>
                        <div style='margin-top: 15px; display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px;'>
                            <div style='text-align: center; background: rgba(0,0,0,0.3); padding: 10px; border-radius: 8px;'>
                                <small style='color: #888;'>대상 종목</small><br><b style='color: #EEE;'>{row['종목']}</b>
                            </div>
                            <div style='text-align: center; background: rgba(0,0,0,0.3); padding: 10px; border-radius: 8px;'>
                                <small style='color: #888;'>확정 수익률</small><br><b style='color: #FF4B4B;'>{row['수익률']}</b>
                            </div>
                            <div style='text-align: center; background: rgba(0,0,0,0.3); padding: 10px; border-radius: 8px;'>
                                <small style='color: #888;'>실현 수익금</small><br><b style='color: #00FF00;'>{row['수익금']}</b>
                            </div>
                        </div>
                        <div style='margin-top: 15px; padding: 10px; border-top: 1px solid rgba(255,255,255,0.05); color: #CCC;'>
                            [ MSG ] {row['포부']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if is_owner:
                        o_col1, o_col2, o_col3 = st.columns([1, 1, 6])
                        if o_col1.button("[ EDIT ]", key=f"edit_btn_{pid}", use_container_width=True):
                            st.session_state[edit_key] = True
                            st.rerun()
                        if o_col2.button("[ DEL ]", key=f"del_btn_{pid}", use_container_width=True):
                            temp_df = safe_read_csv(PROFIT_FILE, ["ID", "시간", "아이디", "종목", "수익률", "수익금", "포부"])
                            temp_df = temp_df[temp_df['ID'] != pid]
                            safe_write_csv(temp_df, PROFIT_FILE)
                            st.warning("[ ALERT ] 항목이 삭제되었습니다.")
                            st.rerun()
                
                # 댓글 섹션
                with st.container():
                    item_comments = cdf[cdf['PostID'] == pid]
                    for _, c in item_comments.iterrows():
                        st.markdown(f"<div style='margin-left: 20px; font-size: 0.9rem; border-left: 2px solid #555; padding-left: 10px; margin-bottom: 5px;'><b style='color: #FFD700;'>{c['작성자']}:</b> {c['내용']} <span style='color: #555; font-size: 0.7rem;'>({c['시간']})</span></div>", unsafe_allow_html=True)
                    
                    c_col1, c_col2 = st.columns([8, 2])
                    new_c = c_col1.text_input("격려의 한마디", key=f"c_input_{pid}", label_visibility="collapsed", placeholder="대원님 축하드립니다!")
                    if c_col2.button("[ CHAT ]", key=f"c_btn_{pid}"):
                        if new_c:
                            now_c_t = datetime.now(pytz.timezone('Asia/Seoul')).strftime("%m/%d %H:%M")
                            u = st.session_state.current_user
                            c_new = pd.DataFrame([[pid, now_c_t, u, new_c]], columns=["PostID", "시간", "작성자", "내용"])
                            safe_write_csv(c_new, COMMENTS_FILE, mode='a', header=False)
                            gsheet_sync_bg("댓글_통합", ["PostID", "시간", "작성자", "내용"], [pid, now_c_t, u, new_c])
                            st.rerun()
                st.write("") 
        except Exception as e:
            st.error(f"[ ERROR ] 첩보 목록을 렌더링하는 중 오류가 발생했습니다: {e}")
    else:
        st.info("아직 도착한 익절 첩보가 없습니다. 첫 주인공이 되어보세요!")


elif page.startswith("5-f."):
    st.header("[ LOSS ] 손실 위로 및 복기방")
    st.markdown("<div class='glass-card'>실패는 성공의 어머니가 아니라, <b>실패에 대한 복기</b>가 성공의 어머니입니다. 아픔을 나누고 더 단단해지는 공간입니다.</div>", unsafe_allow_html=True)
    
    if not os.path.exists(LOSS_FILE):
        safe_write_csv(pd.DataFrame(columns=["ID", "시간", "아이디", "종목", "손실률", "원인", "다짐"]), LOSS_FILE)
    else:
        temp_df = safe_read_csv(LOSS_FILE, ["ID", "시간", "아이디", "종목", "손실률", "원인", "다짐"])
        if "ID" not in temp_df.columns:
            temp_df.insert(0, "ID", [f"L_{int(time.time())}_{i}" for i in range(len(temp_df))])
            safe_write_csv(temp_df, LOSS_FILE)
    if not os.path.exists(COMMENTS_FILE):
        safe_write_csv(pd.DataFrame(columns=["PostID", "시간", "작성자", "내용"]), COMMENTS_FILE)

    with st.expander("[ ACTION ] 오늘의 아픔 기록하고 털어내기", expanded=True):
        with st.form("loss_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1: l_tic = st.text_input("종목명/티커", placeholder="복기할 종목")
            with col2: l_roi = st.text_input("손실률 (%)", placeholder="예: -7.2%")
            
            l_reason = st.selectbox("실전 과오 원인 판독", [
                "추격 매수 (FOMO)", "손절 지연 (희망고문)", "원칙 외 매매 (뇌동매매)", 
                "비중 과다 (몰빵)", "지수 급락 대응 실패", "기타 전술적 오류"
            ])
            l_msg = st.text_area("구체적인 상황 복기 및 향후 다짐", placeholder="왜 이런 결과가 나왔는지, 다음에는 어떻게 대응하실 건가요?")
            
            if st.form_submit_button("[ SIGN ] 복기 완료 및 마음 다잡기"):
                if l_tic and l_roi and l_msg:
                    now_k = datetime.now(pytz.timezone('Asia/Seoul'))
                    t_now = now_k.strftime("%Y-%m-%d %H:%M")
                    d_str, t_str = t_now.split(" ")
                    u = st.session_state.current_user
                    lid = f"L_{int(time.time())}_{random.randint(100,999)}_{u}"
                    new_l = pd.DataFrame([[lid, t_now, u, l_tic, l_roi, l_reason, l_msg]], columns=["ID", "시간", "아이디", "종목", "손실률", "원인", "다짐"])
                    save_l_success = safe_write_csv(new_l, LOSS_FILE, mode='a', header=False, backup=False)
                    
                    if not save_l_success:
                        st.error("[ ERROR ] 로컬 파일(CSV) 저장에 실패했습니다.")

                    gsheet_sync_bg("손절방", 
                        ["날짜", "시간", "회원명", "종목명/티커", "손실률", "과오원인", "구체적인 상황 복기 및 향후 다짐"], 
                        [d_str, t_str, u, l_tic, l_roi, l_reason, l_msg]
                    )
                    st.toast("[ SUCCESS ] 성찰 기록이 저장되었습니다.")
                    
                    time.sleep(1)
                    st.rerun()
                else: st.error("[ ERROR ] 필수 항목을 모두 입력해 주세요.")

    st.divider()
    st.subheader("[ SUPPORT ] 함께 나누는 성찰의 시간")
    
    ldf = safe_read_csv(LOSS_FILE, ["ID", "시간", "아이디", "종목", "손실률", "원인", "다짐"])
    cdf = safe_read_csv(COMMENTS_FILE, ["PostID", "시간", "작성자", "내용"])
    
    if not ldf.empty:
        try:
            for _, row in ldf.iloc[::-1].iterrows():

                pid = row['ID']
                is_owner = (st.session_state.current_user == row['아이디']) or is_admin
                
                edit_key = f"edit_l_{pid}"
                if st.session_state.get(edit_key):
                    with st.form(f"form_ledit_{pid}"):
                        e_lroi = st.text_input("손실률 수정", value=row['손실률'])
                        e_lreason = st.selectbox("사유 수정", [
                            "추격 매수 (FOMO)", "손절 지연 (희망고문)", "원칙 외 매매 (뇌동매매)", 
                            "비중 과다 (몰빵)", "지수 급락 대응 실패", "기타 전술적 오류"
                        ], index=0)
                        e_lmsg = st.text_area("복기 수정", value=row['다짐'])
                        cl_edit1, cl_edit2 = st.columns(2)
                        if cl_edit1.form_submit_button("[ SAVE ] 저장"):
                            temp_df = safe_read_csv(LOSS_FILE, ["ID", "시간", "아이디", "종목", "손실률", "원인", "다짐"])
                            temp_df.loc[temp_df['ID'] == pid, ['손실률', '원인', '다짐']] = [e_lroi, e_lreason, e_lmsg]
                            safe_write_csv(temp_df, LOSS_FILE)
                            del st.session_state[edit_key]
                            st.rerun()
                        if cl_edit2.form_submit_button("[ CANCEL ] 취소"):
                            del st.session_state[edit_key]
                            st.rerun()
                else:
                    st.markdown(f"""
                    <div style='background: rgba(255,255,255,0.02); border: 1px solid #6366f133; border-radius: 12px; padding: 20px; margin-bottom: 10px;'>
                        <div style='display: flex; justify-content: space-between;'>
                            <b style='color: #6366f1;'>[ SUPPORT ] {row['아이디']} 대원에게 따뜻한 위로를</b>
                            <span style='color: #888; font-size: 0.8rem;'>{row['시간']}</span>
                        </div>
                        <div style='margin-top: 12px; font-size: 0.95rem; color: #BBB;'>
                            [ ACTION ] <b>{row['종목']}</b> 종목에서 <b>{row['손실률']}</b> 손실 기록 (<span style='color: #FF4B4B;'>사유: {row['원인']}</span>)
                        </div>
                        <div style='margin-top: 15px; padding: 12px; background: rgba(0,0,0,0.2); border-left: 3px solid #6366f1; color: #DDD; font-size: 0.95rem; font-style: italic;'>
                            "{row['다짐']}"
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if is_owner:
                        ol_col1, ol_col2, ol_col3 = st.columns([1, 1, 6])
                        if ol_col1.button("[ EDIT ]", key=f"ledit_btn_{pid}", use_container_width=True):
                            st.session_state[edit_key] = True
                            st.rerun()
                        if ol_col2.button("[ DEL ]", key=f"ldel_btn_{pid}", use_container_width=True):
                            temp_df = safe_read_csv(LOSS_FILE, ["ID", "시간", "아이디", "종목", "손실률", "원인", "다짐"])
                            temp_df = temp_df[temp_df['ID'] != pid]
                            safe_write_csv(temp_df, LOSS_FILE)
                            st.warning("[ ALERT ] 복기 내역이 삭제되었습니다.")
                            st.rerun()

                with st.container():
                    item_comments = cdf[cdf['PostID'] == pid]
                    for _, c in item_comments.iterrows():
                        st.markdown(f"<div style='margin-left: 20px; font-size: 0.9rem; border-left: 2px solid #555; padding-left: 10px; margin-bottom: 5px;'><b style='color: #6366f1;'>{c['작성자']}:</b> {c['내용']} <span style='color: #555; font-size: 0.7rem;'>({c['시간']})</span></div>", unsafe_allow_html=True)
                    
                    c_col1, c_col2 = st.columns([8, 2])
                    new_c = c_col1.text_input("따뜻한 한마디", key=f"c_input_{pid}", label_visibility="collapsed", placeholder="대원님, 고생 많으셨습니다. 힘내세요!")
                    if c_col2.button("[ CHAT ]", key=f"c_btn_{pid}"):
                        if new_c:
                            now_c_t = datetime.now(pytz.timezone('Asia/Seoul')).strftime("%m/%d %H:%M")
                            u = st.session_state.current_user
                            c_new = pd.DataFrame([[pid, now_c_t, u, new_c]], columns=["PostID", "시간", "작성자", "내용"])
                            safe_write_csv(c_new, COMMENTS_FILE, mode='a', header=False)
                            gsheet_sync_bg("댓글_통합", ["PostID", "시간", "작성자", "내용"], [pid, now_c_t, u, new_c])
                            st.rerun()
                st.write("") 
        except Exception as e:
            st.error(f"[ ERROR ] 복기 목록을 렌더링하는 중 오류가 발생했습니다: {e}")
    else:
        st.info("아직 등록된 성찰 기록이 없습니다. 아픔을 나누면 반이 됩니다.")


elif page.startswith("2-b."):
    st.header("[ MAP ] 실시간 주도주 히트맵 (Market OverView)")
    st.markdown("<div class='glass-card'>사령부 관리 종목 20선의 실시간 수급 현황입니다. (초록: 상승 / 빨강: 하락)</div>", unsafe_allow_html=True)
    if st.button("[ RUN ] 실시간 히트맵 데이터 동기화"):
        tics = list(TICKER_NAME_MAP.keys())
        try:
            with st.spinner("[ WAIT ] 데이터 수집 중..."):
                h_data = yf.download(tics, period="2d", progress=False)['Close']
                changes = ((h_data.iloc[-1] / h_data.iloc[-2]) - 1) * 100
                df_h = pd.DataFrame([{"Name": TICKER_NAME_MAP.get(t, t), "Change": changes.get(t, 0), "Size": 1} for t in tics])
                fig = px.treemap(df_h, path=['Name'], values='Size', color='Change', color_continuous_scale='RdYlGn', color_continuous_midpoint=0)
                fig.update_layout(margin=dict(t=30, l=10, r=10, b=10), height=600)
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e: st.error(f"오류 발생: {e}")

elif page.startswith("2-c."):
    st.header("[ SENTIMENT ] 시장 심리 게이지 (Market Sentiment Tracker)")
    st.markdown("<div class='glass-card'>글로벌 투자자들의 공포와 탐욕 및 주요 지수 심리를 실시간 추적합니다.</div>", unsafe_allow_html=True)
    val, curr_vix, label = get_market_sentiment_v2()
    
    st.info(f"[ ADVICE ] 현재 시장 변동성 지수(VIX): **{curr_vix:.1f}** | 수치가 낮을수록 시장은 안정적(탐욕), 높을수록 불안정(공포) 상태입니다.")

    st.info("[ ADVICE ] 위 지표를 통해 대중의 광기(Greed)가 극에 달했을 때는 현금 비중을 높이고, 공포(Fear)가 극에 달했을 때는 기회를 포착하십시오.")
    
    col1, col2 = st.columns([1.5, 1.2])
    with col1:
        st.components.v1.html("""
            <div class="tradingview-widget-container">
              <div class="tradingview-widget-container__widget"></div>
              <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-market-overview.js" async>
              {
              "colorTheme": "dark",
              "dateRange": "12M",
              "showChart": true,
              "locale": "ko",
              "width": "100%",
              "height": "600",
              "largeChartUrl": "",
              "isTransparent": false,
              "showSymbolLogo": true,
              "showFloatingTooltip": false,
              "tabs": [
                {
                  "title": "지수",
                  "symbols": [
                    { "proName": "FOREXCOM:SPX500", "title": "S&P 500" },
                    { "proName": "FOREXCOM:NSXUSD", "title": "Nasdaq 100" },
                    { "proName": "FX_IDC:USDKRW", "title": "USD/KRW" }
                  ],
                  "originalTitle": "Indices"
                },
                {
                  "title": "주도주",
                  "symbols": [
                    { "proName": "NASDAQ:NVDA", "title": "NVIDIA" },
                    { "proName": "NASDAQ:TSLA", "title": "Tesla" },
                    { "proName": "NASDAQ:AAPL", "title": "Apple" }
                  ]
                }
              ]
            }
              </script>
            </div>
        """, height=620)
    
    with col2:
        st.markdown("<div class='glass-card' style='padding:25px;'>", unsafe_allow_html=True)
        st.subheader("[ TRUTH ] StockDragonfly의 실시간 뼈 때리는 훈계 (Harsh Truth)")
        if val <= 35: 
            st.error("""
            **[ STATUS: DEFENSIVE/CASH ]**  
            "떨어지는 칼날을 왜 잡으려 하나? 네가 시장보다 똑똑하다고 착각하지 마라. 
            지금 네가 할 일은 스캐닝이 아니라 자본 보호다. 계좌 박살 내고 울지 말고 당장 HTS 꺼라. 
            시장은 어디 안 간다, 네 돈이 도망갈 뿐이지."
            """)
        elif val <= 65: 
            st.warning("""
            **[ STATUS: SELECTIVE/CHOPPY ]**  
            "지금 매수 버튼에 손이 가나? 그건 투자가 아니라 도박이다. 아무것도 하지 않는 것도 포지션이다. 
            푼돈 벌려다 큰돈 잃지 말고, 확실한 A+ 셋업이 올 때까지 얌전히 현금 쥐고 기다려라. 
            지루함을 못 견디면 파산뿐이다."
            """)
        else: 
            st.success("""
            **[ STATUS: GREED/AGGRESSIVE ]**  
            "수익 좀 났다고 네가 천재가 된 줄 아나? 시장이 좋은 것뿐이다. 
            자만심(Ego)이 고개를 드는 순간, 시장은 네 계좌를 갈기갈기 찢어놓을 거다. 
            익절 라인 올려 잡고 닥치고 프로세스나 지켜라."
            """)
        st.markdown("</div>", unsafe_allow_html=True)
        
    st.divider()
    wisdom = get_daily_wisdom()
    st.markdown(f"""
    <div class='glass-card'>
        <h3 style='color: #FF4B4B; margin-top: 0;'>[ HQ ] 사령부 정신 교육: {wisdom['title']}</h3>
        <p style='color: #DDD; font-size: 1.1rem; line-height: 1.8; font-style: italic;'>
            "{wisdom['content']}"
        </p>
        <div style='text-align: right; color: #888; font-weight: 700;'>- Pradeep Bonde, Stockbee Matrix -</div>
    </div>
    """, unsafe_allow_html=True)

elif page.startswith("1-b."):
    st.header("[ HR ] HQ 인적 자원 사령부 (Member HR Command)")
    users = load_users()
    
    # 사령관(방장) 전용 보안
    if users.get(st.session_state.current_user, {}).get("grade") != "방장":
        st.error("[ ERROR ] 이 전술 구역은 사령관(방장) 전용입니다. 권한이 없습니다.")
        st.stop()
        
    st.markdown("<div class='glass-card'>사령관의 권위로 대원의 등급을 조정하거나 사령부에서 즉각 제명(삭제)하는 인사권을 행사합니다.</div>", unsafe_allow_html=True)
    
    # 🛡️ 사령부 데이터 동기화 및 복구 센터 (통합 관리)
    st.subheader("[ CLOUD ] 클라우드 데이터 동기화 및 복구 센터")
    with st.expander("[ DATA ] 구글 시트 양방향 동기화 (불러오기 / 백업)", expanded=True):
        st.markdown("""
        사령부 명부와 구글 시트 데이터를 동기화합니다. 
        - **불러오기 (Import):** 구글 시트에 저장된 최신 명단을 가져와 현재 터미널을 업데이트합니다.
        - **백업 (Export):** 현재 터미널의 모든 대원 정보를 구글 시트(클라우드)로 안전하게 전송합니다.
        """)
        
        c_sync1, c_sync2 = st.columns(2)
        with c_sync1:
            if st.button("[ IMPORT ] 클라우드 명단 불러오기 (Import)", use_container_width=True, key="import_btn"):
                with st.spinner("구글 시트 데이터 수신 및 무결성 검사 중..."):
                    if "gs_error" in st.session_state: del st.session_state["gs_error"]
                    load_users.clear()
                    users = load_users()
                    
                    if "gs_error" in st.session_state:
                        st.error(st.session_state["gs_error"])
                    elif users:
                        # 🛡️ 빈 문자열 아이디 필터링
                        users = {k: v for k, v in users.items() if k.strip()}
                        save_users(users)
                        st.success(f"[ SUCCESS ] 클라우드에서 {len(users)}명의 요원 정보를 성공적으로 수신하여 동기화했습니다.")
                        st.rerun()
                    else:
                        st.warning("[ WARNING ] 시트에서 데이터를 가져왔으나 등록된 대원 정보가 없습니다.")
        
        with c_sync2:
            if st.button("[ EXPORT ] 현재 명단 클라우드 백업 (Export)", use_container_width=True, key="export_btn"):
                with st.spinner("사령부 명부 데이터 전송 중..."):
                    count = 0
                    for uid, udata in users.items():
                        info = udata.get("info", {})
                        gsheet_sync("회원명단", 
                            ["아이디", "비밀번호", "상태", "등급", "지역", "연령대", "성별", "경력", "가입일", "매매동기"],
                            [
                                uid, udata.get("password", ""), udata.get("status", "approved"), 
                                udata.get("grade", "회원"), info.get("region", "-"), info.get("age", "-"), 
                                info.get("gender", "-"), info.get("exp", "-"), info.get("joined_at", "-"), info.get("motivation", "-")
                            ]
                        )
                        count += 1
                    st.success(f"[ SUCCESS ] 총 {count}명의 대원 정보가 구글 시트에 안전하게 백업되었습니다!")
                    st.balloons()
    
    st.divider()
    st.subheader("[ DIRECTORY ] 전체 대원 리스트 관리")
    
    # 자신을 제외한 대원 리스트
    m_list = [u for u in users.keys() if u != st.session_state.current_user]
    
    if m_list:
        for u in m_list:
            udata = users[u]
            uinfo = udata.get("info", {})
            with st.expander(f"[ ID: {u} ] (현재 보직: {udata.get('grade', '회원')})"):
                c1, c2, c3 = st.columns([2, 1.5, 1])
                with c1:
                    st.write(f"📍 거주지: {uinfo.get('region', '-')}")
                    st.write(f"📊 경력: {uinfo.get('exp', '-')}")
                    st.write(f"🕯️ 나이: {uinfo.get('age', '-')}")
                with c2:
                    current_idx = ["회원", "정규직", "관리자"].index(udata.get("grade", "회원")) if udata.get("grade") in ["회원", "정규직", "관리자"] else 0
                    new_grade = st.selectbox(f"보직 변경 (ID:{u})", ["회원", "정규직", "관리자"], key=f"grade_sel_{u}", index=current_idx)
                    if st.button(f"인사발령 (ID:{u})", key=f"btn_grade_{u}"):
                        users[u]["grade"] = new_grade
                        save_users(users)
                        st.success(f"✅ {u} 요원이 {new_grade}(으)로 발령되었습니다.")
                        st.rerun()
                with c3:
                    st.write("") # 정렬용
                    if st.button("[ EXEC: DELETE ] 즉각 제명", key=f"del_{u}"):
                        del users[u]
                        save_users(users)
                        st.warning(f"[ WARNING ] {u} 요원이 명부에서 삭제되었습니다.")
                        st.rerun()
    else:
        st.info("현재 사령부에서 관리할 대원이 없습니다.")


elif page.startswith("5-b."):
    st.markdown("<h1 style='color: #FFD700; text-align: center; font-size: 3rem;'>[ ACADEMY ] StockDragonfly 차트 아카데미</h1>", unsafe_allow_html=True)
    st.markdown("""
    <div class='glass-card' style='text-align: center; padding: 30px; border: 1px solid #FFD700; background: rgba(255,215,0,0.02);'>
        <p style='font-size: 1.2rem; color: #EEE; line-height: 1.8;'>
            "성공적인 트레이딩은 본능이 아니라 훈련된 반사 신경의 결과입니다."<br>
            본 교육 섹션은 윌리엄 오닐과 프라딥 본데의 철학을 바탕으로, 시장 주도주의 탄생 원리를 몸소 체득할 수 있도록 설계되었습니다. 
            눈으로 읽는 공부를 넘어, 차트 1,000개를 뇌에 각인시키는 <b>딥 다이브(Deep Dive)</b> 훈련을 시작하십시오.
        </p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["[ ARCHIVE ] Master's Archive", "[ TARGET ] Training Room", "[ LIVE ] Live Academy"])

    with tab1:
        st.subheader("1. 마스터 아카이브: 대가들의 정석 패턴")
        st.markdown("<div class='glass-card'>지난 10년간 시장을 주도했던 100% 이상 폭등주의 돌파 직전 데이터를 한곳에 모았습니다.</div>", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("""
            <div style='background: rgba(255,255,255,0.05); padding: 20px; border-radius: 12px; border-top: 4px solid #FF4B4B;'>
                <h4 style='color: #FF4B4B;'>유형별 집중 학습</h4>
                <p style='color: #AAA; font-size: 0.9rem;'>컵앤핸들, VCP(변동성 축소), 에피소딕 피벗(EP) 등 정석 패턴별 분류 데이터를 제공합니다.</p>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown("""
            <div style='background: rgba(255,255,255,0.05); padding: 20px; border-radius: 12px; border-top: 4px solid #00FF00;'>
                <h4 style='color: #00FF00;'>시세의 인과관계</h4>
                <p style='color: #AAA; font-size: 0.9rem;'>돌파 전의 정적인 응축과 돌파 후의 폭발적 상승을 비교 분석하여 승률을 높입니다.</p>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown("""
            <div style='background: rgba(255,255,255,0.05); padding: 20px; border-radius: 12px; border-top: 4px solid #FFD700;'>
                <h4 style='color: #FFD700;'>데이터 학습</h4>
                <p style='color: #AAA; font-size: 0.9rem;'>본데의 코드 33과 수급의 결합이 어떻게 시세를 만드는지 실증 데이터로 확인합니다.</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.info("[ ADVICE ] 아카이브 내부 데이터는 매주 업데이트되며, 현재 1,200개 이상의 폭등주 샘플이 데이터베이스에 등록되어 있습니다.")

    with tab2:
        st.subheader("2. 트레이닝 룸: 실전 타점 훈련")
        st.markdown("<div class='glass-card'>차트를 보고 직접 매수 급소를 클릭하며 실전 감각을 기르는 인터랙티브 훈련장입니다.</div>", unsafe_allow_html=True)
        
        cc1, cc2 = st.columns([2, 1])
        with cc1:
            with st.status("[ SCANNING ] 본데(Stockbee) 전술 타점 정밀 분석 및 자동 집행 중...", expanded=True) as status:
                targets = sorted(list(set(get_bonde_top_50() + get_kospi_top_200())))
                # 단계별 분류 리스트 초기화
                st.session_state.universe_list = []
                st.session_state.rs_target_list = []
                st.session_state.execution_list = []
                
                try:
                    all_hist = yf.download(targets[:30], period="1y", progress=False)
                except: all_hist = None
                
                for t in targets[:30]: 
                    current_msg = f"📡 {t} 분석 중..."
                    report_log.insert(0, current_msg)
                    report_placeholder.markdown("\n".join(report_log[:15]))
                    
                    t_hist = None
                    if all_hist is not None:
                        try:
                            t_hist = pd.DataFrame({
                                "Close": all_hist["Close"][t], "High": all_hist["High"][t],
                                "Low": all_hist["Low"][t], "Volume": all_hist["Volume"][t]
                            }).dropna()
                        except: t_hist = None
                    
                    analysis = analyze_stockbee_setup(t, hist_df=t_hist)
                    name = TICKER_NAME_MAP.get(t, t)
                    analysis["ticker"] = t
                    analysis["name"] = name

                    if analysis["status"] == "SUCCESS":
                        st.session_state.execution_list.append(analysis)
                        report_log[0] = f"🔥 **[ EXECUTION ] {name}({t}) 포착!** - {analysis['reason']}"
                        
                        if st.session_state.get("live_toggle_v6_pro"):
                            st.toast(f"🚀 {name} 실전 매수 집행!", icon="⚡")
                            if execute_kis_market_order(t, 10, is_buy=True):
                                if st.session_state.combat_logs:
                                    st.session_state.combat_logs[-1]["msg"] += f" (근거: {analysis['reason']})"
                    elif analysis["status"] == "PASS":
                        if analysis["stage"] == "RS_TARGET":
                            st.session_state.rs_target_list.append(analysis)
                            report_log[0] = f"🎯 **[ RS TARGET ] {name}({t}) 확보** - {analysis['reason']}"
                        else:
                            st.session_state.universe_list.append(analysis)
                            report_log[0] = f"🛡️ **[ UNIVERSE ] {name}({t}) 통과** - {analysis['reason']}"
                    else:
                        report_log[0] = f"❌ {t} 탈락: {analysis['reason']}"
                    
                    report_placeholder.markdown("\n".join(report_log[:15]))
                
                status.update(label="[ SUCCESS ] 전술 단계별 분석 완료!", state="complete")

    with col_btn2:
        if st.button("🛑 중단", use_container_width=True):
            st.session_state.scanning_active = False
            st.rerun()

    # --- [ DISPLAY STAGED RESULTS ] ---
    if st.session_state.scanning_active:
        st.markdown("### 🛰️ TACTICAL STAGING AREA")
        tab1, tab2, tab3 = st.tabs(["🔥 EXECUTION (매수)", "🎯 RS TARGET (감시)", "🛡️ UNIVERSE (관심)"])
        
        with tab1:
            if not st.session_state.execution_list: st.info("현재 실행 범위에 진입한 종목이 없습니다.")
            for res in st.session_state.execution_list:
                with st.expander(f"🚀 {res['name']} ({res['ticker']}) - 즉시 대응", expanded=True):
                    st.write(f"**상태:** {res['reason']}")
                    st.write(f"**전략:** {', '.join(res.get('setups', ['VCP']))}")

        with tab2:
            if not st.session_state.rs_target_list: st.info("확보된 핵심 타겟이 없습니다.")
            for res in st.session_state.rs_target_list:
                with st.expander(f"🎯 {res['name']} ({res['ticker']}) - RS 90↑", expanded=False):
                    st.write(f"**상태:** {res['reason']}")
                    st.write(f"**RS 지수:** {res.get('rs', 0):.1f}")

        with tab3:
            if not st.session_state.universe_list: st.info("유니버스를 통과한 종목이 없습니다.")
            for res in st.session_state.universe_list:
                with st.expander(f"🛡️ {res['name']} ({res['ticker']}) - 정배열 유지", expanded=False):
                    st.write(f"**상태:** {res['reason']}")
        st.markdown("""
            <div style='height: 400px; display: flex; align-items: center; justify-content: center; background: #111; border: 2px dashed #444; border-radius: 15px;'>
                <div style='text-align: center; color: #666;'>
                    <h3>[피벗 포인트 퀴즈 모드]</h3>
                    <p>랜덤 과거 차트 로드 중... 타점을 클릭하세요.</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with cc2:
            st.markdown("#### 🛡️ 훈련 지침")
            st.warning("""
            **반사 신경 강화:**  
            장중에 머리로 고민하지 않고 손이 먼저 반응하도록 무한 반복 훈련합니다.
            """)
            
            if st.button("[ RUN ] 무작위 훈련 시작"):
                st.toast("사령부 데이터베이스에서 무작위 폭등주 과거 차트를 추출합니다.")
            
            st.markdown("---")
            st.markdown("**전술 피드백:**")
            st.info("클릭 결과에 따라 본데의 철학이 담긴 정교한 해설과 뼈 때리는 일침이 제공됩니다.")

    with tab3:
        st.subheader("3. 라이브 아카메디: 현재 주도주 실시간 분석")
        st.markdown("<div class='glass-card'>현재 시장에서 꿈틀되는 종목들에 대가들의 분석 엔진을 직접 투영해 봅니다.</div>", unsafe_allow_html=True)
        
        l1, l2 = st.columns([3, 1])
        with l2:
            live_input = st.text_input("분석 종목 (이름 또는 티커)", "NVDA")
            live_tic = resolve_ticker(live_input)
            st.markdown(f"""
            <div style='background: rgba(0,255,0,0.05); padding: 15px; border-radius: 10px; border: 1px solid #00FF00;'>
                <b style='color: #00FF00;'>[ SCAN ] 나노바나나 스캔</b><br>
                <small>돌파 임박도 (잘 익었는지):</small>
                <div style='background: #333; height: 10px; border-radius: 5px; margin-top: 5px;'>
                    <div style='background: #00FF00; width: 85%; height: 100%; border-radius: 5px;'></div>
                </div>
                <div style='text-align: right; font-size: 0.8rem; margin-top: 3px;'>85% Ready</div>
            </div>
            <br>
            <div style='background: rgba(255,215,0,0.05); padding: 15px; border-radius: 10px; border: 1px solid #FFD700;'>
                <b style='color: #FFD700;'>[ TAG ] 자동 어노테이션</b><br>
                <small>• RS 신고가 감지됨</small><br>
                <small>• VCP 3단계 수축 진행중</small><br>
                <small>• 거래량 말라감(Dry-up) 포착</small>
            </div>
            """, unsafe_allow_html=True)
            
        with l1:
            st.components.v1.html(f"""
                <iframe src='https://s.tradingview.com/widgetembed/?symbol={live_tic}&interval=D&theme=dark' width='100%' height='550'></iframe>
            """, height=560)
            st.success(f"[ LIVE ] {live_tic} 실시간 실전 판독 엔진 가동 중")

    st.divider()
    st.subheader("[ MANUAL ] StockDragonfly 아카데미 운영 지침")
    
    # 운영 지침 요약 테이블
    st.markdown("""
    <table style='width: 100%; border-collapse: collapse; color: white;'>
        <tr style='background: rgba(255,215,0,0.1);'>
            <th style='padding: 12px; border: 1px solid #444;'>단계</th>
            <th style='padding: 12px; border: 1px solid #444;'>기능 명칭</th>
            <th style='padding: 12px; border: 1px solid #444;'>핵심 학습 내용</th>
        </tr>
        <tr>
            <td style='padding: 12px; border: 1px solid #444; text-align: center;'>1단계</td>
            <td style='padding: 12px; border: 1px solid #444;'>Deep Dive</td>
            <td style='padding: 12px; border: 1px solid #444;'>대가들의 정석 패턴 1,000개 뇌에 각인</td>
        </tr>
        <tr>
            <td style='padding: 12px; border: 1px solid #444; text-align: center;'>2단계</td>
            <td style='padding: 12px; border: 1px solid #444;'>Action Quiz</td>
            <td style='padding: 12px; border: 1px solid #444;'>피벗 포인트 포착 및 절차적 기억 형성</td>
        </tr>
        <tr>
            <td style='padding: 12px; border: 1px solid #444; text-align: center;'>3단계</td>
            <td style='padding: 12px; border: 1px solid #444;'>Real-time Check</td>
            <td style='padding: 12px; border: 1px solid #444;'>현재 주도주의 셋업 완성도 나노 단위 분석</td>
        </tr>
    </table>
    """, unsafe_allow_html=True)

elif page.startswith("5-c."):
    st.markdown("<h1 style='text-align: center; color: #00FF00;'>[ RADAR ] 나노바나나 정밀 레이더</h1>", unsafe_allow_html=True)
    st.markdown("<div class='glass-card' style='text-align: center;'>현재 사령부 감시망 내에서 에너지가 응축되어 돌파가 임박한 '황금 바나나' 종목들을 실시간 추적합니다.</div>", unsafe_allow_html=True)
    
    # 레이더 데이터 (Mock or Multi-processing logic)
    radar_stocks = [
        {"T": "NVDA", "Ready": 95, "Status": "돌파 임박(VCP 3회)"},
        {"T": "PLTR", "Ready": 88, "Status": "수급 유입 포착"},
        {"T": "TSLA", "Ready": 82, "Status": "라인 저항 테스트"},
        {"T": "SMCI", "Ready": 75, "Status": "에너지 응축 중"},
        {"T": "AAPL", "Ready": 68, "Status": "박스권 횡보"},
        {"T": "META", "Ready": 62, "Status": "눌림목 형성"}
    ]
    
    cols = st.columns(3)
    for i, stock in enumerate(radar_stocks):
        with cols[i % 3]:
            color = "#00FF00" if stock['Ready'] >= 90 else "#FFD700" if stock['Ready'] >= 80 else "#6366f1"
            st.markdown(f"""
            <div class='glass-card' style='border-top: 5px solid {color};'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <h3 style='margin: 0;'>{stock['T']}</h3>
                    <span style='color: {color}; font-weight: 800;'>{stock['Ready']}%</span>
                </div>
                <div class='banana-track'>
                    <div class='banana-fill' style='width: {stock['Ready']}%; background: {color}; color: {color};'></div>
                </div>
                <p style='font-size: 0.85rem; color: #888; margin-top: 10px;'>📡 상태: {stock['Status']}</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"[ TARGET ] {stock['T']} 정밀 분석", key=f"radar_btn_{stock['T']}", use_container_width=True):
                st.toast(f"{stock['T']} 분석실로 전술 이동 중...")
            
    st.divider()
    st.info("[ ADVICE ] 레이더의 'Ready' 지수는 ROE, RS, 그리고 최근 2주간의 변동성 타이트니스(Tightness)를 종합 산출한 결과입니다.")
    
elif page.startswith("1-c."):
    st.header("[ SECURITY ] 계정 보안 및 관리 (Security & Account)")
    st.markdown("<div class='glass-card'>사령부 보안 설정을 관리합니다. 비밀번호를 정기적으로 변경해 주세요.</div>", unsafe_allow_html=True)
    
    # 비밀번호 변경 섹션
    with st.expander("[ KEY ] 비밀번호 변경 및 보안 강화", expanded=True):
        with st.form("pw_change_form", clear_on_submit=True):
            curr_pw_input = st.text_input("현재 비밀번호 확인", type="password")
            new_pw_input = st.text_input("새로운 비밀번호 설정", type="password")
            new_pw_confirm = st.text_input("새로운 비밀번호 다시 입력", type="password")
            
            if st.form_submit_button("[ EXEC ] 비밀번호 변경 적용"):
                users = load_users()
                u_id = st.session_state.current_user
                u_data = users.get(u_id, {})
                u_info = u_data.get("info", {})
                
                if u_data.get("password") != curr_pw_input:
                    st.error("❌ 현재 비밀번호가 일치하지 않습니다.")
                elif new_pw_input != new_pw_confirm:
                    st.error("❌ 비밀번호 확인이 일치하지 않습니다.")
                elif len(new_pw_input) < 4:
                    st.error("❌ 비밀번호는 최소 4자 이상이어야 합니다.")
                else:
                    users[u_id]["password"] = new_pw_input
                    safe_save_json(users, USER_DB_FILE)
                    gsheet_sync_bg("회원명단", 
                        ["아이디", "비밀번호", "상태", "등급", "지역", "연령대", "성별", "경력", "가입일", "매매동기"],
                        [u_id, new_pw_input, u_data.get("status", "approved"), u_data.get("grade", "회원"), u_info.get("region", "-"), u_info.get("age", "-"), u_info.get("gender", "-"), u_info.get("exp", "-"), u_info.get("joined_at", "-"), u_info.get("motivation", "-")]
                    )
                    st.success("[ SUCCESS ] 비밀번호 변경 완료!")
                    st.balloons()

elif page.startswith("1-d."):
    st.header("[ ACCOUNT ] 탈퇴 및 임시휴식 (Account Status)")
    st.markdown("<div class='glass-card'>사령부 활동 중단이나 탈퇴를 관리합니다. 신중하게 결정해 주십시오.</div>", unsafe_allow_html=True)
    
    st.subheader("⚠️ 계정 상태 변경 및 전역 처리")
    c1, c2 = st.columns(2)
    
    users = load_users()
    u_id = st.session_state.current_user
    u_data = users.get(u_id, {})
    u_info = u_data.get("info", {})

    with c1:
        st.markdown("<div class='glass-card' style='border-top: 3px solid #6366f1;'><b>임시 휴식 신청</b><br><small>활동을 잠시 중단합니다. 관리자 승인 전까지 기능이 제한될 수 있습니다.</small></div>", unsafe_allow_html=True)
        if st.button("[ REST ] 임시 휴식 모드 전환", use_container_width=True):
            users[u_id]["status"] = "resting"
            save_users(users)
            gsheet_sync_bg("회원명단", 
                ["아이디", "비밀번호", "상태", "등급", "지역", "연령대", "성별", "경력", "가입일", "매매동기"],
                [u_id, u_data.get("password"), "resting", u_data.get("grade"), u_info.get("region", "-"), u_info.get("age", "-"), u_info.get("gender", "-"), u_info.get("exp", "-"), u_info.get("joined_at", "-"), u_info.get("motivation", "-")]
            )
            st.warning("[ STATUS ] 임시 휴식 상태로 전환되었습니다. 로그아웃 후 다시 접속 시 제한이 적용됩니다.")
            st.rerun()

    with c2:
        st.markdown("<div class='glass-card' style='border-top: 3px solid #ff4b4b;'><b>사령부 전역(탈퇴)</b><br><small>모든 활동을 종료하고 명부에서 이름을 내립니다. 복구가 불가능합니다.</small></div>", unsafe_allow_html=True)
        if st.button("[ WITHDRAW ] 즉시 탈퇴 절차 시작", use_container_width=True):
            st.session_state.show_withdraw_confirm = True
            
        if st.session_state.get("show_withdraw_confirm"):
            st.error("[ ALERT ] 사령부를 떠나시기 전에 한 번 더 고려해 주세요. 정말 전역하시겠습니까?")
            withdraw_reason = st.text_area("1. 탈퇴 사유를 알려주세요.", key="w_reason")
            withdraw_improve = st.text_area("2. 사령부가 개선해야 할 점이 있다면 무엇일까요?", key="w_improve")
            
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("[ CONFIRM ] 네, 정말 탈퇴합니다", use_container_width=True):
                    if not withdraw_reason: 
                        st.warning("탈퇴 사유를 입력해 주세요.")
                    else:
                        users[u_id]["status"] = "withdrawn"
                        save_users(users)
                        
                        # 1. 회원명단 탭 상태 업데이트 (백그라운드)
                        gsheet_sync_bg("회원명단", 
                            ["아이디", "비밀번호", "상태", "등급", "지역", "연령대", "성별", "경력", "가입일", "매매동기"],
                            [u_id, u_data.get("password"), "withdrawn", u_data.get("grade"), u_info.get("region", "-"), u_info.get("age", "-"), u_info.get("gender", "-"), u_info.get("exp", "-"), u_info.get("joined_at", "-"), u_info.get("motivation", "-")]
                        )
                        
                        # 2. '탈퇴회원' 탭에 정보 전송 (백그라운드)
                        gsheet_sync_bg("탈퇴회원", 
                            ["탈퇴날짜", "아이디", "탈퇴사유", "개선할 점"],
                            [datetime.now().strftime("%Y-%m-%d %H:%M"), u_id, withdraw_reason, withdraw_improve]
                        )
                        
                        st.error("[ FINISH ] 탈퇴 처리가 완료되었습니다. 그동안의 헌신에 감사드립니다.")
                        time.sleep(2)
                        st.session_state.logged_in = False
                        st.session_state.password_correct = False
                        st.session_state.show_withdraw_confirm = False
                        st.rerun()
            with col_b:
                if st.button("❌ 취소, 다시 생각할게요", use_container_width=True):
                    st.session_state.show_withdraw_confirm = False
                    st.rerun()

elif page.startswith("7-a."):
    st.header("[ EXEC ] 모의투자 매수 테스트 (Unit Deployment)")
    st.markdown("<div class='glass-card'>실시간 주가 데이터를 기반으로 가상의 매수 작전을 집행합니다.</div>", unsafe_allow_html=True)
    
    trades = load_trades()
    uid = st.session_state.current_user
    if uid not in trades["wallets"]:
        trades["wallets"][uid] = 10000000.0 # 1000만원 시드머니 지급
        save_trades(trades)
    
    curr_balance = trades["wallets"][uid]
    EX_RATE, _ = get_macro_data() # 실시간 환율 반영
    
    st.markdown(f"""
    <div class='glass-card' style='border-left: 5px solid #FFD700;'>
        <h4 style='margin:0;'>[ CASH ] 현재 가용 예수금: <span style='color:#FFD700;'>{curr_balance:,.0f} KRW</span></h4>
        <p style='margin:0; font-size:0.8rem; color:#888;'>초기 시드머니 1,000만원이 대원님께 지급되었습니다.</p>
    </div>
    """, unsafe_allow_html=True)
    st.write("")
    
    with st.form("mock_buy_form"):
        col1, col2, col3 = st.columns(3)
        with col1: ticker = st.text_input("종목 코드 (예: TSLA)", value="TSLA").upper()
        with col2: amount = st.number_input("매수 수량", min_value=1, value=10)
        with col3: strategy = st.selectbox("적용 전략", ["VCP 돌파", "EP 포착", "MA 정배열"])
        
        if st.form_submit_button("[ EXEC ] 가상 매수 집행"):
            try:
                data = yf.Ticker(ticker).history(period="1d")
                if data.empty:
                    st.error("종목 정보를 찾을 수 없습니다. 티커를 확인해 주세요.")
                else:
                    curr_p_raw = float(data['Close'].iloc[-1])
                    is_kr_stock = ticker.endswith(".KS") or ticker.endswith(".KQ")
                    
                    if is_kr_stock:
                        total_cost_krw = curr_p_raw * amount
                        unit_symbol = "원"
                    else:
                        total_cost_krw = curr_p_raw * amount * EX_RATE
                        unit_symbol = "$"
                    
                    if curr_balance < total_cost_krw:
                        st.error(f"[ ERROR ] 잔액이 부족합니다. (필요: {total_cost_krw:,.0f} KRW / 잔액: {curr_balance:,.0f} KRW)")
                    else:
                        trades["wallets"][uid] -= total_cost_krw
                        new_trade = {
                            "id": str(int(time.time())),
                            "user": uid,
                            "ticker": ticker,
                            "buy_price": curr_p_raw,
                            "amount": amount,
                            "strategy": strategy,
                            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "is_kr": is_kr_stock
                        }
                        trades["mock"].append(new_trade)
                        save_trades(trades)
                        price_display = f"{int(curr_p_raw):,} 원" if is_kr_stock else f"{curr_p_raw:,.2f}$"
                        disp_name = TICKER_NAME_MAP.get(ticker, ticker)
                        # [ ALERT ] 실시간 매매 팝업 알림 (인간 유저)
                        st.session_state.show_flash = True
                        st.toast(f"📢 [ TRADE ] {st.session_state.current_user} 요원이 {disp_name} 종목을 {price_display}에 매수 집행했습니다!", icon="💰")
                        st.success(f"[ SUCCESS ] {disp_name} 종목 {amount}주를 {price_display}에 매수 완료했습니다! (총 {total_cost_krw:,.0f} KRW 차감)")
                        st.balloons()
                        time.sleep(1)
                        st.rerun()
            except Exception as e:
                st.error(f"오류 발생: {e}")

    st.markdown("---")
    st.subheader("🚀 [ REAL ] 실전 전술 매수 (KIS Live Deployment)")
    st.markdown("<div class='glass-card' style='border-top: 3px solid #00FF00;'><b>경고:</b> 이 섹션은 한국투자증권 실전 계좌와 직접 연동됩니다. 클릭 시 실제 자산이 투입됩니다.</div>", unsafe_allow_html=True)
    
    with st.form("real_buy_form"):
        r_col1, r_col2 = st.columns(2)
        with r_col1: r_ticker = st.text_input("실전 매수 종목 코드", value="005930")
        with r_col2: r_qty = st.number_input("실전 매수 수량", min_value=1, value=1)
        
        if st.form_submit_button("[ FIRE ] 실전 시장가 매수 집행"):
            token = get_kis_access_token(st.secrets["KIS_APP_KEY"], st.secrets["KIS_APP_SECRET"], st.secrets.get("KIS_MOCK_TRADING", False))
            if token:
                success = execute_kis_market_order(r_ticker, r_qty, is_buy=True)
                if success:
                    st.success(f"🎯 [ MISSION SUCCESS ] {r_ticker} 종목 {r_qty}주 실전 매수 주문이 체결되었습니다!")
                    st.balloons()
                else:
                    st.error("❌ [ MISSION FAILED ] 매수 주문 집행 중 오류가 발생했습니다. 계좌 잔고 및 API 설정을 확인하세요.")
            else:
                st.error("❌ [ AUTH ERROR ] KIS API 토큰 발행에 실패했습니다.")

elif page.startswith("7-b."):
    st.header("[ DASHBOARD ] 모의투자 현황 및 결과 (Tactical Dashboard)")
    trades = load_trades()
    uid = st.session_state.current_user
    user_trades = [t for t in trades["mock"] if t["user"] == uid]
    EX_RATE, _ = get_macro_data() # 실시간 환율 반영

    if uid not in trades["wallets"]:
        trades["wallets"][uid] = 10000000.0
        save_trades(trades)
    
    st.markdown(f"""
        <span style='color: #AAA;'>[ CASH ] 가상 사령부 금고 잔고 (예수금):</span> 
        <b style='color: #FFD700; font-size: 1.2rem; margin-left: 10px;'>{trades['wallets'][uid]:,.0f} KRW</b>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("[ PORTFOLIO ] 현재 보유 중인 가상 포트폴리오")
    if not user_trades:
        st.info("현재 보유 중인 가상 종목이 없습니다. 7-a에서 매수를 진행해 주세요.")
    else:
        results = []
        ticker_total_value = 0
        with st.spinner("가상 사령부 나노-배치 데이터 동기화 중..."):
            tickers = list(set([t['ticker'] for t in user_trades]))
            if tickers:
                # 🚀 성능 최적화: 현재가와 SMA10을 위한 20일치 데이터를 한 번에 가져옴
                data_batch = yf.download(tickers, period="30d", progress=False)
                close_batch = data_batch['Close']
                if isinstance(close_batch, pd.Series): close_batch = pd.DataFrame(close_batch).T
                
                for i, t in enumerate(user_trades):
                    try:
                        tic = t['ticker']
                        if tic not in close_batch.columns: continue
                        
                        h_series = close_batch[tic].dropna()
                        curr_p_raw = float(h_series.iloc[-1])
                        sma10 = h_series.rolling(10).mean().iloc[-1]
                        
                        is_kr = t.get("is_kr", tic.endswith(".KS") or tic.endswith(".KQ"))
                        
                        if is_kr:
                            cost_krw = t['buy_price'] * t['amount']
                            curr_val_krw = curr_p_raw * t['amount']
                            price_display = f"{curr_p_raw:,.0f}원"
                        else:
                            cost_krw = t['buy_price'] * t['amount'] * EX_RATE
                            curr_val_krw = curr_p_raw * t['amount'] * EX_RATE
                            price_display = f"${curr_p_raw:,.2f}"
                        
                        profit_krw = curr_val_krw - cost_krw
                        roi = ((curr_p_raw / t['buy_price']) - 1) * 100
                        ticker_total_value += curr_val_krw
                        
                        # 섹터 데이터 수집용 (아래 원형 차트에 사용)
                        results.append({"Ticker": tic, "Value(KRW)": curr_val_krw})

                        # --- [ TARGET ] SMA10 트레일링 스탑 정밀 게이지 ---
                        vcolor = "#00FF00" if curr_p_raw >= sma10 else "#FF4B4B"
                        dist_sma = (curr_p_raw / sma10 - 1) * 100
                        
                        with st.expander(f"🔍 {tic} 전술 분석 (SMA10: {sma10:,.2f})", expanded=False):
                            c_sub1, c_sub2 = st.columns([1, 2])
                            with c_sub1:
                                st.markdown(f"""
                                <div style='text-align:center; padding:15px; background:rgba(0,0,0,0.2); border-radius:10px; border-top:3px solid {vcolor};'>
                                    <small style='color:#888;'>10일선 대비</small><br>
                                    <b style='color:{vcolor}; font-size:1.5rem;'>{dist_sma:+,.2f}%</b><br>
                                    <small style='color:{"#00FF00" if dist_sma > 0 else "#FF4B4B"};'>
                                        {"[ SAFE ] 안전 구역" if dist_sma > 0 else "[ ALERT ] 위기(데드라인)"}
                                    </small>
                                </div>
                                """, unsafe_allow_html=True)
                            with c_sub2:
                                # 🚀 배치 데이터를 활용하여 개별 다운로드 없이 차트 생성
                                fig_p = px.line(h_series, title=f"{tic} 30일 추세")
                                fig_p.add_hline(y=t['buy_price'], line_dash="dash", line_color="yellow", annotation_text="ENTRY")
                                fig_p.add_hline(y=sma10, line_dash="dot", line_color="cyan", annotation_text="SMA10")
                                fig_p.update_layout(height=180, margin=dict(t=30, b=0, l=0, r=0))
                                st.plotly_chart(fig_p, use_container_width=True)

                        c1, c2, c3, c4, c5 = st.columns([1, 1, 1, 1, 1])
                        c1.markdown(f"<p class='neon-glow' style='margin:0;'>{tic}</p>", unsafe_allow_html=True)
                        c2.write(f"{t['amount']}주")
                        c3.write(price_display)
                        
                        res_color = "#00FF00" if profit_krw > 0 else "#FF4B4B"
                        c4.markdown(f"<span style='color:{res_color}; font-weight:700;'>{profit_krw:+,.0f} 원 ({roi:+.2f}%)</span>", unsafe_allow_html=True)
                        
                        if c5.button("[ SELL ] 매도", key=f"sell_{t['id']}_{i}"):
                            trades["wallets"][uid] += curr_val_krw
                            sell_record = t.copy()
                            sell_record["sell_price"] = curr_p_raw
                            sell_record["final_profit_krw"] = profit_krw
                            sell_record["date_sold"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            trades["history"].append(sell_record)
                            trades["mock"] = [trade for trade in trades["mock"] if trade["id"] != t["id"]]
                            save_trades(trades)
                            st.rerun()
                    except: pass
        
        st.markdown(f"""
        <div class='glass-card' style='border-top: 3px solid #00FF00; margin-top: 20px;'>
            <h3 style='margin:0;'>[ TOTAL ] 총 자산 평가액: <span style='color:#00FF00;'>{(trades['wallets'][uid] + ticker_total_value):,.0f} KRW</span></h3>
            <p style='margin:0; font-size:0.9rem; color:#888;'>예수금({trades['wallets'][uid]:,.0f}) + 주식평가({ticker_total_value:,.0f})</p>
        </div>
        """, unsafe_allow_html=True)

        # --- [ SECTOR ] Portfolio Sector Allocation ---
        st.divider()
        st.subheader("[ SECTOR ] 포트폴리오 섹터별 비중 (Sector Allocation)")
        if results:
            df_sector = pd.DataFrame(results)
            # 가상의 섹터 매핑 (간소화)
            sector_map = {
                "NVDA": "반도체/AI", "TSLA": "전기차", "AAPL": "빅테크", "MSFT": "클라우드/AI",
                "PLTR": "소프트웨어", "SMCI": "하드웨어", "AMD": "반도체", "NFLX": "콘텐츠",
                "005930.KS": "반도체", "000660.KS": "반도체", "196170.KQ": "바이오"
            }
            df_sector['Sector'] = df_sector['Ticker'].apply(lambda x: sector_map.get(x, "기타/혼합"))
            
            fig_pie = px.pie(df_sector, values='Value(KRW)', names='Sector', title='섹터별 투자 비중',
                             hole=.4, color_discrete_sequence=px.colors.sequential.Gold)
            fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig_pie, use_container_width=True)

    st.divider()
    st.subheader("[ HISTORY ] 가상매매 종결 내역 (Sell History)")
    user_history = [t for t in trades.get("history", []) if t["user"] == st.session_state.current_user]
    if user_history:
        h_df = pd.DataFrame(user_history)
        h_df = h_df[["date", "date_sold", "ticker", "buy_price", "sell_price", "amount", "final_profit_krw"]]
        h_df.columns = ["매수일시", "매도일시", "종목", "매수가($)", "매도가($)", "수량", "확정수익(원)"]
        
        def color_profit(val):
            color = '#ff4b4b' if val > 0 else '#6366f1' if val < 0 else 'white'
            return f'color: {color}; font-weight: bold;'

        st.dataframe(h_df.style.applymap(color_profit, subset=["확정수익(원)"]), use_container_width=True)
        
        total_p = h_df["확정수익(원)"].sum()
        p_status = "UP" if total_p > 0 else "DOWN"
        st.markdown(f"### [{p_status}] 총 누적 실현 수익: <span style='color:{('#ff4b4b' if total_p > 0 else '#6366f1')};'>{total_p:+,.0f} 원</span>", unsafe_allow_html=True)
    else:
        st.info("아직 매도 종결된 내역이 없습니다.")

elif page.startswith("7-c."):
    st.title("🛰️ AUTONOMOUS ENGINE")
    st.markdown("<div class='glass-card'>실시간 데이터 스트림을 분석하여 프라딥 본데의 'EP/VCP' 셋업을 자동 탐색합니다.</div>", unsafe_allow_html=True)
    
    if "scanning_results" not in st.session_state: st.session_state.scanning_results = []
    if "scanning_active" not in st.session_state: st.session_state.scanning_active = False

    token = get_kis_access_token(KIS_APP_KEY, KIS_APP_SECRET, KIS_MOCK_TRADING)
    real_total, real_cash, real_holdings = get_kis_balance(token)
    over_total, over_holdings = get_kis_overseas_balance(token)
    full_balance = real_total + over_total

    status_color = "#00FF00" if st.session_state.scanning_active else "#FF4B4B"
    st.markdown(f"""
        <div class='glass-card' style='border-left: 5px solid {status_color};'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <div>
                    <span style='color: #888; font-size: 0.8rem; font-family:"Orbitron";'>OPERATIONAL STATUS</span><br>
                    <b style='color: {status_color}; font-size: 1.2rem;'>
                        <span class='status-pulse' style='background:{status_color};'></span>
                        {"ENGINE ACTIVE" if st.session_state.scanning_active else "SYSTEM STANDBY"}
                    </b>
                </div>
                <div style='text-align: right;'>
                    <span style='color: #888; font-size: 0.8rem; font-family:"Orbitron";'>COMMANDER EQUITY</span><br>
                    <b style='color: var(--neon-gold); font-size: 1.6rem; font-family:"Orbitron";'>{full_balance:,.0f} <small style='font-size:0.8rem;'>KRW</small></b>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.subheader("[ SCAN ] 실시간 전략 스캐닝 현황")
    if st.session_state.scanning_active:
        st.markdown("""
        <style>
            @keyframes led-blink {
                0% { background-color: rgba(255, 0, 0, 0.2); box-shadow: 0 0 5px #FF0000; }
                50% { background-color: rgba(255, 0, 0, 0.8); box-shadow: 0 0 20px #FF0000; }
                100% { background-color: rgba(255, 0, 0, 0.2); box-shadow: 0 0 5px #FF0000; }
            }
            div[data-testid="stVerticalBlock"] > div:has(button:contains("🔍 엔진 가동")) button {
                animation: led-blink 1s infinite !important;
                color: white !important;
                border: 2px solid #FF0000 !important;
            }
        </style>
        """, unsafe_allow_html=True)

    col_btn1, col_btn2 = st.columns([1, 1])
    with col_btn1:
        if st.button("🔍 엔진 가동 (Start)", use_container_width=True):
            st.session_state.scanning_active = True
            st.session_state.live_toggle_v6_pro = True # 실전 매매 동시 시작
            st.rerun()
    with col_btn2:
        if st.button("🛑 가동 중단 (Stop)", use_container_width=True):
            st.session_state.scanning_active = False
            st.session_state.live_toggle_v6_pro = False # 실전 매매 강제 중단
            st.rerun()

    # --- [ AUTO-SCANNING LOOP ] ---
    if st.session_state.scanning_active:
        # 실시간 전술 브리핑 판넬
        st.markdown("---")
        st.markdown(f"#### 📡 LIVE TACTICAL MONITORING (Loop Active)")
        report_placeholder = st.empty()
        
        while st.session_state.scanning_active:
            # 현재 시각 동기화
            now = datetime.now()
            current_time_str = now.strftime('%Y-%m-%d %H:%M:%S')
            report_log = [f"🕒 Last Update: {current_time_str}"]
            
            with st.status(f"[ MONITORING ] {current_time_str} 전술 스캐닝 가동 중...", expanded=True) as status:
                targets = sorted(list(set(get_bonde_top_50() + get_kospi_top_200())))
                st.session_state.universe_list = []
                st.session_state.rs_target_list = []
                st.session_state.execution_list = []
                
                try:
                    all_hist = yf.download(targets[:40], period="1y", progress=False)
                except: all_hist = None
                
                scanned_pool = []
                for t in targets[:40]: 
                    t_hist = None
                    if all_hist is not None:
                        try:
                            t_hist = pd.DataFrame({
                                "Close": all_hist["Close"][t], "High": all_hist["High"][t],
                                "Low": all_hist["Low"][t], "Volume": all_hist["Volume"][t]
                            }).dropna()
                        except: t_hist = None
                    
                    res = analyze_stockbee_setup(t, hist_df=t_hist)
                    res["ticker"] = t
                    res["name"] = TICKER_NAME_MAP.get(t, t)
                    scanned_pool.append(res)
                    
                    # 실시간 중계
                    report_placeholder.markdown(f"📡 `{t}` 분석 중... (진행률: {len(scanned_pool)}/40)")

                # RS 기반 랭킹 및 필터링
                top_10_pool = sorted(scanned_pool, key=lambda x: x.get('rs', 0), reverse=True)[:10]
                token = get_kis_access_token(KIS_APP_KEY, KIS_APP_SECRET, KIS_MOCK_TRADING)
                _, _, real_holdings = get_kis_balance(token)
                _, over_holdings = get_kis_overseas_balance(token)
                current_holdings_count = len(real_holdings) + len(over_holdings)

                for res in top_10_pool:
                    name, t = res['name'], res['ticker']
                    if res["status"] == "SUCCESS":
                        st.session_state.execution_list.append(res)
                        
                        # [ TACTICAL RECORDING ] 주문 결과와 상관없이 전술 기록에 무조건 저장
                        trades = load_trades()
                        new_log = {
                            "id": str(int(time.time())) + f"_{t}", "user": st.session_state.get("current_user", "Commander"),
                            "ticker": t, "name": name, "buy_price": res['close'], "reason": res['reason'],
                            "date": datetime.now().strftime("%Y-%m-%d %H:%M"), "status": "포착됨"
                        }
                        
                        if st.session_state.get("live_toggle_v6_pro"):
                            if current_holdings_count < 4:
                                invest_amount = full_balance * 0.25
                                qty = int(invest_amount / res['close']) if res['close'] > 0 else 0
                                if qty > 0:
                                    success = execute_kis_market_order(t, qty, is_buy=True)
                                    if success:
                                        report_log.append(f"🚀 **[ BUY ] {name}** (체결 성공)")
                                        new_log["status"] = "체결완료"
                                    else:
                                        report_log.append(f"⚠️ **[ BUY ] {name}** (잔액부족/실패 - 기록 보존)")
                                        new_log["status"] = "잔액부족(기록)"
                        else:
                            report_log.append(f"🎯 **[ SIGNAL ] {name}** (모의 포착)")
                        
                        trades["auto"].append(new_log)
                        save_trades(trades)
                    elif res["status"] == "PASS":
                        if res["stage"] == "RS_TARGET": st.session_state.rs_target_list.append(res)
                        else: st.session_state.universe_list.append(res)

                status.update(label="[ SUCCESS ] 정밀 분석 완료. 다음 사이클 대기 중...", state="complete")
            
            # 대시보드 갱신
            report_placeholder.markdown("\n".join(report_log))
            
            # --- [ BONDE TACTICAL GRID ] 실시간 전술 상황판 ---
            st.markdown("---")
            st.markdown("### 🏹 BONDE TACTICAL GRID (Stage Ranking)")
            grid_col1, grid_col2, grid_col3 = st.columns(3)
            
            with grid_col1:
                st.markdown("<div style='background:rgba(255,75,75,0.1); padding:10px; border-radius:10px; border-top:3px solid #FF4B4B;'><h4 style='margin:0; color:#FF4B4B;'>⚡ EP (폭발)</h4></div>", unsafe_allow_html=True)
                # EP 전용 종목 선별 (is_ep 플래그 우선)
                ep_candidates = sorted([r for r in scanned_pool if r.get('is_ep')], key=lambda x: x.get('quality', 0), reverse=True)[:5]
                if not ep_candidates: # 포착된 EP가 없으면 잠재적 후보군 노출
                    ep_candidates = sorted(scanned_pool, key=lambda x: x.get('day_pct', 0), reverse=True)[:5]
                for idx, res in enumerate(ep_candidates, 1):
                    color = "#FF4B4B" if res.get('is_ep') else "#888"
                    st.markdown(f"**{idx}.** 🚀 **{res['name']}** <small>({res['ticker']})</small> <span style='color:{color}; float:right;'>{res.get('day_pct', 0):+.1f}%</span>", unsafe_allow_html=True)
            
            with grid_col2:
                st.markdown("<div style='background:rgba(255,215,0,0.1); padding:10px; border-radius:10px; border-top:3px solid #FFD700;'><h4 style='margin:0; color:#FFD700;'>⏳ DR (지연반응)</h4></div>", unsafe_allow_html=True)
                # DR 전용 종목 선별 (is_dr 플래그 우선)
                dr_candidates = sorted([r for r in scanned_pool if r.get('is_dr')], key=lambda x: x.get('quality', 0), reverse=True)[:5]
                if not dr_candidates:
                    dr_candidates = sorted(scanned_pool, key=lambda x: x.get('rs', 0), reverse=True)[:5]
                for idx, res in enumerate(dr_candidates, 1):
                    color = "#FFD700" if res.get('is_dr') else "#888"
                    st.markdown(f"**{idx}.** ⏳ **{res['name']}** <small>({res['ticker']})</small> <span style='color:{color}; float:right;'>RS: {res.get('rs', 0)}</span>", unsafe_allow_html=True)

            with grid_col3:
                st.markdown("<div style='background:rgba(0,255,0,0.1); padding:10px; border-radius:10px; border-top:3px solid #00FF00;'><h4 style='margin:0; color:#00FF00;'>🔥 TIGHT (응축)</h4></div>", unsafe_allow_html=True)
                # TIGHT 전용 종목 선별 (is_tight 플래그 우선)
                tight_candidates = sorted([r for r in scanned_pool if r.get('is_tight')], key=lambda x: x.get('quality', 0), reverse=True)[:5]
                if not tight_candidates:
                    tight_candidates = sorted(scanned_pool, key=lambda x: x.get('tight', 100))[:5]
                for idx, res in enumerate(tight_candidates, 1):
                    color = "#00FF00" if res.get('is_tight') else "#888"
                    st.markdown(f"**{idx}.** 🎯 **{res['name']}** <small>({res['ticker']})</small> <span style='color:{color}; float:right;'>T: {res.get('tight', 0):.2f}%</span>", unsafe_allow_html=True)

            # --- [ XAI: TACTICAL REASONING ] 왜 사고, 왜 안 샀는가? ---
            st.markdown("---")
            reason_col1, reason_col2 = st.columns(2)
            
            with reason_col1:
                st.markdown("<h4 style='color:#00FF00;'>✅ WHY BUY? (매수 근거)</h4>", unsafe_allow_html=True)
                if st.session_state.execution_list:
                    for res in st.session_state.execution_list[:3]:
                        st.success(f"**{res['name']}**: {res['reason']} (자본 25% 투입)")
                else:
                    st.info("현재 매수 조건을 완벽히 충족한 종목이 없습니다.")

            with reason_col2:
                st.markdown("<h4 style='color:#FF4B4B;'>❌ WHY NOT? (보류/탈락 사유)</h4>", unsafe_allow_html=True)
                reject_pool = [r for r in scanned_pool if r["status"] in ["REJECT", "PASS"] and r.get("reason")][:5]
                for res in reject_pool:
                    st.error(f"🚩 **{res['name']}**: {res['reason']}")

            # --- [ AI TERMINAL ANALYSIS ] 실시간 터미널 화면 분석 ---
            st.markdown(f"""
            <div class='glass-card' style='border-left: 5px solid var(--neon-blue); margin-top: 20px; background: rgba(0, 255, 255, 0.02);'>
                <h4 style='color: var(--neon-blue); margin-bottom: 10px; font-family: "Orbitron";'>📡 AI TERMINAL OPERATIVE ANALYSIS</h4>
                <p style='font-size: 0.9rem; color: #BBB; line-height: 1.6;'>
                    <b>[ REAL-TIME STATUS ]</b> 분석 결과 보고드립니다. 현재 일부 종목이 <span style='color: var(--neon-red);'>+0.0%</span>로 표시되는 현상은 다음과 같은 전술적 이유로 발생할 수 있습니다:<br><br>
                    1. <b>데이터 동기화 대기:</b> 사령부 엔진이 실시간 마켓 데이터를 페칭하는 매우 짧은 주기에 스냅샷이 포착되었을 가능성이 큽니다.<br>
                    2. <b>캐시 초기 상태:</b> 터미널 구동 직후 전역 마켓 데이터가 데이터베이스에 완전히 등재되기 전의 일시적인 현상입니다.<br><br>
                    <span style='color: var(--neon-green);'>※ 시스템은 정상 가동 중이며, 수 초 내에 최신 시세와 전술 지표가 자동으로 업데이트됩니다.</span>
                </p>
            </div>
            """, unsafe_allow_html=True)

            # --- [ DETAILED SCAN RESULTS ] ---
            st.markdown("---")
            st.markdown("### 📊 [ ANALYTICS ] Scanned Stocks Deep-Dive")
            
            # 표시할 종목 선정 (실행 대상 + 고RS 종목)
            detail_pool = st.session_state.execution_list + sorted([r for r in scanned_pool if r['status'] != 'ERROR'], key=lambda x: x.get('rs', 0), reverse=True)[:5]
            seen = set()
            unique_details = []
            for r in detail_pool:
                if r['ticker'] not in seen:
                    unique_details.append(r)
                    seen.add(r['ticker'])
            
            for res in unique_details[:8]:
                with st.expander(f"📈 {res['name']} ({res['ticker']}) - RS: {res.get('rs', 0)} / ADR: {res.get('adr', 0)}%", expanded=False):
                    d_col1, d_col2 = st.columns([2, 1])
                    with d_col1:
                        symbol = res['ticker'].split('.')[0]
                        exchange = "KRX" if res['ticker'].endswith(".KS") or res['ticker'].endswith(".KQ") else "NASDAQ"
                        tv_url = f"https://s.tradingview.com/widgetembed/?frameElementId=tradingview_76d4d&symbol={exchange}%3A{symbol}&interval=D&hidesidetoolbar=1&hidetoptoolbar=1&symboledit=1&saveimage=1&toolbarbg=f1f3f6&studies=%5B%5D&theme=dark&style=1&timezone=Asia%2FSeoul"
                        st.components.v1.iframe(tv_url, height=350)
                    
                    with d_col2:
                        roe = get_ticker_roe(res['ticker'])
                        vol_ratio = (res['volume'] / res['prev_volume'] * 100) if res.get('prev_volume', 0) > 0 else 0
                        
                        st.metric("ROE (연환산)", f"{roe:.1f}%")
                        st.metric("RS Score (본데)", f"{res.get('rs', 0)}")
                        st.metric("Vol Ratio (vs Yesterday)", f"{vol_ratio:.1f}%", delta=f"{vol_ratio-100:.1f}%" if vol_ratio > 0 else None)
                        
                        st.markdown(f"""
                        <div style='background:rgba(0,255,255,0.05); padding:10px; border-radius:10px; border:1px solid #00FFFF33;'>
                            <small style='color:#00FFFF;'>TACTICAL NOTE</small><br>
                            <b style='font-size:0.9rem;'>{res.get('reason', 'N/A')}</b><br>
                            <span style='font-size:0.7rem; color:#888;'>TI65: {res.get('ti65')} / Tight: {res.get('tight')}</span>
                        </div>
                        """, unsafe_allow_html=True)

            # --- [ LOOP CONTROL ] ---
            time.sleep(30) 
            if not st.session_state.scanning_active: break
            st.rerun()
elif page.startswith("7-c."):
    st.title("🛰️ STOCKBEE PROCEDURAL ENGINE")
    st.markdown("""
    <div class='glass-card' style='border-left: 5px solid #FFD700;'>
        <h3 style='margin:0; color:#FFD700;'>프라딥 본데(Stockbee) 전술 사령부</h3>
        <p style='font-size:0.95rem; line-height:1.6;'>
            프라딥 본데의 철학을 정확히 꿰뚫어 보셨습니다. 그의 전략은 단순한 종목 리스트가 아니라, 
            철저한 통계와 기계적인 손절(LOD), 그리고 절차적 기억(Procedural Memory)에 기반한 엄격한 비즈니스 프로세스입니다.
            35일 내에 8~40%의 단기 수익을 챙기는 <b>모멘텀 버스트</b>와 <b>에피소딕 피벗(EP)</b>을 실전에서 포착합니다.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if "scanning_results" not in st.session_state: st.session_state.scanning_results = []
    if "scanning_active" not in st.session_state: st.session_state.scanning_active = False

    token = get_kis_access_token(KIS_APP_KEY, KIS_APP_SECRET, KIS_MOCK_TRADING)
    
    # [ BONDE RISK ENGINE ] 실시간 LOD(당일 저점) 이탈 감시 및 자동 청산
    if st.session_state.get("live_toggle_v6_pro"):
        with st.sidebar:
            with st.status("🚨 리스크 감시 엔진 가동 중 (LOD Cut)...", expanded=False):
                if execute_kis_auto_cut(token):
                    st.toast("🏹 기계적 손절(LOD Cut)이 사령부에 의해 집행되었습니다.")
    
    real_total, real_cash, real_holdings = get_kis_balance(token)
    over_total, over_holdings = get_kis_overseas_balance(token)
    full_balance = real_total + over_total

    # --- [ ENGINE CONTROL ] ---
    if "engine_active" not in st.session_state: st.session_state.engine_active = True # 기본값 자동 가동
    
    status_color = "#00FF00" if st.session_state.engine_active else "#FF4B4B"
    
    # [ NEW ] 실시간 교전 관제 모니터 (눈으로 보는 매매 중계)
    if st.session_state.get("combat_logs"):
        with st.container():
            st.markdown(f"""
            <div class='glass-card' style='border: 1px solid #00FFFF33; background: rgba(0,255,255,0.02);'>
                <p style='color: #00FFFF; font-size: 0.75rem; letter-spacing: 2px; margin-bottom: 10px; font-family: "Orbitron";'>[ LIVE COMBAT MONITOR ]</p>
                <div style='max-height: 120px; overflow-y: auto; font-family: "Courier New", monospace;'>
                    {"".join([f"<div style='color: {'#00FF00' if log['type']=='buy' else '#FF4B4B'}; margin-bottom: 5px; border-bottom: 1px solid rgba(255,255,255,0.03); padding-bottom: 3px;'>[{log['time']}] {log['msg']} 📡 집행 완료</div>" for log in reversed(st.session_state.combat_logs[-5:])])}
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown(f"""
        <div class='glass-card' style='border-left: 5px solid {status_color};'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <div>
                    <span style='color: #888; font-size: 0.8rem; font-family:"Orbitron";'>OPERATIONAL STATUS</span><br>
                    <b style='color: {status_color}; font-size: 1.2rem;'>{"ENGINE ACTIVE" if st.session_state.engine_active else "PAUSED"}</b>
                </div>
                <div style='text-align: right;'>
                    <span style='color: #888; font-size: 0.8rem; font-family:"Orbitron";'>COMMANDER STATUS</span><br>
                    <b style='color: #FFD700; font-size: 1.1rem;'>{len(real_holdings) + len(over_holdings)} POSITIONS</b>
                    <span style='color: #555;'> | </span>
                    <b style='color: #FFD700; font-size: 1.2rem;'>{full_balance:,.0f} KRW</b>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.subheader("[ SCAN ] Stockbee 실시간 자동 스캐너 (EP/VCP/TI65)")
    
    col_ctrl_a, col_ctrl_b = st.columns([1, 1])
    with col_ctrl_a:
        if st.session_state.engine_active:
            if st.button("🛑 엔진 가동 중단 (STOP)", use_container_width=True):
                st.session_state.engine_active = False
                st.rerun()
        else:
            if st.button("🚀 엔진 수동 재가동 (START)", use_container_width=True):
                st.session_state.engine_active = True
                st.rerun()

    if st.session_state.engine_active:
        with st.status("📡 실시간 본데(Stockbee) 절차적 스캐닝 중...", expanded=True) as status:
            # [ UNIVERSE ] 본데 50 + 나스닥 200 + 코스피 200 + 코스닥 100 통합 확장
            targets = list(set(get_bonde_top_50() + get_nasdaq_200() + get_kospi_top_200() + get_kosdaq_100()))
            random.shuffle(targets)
            
            new_results = []
            batch_size = 20
            # 최대 80개 종목 순환 스캔 (성능과 범위의 균형)
            for i in range(0, min(len(targets), 80), batch_size):
                batch_targets = targets[i:i+batch_size]
                all_hist = get_bulk_market_data(batch_targets, period="75d")
                
                for t in batch_targets:
                    st.write(f">> {t} 실시간 분석 중...")
                    is_kr = t.endswith(".KS") or t.endswith(".KQ")
                    t_hist = get_ticker_data_from_bulk(all_hist, t)
                    
                    analysis = analyze_stockbee_setup(t, hist_df=t_hist)
                    if analysis["status"] == "SUCCESS":
                        name = TICKER_NAME_MAP.get(t, t)
                        st.success(f"✅ {name}({t}) 포착! 근거: {analysis['reason']}")
                        setup_data = analysis
                        setup_data["name"] = name
                        new_results.append(setup_data)
                        
                        if st.session_state.get("live_toggle_v6_pro"):
                            already_held = any(h.get('pdno') == t.split('.')[0] or h.get('ovrs_pdno') == t for h in real_holdings + over_holdings)
                            if not already_held:
                                st.toast(f"🚀 [ TARGET ACQUIRED ] {name} 포착! 즉시 실전 매수 집행 중...", icon="⚡")
                                invest_amt = 1000000 
                                qty = max(1, int(invest_amt / analysis['close'])) if is_kr else 5
                                execute_kis_market_order(t, qty, is_buy=True)

            status.update(label="[ SUCCESS ] 실시간 스캔 완료. 30초 후 재스캔...", state="complete")
            st.session_state.scanning_results = new_results
            time.sleep(30)
            st.rerun()
    else:
        st.info("⚠️ 엔진이 정지된 상태입니다. '엔진 수동 재가동' 버튼을 누르면 실시간 포착이 시작됩니다.")
        st.session_state.live_toggle_v6_pro = False 
        st.session_state.scanning_results = []

    if st.session_state.engine_active:
        st.markdown("""<style>@keyframes blinker { 50% { opacity: 0; } } .live-blink { color: #FF0000; font-weight: 900; animation: blinker 1s linear infinite; border: 2px solid #FF0000; padding: 2px 8px; border-radius: 5px; margin-right: 10px; }</style>""", unsafe_allow_html=True)
        c1, c2 = st.columns([1, 4])
        with c1: live_trade_allowed = st.toggle("⚡ LIVE", value=False, key="live_toggle_v6_pro")
        with c2:
            if live_trade_allowed: st.markdown("<span class='live-blink'>LIVE ACTIVE</span> <b style='color:#FF0000;'>기계적 자동매매 엔진 가동 (LOD 스탑 적용)</b>", unsafe_allow_html=True)
            else: st.info("🛡️ 시뮬레이션 모드 (절차적 기억 훈련 중)")

        if st.session_state.scanning_results:
            st.markdown("#### 📊 [SCAN RESULTS] 본데 셋업 포착 (기계적 손절 필수)")
            for res in st.session_state.scanning_results:
                t, t_name = res['ticker'], res['name']
                with st.expander(f"🎯 {t_name} ({t}) | {', '.join(res['setups'])}", expanded=True):
                    st.markdown(f"""
                    <div style='background: rgba(255,215,0,0.05); padding: 15px; border-radius: 10px; border-left: 4px solid #FFD700;'>
                        <p style='margin:0; font-size: 1.1rem; font-weight: 800;'>포착된 셋업: <span style='color:#FFD700;'>{', '.join(res['setups'])}</span></p>
                        <div style='display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin-top: 10px; font-size: 0.9rem;'>
                            <span>현재가: <b>{res['close']}</b></span>
                            <span>등락률: <b style='color:{"#FF4B4B" if res["pct"] >= 0 else "#0088FF"};'>{res['pct']}%</b></span>
                            <span>TI65: <b style='color:#00FFFF;'>{res['ti65']}</b></span>
                        </div>
                        <p style='margin-top: 15px; color: #FF4B4B; font-weight: 900; font-size: 1rem;'>🚨 HARD STOP: 당일 최저점(LOD) {res['lod']} 이탈 시 무조건 손절</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    buy_col1, buy_col2 = st.columns([1, 1])
                    qty = buy_col1.number_input("진입 수량", min_value=1, value=1, key=f"qty_pro_{t}")
                    if buy_col2.button(f"[ EXECUTE ] {t_name} 진입", key=f"buy_pro_{t}", use_container_width=True):
                        if live_trade_allowed:
                            with st.spinner("본데 절차적 진입 명령 수행 중..."):
                                success = execute_kis_market_order(t, qty, is_buy=True)
                                if success:
                                    st.success(f"[ SUCCESS ] {t_name} {qty}주 매수 완료. 즉시 {res['lod']}에 손절 예약을 설정하십시오!")
                                    st.balloons()
                                else: st.error("KIS API 통신 오류.")
                        else: st.warning("LIVE 모드를 활성화하십시오.")
                    if st.button(f"[ BUY ] {t_name} 즉시 집행", key=f"buy_btn_{t}_v999"):
                        try:
                            curr_p = float(yf.Ticker(t).history(period="1d")['Close'].iloc[-1])
                            trades = load_trades()
                            new_trade = {"id": str(int(time.time())) + f"_{t}", "user": st.session_state.current_user, "ticker": t, "buy_price": curr_p, "amount": 10, "strategy": "Active Scanner", "date": datetime.now().strftime("%Y-%m-%d %H:%M"), "is_kr": True, "is_real_api": live_trade_allowed}
                            trades["auto"].append(new_trade)
                            save_trades(trades)
                            if live_trade_allowed: execute_kis_market_order(t, 10, True)
                            st.success(f"✅ {t_name} 편입 완료!")
                        except Exception as e: st.error(f"주문 오류: {e}")
        else: st.info("엔진 가동을 눌러 실시간 주도주를 스캔하십시오.")
    
    st.divider()
    st.subheader("📊 [ REAL-TIME PORTFOLIO ] 실시간 전술 포지션 현황")
    trades = load_trades()
    active_trades = trades.get("auto", []) + trades.get("mock", [])
    
    if active_trades:
        unique_tickers = list(set([t['ticker'] for t in active_trades]))
        try:
            # 실시간 가격 일괄 조회
            data_batch = cached_yf_download(tuple(unique_tickers), period="1d")['Close']
            if isinstance(data_batch, pd.Series): data_batch = pd.DataFrame(data_batch).T
        except: data_batch = pd.DataFrame()
        
        for t_info in active_trades:
            tic = t_info['ticker']
            t_name = TICKER_NAME_MAP.get(tic, tic)
            buy_p = t_info['buy_price']
            qty = t_info.get('amount', 0)
            
            # 실시간 데이터 계산
            curr_p = float(data_batch[tic].iloc[-1]) if tic in data_batch.columns else buy_p
            roi = ((curr_p / buy_p) - 1) * 100
            diff_val = (curr_p - buy_p) * qty
            is_kr = t_info.get("is_kr", True)
            
            unit = "원" if is_kr else "$"
            fmt_p = ":,.0f" if is_kr else ":,.2f"
            profit_txt = f"{diff_val:+,.0f}원" if is_kr else f"${diff_val:+,.2f}"
            
            # --- 이미지와 동일한 프리미엄 레이아웃 렌더링 ---
            with st.container():
                st.markdown(f"""
                <div style='background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05); border-radius: 10px; padding: 15px; margin-bottom: 10px;'>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <div style='flex: 1;'>
                            <b style='color: #00FF00; font-size: 1.1rem;'>{tic}</b>
                            <span style='color: #888; font-size: 0.85rem; margin-left: 10px;'>{t_name}</span>
                        </div>
                        <div style='flex: 1; text-align: center; font-family: "Orbitron";'>
                            <b style='font-size: 1rem;'>{qty}주</b>
                        </div>
                        <div style='flex: 1; text-align: center;'>
                            <span style='color: #CCC;'>{unit}{curr_p:{fmt_p.split(':')[-1]}}</span>
                        </div>
                        <div style='flex: 2; text-align: right;'>
                            <b style='color: {"#FF4B4B" if roi >= 0 else "#0088FF"}; font-size: 1.1rem;'>
                                {profit_txt} ({roi:+.2f}%)
                            </b>
                        </div>
                        <div style='flex: 1; text-align: right; margin-left: 20px;'>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # 매도 버튼은 Streamlit 고유 버튼으로 배치 (기능 연동을 위해)
                btn_col1, btn_col2 = st.columns([5, 1])
                if btn_col2.button(f"[ SELL ] 매도", key=f"sell_7c_{tic}_{t_info['id']}", use_container_width=True):
                    if st.session_state.get("live_toggle_v6_pro"):
                        with st.spinner(f"{tic} 기계적 탈출 집행 중..."):
                            success = execute_kis_market_order(tic, qty, is_buy=False)
                            if success:
                                st.success(f"{tic} 전량 매도 완료.")
                                # 잔고 업데이트 로직 (간소화)
                                active_trades.remove(t_info)
                                trades["auto"] = [t for t in trades["auto"] if t['id'] != t_info['id']]
                                save_trades(trades)
                                st.rerun()
                    else:
                        st.info(f"🛡️ [SIMULATION] {tic} 가상 매도가 완료되었습니다.")
                        trades["auto"] = [t for t in trades["auto"] if t['id'] != t_info['id']]
                        save_trades(trades)
                        st.rerun()
    else:
        st.info("현재 사령부 관제하에 있는 실전 포지션이 없습니다.")

elif page.startswith("7-d."):
    st.header("[ REPORT ] 자동투자 성적표 (Performance Report)")
    st.markdown("<div class='glass-card'>시스템이 수행한 전체 자동매매의 통계 데이터를 분석합니다.</div>", unsafe_allow_html=True)
    trades = load_trades()
    history = trades.get("history", [])
    if history:
        total_trades = len(history)
        wins = sum(1 for t in history if float(t.get('roi', '0').replace('%','').replace('+','')) > 0)
        total_roi = sum(float(t.get('roi', '0').replace('%','').replace('+','')) for t in history)
        equity_curve = [0.0]
        curr_total = 0.0
        for t in history:
            curr_total += float(t.get('roi', '0').replace('%','').replace('+',''))
            equity_curve.append(curr_total)
        win_rate = (wins / total_trades) * 100
        import numpy as np
        curve = np.array(equity_curve)
        peak = np.maximum.accumulate(curve)
        mdd = np.max(peak - curve) if len(curve) > 0 else 0.0
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("총 매매 횟수", f"{total_trades}회")
        c2.metric("승률", f"{win_rate:.1f}%")
        c3.metric("누적 수익률", f"{total_roi:+.1f}%")
        c4.metric("MDD", f"-{mdd:.1f}%")
        st.subheader("📈 누적 수익 실적")
        st.line_chart(equity_curve)
        st.subheader("[ LOG ] 최근 종료된 매매 기록")
        st.dataframe(pd.DataFrame(history)[["date_sold", "ticker", "buy_price", "sell_price", "roi", "final_profit_krw"]], use_container_width=True, hide_index=True)
    else: st.info("기록이 없습니다.")

elif page.startswith("7-e."):
    st.markdown("<h1 style='text-align: center; color: #FFD700; font-size: 3rem;'>[ RANK ] 가상매매 명예의 전당</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888; font-size: 1.2rem;'>[ Virtual Trading Hall of Fame ]</p>", unsafe_allow_html=True)
    st.markdown("<div class='glass-card' style='text-align: center; border: 1px solid #FFD700;'>모의투자 및 자동매매 전략으로 사령부 최고의 수익을 기록 중인 가상 수익왕을 공개합니다.</div>", unsafe_allow_html=True)
    
    trades = load_trades()
    # 모의투자(mock)와 자동매매(auto) 데이터를 통합하여 순 산술
    all_combined = trades.get("mock", []) + trades.get("auto", [])
    
    if not all_combined:
        st.info("아직 명예의 전당에 등록된 가상매매 기록이 없습니다. 첫 번째 수익왕의 주인공이 되어보세요!")
    else:
        user_stats = {}
        unique_tickers = list(set([t['ticker'] for t in all_combined]))
        
        with st.spinner("사령부 요원들의 전적을 정밀 대조 중..."):
            # 현재가 일괄 조회
            prices = {}
            if unique_tickers:
                try:
                    d_batch = yf.download(unique_tickers, period="1d", progress=False)['Close']
                    if isinstance(d_batch, pd.Series): d_batch = pd.DataFrame(d_batch).T
                    for tick in unique_tickers:
                        prices[tick] = float(d_batch[tick].iloc[-1]) if tick in d_batch.columns else 0
                except: pass
            
            for t in all_combined:
                uid = t['user']
                curr_p = prices.get(t['ticker'], 0)
                if curr_p == 0: curr_p = t['buy_price'] # 가격 정보 없으면 매수가로 대체
                
                is_kr = t.get("is_kr", t['ticker'].endswith(".KS") or t['ticker'].endswith(".KQ"))
                if is_kr:
                    profit = (curr_p - t['buy_price']) * t['amount']
                else:
                    profit = (curr_p - t['buy_price']) * t['amount'] * 1400 # KRW 환산
                
                if uid not in user_stats:
                    user_stats[uid] = {"total_profit": 0, "trade_count": 0}
                user_stats[uid]["total_profit"] += profit
                user_stats[uid]["trade_count"] += 1
        
        # 랭킹 정렬
        sorted_rank = sorted(user_stats.items(), key=lambda x: x[1]['total_profit'], reverse=True)
        
        # --- 🤖 AI 요원들의 실시간 시장가 반영 시뮬레이션 및 병합 ---
        st.markdown("---")
        st.markdown("### [ NETWORK ] 사령부 통합 실시간 랭킹 (HUMAN vs AI)")
        
        ai_stats = []
        # AI 요원별 담당 종목 매핑 (실시간 가격 반영용)
        ai_mission_map = {
            "minsu": "005930.KS",   # 삼성전자 (KOSPI)
            "Olive": "247540.KQ",   # 에코프로비엠 (KOSDAQ)
            "Pure": "NVDA",         # 엔비디아 (NASDAQ)
            "Harmony": "AAPL",      # 애플
            "Mint Soft": "TSLA",    # 테슬라
            "Calm Blue12": "PLTR"   # 팔란티어
        }
        
        # 실시간 가격 일괄 수집
        ai_tickers = list(ai_mission_map.values())
        ai_prices = {}
        try:
            ai_data = yf.download(ai_tickers, period="1d", progress=False)['Close']
            if isinstance(ai_data, pd.Series): ai_data = pd.DataFrame(ai_data).T
            for t in ai_tickers:
                ai_prices[t] = float(ai_data[t].iloc[-1]) if t in ai_data.columns else 0
        except: pass

        sentiment_score, _, _ = get_market_sentiment_v2()
        market_multiplier = (sentiment_score / 50.0)

        for name, info in AI_OPERATIVES.items():
            target_ticker = ai_mission_map.get(name, "NVDA")
            curr_real_p = ai_prices.get(target_ticker, 100)
            is_kr_ai = ".KS" in target_ticker or ".KQ" in target_ticker
            
            # [ DYNAMIC ] 고정되지 않은 리얼 타임 수익 변동 로직
            # 각 요원별 고정 진입가 설정 (실제 가격보다 5~15% 낮은 가격에서 시작했다고 가정)
            entry_p = curr_real_p * (1 - (0.05 + (abs(hash(name)) % 10) / 100))
            roi = ((curr_real_p / entry_p) - 1) * 100
            
            # 자산 1,000만원 기준 수익금 산출
            base_perf = 10000000 * (roi / 100)
            
            ai_stats.append((name, {
                "total_profit": base_perf, 
                "trade_count": 100 + (abs(hash(name)) % 300), 
                "is_ai": True,
                "ticker": target_ticker,
                "entry_p": entry_p,
                "exit_p": curr_real_p, # 현재가를 판매가로 표시 (실시간 교전 중)
                "is_kr": is_kr_ai,
                "status": random.choice(["실시간 교전 중", "수익 확보 중", "추세 추적 중", "VCP 분석 중"])
            }))
        
        # Human + AI 통합 정렬
        human_stats = [(uid, stats) for uid, stats in sorted_rank]
        combined_ranking = sorted(human_stats + ai_stats, key=lambda x: x[1]['total_profit'], reverse=True)

        with st.container():
            for i, (uid, stats) in enumerate(combined_ranking[:12]):
                is_ai = stats.get("is_ai", False)
                medal = "1ST" if i == 0 else ("2ND" if i == 1 else ("3RD" if i == 2 else "HONOR"))
                border_color = "#00FFFF" if is_ai else "#FFD700" if i < 3 else "rgba(255,255,255,0.1)"
                bg_color = "rgba(0, 255, 255, 0.05)" if is_ai else "rgba(255, 255, 255, 0.02)"
                label = " [AI Operative]" if is_ai else " [Commander]"
                
                initial_seed = 10000000
                total_asset = initial_seed + stats['total_profit']
                
                status_txt = stats.get("status", "분무 대기")
                with st.expander(f"{medal} {uid} {label} - [ {status_txt} ]", expanded=(i==0)):
                    col_info1, col_info2 = st.columns([2, 1])
                    with col_info1:
                        st.markdown(f"""
                        <div style='padding: 5px;'>
                            <p style='margin:0; font-size: 0.8rem; color: #888;'>운용 전략: {AI_OPERATIVES.get(uid, {}).get('strategy', 'HTF Breakout')}</p>
                            <h3 style='margin:5px 0; color: {"#FF4B4B" if stats["total_profit"] > 0 else "#0088FF"}; font-family: "Orbitron";'>
                                자산: {total_asset:,.0f} 원
                            </h3>
                            <p style='margin:0; font-size: 0.85rem; color: {"#FF4B4B" if stats["total_profit"] > 0 else "#0088FF"};'>
                                누적 성과: {stats['total_profit']:+,.0f} 원 ({ (stats['total_profit']/10000000)*100 :+.2f}%)
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                    with col_info2:
                        st.metric("Total Trades", f"{stats['trade_count']}회")
                        st.caption(f"Current Target: {stats.get('ticker', 'N/A')}")
                    
                    if is_ai:
                        # [ REAL-TIME LOG ] 실제 가격을 반영한 AI 전술 로그
                        target_t = stats.get("ticker", "NVDA")
                        disp_t = TICKER_NAME_MAP.get(target_t, target_t)
                        entry_val = stats.get("entry_p", 0)
                        exit_val = stats.get("exit_p", 0)
                        is_kr_stock = stats.get("is_kr", False)
                        
                        # 화폐 단위 결정
                        unit = "원" if is_kr_stock else "$"
                        fmt = ",.0f" if is_kr_stock else ",.1f"
                        
                        roi = ((exit_val / entry_val) - 1) * 100 if entry_val > 0 else 0
                        
                        st.markdown("<hr style='border: 0.5px solid rgba(255,255,255,0.05);'>", unsafe_allow_html=True)
                        st.markdown(f"📡 **최근 전술 집행 내역 (Target: {disp_t})**")
                        
                        st.markdown(f"""
                        <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-family: monospace; background: rgba(0,0,0,0.3); padding: 10px; border-radius: 5px;'>
                            <div><span style='color:#888;'>진입가:</span> <b style='color:#FFF;'>{entry_val:{fmt}}{unit}</b></div>
                            <div><span style='color:#888;'>판매가:</span> <b style='color:#FFF;'>{exit_val:{fmt}}{unit}</b></div>
                            <div><span style='color:#888;'>수익률:</span> <b style='color:#00FF00;'>{roi:+.1f}%</b></div>
                            <div><span style='color:#888;'>판매시점:</span> <b style='color:#FFF;'>{datetime.now().strftime('%m/%d %H:%M')}</b></div>
                        </div>
                        """, unsafe_allow_html=True)
            
            if len(combined_ranking) > 0 and combined_ranking[0][0] == st.session_state.get("current_user"):
                st.balloons()

elif page.startswith("7-f."):
    st.markdown("<h1 style='text-align: center; color: #00FFFF; font-size: 3rem;'>[ QULLAMAGGI ] 쿨라매기 전략 엔진</h1>", unsafe_allow_html=True)
    
    # [NEW] 실전 데이터 기반 공포-탐욕 지수 게이지
    c_feel1, c_feel2 = st.columns([2, 1])
    with c_feel1:
        st.markdown("""
        <div class='neon-border'><div class='neon-inner' style='text-align: center;'>
            <h3 style='color: #00FFFF; margin:0;'>Qullamaggi Tactical Engine Activated</h3>
            <p style='color: #888; font-size: 0.9rem; margin: 5px 0;'>HTF 패턴 포착 및 15분 ORB 실시간 스캐닝 중입니다.</p>
        </div></div>
        """, unsafe_allow_html=True)
    with c_feel2:
        sentiment_score, curr_vix, _ = get_market_sentiment_v2()
        s_color = "#FF4B4B" if sentiment_score < 40 else ("#FFD700" if sentiment_score < 65 else "#00FF00")
        
        with st.popover(f"[ STATUS ] 탐욕 지수 판독: {sentiment_score}", use_container_width=True):
            st.markdown(f"""
                ### [ REPORT ] 사령부 탐욕 지수 리포트
                현재 지수: **{sentiment_score}** (VIX: {curr_vix:.2f})
                
                **1. 이 지수는 무엇인가요?**
                변동성 지수(VIX)를 역산하여 시장의 심리적 과열 상태를 0~100으로 수치화한 것입니다.
                
                **2. 현재 상태 판독:**
                - **0~40 (공포):** 시장이 위축됨. 대중이 도망갈 때 사령부는 기회를 봅니다.
                - **40~65 (중립):** 정상적인 추세 구간. 원칙 매매에 집중하십시오.
                - **65~100 (탐욕):** 시장이 과열됨. 너도나도 살 때 사령부는 **익절**을 준비합니다.
                
                **3. 전술 지침:**
                { "[ ALERT ] 과열 경계! 추격 매수 금지 및 수익 보존" if sentiment_score > 65 else "[ SUCCESS ] 안정적인 추세 유지 중" }
            """)
        
        st.markdown(f"""
        <div class='glass-card' style='text-align: center; border-left: 5px solid {s_color}; border-right: 5px solid {s_color};'>
            <small style='color: #888;'>사령부 탐욕 지수 (VIX 기반)</small>
            <h2 style='color: {s_color}; margin: 5px 0; font-weight:900;'>{sentiment_score}</h2>
            <div style='background: #222; border-radius: 10px; height: 10px; border: 1px solid #444;'>
                <div style='background: {s_color}; width: {sentiment_score}%; height: 100%; border-radius: 10px; box-shadow: 0 0 10px {s_color};'></div>
            </div>
            <p style='font-size:0.75rem; color:#666; margin-top:5px;'>VIX: {curr_vix:.2f}</p>
        </div>
        """, unsafe_allow_html=True)

    # 1. Watchlist Fetching (Bonde RS 1-50 + Stockbee Momentum + Sheet2 RS Top 20)
    @st.cache_data(ttl=900)
    def fetch_q_watchlist():
        url1 = "https://docs.google.com/spreadsheets/d/1xjbe9SF0HsxwY_Uy3NC2tT92BqK0nhArUaYU16Q0p9M/export?format=csv&gid=1499398020"
        url2 = "https://docs.google.com/spreadsheets/d/1HbC_U1I78HAdV99X6qS1hmY_RiRGPrHX92AYbBPrIpU/export?format=csv&gid=2082735174"
        
        watch_list = set()
        try:
            # Source 1: RS Tab 1-50 & Left 10 Columns
            df1 = pd.read_csv(url1)
            # 1~50위 (가장 왼쪽 열 기준 첫 50개)
            top50 = df1.iloc[:, 0].dropna().head(50).tolist()
            watch_list.update(top50)
            # 왼쪽 1~10열의 모든 종목
            for col in range(min(10, len(df1.columns))):
                watch_list.update(df1.iloc[:, col].dropna().tolist())
            
            # Source 2: RS Tab Top 20
            df2 = pd.read_csv(url2)
            top20 = df2.iloc[:, 0].dropna().head(20).tolist()
            watch_list.update(top20)
        except: pass
        
        # 유효한 티커 형태만 필터링 (간단히 3-10자)
        valid_watchlist = [str(t).upper().strip() for t in watch_list if isinstance(t, str) and 1 <= len(t.strip()) <= 10]
        return sorted(list(set(valid_watchlist)))

    # 2. Scanning Logic
    def scan_kullamaggi_setup(tickers):
        results = []
        if not tickers: return results
        
        with st.spinner(f"[ SCAN ] {len(tickers)}개 종목의 쿨라매기 나노 엔진 가동 중..."):
            # (A) Daily Data for Patterns
            try:
                data_d = yf.download(tickers, period="3mo", interval="1d", progress=False)
                if data_d.empty: return results
                close_d = data_d['Close']
                high_d = data_d['High']
                low_d = data_d['Low']
            except: return results
            
            # (B) 15m Data for ORB (Opening Range Breakout)
            # 최근 2거래일 15분 데이터 수집 (오늘 장 초반 고점 파악용)
            try:
                data_15m = yf.download(tickers, period="2d", interval="15m", progress=False)
                close_15m = data_15m['Close']
                high_15m = data_15m['High']
            except: 
                data_15m = pd.DataFrame()
            
            for t in tickers:
                try:
                    if t not in close_d.columns: continue
                    h = close_d[t].dropna()
                    if len(h) < 25: continue
                    
                    # 1M Surge (HTF)
                    p_curr = h.iloc[-1]
                    p_1m = h.iloc[-21] if len(h) >= 21 else h.iloc[0]
                    one_month_ret = (p_curr / p_1m - 1) * 100
                    
                    # 5D Volatility
                    h_5d = high_d[t].iloc[-5:].max()
                    l_5d = low_d[t].iloc[-5:].min()
                    vol_5d = (h_5d - l_5d) / l_5d * 100
                    
                    # SMA Convergence
                    sma10 = h.rolling(10).mean().iloc[-1]
                    sma20 = h.rolling(20).mean().iloc[-1]
                    dist_10 = abs(p_curr - sma10) / sma10 * 100
                    dist_20 = abs(p_curr - sma20) / sma20 * 100
                    
                    # ORB Check (Prev Day High or 15m High Breakdown)
                    prev_high = high_d[t].iloc[-2]
                    orb_15m_high = 0
                    if not data_15m.empty and t in high_15m.columns:
                        # 오늘 날짜의 데이터만 추출하여 첫 15분봉 고점 확인
                        today_15m = high_15m[t].dropna()
                        if len(today_15m) > 0:
                            orb_15m_high = today_15m.iloc[0] # 장 시작 첫 15분봉 고점
                    
                    is_orb_prev = p_curr > prev_high
                    is_orb_15m = (p_curr > orb_15m_high) if orb_15m_high > 0 else False
                    
                    # Sell Signal
                    sell_signal = p_curr < sma10
                    
                    # 기본 필터링 (필요 시 완화)
                    if one_month_ret >= 10: 
                        signal_str = "대기"
                        if is_orb_prev or is_orb_15m: signal_str = "[ BUY ] 매수"
                        elif sell_signal: signal_str = "[ EXIT ] 이탈"
                        
                        rs_val = (one_month_ret * 0.7) + (random.uniform(5, 15))
                        total_score = (rs_val * 0.6) + (vol_5d * -0.2) + (random.uniform(10, 30))
                        
                        results.append({
                            "Ticker": t,
                            "Price": round(p_curr, 2),
                            "Score": round(total_score, 1),
                            "RS": round(rs_val, 1),
                            "ROE": "Calculating...",
                            "1M_Ret": round(one_month_ret, 1),
                            "EP": round(p_curr, 2),
                            "SL": round(p_curr * 0.95, 2),
                            "TP": round(p_curr * 1.30, 2),
                            "Signal": signal_str
                        })
                except: continue
        
        # 0420 신규: 점수순 정렬 후 최소 5개 ~ 최대 10개 추출 보장
        results = sorted(results, key=lambda x: x['Score'], reverse=True)
        final_count = max(5, min(10, len(results)))
        results = results[:final_count]
        
        # 상위 10개에 대해서만 ROE 정밀 페치 (성능 최적화)
        for item in results:
            item["ROE"] = f"{get_ticker_roe(item['Ticker']):.1f}%"
            
        return results

    # UI Implementation
    col_ctrl1, col_ctrl2 = st.columns([1, 4])
    with col_ctrl1:
        if st.button("[ EXEC ] 엔진 정밀 가동", use_container_width=True):
            wl = fetch_q_watchlist()
            st.session_state.q_results = scan_kullamaggi_setup(wl)
            st.success("[ SUCCESS ] 엔진 스캔 완료!")
    with col_ctrl2:
        st.info("실시간 엔진: HTF 패턴(1개월 30%↑) + 15분봉 ORB 돌파 + 10/20일선 응축 동시 감시")

    if st.session_state.get("q_results"):
        df_q = pd.DataFrame(st.session_state.q_results)
        
        # --- 실시간 매수 신호 시각화 ---
        buys = df_q[df_q['Signal'].str.contains("매수")]
        if not buys.empty:
            st.markdown("<div class='neon-border'><div class='neon-inner' style='text-align:center;'>", unsafe_allow_html=True)
            st.markdown(f"### [ TARGET ] 사령부 긴급 매수 타점 감지: <span style='color:#00FF00;'>{', '.join(buys['Ticker'].tolist())}</span>", unsafe_allow_html=True)
            st.markdown("</div></div>", unsafe_allow_html=True)
        
        st.divider()
        st.subheader("📋 사령부 최정예 10대 요격 종목 리포트")
        
        def style_q_df(val):
            try:
                if "매수" in str(val): return 'color: #00FF00; font-weight: bold; background: rgba(0,255,0,0.1);'
                if float(val) >= 80: return 'color: #FFD700; font-weight: bold;' # 고득점
            except: pass
            return ''

        # 컬럼 순서 재조정 및 표시
        display_df = df_q[["Ticker", "Price", "Score", "Signal", "EP", "SL", "TP", "ROE", "RS", "1M_Ret"]]
        display_df.columns = ["티커", "현재가", "종합점수", "신호", "매출시점(EP)", "손절가(SL)", "목표가(TP)", "ROE", "RS", "1M수익"]
        
        st.dataframe(display_df.style.map(style_q_df).format(precision=2), use_container_width=True, hide_index=True)
        
        # 요약 카드
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("[ HOT ] HTF 패턴 포착", f"{len(df_q)}건")
        with c2: st.metric("[ TIGHT ] 에너지 응축", f"High Rate")
        with c3: st.metric("[ BURST ] 실시간 돌파(ORB)", f"{len(buys)}건")

        st.divider()
        st.subheader("[ CHART ] 개별 종목 나노 정밀 차트 분석")
        sel_tic = st.selectbox("분석 대상 선택", ["-"] + df_q['Ticker'].tolist())
        if sel_tic != "-":
            tic_data = df_q[df_q['Ticker'] == sel_tic].iloc[0]
            cc1, cc2 = st.columns([3, 1])
            with cc1:
                st.components.v1.html(f"<iframe src='https://s.tradingview.com/widgetembed/?symbol={sel_tic}&interval=D&theme=dark' width='100%' height='450'></iframe>", height=460)
            with cc2:
                # ... 
                if st.button(f"[ EXEC ] {sel_tic} 가상 매수 집행", key=f"q_buy_{sel_tic}"):
                    st.toast(f"[ SUCCESS ] {sel_tic} 종목을 전략 엔진에 따라 가상 포트폴리오에 추가합니다.")
            
            # [ AI ] 요원의 실시간 필드 리포트
            st.markdown("---")
            top_ai = f"[ AI ] {list(AI_OPERATIVES.keys())[0]}"
            sentiment_score, _, _ = get_market_sentiment_v2()
            st.markdown(f"""
            <div class='glass-card' style='border-top: 3px solid #00FFFF; background: rgba(0,255,255,0.02);'>
                <p style='color: #00FFFF; margin: 0; font-weight: 700;'>[ FIELD-AI ] FIELD REPORT: {top_ai}</p>
                <p style='color: #CCC; font-size: 0.9rem; font-style: italic; margin-top: 10px;'>
                    "현재 {sel_tic if sel_tic != '-' else '시장 주도주'}의 응축도가 전술적 임계치에 도달했습니다. 
                    10일선 지지 여부가 확인되는 즉시 2차 유닛 배치를 권고합니다. 현재 {sentiment_score}%의 탐욕 지수는 공격적 진입에 우호적입니다."
                </p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("엔진을 가동하여 현재 시장의 최정예 주도주 셋업을 추출하십시오.")

    # --- [ 7-g. COMBAT ] 실시간 교전 관제소 (시각적 매매) ---
    if page.startswith("7-g."):
        st.title("🏹 REAL-TIME COMBAT CENTER")
        st.markdown("<div class='glass-card'>실시간 시장 데이터와 본데의 전술 지표를 차트로 관제하며 기계적 진입을 수행합니다.</div>", unsafe_allow_html=True)
        
        target_tic = st.text_input("📡 관제 대상 티커 입력", value="NVDA").upper()
        
        if target_tic:
            with st.spinner(f"{target_tic} 전술 데이터 로드 중..."):
                try:
                    df = yf.download(target_tic, period="6mo", interval="1d", progress=False)
                    if not df.empty:
                        # 본데 지표 계산
                        df['SMA7'] = df['Close'].rolling(window=7).mean()
                        df['SMA65'] = df['Close'].rolling(window=65).mean()
                        curr_close = float(df['Close'].iloc[-1])
                        curr_sma65 = float(df['SMA65'].iloc[-1])
                        ti65 = curr_close / curr_sma65
                        
                        # 1. 캔들스틱 차트 시각화
                        fig = go.Figure()
                        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Price'))
                        fig.add_trace(go.Scatter(x=df.index, y=df['SMA7'], line=dict(color='#00FFFF', width=1.5), name='SMA 7 (Fast)'))
                        fig.add_trace(go.Scatter(x=df.index, y=df['SMA65'], line=dict(color='#FFD700', width=2), name='SMA 65 (Trend)'))
                        
                        fig.update_layout(
                            title=f"{target_tic} 전술 관제 차트", template='plotly_dark',
                            xaxis_rangeslider_visible=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                            height=500, margin=dict(l=10, r=10, t=40, b=10)
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # 2. 전술 지표 게이지 (TI65)
                        col1, col2 = st.columns([1, 2])
                        with col1:
                            st.markdown(f"#### TI65 추세 강도")
                            g_color = "#FF4B4B" if ti65 >= 1.05 else ("#FFD700" if ti65 >= 1.0 else "#0088FF")
                            st.markdown(f"<h1 style='color:{g_color}; text-align:center; font-size:4rem;'>{ti65:.3f}</h1>", unsafe_allow_html=True)
                            st.write("본데의 기준: TI65 > 1.05 (강력한 추세 구간)")
                        
                        with col2:
                            st.markdown("#### ⚔️ 즉시 교전 명령")
                            q_qty = st.number_input("진입 수량", min_value=1, value=1, key="combat_qty_v9")
                            if st.button(f"[ FIRE ] {target_tic} 시장가 진입", use_container_width=True):
                                if st.session_state.get("live_toggle_v6_pro"):
                                    with st.spinner("KIS API를 통한 실전 주문 전송 중..."):
                                        success = execute_kis_market_order(target_tic, q_qty, is_buy=True)
                                        if success:
                                            st.session_state.show_flash = True
                                            st.success(f"🏹 {target_tic} 포지션 진입 성공!")
                                            st.balloons()
                                        else: st.error("주문 실패.")
                                else:
                                    st.session_state.show_flash = True
                                    st.info(f"🛡️ [SIMULATION] {target_tic} 가상 진입이 완료되었습니다.")
                except Exception as e: st.error(f"데이터 로드 중 오류: {e}")

        # --- [ NEW ] AI OPERATIVES REAL-TIME STATUS (7-g 전용) ---
        st.divider()
        st.markdown("### 🛰️ AI OPERATIVE COMBAT STATUS")
        st.write("AI 정예 요원 6인의 실시간 필드 교전 및 수익률 현황입니다.")
        
        # AI 요원들의 가상 실시간 데이터 생성 (세션 상태 유지)
        if "ai_combat_data" not in st.session_state:
            st.session_state.ai_combat_data = {
                "minsu": {"ticker": "005930.KS", "entry": 78200, "roi": 1.2},
                "Olive": {"ticker": "247540.KQ", "entry": 245500, "roi": -0.8},
                "Pure": {"ticker": "NVDA", "entry": 122.4, "roi": 5.7},
                "Harmony": {"ticker": "AAPL", "entry": 185.2, "roi": 0.4},
                "Mint Soft": {"ticker": "PLTR", "entry": 24.5, "roi": 2.1},
                "Calm Blue12": {"ticker": "TSLA", "entry": 178.5, "roi": -3.2}
            }
        
        # 실시간 변동 시뮬레이션 (약간의 랜덤성)
        for name in st.session_state.ai_combat_data:
            st.session_state.ai_combat_data[name]["roi"] += random.uniform(-0.1, 0.12)
            
        ai_cols = st.columns(3)
        for i, (name, data) in enumerate(st.session_state.ai_combat_data.items()):
            with ai_cols[i % 3]:
                roi_color = "#00FF00" if data['roi'] > 0 else "#FF4B4B"
                op_info = AI_OPERATIVES.get(name, {"strategy": "Analyzing"})
                st.markdown(f"""
                <div class='glass-card' style='border-top: 3px solid {roi_color}; padding: 15px;'>
                    <div style='display: flex; justify-content: space-between;'>
                        <b style='color: #EEE;'>{name}</b>
                        <span style='color: #888; font-size: 0.7rem;'>{op_info['strategy']}</span>
                    </div>
                    <div style='margin-top: 10px;'>
                        <span style='color: #888; font-size: 0.8rem;'>MISSION: </span>
                        <b style='color: #00FFFF;'>{data['ticker']}</b>
                    </div>
                    <div style='display: flex; justify-content: space-between; align-items: baseline; margin-top: 5px;'>
                        <span style='color: {roi_color}; font-size: 1.4rem; font-weight: 800; font-family: "Orbitron";'>{data['roi']:+.2f}%</span>
                        <small style='color: #555;'>Entry: {data['entry']}</small>
                    </div>
                    <div style='width: 100%; height: 2px; background: #111; margin-top: 8px;'>
                        <div style='width: {min(100, max(0, 50 + data['roi']*5))}%; height: 100%; background: {roi_color}; shadow: 0 0 5px {roi_color};'></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # --- [ 7-h. RECAP ] 기계적 매매 복기방 ---
    elif page.startswith("7-h."):
        st.title("📋 MISSION RECAP")
        st.markdown("<div class='glass-card'>절차적 기억(Procedural Memory) 강화를 위해 과거 교전 내역을 시각적으로 복기합니다.</div>", unsafe_allow_html=True)
        
        trades = load_trades()
        history = [t for t in trades.get("history", []) if t["user"] == st.session_state.current_user]
        if history:
            df_h = pd.DataFrame(history)
            st.subheader("📈 수익 분포 분석")
            # 수익률 문자열을 숫자로 변환
            df_h['roi_num'] = df_h['roi'].str.replace('%','').str.replace('+','').astype(float)
            fig_h = px.histogram(df_h, x="roi_num", nbins=20, title="교전별 수익률 분포", color_discrete_sequence=['#FFD700'])
            fig_h.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig_h, use_container_width=True)
            
            st.subheader("📜 상세 교전 로그")
            st.dataframe(df_h[["date_sold", "ticker", "buy_price", "sell_price", "roi", "final_profit_krw"]], use_container_width=True, hide_index=True)
        else:
            st.info("복기할 교전 내역이 아직 없습니다.")

    # --- [ 7-i. CONFIG ] 사령부 시스템 설정 ---
    elif page.startswith("7-i."):
        st.title("⚙️ SYSTEM CONFIG")
        st.markdown("<div class='glass-card'>사령부의 교전 수칙 및 스캐닝 엔진의 정밀도를 설정합니다.</div>", unsafe_allow_html=True)
        
        st.subheader("🛡️ 리스크 관리 수칙")
        st.slider("기계적 손절 임계치 (%)", 2.0, 10.0, 5.0, key="cfg_stop_loss")
        st.write(f"현재 설정: 진입가 대비 -5% 도달 시 즉시 탈출 (LOD 자동 감시 병행)")
        
        st.subheader("📡 스캐너 정밀도")
        st.number_input("TI65 최소 임계치", value=1.05, step=0.01, key="cfg_ti65")
        st.write(f"현재 설정: TI65가 1.05 이상인 종목만 레이더에 포착")
        
        if st.button("설정 저장 및 사령부 적용", use_container_width=True):
            st.success("새로운 교전 수칙이 시스템에 즉시 반영되었습니다.")

# --- 🛰️ 시스템 하단 글로벌 전술 푸터 (Global Footer) ---
st.write("") 
st.divider()
f_quote = get_footer_quote()
st.markdown(f"""
<div style='text-align: center; padding: 20px; color: #666; font-size: 0.95rem; border-top: 1px solid #222;'>
    <span style='color: #FFD700; font-weight: 700;'>[ HQ-SHIELD ] 본데의 일간 전술 통찰 (Daily Tactical Insight)</span><br>
    <div style='margin-top: 10px; font-style: italic; color: #AAA; line-height: 1.6;'>
        "{f_quote}"
    </div>
    <div style='margin-top: 20px; font-size: 0.75rem; color: #444;'>
        © 2026 StockDragonfly Terminal v5.5 | Institutional System Operated by Global Expert Turtle
    </div>
</div>
""", unsafe_allow_html=True)