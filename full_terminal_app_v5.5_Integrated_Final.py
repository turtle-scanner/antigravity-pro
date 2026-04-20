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

# --- 🛰️ [GLOBAL HELPER] Safe Network Request ---
def safe_get(url, timeout=3):
    """지연 및 멈춤 방지를 위한 글로벌 네트워크 헬퍼"""
    try:
        resp = requests.get(url, timeout=timeout)
        if resp.status_code == 200: return resp
    except: pass
    return None

# --- 🤖 Rule-based Tactical Advisor (Platinum Engine) ---
def get_tactical_advice(tic, rs, roe):
    """종목의 RS와 ROE를 기반으로 전술적 조언 산출 (글로벌 스코프)"""
    advice = []
    if rs > 80: advice.append("🚀 강력한 Relative Strength 포착. 시장을 압도하는 주도주입니다.")
    elif rs > 50: advice.append("📈 양호한 추세 유지 중. 섹터 순환매 수급을 확인하십시오.")
    else: advice.append("⚠️ 추세가 다소 정체됨. 지지선 이탈 여부를 엄격히 감시하십시오.")
    
    if roe > 20: advice.append("💎 압도적 ROE. 기관이 가장 선호하는 우량 성장주 셋업입니다.")
    elif roe > 10: advice.append("✅ 견고한 펀더멘털. 실적 발표 전후 돌파 타점을 노리십시오.")
    
    # 보너스 스타일 조언
    quotes = [
        "시장이 혼란스러울수록 기본에 충실하십시오. VCP의 끝자락은 항상 조용합니다.",
        "손절은 패배가 아닌, 다음 승리를 위한 보험료입니다.",
        "거래량이 마를 때를 기다리십시오. 폭발은 고요함 속에서 시작됩니다."
    ]
    advice.append(f"\n💡 **Bonde's Insight:** {random.choice(quotes)}")
    return "\n".join(advice)

# --- 💾 데이터베이스 및 영구 보존 설정 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
def get_db_path(f): return os.path.join(BASE_DIR, f)

BACKUP_DIR = get_db_path("backups")

def auto_backup(file_path, force=False):
    if not os.path.exists(file_path): return
    try:
        fname = os.path.basename(file_path)
        os.makedirs(BACKUP_DIR, exist_ok=True)
        if not force and fname in ["attendance.csv", "chat_log.csv", "shared_comments.csv"]: return
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(BACKUP_DIR, f"{fname}_{timestamp}.bak")
        shutil.copy2(file_path, backup_path)
        if random.random() < 0.1:
            all_backups = sorted([os.path.join(BACKUP_DIR, f) for f in os.listdir(BACKUP_DIR) if f.startswith(fname)], key=os.path.getmtime)
            if len(all_backups) > 30:
                for old_f in all_backups[:-30]: os.remove(old_f)
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


def safe_read_csv(file_path, columns=None):
    if not os.path.exists(file_path): return pd.DataFrame(columns=columns) if columns else pd.DataFrame()
    try:
        df = pd.read_csv(file_path, encoding='utf-8-sig', on_bad_lines='skip')
        if columns:
            for col in columns:
                if col not in df.columns: df[col] = "nan"
            return df[columns]
        return df
    exceptException as e:
        st.warning(f"⚠️ 데이터 파일([.csv]) 읽기 시도 중 지연이 발생하고 있습니다. 잠시 후 자동 복구됩니다. ({os.path.basename(file_path)})")
        return pd.DataFrame(columns=columns) if columns else pd.DataFrame()

def safe_write_csv(df, file_path, mode='w', header=True, backup=False):
    try:
        if backup and os.path.exists(file_path): auto_backup(file_path)
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        if mode == 'a' and os.path.exists(file_path): header = False
        df.to_csv(file_path, index=False, encoding='utf-8-sig', mode=mode, header=header)
        return True
    except: return False

def safe_save_json(data, file_path):
    try:
        if os.path.exists(file_path): auto_backup(file_path)
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    except: return False

def safe_load_json(file_path, default=None):
    if not os.path.exists(file_path): return default if default is not None else {}
    try:
        with open(file_path, "r", encoding="utf-8") as f: return json.load(f)
    except: return default if default is not None else {}

# 🛡️ 영구 백업용 구글 시트 URL
USERS_SHEET_URL = st.secrets.get("USERS_SHEET_URL", "https://docs.google.com/spreadsheets/d/1HbC_U1I78HAdV99X6qS1hmY_RiRGPrHX92AYbBPrIpU/export?format=csv&gid=1180564490")
ATTENDANCE_SHEET_URL = st.secrets.get("ATTENDANCE_SHEET_URL", "https://docs.google.com/spreadsheets/d/1HbC_U1I78HAdV99X6qS1hmY_RiRGPrHX92AYbBPrIpU/export?format=csv&gid=0")
CHAT_SHEET_URL = st.secrets.get("CHAT_SHEET_URL", "https://docs.google.com/spreadsheets/d/1HbC_U1I78HAdV99X6qS1hmY_RiRGPrHX92AYbBPrIpU/export?format=csv&gid=2147147361")
VISITOR_SHEET_URL = st.secrets.get("VISITOR_SHEET_URL", "https://docs.google.com/spreadsheets/d/1HbC_U1I78HAdV99X6qS1hmY_RiRGPrHX92AYbBPrIpU/export?format=csv&gid=621380834")
WITHDRAWN_SHEET_URL = st.secrets.get("WITHDRAWN_SHEET_URL", "https://docs.google.com/spreadsheets/d/1HbC_U1I78HAdV99X6qS1hmY_RiRGPrHX92AYbBPrIpU/export?format=csv&gid=1873947039")
# 🌍 전역 공지 및 UI 레이아웃 설정
NOTICE_SHEET_URL = st.secrets.get("NOTICE_SHEET_URL", "https://docs.google.com/spreadsheets/d/1HbC_U1I78HAdV99X6qS1hmY_RiRGPrHX92AYbBPrIpU/export?format=csv&gid=1619623253")

TICKER_NAME_MAP = {
    "NVDA": "엔비디아", "TSLA": "테슬라", "AAPL": "애플", "MSFT": "마이크로소프트", "PLTR": "팔란티어", "SMCI": "슈퍼마이크로", 
    "AMD": "AMD", "META": "메타", "GOOGL": "구글", "AVGO": "브로드컴", "CRWD": "크라우드스트라이크", "005930.KS": "삼성전자", 
    "000660.KS": "SK하이닉스", "196170.KQ": "알테오젠", "042700.KS": "한미반도체", "105560.KS": "KB금융", "055550.KS": "신한지주",
    "005490.KS": "POSCO홀딩스", "000270.KS": "기아", "066570.KS": "LG전자", "035720.KS": "카카오", "035420.KS": "NAVER",
    "005380.KS": "현대차", "000810.KS": "삼성화재", "NFLX": "넷플릭스", "MSTR": "마이크로스트래티지", "COIN": "코인베이스", 
    "MARA": "마라톤디지털", "PANW": "팔로알토", "SNOW": "스노우플레이크", "STX": "씨게이트", "WDC": "웨스턴디지털"
}

REVERSE_TICKER_MAP = {v: k for k, v in TICKER_NAME_MAP.items()}

def resolve_ticker(query):
    query = query.strip()
    if query.isdigit() and len(query) == 6: return query + ".KS"
    if query in TICKER_NAME_MAP: return query
    if query.upper() in TICKER_NAME_MAP: return query.upper()
    if query in REVERSE_TICKER_MAP: return REVERSE_TICKER_MAP[query]
    return query.upper()

# --- 🛰️ 거시지표 매크로 바 ---
@st.cache_data(ttl=600)
def get_macro_data():
    try:
        m_data = yf.download(["USDKRW=X", "^TNX"], period="5d", progress=False)['Close']
        rate_series = m_data["USDKRW=X"].dropna()
        rate = float(rate_series.iloc[-1]) if not rate_series.empty else 1400.0
        yield_series = m_data["^TNX"].dropna()
        yield10y = float(yield_series.iloc[-1]) if not yield_series.empty else 4.3
        return rate, yield10y
    except: return 1400.0, 4.3

def get_macro_indicators():
    rate, yield10y = get_macro_data()
    return f"💵 USD/KRW: {rate:,.1f}원 | 🏦 US 10Y Yield: {yield10y:.2f}%"

@st.cache_data(ttl=300)
def load_users():
    users = {}
    if os.path.exists(USER_DB_FILE):
        try:
            with open(USER_DB_FILE, "r", encoding="utf-8") as f: users = json.load(f)
        except: pass
    if USERS_SHEET_URL:
        try:
            response = safe_get(USERS_SHEET_URL, timeout=4)
            if response:
                import io
                df_u = pd.read_csv(io.StringIO(response.text))
                new_users_found = False
                for _, row in df_u.iterrows():
                    try:
                        u_id = str(row.get('아이디', row.get('ID', ''))).strip()
                        if not u_id or u_id == 'nan' or u_id == '': continue
                        new_users_found = True
                        users[u_id] = {
                            "password": str(row.get('비밀번호', u_id)),
                            "status": str(row.get('상태', 'approved')),
                            "grade": str(row.get('등급', '회원')),
                            "info": {
                                "region": row.get('지역', '-'),
                                "age": row.get('연령대', row.get('연령', '-')),
                                "gender": row.get('성별', '-'),
                                "motivation": row.get('매매동기', row.get('매매 동기', '-')),
                                "exp": row.get('경력', '-'),
                                "joined_at": row.get('가입일', row.get('합류일', '-'))
                            }
                        }
                    except: continue
                if new_users_found:
                    with open(USER_DB_FILE, "w", encoding="utf-8") as f: json.dump(users, f, ensure_ascii=False, indent=4)
        except: pass
    if "cntfed" not in users:
        users["cntfed"] = {"password": "cntfed", "status": "approved", "grade": "방장"}
    users["cntfed"]["grade"] = "방장"
    users["cntfed"]["status"] = "approved"
    return users

def hash_password(password): return hashlib.sha256(password.encode()).hexdigest()

def save_users(users):
    safe_save_json(users, USER_DB_FILE)
    load_users.clear()

@st.cache_data(ttl=600)
def fetch_gs_attendance():
    try:
        response = safe_get(ATTENDANCE_SHEET_URL, timeout=4)
        if response:
            import io
            df = pd.read_csv(io.StringIO(response.text))
            df = df.rename(columns={
                '시간': '시간', 'date': '시간', '날짜': '시간', '일시': '시간',
                '아이디': '아이디', 'id': '아이디', 'ID': '아이디', 'User': '아이디',
                '인사': '인사', '한줄인사': '인사', '내용': '인사', '댓글': '인사',
                '등급': '등급', 'grade': '등급', 'Level': '등급'
            })
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
    exceptException as e: print(f"DEBUG: Visitor Fetch Error: {e}")
    return pd.DataFrame()

@st.cache_data(ttl=86400)
def get_ticker_roe(tic):
    try:
        tk = yf.Ticker(tic)
        info = tk.info
        return info.get('returnOnEquity', 0) * 100
    except: return 0

@st.cache_data(ttl=900)
def fetch_gs_notices():
    try:
        response = safe_get(NOTICE_SHEET_URL, timeout=4)
        if response:
            import io
            df = pd.read_csv(io.StringIO(response.text))
            if not df.empty:
                last_notice = df.iloc[-1]
                return {"title": str(last_notice.get("제목", "📢 사령부 보안 업데이트 안내")), "content": str(last_notice.get("내용", "쾌적한 서비스 제공을 위해 엔진을 전면 개편하였습니다."))}
    except: pass
    return {
        "title": "🛡️ 사령부 고정 공지", 
        "content": "개인정보 보호 및 시스템 고도화를 위해 서버 업데이트를 완료했습니다. 초기 비밀번호는 1234입니다. [계정 보안 설정]에서 변경하십시오."
    }

@st.cache_data
def get_cached_bg_b64():
    if os.path.exists("StockDragonfly2.png"):
        with open("StockDragonfly2.png", "rb") as imm: return base64.b64encode(imm.read()).decode()
    elif os.path.exists("StockDragonfly.png"):
        with open("StockDragonfly.png", "rb") as imm: return base64.b64encode(imm.read()).decode()
    return ""

st.markdown("""
<style>
    .stApp { background: radial-gradient(circle at center, #1a1a2e 0%, #0f0f12 100%); background-attachment: fixed; }
    .glass-card { background: rgba(255, 255, 255, 0.03) !important; backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.05) !important; border-radius: 15px; padding: 20px; margin-bottom: 20px; box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37); }
    .main-title { background: linear-gradient(to right, #FFD700, #FFA500); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 900; text-align: center; }
</style>
""", unsafe_allow_html=True)

ZONE_CONFIG = {
    "🏰 1. 본부 사령부": ["1-a. 👑 관리자 승인 센터", "1-b. 🎖️ HQ 인적 자원 사령부", "1-c. 🔐 계정 보안 및 관리(18.)", "1-d. 🌙 탈퇴/휴식 신청"],
    "📡 2. 시장 상황실": ["2-a. 📈 마켓 트렌드 요약", "2-b. 🗺️ 실시간 히트맵", "2-c. 🌡️ 시장 심리 게이지", "2-d. 🏛️ 제작 동기"],
    "🏹 3. 주도주 추격대": ["3-a. 🎯 주도주 타점 스캐너", "3-b. 🚀 주도주 랭킹 TOP 50", "3-c. 📊 본데 감시 리스트", "3-d. 📉 산업동향(TOP 10)", "3-e. 🌡️ RS 강도(TOP 10)"],
    "🛡️ 4. 전략 및 리스크": ["4-a. 💎 프로 분석 리포트", "4-b. 🧮 리스크 계산기", "4-c. 🛡️ 리스크 방패"],
    "🏛️ 5. 마스터 훈련소": ["5-a. 🐝 본데는 누구인가?", "5-b. 📚 주식공부방(차트)", "5-c. 🛰️ 나노바나나 레이더", "5-d. 📝 정기 승급 시험 안내", "5-e. 🤑 실전 익절 자랑방", "5-f. 🩹 손실 위로 및 복기방"],
    "☕ 6. 안티그래비티 광장": ["6-a. 📌 출석체크(오늘한줄)", "6-b. 💬 소통 대화방", "6-c. 🤝 방문자 인사 신청"],
    "🤖 7. 자동매매 사령부": ["7-a. 🚀 모의투자 매수테스트", "7-b. 📊 모의투자 현황/결과", "7-c. ⚙️ 자동매매 전략엔진", "7-d. 📈 자동투자 성적표", "7-e. 🏆 사령부 명예의 전당"]
}

def load_trades():
    data = safe_load_json(TRADES_DB, {"mock": [], "auto": [], "history": [], "wallets": {}})
    if "wallets" not in data: data["wallets"] = {}
    return data

def save_trades(trades): safe_save_json(trades, TRADES_DB)

def gsheet_sync(sheet_name, headers, values):
    payload = {"sheetName": sheet_name, "headers": headers, "values": values}
    try:
        resp = requests.post(MASTER_GAS_URL, json=payload, timeout=7)
        return resp
    except: return None

def gsheet_sync_bg(sheet_name, headers, values):
    threading.Thread(target=gsheet_sync, args=(sheet_name, headers, values), daemon=True).start()

st.set_page_config(page_title="StockDragonfly Pro", page_icon="🔴", layout="wide")

if "is_mobile" not in st.session_state: st.session_state.is_mobile = False

bg_b64 = ""
logo_b64 = ""
if os.path.exists("StockDragonfly2.png"):
    with open("StockDragonfly2.png", "rb") as imm: bg_b64 = base64.b64encode(imm.read()).decode()
elif os.path.exists("StockDragonfly.png"):
    with open("StockDragonfly.png", "rb") as imm: bg_b64 = base64.b64encode(imm.read()).decode()

if os.path.exists("StockDragonfly.png"):
    with open("StockDragonfly.png", "rb") as f: logo_b64 = base64.b64encode(f.read()).decode()

st.markdown(f"""
    <style>
    .stApp {{ background-color: #000; {f'background-image: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), url("data:image/png;base64,{bg_b64}");' if bg_b64 else ""} background-size: cover; background-position: center; background-attachment: fixed; }}
    [data-testid="stSidebar"] {{ background-color: rgba(2,2,2,0.98) !important; border-right: 1px solid #FFD70022; backdrop-filter: blur(40px); }}
    .main-title {{ font-family: 'Outfit', sans-serif; background: linear-gradient(to right, #FFD700, #FFF, #FFD700); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 900; font-size: 4.5rem; text-align: center; margin-bottom: 0px; filter: drop-shadow(0 0 20px rgba(255,215,0,0.5)); }}
    h1, h2 {{ color: #FFD700 !important; font-weight: 900; text-shadow: 0 0 15px rgba(255,215,0,0.3); }}
    .glass-card {{ background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 18px; padding: 25px; backdrop-filter: blur(20px); margin-bottom: 30px; transition: all 0.5s cubic-bezier(0.23, 1, 0.32, 1); position: relative; overflow: hidden; }}
    .glass-card:hover {{ border-color: #FFD70066; transform: translateY(-8px) scale(1.01); box-shadow: 0 20px 40px rgba(0,0,0,0.6), 0 0 20px rgba(255,215,0,0.1); }}
    @keyframes pulse-glow {{ 0% {{ box-shadow: 0 0 10px rgba(0,255,0,0.2); opacity: 0.8; }} 50% {{ box-shadow: 0 0 30px rgba(0,255,0,0.5); opacity: 1; }} 100% {{ box-shadow: 0 0 10px rgba(0,255,0,0.2); opacity: 0.8; }} }}
    .status-pulse {{ border: 1px solid #00FF0044; animation: pulse-glow 2s infinite; }}
    @keyframes ticker {{ 0% {{ transform: translateX(100%); }} 100% {{ transform: translateX(-100%); }} }}
    .ticker-wrap {{ overflow: hidden; background: rgba(0,0,0,0.6); white-space: nowrap; padding: 12px 0; border-bottom: 2px solid rgba(255,215,0,0.2); margin-bottom: 20px; backdrop-filter: blur(15px); }}
    .ticker-content {{ display: inline-block; animation: ticker 250s linear infinite; color: #FFD700; font-size: 0.95rem; font-weight: 600; animation-delay: 1s; }}
    .ticker-item {{ margin: 0 40px; display: inline-block; }}
    [data-testid="stSidebarNav"] {{ display: none; }}
    </style>
""", unsafe_allow_html=True)

if "password_correct" not in st.session_state: st.session_state["password_correct"] = False
if not st.session_state["password_correct"]:
    c1, m, c2 = st.columns([1, 2, 1])
    with m:
        st.markdown("<div class='main-title'>StockDragonfly</div>", unsafe_allow_html=True)
        if logo_b64: st.markdown(f'<img src="data:image/png;base64,{logo_b64}" style="width:100%; border-radius:15px; margin-bottom:20px;">', unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["🚀 Log-In", "📝 Join"])
        with tab1:
            l_id = st.text_input("아이디", key="l_id")
            l_pw = st.text_input("비밀번호", type="password", key="l_pw")
            if st.button("Terminal Operation Start", use_container_width=True):
                users = load_users()
                if l_id in users:
                    u = users[l_id]
                    if u.get("password") == l_pw or u.get("password") == hash_password(l_pw):
                        st.session_state["password_correct"] = True
                        st.session_state.current_user = l_id
                        st.rerun()
                    else: st.error("❌ 비밀번호 오류")
                else: st.error("❌ 아이디 오류")
    st.stop()

with st.sidebar:
    if logo_b64: st.markdown(f'<img src="data:image/png;base64,{logo_b64}" style="width:100%; border-radius:10px; margin-bottom:10px;">', unsafe_allow_html=True)
    st.markdown("<p style='color:#FF914D; font-size:1.5rem; font-weight:900;'>🔴 StockDragonfly v9.9</p>", unsafe_allow_html=True)
    macro_info = get_macro_indicators()
    st.markdown(f"<div style='background: rgba(255,255,255,0.05); padding: 5px; border-radius: 5px; border: 1px solid #333; text-align: center; font-size: 0.75rem; color: #AAA; margin-bottom: 20px;'>{macro_info}</div>", unsafe_allow_html=True)
    
    for zone_name, missions in ZONE_CONFIG.items():
        with st.expander(zone_name, expanded=(st.session_state.get("page") in missions)):
            for m in missions:
                if st.button(m, key=f"nav_{m}", use_container_width=True):
                    st.session_state.page = m
                    st.rerun()

now_kst = datetime.now(pytz.timezone('Asia/Seoul'))
page = st.session_state.get("page", "6-a. 📌 출석체크(오늘한줄)")

# --- 🐉 전광판 티커 ---
@st.cache_data(ttl=300)
def get_ticker_tape():
    watch = {"^IXIC": "NASDAQ", "NVDA": "NVDA", "TSLA": "TSLA", "^KS11": "KOSPI", "BTC-USD": "BTC"}
    items = []
    try:
        data = yf.download(list(watch.keys()), period="2d", progress=False)['Close']
        for s, n in watch.items():
            try:
                c = ((data[s].iloc[-1] / data[s].iloc[-2]) - 1) * 100
                items.append(f"<span class='ticker-item'>{n} {data[s].iloc[-1]:,.1f} <span style='color:{'#00FF00' if c>=0 else '#FF4B4B'};'>{c:+.2f}%</span></span>")
            except: pass
    except: pass
    return "".join(items)

ticker_html = get_ticker_tape()
st.markdown(f"<div class='ticker-wrap'><div class='ticker-content'>{ticker_html * 10}</div></div>", unsafe_allow_html=True)

# --- 🛰️ 마켓 게이지 헤더 ---
st.markdown("""<div class='status-pulse' style='background: rgba(0,0,0,0.85); border: 2px solid #FFD700; border-radius: 15px; padding: 25px; text-align: center; margin-bottom: 25px;'><h1 style='color: #00FF00; margin: 0; font-size: 2.2rem;'>🟢 GREEN MARKET ACTIVE</h1><p style='color: #FFD700; font-size: 1.1rem; margin-top: 10px; font-weight: 700;'>🛡️ 사령부 상태: 매수 윈도우 개방</p></div>""", unsafe_allow_html=True)

# --- BONDE WISDOM ---
BONDE_WISDOM = [
    {"title": "🚫 '비밀 지표'를 찾지 마라", "content": "비밀 지표는 없다. 과거 폭등주 차트 5천개를 파고들어 뇌에 패턴을 각인시켜라."},
    {"title": "🚫 수익금에 집착하지 마라", "content": "수익은 올바른 '프로세스'를 지켰을 때 따라오는 부산물일 뿐이다. 첫 번째 손실이 가장 좋은 손실이다."}
]

# --- PAGES ---
if page.startswith("6-a."):
    st.header("📌 출석체크")
    total_visits = len(safe_read_csv(ATTENDANCE_FILE)) + 500
    st.metric("🛸 누적 방문", f"{total_visits:,} 회")
    with st.form("attendance_form", clear_on_submit=True):
        greeting = st.text_input("오늘 한 줄 다짐")
        if st.form_submit_button("🛡️ 출석 서명"):
            if greeting:
                now_s = datetime.now(pytz.timezone('Asia/Seoul')).strftime("%Y-%m-%d %H:%M")
                safe_write_csv(pd.DataFrame([[now_s, st.session_state.current_user, greeting, "회원"]], columns=["시간", "아이디", "인사", "등급"]), ATTENDANCE_FILE, mode='a')
                st.success("✅ 등록 완료")
                st.rerun()

elif page.startswith("3-a."):
    st.header("🎯 주도주 VCP & EP 마스터 스캐너")
    
    def run_4stage_sc():
        full_list = ["NVDA", "TSLA", "AAPL", "MSFT", "AMZN", "005930.KS", "000660.KS", "196170.KQ"]
        st_txt = st.empty()
        st_txt.info("📡 데이터 수집 중...")
        try:
            data = yf.download(full_list, period="1y", progress=False)
            close = data['Close']
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
                roe_map = {tic: res for tic, res in zip(full_list, ex.map(get_ticker_roe, full_list))}
            
            all_res = []
            for tic in full_list:
                try:
                    h = close[tic].dropna()
                    if len(h) < 100: continue
                    cp = h.iloc[-1]
                    ch = (cp/h.iloc[-2] - 1) * 100
                    rs = (cp/h.iloc[0] - 1) * 100
                    roe = roe_map.get(tic, 0)
                    score = rs + (roe * 1.2)
                    all_res.append({"T": TICKER_NAME_MAP.get(tic, tic), "TIC": tic, "P": f"{cp:,.1f}", "CH": f"{ch:+.1f}%", "ROE": roe, "RS": rs, "SCORE": score})
                except: continue
            
            if all_res:
                df = pd.DataFrame(all_res)
                st.session_state.scan_results = df
                st.success("✅ 스캔 완료")
                with st.expander("🤖 AI 전술 보고서", expanded=True):
                    top = df.sort_values("SCORE", ascending=False).iloc[0]
                    # 글로벌 함수 호출 (fix됨)
                    advice = get_tactical_advice(top['T'], top['RS'], top['ROE'])
                    st.markdown(f"**대상: {top['T']} ({top['TIC']})**")
                    st.info(advice)
        except Exception as e: st.error(f"오류: {e}")
        st_txt.empty()

    if st.button("🚀 정밀 스캔 시작"): run_4stage_sc()
    
    if "scan_results" in st.session_state:
        st.dataframe(st.session_state.scan_results, use_container_width=True)

elif page.startswith("3-d."):
    st.header("📉 산업동향 (Industry Trends TOP 10)")
    url = st.secrets.get("INDUSTRY_SHEET_URL", "https://docs.google.com/spreadsheets/d/1xjbe9SF0HsxwY_Uy3NC2tT92BqK0nhArUaYU16Q0p9M/export?format=csv&gid=1156221191")
    try:
        df = pd.read_csv(url)
        st.dataframe(df.head(10), use_container_width=True)
    except Exception as e: st.error(f"로드 실패: {e}")

elif page.startswith("3-e."):
    st.header("📊 RS 강도 분석 (Relative Strength Strength)")
    url = st.secrets.get("RS_SHEET_URL", "https://docs.google.com/spreadsheets/d/1xjbe9SF0HsxwY_Uy3NC2tT92BqK0nhArUaYU16Q0p9M/export?format=csv&gid=1220465228")
    try:
        df = pd.read_csv(url)
        def highlight_rs(val):
            if isinstance(val, str) and '^' in val: return 'background-color: rgba(0,255,0,0.1); color: #00FF00; font-weight: bold;'
            return ''
        st.dataframe(df.style.applymap(highlight_rs), use_container_width=True)
    except Exception as e: st.error(f"로드 실패: {e}")

elif page.startswith("4-c."):
    st.header("🛡️ 리스크 방패")
    st.error("**손절선 -3%는 생명줄입니다.**")
    st.write("진입 후 -3% 후퇴는 사령부의 타점이 틀렸다는 시장의 명확한 신호입니다.")

# --- FOOTER ---
st.divider()
f_quote = random.choice(["당신은 똑똑함을 증명하려 하지 마라. 시장은 자존심에 관심이 없다.", "손절은 보험료다. 큰 승리를 위해 기꺼이 지불하라."])
st.markdown(f"<div style='text-align: center; color: #666; font-size: 0.8rem;'>{f_quote}<br>© 2026 StockDragonfly v9.9</div>", unsafe_allow_html=True)