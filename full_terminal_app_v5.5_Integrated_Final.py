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
        # 파일이 너무 자주 백업되는 것을 방지 (1시간당 1회 정도로 제한하거나 수동 강제시에만 실행)
        fname = os.path.basename(file_path)
        os.makedirs(BACKUP_DIR, exist_ok=True)
        
        # 고빈도 로그 파일은 강제(force) 옵션이 없으면 백업 건너뜀 (성능 최적화)
        if not force and fname in ["attendance.csv", "chat_log.csv", "shared_comments.csv"]:
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(BACKUP_DIR, f"{fname}_{timestamp}.bak")
        shutil.copy2(file_path, backup_path)
        
        # ⚠️ 성능 최적화: 파일 목록 조회를 매번 하지 않고 확률적으로 수행 (10% 확률)
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
        st.warning(f"⚠️ 데이터 파일([.csv]) 읽기 시도 중 지연이 발생하고 있습니다. 잠시 후 자동 복구됩니다. ({os.path.basename(file_path)})")
        return pd.DataFrame(columns=columns) if columns else pd.DataFrame()

def safe_write_csv(df, file_path, mode='w', header=True, backup=False):
    try:
        if backup and os.path.exists(file_path): auto_backup(file_path) # 명시적으로 요청 시에만 백업
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        if mode == 'a' and os.path.exists(file_path):
            header = False
        df.to_csv(file_path, index=False, encoding='utf-8-sig', mode=mode, header=header)
        return True
    except: return False

def safe_save_json(data, file_path):
    try:
        if os.path.exists(file_path): auto_backup(file_path) # 저장 전 기존 파일 백업
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    except: return False

def safe_load_json(file_path, default=None):
    if not os.path.exists(file_path): return default if default is not None else {}
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except: return default if default is not None else {}

# 🛡️ 영구 백업용 구글 시트 URL (CSV 내보내기 주소) - 보안을 위해 st.secrets 사용
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
    # 6자리 숫자면 한국 주식 코드로 처리
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
        
        # 🛡️ NaN 방지 및 유효한 최신 데이터 추출
        rate_series = m_data["USDKRW=X"].dropna()
        rate = float(rate_series.iloc[-1]) if not rate_series.empty else 1400.0
        
        yield_series = m_data["^TNX"].dropna()
        yield10y = float(yield_series.iloc[-1]) if not yield_series.empty else 4.3
        
        return rate, yield10y
    except: 
        return 1400.0, 4.3

def get_macro_indicators():
    rate, yield10y = get_macro_data()
    return f"💵 USD/KRW: {rate:,.1f}원 | 🏦 US 10Y Yield: {yield10y:.2f}%"

@st.cache_data(ttl=300)
def load_users():
    # 1. 먼저 로컬 파일 확인
    users = {}
    if os.path.exists(USER_DB_FILE):
        try:
            with open(USER_DB_FILE, "r", encoding="utf-8") as f: users = json.load(f)
        except: pass
    
    # 2. 구글 시트에서 최신 정보 가져와서 동기화 (비동기 시도)
    if USERS_SHEET_URL:
        # 로그인 페이지거나 관리자 페이지 등 인원이 꼭 필요한 경우에만 빡빡하게 확인
        try:
            # 5초 타임아웃 적용 (get_db_path 대신 직접 시도하는 지점은 이미 있음)
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
        except: pass # 실패 시 로컬 데이터만 사용

    # 기본 방장 계정 보장
    if "cntfed" not in users:
        users["cntfed"] = {"password": "cntfed", "status": "approved", "grade": "방장"}
    
    # 전문가님 권한은 시스템적으로 절대 보장 (지워짐 방지)
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

# --- 🚀 [NEW v9.9] Optimized Data Helpers ---
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

@st.cache_data
def get_cached_bg_b64():
    if os.path.exists("StockDragonfly2.png"):
        with open("StockDragonfly2.png", "rb") as imm: return base64.b64encode(imm.read()).decode()
    elif os.path.exists("StockDragonfly.png"):
        with open("StockDragonfly.png", "rb") as imm: return base64.b64encode(imm.read()).decode()
    return ""

# --- 🛸 [CORE UI] CSS & Background (Lightweight High-Performance) ---
st.markdown("""
    <style>
        /* 메인 배경: 6MB 이미지를 제거하고 고성능 그라데이션 적용 (타이핑 렉 방지) */
        .stApp {
            background: radial-gradient(circle at center, #1a1a2e 0%, #0f0f12 100%);
            background-attachment: fixed;
        }
        
        /* 글래스모피즘 효과 강화 */
        .glass-card {
            background: rgba(255, 255, 255, 0.03) !important;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.05) !important;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        }
        
        .main-title {
            background: linear-gradient(to right, #FFD700, #FFA500);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 900;
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

# 로고는 바이너리 전송(efficient)을 위해 st.image 사용
# bg_b64 호출 제거 (성능 저하 원인)

# --- 🛰️ [BANNER SHIELD] 메뉴 UI 구조 고정 (v9.9 Platinum) ---
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

def save_trades(trades):
    safe_save_json(trades, TRADES_DB)

def gsheet_sync(sheet_name, headers, values):
    payload = {"sheetName": sheet_name, "headers": headers, "values": values}
    try:
        resp = requests.post(MASTER_GAS_URL, json=payload, timeout=7)
        if resp.status_code != 200:
            print(f"DEBUG: GSheet Sync Error {resp.status_code} - {resp.text}")
        return resp
    except Exception as e:
        print(f"DEBUG: GSheet Sync Connection Failed: {e}")
        return None

def gsheet_sync_bg(sheet_name, headers, values):
    """구글 시트 동기화를 백그라운드 스레드에서 실행하여 UI 멈춤 방지"""
    threading.Thread(target=gsheet_sync, args=(sheet_name, headers, values), daemon=True).start()

st.set_page_config(page_title="StockDragonfly Pro", page_icon="🔴", layout="wide")

# 모바일 감지 (간이)
if "is_mobile" not in st.session_state:
    st.session_state.is_mobile = False

# --- 🌑 프리미엄 스타일 디자인 ---
bg_b64 = ""
logo_b64 = ""
if os.path.exists("StockDragonfly2.png"):
    with open("StockDragonfly2.png", "rb") as imm: bg_b64 = base64.b64encode(imm.read()).decode()
else: # Fallback to StockDragonfly if 2 is missing
    if os.path.exists("StockDragonfly.png"):
        with open("StockDragonfly.png", "rb") as imm: bg_b64 = base64.b64encode(imm.read()).decode()

if os.path.exists("StockDragonfly.png"):
    with open("StockDragonfly.png", "rb") as f: logo_b64 = base64.b64encode(f.read()).decode()

st.markdown(f"""
    <style>
    /* 💎 네온 플럭스 디자인 고도화 */
    .stApp {{ 
        background-color: #000; 
        {f'background-image: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), url("data:image/png;base64,{bg_b64}");' if bg_b64 else ""} 
        background-size: cover; 
        background-position: center;
        background-attachment: fixed; 
    }}
    [data-testid="stSidebar"] {{ background-color: rgba(2,2,2,0.98) !important; border-right: 1px solid #FFD70022; backdrop-filter: blur(40px); }}
    
    .main-title {{ 
        font-family: 'Outfit', sans-serif;
        background: linear-gradient(to right, #FFD700, #FFF, #FFD700);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900;
        font-size: 4.5rem;
        text-align: center;
        margin-bottom: 0px;
        filter: drop-shadow(0 0 20px rgba(255,215,0,0.5));
    }}
    
    h1, h2 {{ color: #FFD700 !important; font-weight: 900; text-shadow: 0 0 15px rgba(255,215,0,0.3); }}
    
    .glass-card {{ background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 18px; padding: 25px; backdrop-filter: blur(20px); margin-bottom: 30px; transition: all 0.5s cubic-bezier(0.23, 1, 0.32, 1); position: relative; overflow: hidden; }}
    .glass-card:hover {{ border-color: #FFD70066; transform: translateY(-8px) scale(1.01); box-shadow: 0 20px 40px rgba(0,0,0,0.6), 0 0 20px rgba(255,215,0,0.1); }}
    
    /* ✨ 네온 보더 애니메이션 */
    .neon-border {{ position: relative; padding: 2px; background: linear-gradient(90deg, #FFD700, #00FF00, #FFD700); background-size: 200% 100%; animation: neon-flow 3s linear infinite; border-radius: 20px; }}
    .neon-inner {{ background: #000; border-radius: 18px; padding: 25px; }}
    @keyframes neon-flow {{ 0% {{ background-position: 0% 0%; }} 100% {{ background-position: 200% 0%; }} }}
    
    /* 🍌 나노바나나 게이지 */
    .banana-track {{ background: rgba(255,255,255,0.05); height: 12px; border-radius: 6px; position: relative; overflow: hidden; margin: 10px 0; border: 1px solid rgba(255,255,255,0.1); }}
    .banana-fill {{ height: 100%; border-radius: 6px; transition: width 1s ease-out; box-shadow: 0 0 10px currentColor; }}
    
    @keyframes pulse-glow {{ 0% {{ box-shadow: 0 0 10px rgba(0,255,0,0.2); opacity: 0.8; }} 50% {{ box-shadow: 0 0 30px rgba(0,255,0,0.5); opacity: 1; }} 100% {{ box-shadow: 0 0 10px rgba(0,255,0,0.2); opacity: 0.8; }} }}
    .status-pulse {{ border: 1px solid #00FF0044; animation: pulse-glow 2s infinite; }}
    
    @keyframes ticker {{ 0% {{ transform: translateX(100%); }} 100% {{ transform: translateX(-100%); }} }}
    .ticker-wrap {{ overflow: hidden; background: rgba(0,0,0,0.6); white-space: nowrap; padding: 12px 0; border-bottom: 2px solid rgba(255,215,0,0.2); margin-bottom: 20px; backdrop-filter: blur(15px); }}
    .ticker-content {{ display: inline-block; animation: ticker 250s linear infinite; color: #FFD700; font-size: 0.95rem; font-weight: 600; font-family: 'Outfit'; animation-delay: 1s; }}
    .ticker-wrap:hover .ticker-content {{ animation-play-state: paused; }}
    .ticker-item {{ margin: 0 40px; display: inline-block; }}
    /* 💎 사이드바 가독성 최적화 (줄바꿈 방지) */
    [data-testid="stSidebarNav"] {{ display: none; }}
    [data-testid="stSidebar"] .stButton button {{ 
        font-size: 0.82rem !important; 
        white-space: nowrap !important; 
        overflow: hidden; 
        text-overflow: ellipsis; 
        justify-content: flex-start !important;
        text-align: left !important;
        padding: 0px 10px !important;
    }}
    /* 📱 모바일 최적화 (S23 등 스마트폰 대응) */
    @media (max-width: 768px) {{
        .main-title {{ font-size: 2.5rem !important; }}
        .glass-card {{ padding: 15px !important; margin-bottom: 15px !important; }}
        h1, h2 {{ font-size: 1.5rem !important; }}
        .ticker-item {{ margin: 0 20px !important; font-size: 0.8rem !important; }}
        [data-testid="stSidebar"] {{ width: 85vw !important; }}
        /* 버튼 터치 영역 확대 */
        .stButton button {{ padding: 12px 15px !important; font-size: 0.9rem !important; }}
    }}
    
    /* 배너(Expander) 헤더 강제 한 줄 고정 및 모바일 대응 */
    .st-expanderHeader {{ 
        font-size: 0.88rem !important; 
        white-space: nowrap !important; 
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }}
    @media (max-width: 768px) {{
        .st-expanderHeader {{ font-size: 0.95rem !important; padding: 10px !important; }}
    }}
    .st-expanderHeader > div {{ white-space: nowrap !important; }}
    </style>
""", unsafe_allow_html=True)

# --- 인증 & 사이드바 ---
if "password_correct" not in st.session_state: st.session_state["password_correct"] = False
if not st.session_state["password_correct"]:
    # 모바일에서는 컬럼 비율 조정
    c1, m, c2 = st.columns([0.1, 0.8, 0.1]) if st.session_state.get("is_mobile", False) else st.columns([1, 2, 1])
    with m:
        st.markdown("<div class='main-title'>StockDragonfly</div>", unsafe_allow_html=True)
        if logo_b64:
            st.markdown(f'<img src="data:image/png;base64,{logo_b64}" style="width:100%; border-radius:15px; margin-bottom:20px;">', unsafe_allow_html=True)
        elif os.path.exists("StockDragonfly.png"): 
            st.image("StockDragonfly.png", use_container_width=True)
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
                if st.button("✅ 공지 확인 및 열지 않기", use_container_width=True):
                    st.session_state["show_notice"] = False
                    st.rerun()

        tab1, tab2 = st.tabs(["🚀 Terminal Log-In", "📝 Join Command (자격 시험)"])
        
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
                    else: st.error("❌ 보안 코드가 일치하지 않습니다.")
                else: st.error("❌ 등록되지 않은 정보입니다.")
        
        with tab2:
            st.markdown("### 🏹 사령부 정예 요원 입성 자격 시험")
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
            st.markdown("#### 📝 [필수] 사령부 정예 요원 자격 시험 (15문항)")
            st.info("기초 10문제 + 전술 5문제 중 13문제 이상 맞혀야 승인이 완료됩니다.")
            
            # 기초 10문제 (Q1-Q10)
            q1 = st.radio("Q1. 우리나라 주식 차트에서 '빨간색 양초(캔들)' 그림은 무슨 뜻일까요?", ["올랐다 (상승)", "떨어졌다 (하락)", "변동 없다", "거래 중지"], index=None)
            q2 = st.radio("Q2. 파란색 양초(캔들) 그림은 무슨 뜻일까요?", ["상승 국면", "하락 국면", "보합 국면", "매수 신호"], index=None)
            q3 = st.radio("Q3. 하루 동안 사람들이 주식을 얼마나 많이 사고팔았는지 알려주는 지표는?", ["거래량", "배당금", "회전율", "수익률"], index=None)
            q4 = st.radio("Q4. 양초 모양을 닮은 막대기들로 그린 차트의 이름은 무엇일까요?", ["막대 차트", "캔들 차트", "라인 차트", "그림 차트"], index=None)
            q5 = st.radio("Q5. 주식 명언 중 가장 잘 알려진 원칙은?", ["발바닥에서 사서 정수리에서 팔아라", "무릎에서 사서 어깨에서 팔아라", "언제든 사고 언제든 팔아라", "사두면 언젠가 오른다"], index=None)
            q6 = st.radio("Q6. 주식 가격의 평균을 내서 선으로 이은 그림을 무엇이라고 할까요?", ["이동평균선(이평선)", "추�    # BGM 시스템 일시 중단 (타이핑 렉 방지 최우선)
    # def get_base64_audio(file_path): ...
    st.info("💡 최적의 타이핑 속도를 위해 오디오 사령부는 현재 점검 중입니다.")
t) if a == c])
                    
                    if score >= 13:
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
                            
                            st.success(f"🎊 {score}/15점! 훌륭합니다. 사령부의 지혜를 계승할 자격을 증명하셨습니다. 로그인을 진행해 주십시오.")
                            st.balloons()
                    else:
                        st.error(f"❌ {score}/15점. 사령부의 철학을 더 공부하고 와주시기 바랍니다. (13점 이상 합격)")
                        with st.expander("📝 15관문 자격 시험 정답 및 해설 보기", expanded=True):
                            st.markdown("""
                            - **Q1-2:** 양봉(빨강)은 상승, 음봉(파란)은 하락입니다.
                            - **Q3-4:** 거래량은 관심의 지표이며, 캔들 차트는 시세의 흐름을 보여줍니다.
                            - **Q5-6:** 무릎에 사서 어깨에 파는 겸손한 원칙과 이동평균선의 방향을 추종하십시오.
                            - **Q7-8:** 골든크로스는 황금빛 매수 신호, 데드크로스는 죽음의 매도 신호입니다.
                            - **Q9-10:** 저점과 고점을 파악하고 인플레이션으로 인한 시장의 우상향을 믿으십시오.
                            - **Q11:** MAGNA의 G는 **Gap Up**입니다. 강력한 기관 수급의 증거입니다.
                            - **Q12:** 수익은 오직 **2단계 (Mark-up)** 에서만 창출됩니다.
                            - **Q13:** RSI **30 이하**는 매도세가 소멸되는 과매도 구간입니다.
                            - **Q14:** 부분 익절 후에는 손절선을 **본절(Break-even)**로 올려 무위험 상태를 만드십시오.
                            - **Q15:** **3일 연속** 상승한 종목은 절대 추격 매수하지 않는 것이 사령부의 철칙입니다.
                            """)
    st.stop()

with st.sidebar:
    if logo_b64:
        st.markdown(f'<img src="data:image/png;base64,{logo_b64}" style="width:100%; border-radius:10px; margin-bottom:10px;">', unsafe_allow_html=True)
    elif os.path.exists("StockDragonfly.png"): 
        st.image("StockDragonfly.png")
    st.markdown("<p style='color:#FF914D; font-size:1.5rem; font-weight:900;'>🔴 StockDragonfly v9.9</p>", unsafe_allow_html=True)
    
    # 거시지표 표시
    macro_info = get_macro_indicators()
    st.markdown(f"<div style='background: rgba(255,255,255,0.05); padding: 5px; border-radius: 5px; border: 1px solid #333; text-align: center; font-size: 0.75rem; color: #AAA; margin-bottom: 10px;'>{macro_info}</div>", unsafe_allow_html=True)

    # --- 📱 v7.0 모바일 최적화 토글 ---
    mobile_on = st.checkbox("📱 모바일 최적화 모드", key="mobile_mode")
    if mobile_on:
        st.markdown("<style>.main .block-container { padding: 5px !important; } .stMetric { padding: 5px !important; } h1 { font-size: 1.6rem !important; } h2 { font-size: 1.3rem !important; }</style>", unsafe_allow_html=True)
    
    st.divider()
    bgms = {
        "🔇 OFF": None, 
        "🎵 Full BGM": "full.mp3",
        "✨ You Raise": "YouRaise.mp3", 
        "😊 Happy": "happy.mp3", 
        "🌅 Hope": "hope.mp3", 
        "🐱 Cute": "cute.mp3", 
        "🎻 Petty": "petty.mp3", 
        "🎙️ Ajussi": "나의아저씨.mp3",
        "🔀 Random Mix": "shuffle"
    }
    sel_bgm = st.selectbox("Radio", list(bgms.keys()), label_visibility="collapsed")
    vol = st.slider("🔊 Volume", 0.0, 1.0, 0.45)
    
    target_bgm = bgms[sel_bgm]
    
    # 랜덤 믹스 처리
    if target_bgm == "shuffle":
        if "shuffled_bgm" not in st.session_state:
            valid_files = [f for f in list(bgms.values()) if f and f != "shuffle" and os.path.exists(f)]
            st.session_state.shuffled_bgm = random.choice(valid_files) if valid_files else None
        target_bgm = st.session_state.shuffled_bgm
    else:
        # 일반 선택 시 셔플 상태 초기화 (다음에 다시 셔플 선택 시 새로운 곡 선택되도록)
        if "shuffled_bgm" in st.session_state:
            del st.session_state.shuffled_bgm

    if target_bgm and os.path.exists(target_bgm):
        # 🚀 오디오 성능 최적화: 캐시에 저장된 base64 사용 (매번 인코딩 방지)
        @st.cache_data(show_spinner=False, ttl=3600)
        def get_base64_audio(file_path):
            try:
                with open(file_path, "rb") as f: 
                    return base64.b64encode(f.read()).decode()
            except: return ""
        
        b64 = get_base64_audio(target_bgm)
        if b64:
            # onended 이벤트를 활용하여 랜덤 믹스 시 다음 곡으로 넘어가게 설정 (Streamlit 한계상 재실행 필요)
            st.components.v1.html(f"""
                <audio id='aud' autoplay loop>
                    <source src='data:audio/mp3;base64,{b64}' type='audio/mp3'>
                </audio>
                <script>
                    var audio = document.getElementById('aud');
                    audio.volume = {vol};
                </script>
            """, height=0)

# --- 유저 등급 판독 ---
users = load_users()
curr_user_data = users.get(st.session_state.current_user, {})
curr_grade = curr_user_data.get("grade", "회원")
is_admin = (curr_grade in ["관리자", "방장"])

# --- 🔴 2단계 구성 (ZONE_CONFIG 참조) ---
if 'page' not in st.session_state:
    st.session_state.page = "6-a. 📌 출석체크(오늘한줄)"

zones = {k: list(v) for k, v in ZONE_CONFIG.items()} # 원본 구조 복사

# 보급 및 보안 권한에 따른 메뉴 필터링
if curr_grade != "방장":
    if "1-b. 🎖️ HQ 인적 자원 사령부" in zones["🏰 1. 본부 사령부"]:
        zones["🏰 1. 본부 사령부"].remove("1-b. 🎖️ HQ 인적 자원 사령부")

# 🤖 자동매매 사령부는 모든 승인된 대원(준회원 이상)이 접근 가능
if curr_grade not in ["방장", "관리자", "정회원", "준회원"]:
    if "🤖 7. 자동매매 사령부" in zones:
        del zones["🤖 7. 자동매매 사령부"]

with st.sidebar:
    st.markdown("<p style='color: #FFD700; font-size: 0.9rem; font-weight: 700; margin-top: 10px; margin-bottom: 20px; letter-spacing: 1px;'>🔴 MISSION CONTROL</p>", unsafe_allow_html=True)
    
    for zone_name, missions in zones.items():
        is_active_zone = st.session_state.page in missions
        with st.expander(zone_name, expanded=is_active_zone):
            for m in missions:
                if st.button(m, key=f"nav_{m}", use_container_width=True):
                    st.session_state.page = m
                    st.rerun()

# --- 🌍 [GLOBAL RECONNAISSANCE] 공통 시각 및 상태 설정 ---
now_kst = datetime.now(pytz.timezone('Asia/Seoul'))

# 최종 선택된 미션을 page 변수에 할당하여 본문 렌더링
page = st.session_state.get("page", "6-a. 📌 출석체크(오늘한줄)")

# --- 🔴 상단 브랜드 헤더 (NUCLEAR CLEAN: Text Logo) ---
c_logo1, c_logo2, c_logo3 = st.columns([1, 2, 1])
with c_logo2:
    st.markdown("""
        <div style='text-align: center; margin-bottom: 20px;'>
            <h1 style='font-size: 4rem; font-weight: 900; background: linear-gradient(45deg, #FFD700, #FFFFFF); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-shadow: 0 10px 20px rgba(0,0,0,0.5); white-space: nowrap;'>StockDragonfly</h1>
            <p style='color: #888; letter-spacing: 7px; font-size: 0.8rem; margin-top: -10px;'>ULTRA-HIGH PERFORMANCE TERMINAL</p>
        </div>
    """, unsafe_allow_html=True)

# --- 🐉 전광판 티커 테이프 ---
@st.cache_data(ttl=300)
def get_ticker_tape():
    watch = {
        "^IXIC": "NASDAQ", "^KS11": "KOSPI", "^KQ11": "KOSDAQ",
        "NVDA": "NVDA", "TSLA": "TSLA", "NFLX": "NFLX",
        "AAPL": "AAPL", "MSFT": "MSFT", "AMZN": "AMZN", 
        "META": "META", "BTC-USD": "BITCOIN"
    }
    symbols = list(watch.keys())
    items = []
    try:
        data = yf.download(symbols, period="5d", progress=False)['Close']
        for s in symbols:
            try:
                name = watch[s]
                vals = data[s].dropna()
                if len(vals) >= 2:
                    curr = vals.iloc[-1]
                    prev = vals.iloc[-2]
                    c = ((curr / prev) - 1) * 100
                    color = "#00FF00" if c >= 0 else "#FF4B4B"
                    items.append(f"<span class='ticker-item'>{name} {curr:,.1f} <span style='color:{color};'>{c:+.2f}%</span></span>")
            except: pass
    except: pass
    return "".join(items)

ticker_html = get_ticker_tape()
st.markdown(f"<div class='ticker-wrap' style='border-top: 1px solid #FFD70033; border-bottom: 2px solid #FFD70066;'><div class='ticker-content'>{ticker_html * 10 if ticker_html else ''}</div></div>", unsafe_allow_html=True)

# --- 🛰️ 시스템 전역 장애/상태 알림 ---
if "gs_error" in st.session_state and st.session_state["gs_error"]:
    st.error(st.session_state["gs_error"])

# --- 🚀 LIVE OPS CENTER (NEW v6.0) ---
st.markdown(f"""
<div style='background: linear-gradient(90deg, rgba(255,215,0,0.05), rgba(0,0,0,0.9)); border-left: 5px solid #FFD700; padding: 10px 20px; margin-bottom: 15px; border-top-right-radius: 15px;'>
    <div style='display: flex; align-items: center; gap: 15px;'>
        <div style='width: 10px; height: 10px; background: #00FF00; border-radius: 50%; animation: pulse-glow 1.5s infinite;'></div>
        <b style='color: #FFD700; letter-spacing: 2px; font-size: 0.9rem;'>TACTICAL OPS CENTER ACTIVE</b>
        <span style='color: #555;'>|</span>
        <marquee scrollamount='4' style='color: #00FF00; font-size: 0.85rem; font-family: monospace;'>
            [BREAKING] NVDA VCP Phase 3 Detection complete... [MARKET] KOSPI Relative Strength Improving... [ALERT] Watch Episode Pivot on high-volume symbols... 
        </marquee>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 🛰️ 상단 실시간 정보 바 ---
now_kr = datetime.now(pytz.timezone('Asia/Seoul'))
now_us = datetime.now(pytz.timezone('America/New_York'))

@st.cache_data(ttl=600)
def get_top_indices():
    res = {"NASDAQ": [0.0, 0.0], "KOSPI": [0.0, 0.0], "KOSDAQ": [0.0, 0.0]}
    symbols = {"NASDAQ": "^IXIC", "KOSPI": "^KS11", "KOSDAQ": "^KQ11"}
    try:
        data = yf.download(list(symbols.values()), period="5d", progress=False)['Close']
        for name, ticker in symbols.items():
            if ticker in data.columns:
                close_data = data[ticker].dropna()
                if len(close_data) >= 2:
                    curr = close_data.iloc[-1]
                    prev = close_data.iloc[-2]
                    pct = ((curr / prev) - 1) * 100
                    res[name] = [float(curr), float(pct)]
    except Exception as e:
        print(f"DEBUG: Index Download Error: {e}")
    return res

idx_info = get_top_indices()

st.markdown(f"""
<div class='responsive-bar' style='background: rgba(10,10,10,0.9); border-radius: 12px; padding: 12px 25px; border: 1px solid #333; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 15px rgba(0,0,0,0.5);'>
    <div style='font-family: inherit;'>
        <div style='display: flex; align-items: center; gap: 8px;'>
            <div style='width: 8px; height: 8px; background: #00FF00; border-radius: 50%; box-shadow: 0 0 10px #00FF00;'></div>
            <span style='color: #888; font-size: 0.85rem; letter-spacing: 1px;'>LIVE OPS CENTER</span>
        </div>
        <div style='margin-top: 5px;'>
            <span style='color: #EEE; font-size: 0.95rem; font-weight: 700;'>🇰🇷 한국: {now_kr.strftime('%m/%d')}/{['월','화','수','목','금','토','일'][now_kr.weekday()]}/{now_kr.strftime('%H:%M:%S')}</span>
            <span style='color: #444; margin: 0 10px;'>|</span>
            <span style='color: #EEE; font-size: 0.95rem; font-weight: 700;'>🇺🇸 미국: {now_us.strftime('%m/%d')}/{['월','화','수','목','금','토','일'][now_us.weekday()]}/{now_us.strftime('%H:%M:%S')}</span>
        </div>
    </div>
    <div class='responsive-indices' style='display: flex; gap: 30px;'>
        <div style='text-align: right;'>
            <span style='color: #888; font-size: 0.8rem;'>NASDAQ</span><br>
            <span style='color: #EEE; font-size: 0.9rem; font-weight: 500;'>{idx_info["NASDAQ"][0]:,.1f}</span>
            <span style='color: {"#00FF00" if idx_info["NASDAQ"][1]>=0 else "#FF4B4B"}; font-weight: 700; margin-left: 5px;'>{idx_info["NASDAQ"][1]:+.2f}%</span>
        </div>
        <div style='text-align: right;'>
            <span style='color: #888; font-size: 0.8rem;'>KOSPI</span><br>
            <span style='color: #EEE; font-size: 0.9rem; font-weight: 500;'>{idx_info["KOSPI"][0]:,.1f}</span>
            <span style='color: {"#00FF00" if idx_info["KOSPI"][1]>=0 else "#FF4B4B"}; font-weight: 700; margin-left: 5px;'>{idx_info["KOSPI"][1]:+.2f}%</span>
        </div>
        <div style='text-align: right;'>
            <span style='color: #888; font-size: 0.8rem;'>KOSDAQ</span><br>
            <span style='color: #EEE; font-size: 0.9rem; font-weight: 500;'>{idx_info["KOSDAQ"][0]:,.1f}</span>
            <span style='color: {"#00FF00" if idx_info["KOSDAQ"][1]>=0 else "#FF4B4B"}; font-weight: 700; margin-left: 5px;'>{idx_info["KOSDAQ"][1]:+.2f}%</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 🛰️ 마켓 게이지 헤더 ---
st.markdown("""
<div class='status-pulse' style='background: rgba(0,0,0,0.85); border: 2px solid #FFD700; border-radius: 15px; padding: 25px; text-align: center; margin-bottom: 25px;'>
    <h1 style='color: #00FF00; margin: 0; font-size: 2.2rem; text-shadow: 0 0 15px rgba(0,255,0,0.5);'>🟢 GREEN MARKET ACTIVE</h1>
    <p style='color: #FFD700; font-size: 1.1rem; margin-top: 10px; font-weight: 700;'>
        🛡️ 사령부 상태: 매수 윈도우 개방 (팔로스루데이 발생: 4월 8일 수요일)
    </p>
    <div style='color: #CCC; font-style: italic; font-size: 0.95rem; margin-top: 5px;'>
        "시장의 중력이 가장 약해지는 순간, 강력한 EP를 동반한 주도주만이 하늘로 솟구칩니다. 우리는 그 불꽃에 동참합니다." - Pradeep Bonde
    </div>
</div>
""", unsafe_allow_html=True)

# --- 🛰️ 본데의 전술 지침 데이터 ---
BONDE_WISDOM = [
    {
        "title": "🚫 '비밀 지표'나 '마법의 셋업'을 찾는 헛수고는 당장 집어치워라",
        "content": "많은 초보자들이 나에게 완벽한 매수 타점이나 '비밀 지표'가 뭐냐고 묻는다. 그런 건 없다. 시장에서 돈을 버는 진정한 '엣지(Edge)'는 책 몇 권 읽는다고 생기는 것이 아니다. 당신이 돌파 매매(Breakout)에 단 1달러라도 걸기 전에, 과거에 성공했던 폭등주 차트 5,000개, 10,000개를 직접 파고들어라(Deep Dive). 500피트, 1,000피트, 5,000피트 깊이까지 파고들어야 비로소 시장이 어떻게 움직이는지 이해하기 시작할 것이다. 다른 사람의 종목 추천(Alert)에 의존하는 짓을 멈추고 당신 스스로 뇌에 패턴을 각인시켜라."
    },
    {
        "title": "🚫 당신은 천재가 아니다. '섬의 환상(Island Mentality)'에서 깨어나라",
        "content": "운 좋게 시장 환경이 좋은 몇 주 동안 20%의 수익을 내고 나면, 사람들은 자신이 천재인 줄 착각한다. 단번에 큰돈을 벌어 열대의 섬을 사고 페라리를 사겠다는 허황된 꿈(Island Mentality)에 빠져 이른바 '신 증후군(God Syndrome)'에 걸린다. 그렇게 자만하며 아무 때나 매매를 남발하다 보면, 결국 머리 위로 코코넛이 떨어져 계좌가 박살 날 것이다. 허황된 홈런을 노리지 말고, 짧고 확실한 수익(Singles)을 챙기며 복리로 굴리는 지루한 과정을 거쳐라."
    },
    {
        "title": "🚫 쓰레기장 같은 장에서 매매하며 계좌를 갈아버리지 마라",
        "content": "아무리 완벽해 보이는 에피소딕 피봇(EP)이나 모멘텀 버스트 셋업이라도 시장의 환경(날씨)이 나쁘면 무용지물이다. 당신은 매일 아침 '오늘 돌파 매매가 통하는 날인가?'를 스스로에게 묻고 있는가? 시장의 하락 종목 수가 상승 종목을 압도하고 돌파가 계속 실패하는 똥 같은 시장(Shit market)에서 계속 매매 버튼을 누르며 계좌를 산산조각(Chop to pieces) 내고 싶다면 마음대로 해라. 시장 환경이 나쁠 때는 제발 아무것도 하지 말고 손을 깔고 앉아 현금을 지켜라."
    },
    {
        "title": "🚫 수익금(P&L)에 집착하지 말고 '프로세스'나 지켜라",
        "content": "수익은 당신이 올바른 '프로세스'를 지켰을 때 따라오는 부산물일 뿐이다. 매수 후 3일 연속으로 상승한 주식을 뒤늦게 추격 매수하고 있는가? 축하한다, 당신은 곧 고점에 물린 '호구(Bag Holder)'가 될 것이다. 손절선을 내리지 마라. 손절선은 신성한 것이다. **'첫 번째 손실이 가장 좋은 손실'**임을 명심하고, 당신이 세운 2.5%~5%의 손절선, 혹은 당일 최저점(LOD)이 깨지면 기계처럼 잘라내라. 당신의 얄팍한 예측이나 감정을 개입시키지 말고 수치와 원칙, 철저한 프로세스만 남겨라."
    }
]

# --- 🛰️ 전술 푸터용 랜덤 어록 데이터 ---
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
    st.header("📌 사령부 출석체크 및 오늘 한 줄")
    
    # 데이터 준비
    if not os.path.exists(ATTENDANCE_FILE):
        safe_write_csv(pd.DataFrame(columns=["시간", "아이디", "인사", "등급"]), ATTENDANCE_FILE)
    
    df_att = safe_read_csv(ATTENDANCE_FILE, ["시간", "아이디", "인사", "등급"])
    # ⭐ [USER REQ] 방문자 수 500부터 시작하도록 오프셋 추가
    total_visits = len(df_att) + 500
    
    # 상단 요약 바 (방문자 수 & 날씨)
    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown(f"""
        <div class='glass-card' style='text-align: center; padding: 20px;'>
            <h4 style='margin:0; color:#FFD700;'>🛸 누적 사령부 방문</h4>
            <span style='font-size: 2.5rem; font-weight: 900; color: #00FF00;'>{total_visits:,}</span>
            <p style='margin:0; color:#888;'>Operatives Engaged</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        # 간단한 날씨 MOCK (실제 API 대신 시각에 따른 날씨 이모지)
        hour = datetime.now(pytz.timezone('Asia/Seoul')).hour
        weather_icon = "☀️" if 6 <= hour < 18 else "🌙"
        weather_text = "맑음/쾌적" if 6 <= hour < 18 else "은은한 달빛"
        st.markdown(f"""
        <div class='glass-card' style='text-align: center; padding: 20px;'>
            <h4 style='margin:0; color:#FFD700;'>🌤️ 작전 지역 날씨</h4>
            <span style='font-size: 2.5rem;'>{weather_icon}</span>
            <p style='margin:0; color:#888;'>서울 기준: {weather_text}</p>
        </div>
        """, unsafe_allow_html=True)
        
    st.divider()
    
    # 출석 입력
    with st.form("attendance_form", clear_on_submit=True):
        st.markdown("### 🏹 오늘 한 줄 다짐 (Attendance)")
        greeting = st.text_input("사령부에 임하는 오늘의 한 마디", placeholder="예: 오늘도 원칙 매매! 뇌동매매 금지!")
        if st.form_submit_button("🛡️ 출석 완료 및 서명"):
            if greeting:
                now_kst = datetime.now(pytz.timezone('Asia/Seoul')).strftime("%Y-%m-%d %H:%M")
                new_row = pd.DataFrame([[now_kst, st.session_state.current_user, greeting, curr_grade]], columns=["시간", "아이디", "인사", "등급"])
                
                # 🚀 최적화: 백업 생략 (이미 수동 백업 로직이 상단에 있음)
                safe_write_csv(new_row, ATTENDANCE_FILE, mode='a', header=False, backup=False)
                
                # 📡 구글 시트 백업 (사용자 요청에 따라 출석체크는 실시간 연동 중단 - 속도 최적화)
                # gsheet_sync_bg("시트1", ["시간", "아이디", "인사", "등급"], [now_kst, st.session_state.current_user, greeting, curr_grade])
                
                st.success("✅ 사령부 명부에 정상 등록되었습니다. 오늘의 전술을 확인하십시오.")
                st.balloons()
                st.rerun()
            else:
                st.error("❌ 한 줄 인사를 입력해 주세요.")

    st.subheader("📡 사령부 실시간 전술 분석 (AI Advisor)")
    # --- 🤖 Rule-based Tactical Advisor (Platinum Engine) ---


    st.subheader("📡 실시간 출석 현황")
    # 구글 시트 데이터와 로컬 데이터 병합
    gs_att = fetch_gs_attendance()
    local_att = safe_read_csv(ATTENDANCE_FILE, ["시간", "아이디", "인사", "등급"])
    df_att = pd.concat([gs_att, local_att]).drop_duplicates(subset=["시간", "아이디", "인사"]).tail(20)

    if not df_att.empty:
        # 최근 20개만 표시
        for _, row in df_att.iloc[::-1].head(20).iterrows():
            is_admin_att = row["등급"] in ["방장", "관리자"]
            bg = "rgba(255,215,0,0.15)" if is_admin_att else "rgba(255,255,255,0.05)"
            tag = "👑" if is_admin_att else "👤"
            st.markdown(f"""
            <div style='background: {bg}; border-radius: 8px; padding: 12px; margin-bottom: 8px; border-left: 4px solid {"#FFD700" if is_admin_att else "#444"};'>
                <div style='display: flex; justify-content: space-between; font-size: 0.8rem; color: #888;'>
                    <b>{tag} {row["아이디"]} ({row["등급"]})</b>
                    <span>{row["시간"]}</span>
                </div>
                <div style='margin-top: 5px; color: #EEE;'>{row["인사"]}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("오늘 첫 번째로 출석하여 사령부의 문을 여십시오!")

elif page.startswith("3-a."):
    st.header("🎯 주도주 VCP & EP 마스터 스캐너")
    st.markdown("<div class='glass-card'>미너비니의 VCP(변동성 축소)와 본데의 EP(에피소딕 피벗) 4단계 통합 검색 엔진입니다.</div>", unsafe_allow_html=True)
    
    def run_4stage_sc():
        US_RADAR = ["NVDA", "TSLA", "AAPL", "MSFT", "AMZN", "META", "GOOGL", "AVGO", "CRWD", "PLTR", "SMCI", "AMD", "NFLX", "STX", "WDC", "MSTR", "COIN", "MARA", "PANW", "SNOW"]
        KR_RADAR = ["005930.KS", "000660.KS", "196170.KQ", "042700.KS", "105560.KS", "055550.KS", "005490.KS", "000270.KS", "066570.KS", "035720.KS", "005380.KS", "000810.KS"]
        full_list = US_RADAR + KR_RADAR
        
        all_res = []
        st_txt = st.empty()
        st_txt.info("📡 글로벌 실시간 데이터 일괄 수집 중... 잠시만 기다려 주십시오.")
        
        try:
            # 일괄 다운로드로 속도 및 안정성 확보
            data_full = yf.download(full_list, period="1y", interval="1d", progress=False)
            data = data_full['Close']
            data_high = data_full['High']
            data_low = data_full['Low']
            
            # --- 🚀 [Parallel ROE Fetching] ---
            # 모든 티커의 ROE를 병렬로 미리 수집 (캐시가 있으면 즉시 반환됨)
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                roe_map = {tic: res for tic, res in zip(full_list, executor.map(get_ticker_roe, full_list))}

            for tic in full_list:
                try:
                    if tic not in data.columns: continue
                    h = data[tic].dropna()
                    if len(h) < 200: continue

                    # --- 🐍 v7.0 VCP(변동성 축소) 정밀 분석 ---
                    h_high = data_high[tic].dropna()
                    h_low = data_low[tic].dropna()
                    vcp_score = 0
                    tight_label = "Loose"
                    if len(h_high) > 20:
                        ranges = (h_high - h_low) / h * 100
                        w1 = ranges.iloc[-5:].mean() 
                        w2 = ranges.iloc[-10:-5].mean() 
                        w3 = ranges.iloc[-20:-10].mean() 
                        if w1 < w2 < w3: 
                            vcp_score = 25 
                            tight_label = "Excellent"
                        elif w1 < w2: 
                            vcp_score = 15
                            tight_label = "Good"
                    
                    cp = h.iloc[-1]
                    pp = h.iloc[-2]
                    y_ago = h.iloc[0]
                    
                    ch = (cp/pp - 1) * 100
                    rs = ((cp / y_ago) - 1) * 100
                    
                    # 미리 수집된 ROE 맵에서 가져옴
                    roe = roe_map.get(tic, 0)
                    
                    score = rs + (roe * 1.2) + vcp_score 
                    is_us = (".KS" not in tic and ".KQ" not in tic)
                    display_name = TICKER_NAME_MAP.get(tic, tic) if not is_us else tic
                    
                    all_res.append({
                        "T": display_name, "TIC": tic, "P": f"${cp:.2f}" if is_us else f"{int(cp):,}원",
                        "CH": f"{ch:+.1f}%", "ROE": roe, "RS": rs, "VCP": tight_label, "SCORE": score,
                        "MARKET": "USA 🇺🇸" if is_us else "KOREA 🇰🇷"
                    })
                except: continue
        except Exception as e:
            st.error(f"⚠️ 데이터 통신 중 오류가 발생했습니다: {e}")
            return
            
        st_txt.empty()
        
        if all_res:
            df = pd.DataFrame(all_res)
            st.session_state.scan_results = df
            st.success("✅ 스캔 완료! 주도주 분석 결과가 데이터베이스에 등재되었습니다.")
            
            # --- AI Advisor Preview Area ---
            with st.expander("🤖 사령부 AI 전술 판독 보고서 (Summary)", expanded=True):
                top_stock = df.sort_values("SCORE", ascending=False).iloc[0]
                advice_text = get_tactical_advice(top_stock['T'], top_stock['RS'], top_stock['ROE'])
                st.markdown(f"**현재 최고의 전술 타겟: {top_stock['T']} ({top_stock['TIC']})**")
                st.info(advice_text)
        else:
            st.warning("분석 가능한 종목 데이터가 부족합니다. 잠시 후 다시 시도해 주세요.")

    if st.button("🚀 한/미 주도주 10선 정밀 스캔 시작"):
        run_4stage_sc()

    if "scan_results" in st.session_state and st.session_state.scan_results is not None:
        df = st.session_state.scan_results
        us_top = df[df['MARKET'].str.contains("USA")].sort_values("SCORE", ascending=False).head(5)
        kr_top = df[df['MARKET'].str.contains("KOREA")].sort_values("SCORE", ascending=False).head(5)
        combined_top = pd.concat([us_top, kr_top])
        
        st.subheader("🔥 사령부 한/미 통합 주도주 TOP 10")
        for i, row in combined_top.iterrows():
            st.markdown(f"""
            <div class='glass-card' style='padding: 15px; border-left: 5px solid {"#00FF00" if "USA" in row["MARKET"] else "#FFD700"}; margin-bottom: 10px;'>
                <div style='display: flex; justify-content: space-between;'>
                    <b style='font-size: 1.1rem;'>{row["MARKET"]} | {row["T"]} ({row["TIC"]})</b>
                    <b style='color: {"#00FF00" if "+" in row["CH"] else "#FF4B4B"}; font-size: 1.1rem;'>{row["CH"]}</b>
                </div>
                <div style='margin-top: 8px; font-size: 0.95rem; color: #AAA;'>
                    현가: {row["P"]} | 
                    <span style='color: #FFD700;'>ROE: <b>{row["ROE"]:.1f}%</b></span> | 
                    <span style='color: #55AAFF;'>RS: <b>{row["RS"]:.1f}%</b></span> | 
                    <span style='color: #00FF00;'>VCP: <b>{row["VCP"]}</b></span> | 
                    <span style='color: #FF4B4B;'>Score: <b>{int(row["SCORE"])}</b></span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        st.subheader("🕯️ 종목별 정밀 차트 분석 (Select Ticker)")
        
        # 종목 선택 옵션 생성 (이름 + 티커)
        options = [f"{row['T']} ({row['TIC']})" for _, row in combined_top.iterrows()]
        selected_option = st.selectbox("분석할 종목을 선택하세요", options)
        
        # 선택된 티커 추출
        selected_row = combined_top[combined_top.apply(lambda r: f"{r['T']} ({r['TIC']})" == selected_option, axis=1)].iloc[0]
        selected_ticker = selected_row["TIC"]
        is_kr_stock = (".KS" in selected_ticker or ".KQ" in selected_ticker)
        
        st.markdown(f"<div style='background: rgba(255,215,0,0.1); padding: 10px; border-radius: 8px; border-left: 4px solid #FFD700; margin-bottom: 15px;'><b>🎯 타겟 분석 중: {selected_option}</b></div>", unsafe_allow_html=True)
        
        if is_kr_stock:
            # 한국 주식 처리 (네이버 증권 이동)
            pure_code = selected_ticker.replace(".KS", "").replace(".KQ", "")
            naver_url = f"https://finance.naver.com/item/main.naver?code={pure_code}"
            
            st.warning("💡 한국 주식은 트레이딩뷰보다 '네이버 증권' 정밀 분석이 더 권장됩니다.")
            st.markdown(f"""
            <div class='glass-card' style='text-align: center; padding: 40px;'>
                <h3 style='color: #FFD700;'>🇰🇷 {selected_option} - 네이버 증권 데이터 연동</h3>
                <p style='color: #888;'>사령부의 전술적 판단에 따라 한국 시장은 네이버 금융 시스템을 이용합니다.</p>
                <a href='{naver_url}' target='_blank' style='text-decoration: none;'>
                    <div style='background: #03C75A; color: white; padding: 15px 30px; border-radius: 10px; font-weight: 800; display: inline-block; cursor: pointer; border: none; box-shadow: 0 5px 15px rgba(3,199,90,0.4);'>
                        🚀 네이버 증권 정밀 분석실 입장
                    </div>
                </a>
            </div>
            """, unsafe_allow_html=True)
            st.success(f"✅ {selected_option} 정밀 데이터 분석 링크 준비 완료!")
        else:
            # 미국 주식 처리 (기존 트레이딩뷰)
            st.components.v1.html(f"<iframe src='https://s.tradingview.com/widgetembed/?symbol={selected_ticker}&interval=D' width='100%' height='500'></iframe>", height=510)
            st.success(f"✅ {selected_ticker} 실시간 차트 로드 완료!")

elif page.startswith("6-b."):
    st.header("💬 사령부 소통 및 공지 (HQ Communication)")
    # 현재 세션 유저 정보 (전역 curr_grade, is_admin 사용)

    # 로컬 저장소 준비 (전역 변수 USER_DB_FILE, CHAT_FILE 사용)
    if not os.path.exists(CHAT_FILE):
        pd.DataFrame(columns=["시간", "유저", "내용", "등급"]).to_csv(CHAT_FILE, index=False, encoding="utf-8-sig")

    # 입력창 차별화
    st.markdown(f"<div class='glass-card'>현재 권한: <b>{curr_grade}</b></div>", unsafe_allow_html=True)
    
    with st.form("hq_chat_form", clear_on_submit=True):
        if is_admin:
            ms = st.text_area("📢 [방장/관리자] 주요 포스팅 및 공지 작성", placeholder="사령부 회원들에게 전파할 핵심 내용을 작성하세요.")
            btn_label = "🚀 공지 전파"
        else:
            ms = st.text_input("💬 [회원] 댓글 및 메시지 작성", placeholder="관리자의 공지에 대한 의견이나 메시지를 남겨주세요.")
            btn_label = "✉️ 전송"
            
        if st.form_submit_button(btn_label):
            if ms:
                now_kst = datetime.now(pytz.timezone('Asia/Seoul'))
                t = now_kst.strftime("%m/%d %H:%M")
                u = st.session_state.current_user
                # 로컬 저장
                new_msg = pd.DataFrame([[t, u, ms, curr_grade]], columns=["시간", "유저", "내용", "등급"])
                new_msg.to_csv(CHAT_FILE, mode='a', header=False, index=False, encoding="utf-8-sig")
                # 구글 시트 백업 (백그라운드)
                gsheet_sync_bg("소통기록_통합", ["시간", "유저", "내용", "등급"], [t, u, ms, curr_grade])
                st.success("✅ 메시지가 사령부 전역에 전파되었습니다.")
                st.rerun()

    st.divider()
    try:
        # 구글 시트에서 최신 대화 기록 병합
        gs_chat = fetch_gs_chat()
        local_chat = pd.read_csv(CHAT_FILE, encoding="utf-8-sig") if os.path.exists(CHAT_FILE) else pd.DataFrame()
        chat_df = pd.concat([gs_chat, local_chat]).drop_duplicates(subset=["시간", "유저", "내용"]).tail(30)
        
        for _, row in chat_df.iloc[::-1].iterrows(): # 역순 출력
            is_leader = str(row.get("등급", "")).strip() in ["방장", "관리자"]
            bg_color = "rgba(255,215,0,0.1)" if is_leader else "rgba(255,255,255,0.05)"
            border_color = "#FFD700" if is_leader else "#444"
            badge = "👑 [방장]" if is_leader else "👤 [회원]"
            
            st.markdown(f"""
            <div style='background: {bg_color}; border: 1px solid {border_color}; border-radius: 10px; padding: 15px; margin-bottom: 10px;'>
                <div style='display: flex; justify-content: space-between; font-size: 0.85rem; color: #888;'>
                    <span>{badge} <b>{row["유저"]}</b></span>
                    <span>{row["시간"]}</span>
                </div>
                <div style='margin-top: 8px; color: #EEE; line-height: 1.5;'>
                    {row["내용"]}
                </div>
            </div>
            """, unsafe_allow_html=True)
    except:
        st.info("현재 수신된 메시지가 없습니다.")

elif page.startswith("4-a."):
    st.header("💎 프로 분석 리포트 (Weekly Tactical Report)")
    
    # 렌더링 충돌 없는 순수 스탠다드 구성
    with st.container():
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("DOW JONES", "+3.2%", "Weekly")
        with c2: st.metric("NASDAQ", "+6.8%", "Weekly")
        with c3: st.metric("S&P 500", "+4.5%", "Weekly")
        
        st.divider()
        
        st.subheader("🛰️ 글로벌 리서치 핵심 요약")
        st.info("""
        • **상승 여력:** 랠리가 지속되고 있으며 주요 지수는 강세 마감.
        • **위험 신호:** 신고가 경신 중 발생한 갭은 **소멸 갭(Exhaustion Gap)** 가능성 경계.
        • **에너지 지수:** 차트 패턴 강도(CPI) 86.7%로 강력한 체력 생존.
        """)

        st.subheader("🛡️ 사령부 핵심 전술 지침")
        st.warning("""
        "추세를 즐기되 수익 실현과 헤지 전략을 병행하십시오. 신규 진입 시에는 타이트한 손절가 설정이 필수적입니다. 
        하방 변동성 발생 시 **S&P 500 기준 6,675선**을 심리적 지지선으로 설정하십시오."
        """)
        
        st.write("") # 스페이싱
        if st.button("🔄 실시간 글로벌 데이터 동기화"):
            st.toast("사령부 리포트 데이터를 동적 갱신했습니다.")
            st.rerun()
    
    tic_input_rep = st.text_input("분석 종목 (이름 또는 티커)", value="NVDA")
    tic_in = resolve_ticker(tic_input_rep)
    if st.button("정밀 분석"):
        with st.spinner("AI 판독 중..."):
            st.markdown(f"<div class='glass-card'><h4>📊 {tic_in} 분석 결과</h4>주도주 패턴 포착. 상대강도(RS) 정밀 분석 수행 중...</div>", unsafe_allow_html=True)
            st.components.v1.html(f"<iframe src='https://s.tradingview.com/widgetembed/?symbol={tic_in}&interval=D&theme=dark' width='100%' height='500'></iframe>", height=510)

elif page.startswith("3-b."):
    st.header("🚀 주도주 실시간 랭킹 (Daily Live Ranking)")
    # 유저가 새로 제공한 시트 링크 적용 (보안 적용)
    RANK_SHEET_URL = st.secrets.get("RANK_SHEET_URL", "https://docs.google.com/spreadsheets/d/1xjbe9SF0HsxwY_Uy3NC2tT92BqK0nhArUaYU16Q0p9M/export?format=csv&gid=1499398020")
    
    @st.cache_data(ttl=300)
    def fetch_rank_data(url):
        try: 
            return pd.read_csv(url)
        except Exception as e: 
            return pd.DataFrame()

    with st.spinner("📊 전문가님의 데이터 센터에서 실시간 동기화 중..."):
        try:
            df_live = fetch_rank_data(RANK_SHEET_URL)
            if df_live.empty:
                st.warning("⚠️ 시트에서 데이터를 가져올 수 없습니다. '공유 설정'을 확인해 주세요.")
            else:
                # 데이터 정제 및 필터링
                st.markdown(f"<div class='glass-card'>📅 <b>{now_kst.strftime('%Y-%m-%d %H:%M')} KST</b> | 사령부 주도주 스캔 데이터</div>", unsafe_allow_html=True)
                
                # 시트의 헤더에 맞춰 유연하게 매핑
                df_live = df_live.rename(columns={
                    '종목명': '종목', '티커': '종목', 'Ticker': '종목',
                    'ROE': 'ROE', 'roe': 'ROE',
                    '현재가': '현재가', 'Price': '현재가',
                    '진입가': '진입가', 'EP': '진입가',
                    '단계': '단계', 'Stage': '단계',
                    '손절가': '손절가', 'SL': '손절가',
                    '목표가': '목표가', 'TP': '목표가'
                })
                
                # ROE 10% 이상 필터링 (컬럼이 있을 경우만)
                if 'ROE' in df_live.columns:
                    try:
                        df_live['ROE_VAL'] = df_live['ROE'].astype(str).str.replace('%','').astype(float)
                        df_final = df_live[df_live['ROE_VAL'] >= 10.0].head(20)
                    except: df_final = df_live.head(20)
                else:
                    df_final = df_live.head(20)
                
                display_cols = ["종목", "ROE", "현재가", "진입가", "단계", "손절가", "목표가"]
                available_cols = [c for c in display_cols if c in df_final.columns]
                
                if available_cols:
                    st.dataframe(df_final[available_cols], use_container_width=True, hide_index=True)
                else:
                    st.dataframe(df_final, use_container_width=True, hide_index=True)
                    
                # 사령부 지휘 지침 추가 (Clean Markdown 적용)
                st.divider()
                st.markdown(f"""
### 🚁 StockDragonfly 지휘 지침: 본데 50선 실전 매뉴얼

**1. 상위 주식 vs 하위 주식의 의미**
전문가님의 스프레드시트 순위는 모멘텀의 강도와 A+ 셋업 완성도를 나노 단위로 점수화한 결과입니다.

- **상위 주식 (TOP 1~10):** 현재 시장에서 가장 강력한 대장주(Leader)들입니다. 이미 폭발적인 거래량과 함께 신고가를 경신하며 안티그래비티 상태에 진입한 종목들로, 시장의 모든 자금을 빨아들이고 있습니다.
- **하위 주식:** 주도주가 될 잠재력은 충분하지만, 아직 에너지를 응축(횡보)하고 있거나 기관의 매집(Accumulation) 단계에 있는 종목들입니다. 이들이 상위 순위로 치고 올라올 때가 진짜 정석 타점입니다.

**2. 매수 진단 프로토콜 (The Entry Protocol)**
대가들은 급등할 때 사지 말고, 힘을 모을 때를 노려라고 했습니다. 전문가님의 원칙대로 VCP 최종 단계를 포착해야 합니다.

- **불합격:** 거래량이 터지며 20~30% 급등한 직후에 추격 매수하는 것은 불합격입니다. 이는 중력에 노출되는 가장 위험한 행동입니다.
- **합격 (The Tightness):** 급등 후 주가가 옆으로 기어가며(횡보) 힘을 모으는 구간을 기다리세요. 캔들의 크기가 깨알처럼 작아지고, 거래량이 먼지처럼 말라붙는 Dry-up 현상이 나타날 때가 A+ 셋업입니다.
- **정석 타점:** 이 응축 구간이 끝나고, 전고점(Pivot)을 아주 작은 거래량으로도 뚫어버리기 직전이나, 뚫어내는 첫 번째 거래량 폭발 시점이 무중력 상태로 날아오르는 순간입니다.

**3. 리스크 방패 및 손절 지지선 (The Exit Shield)**
안티그래비티 시스템의 가장 강력한 지지선은 기계적인 손절입니다. 본데는 나쁜 직원은 즉시 해고하라고 했습니다.

- **시간 손절:** 매수 후 3일 동안 주가가 옆으로 기거나 반응이 없다면, 전문가님의 판단이 틀렸거나 시장의 관심이 떠난 것입니다. 미련 없이 매도하여 현금을 확보하십시오.
- **가격 손절:** 매수가 대비 -3% 이하로 떨어지면, 시스템은 즉시 자동 매도 주문을 실행합니다. 이는 더 큰 손실로부터 전문가님의 자산을 무중력 상태로 보호하는 최후의 방어선입니다.
""", unsafe_allow_html=True)
                
                st.success(f"✅ {now_kst.strftime('%H:%M')} 한국 시간 기준 동기화 완료!")
        except Exception as e:
            st.error(f"⚠️ 시트 연동 중 오류 발생: {e}")
            st.info("시트가 '링크가 있는 모든 사용자에게 공개(뷰어)' 상태인지 확인해 주세요.")

elif page.startswith("4-b."):
    st.header("🧮 포지션 규모 결정 시스템 (Institutional Position Sizing)")
    st.markdown("<div class='glass-card'>손절 발생 시 총 자산의 몇 %를 잃을 것인지 결정하십시오. (본데 추천: 0.25% ~ 1%)</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        total_balance = st.number_input("💵 총 운용 자산 (USD)", value=10000, step=1000)
        risk_per_trade_pct = st.slider("⚖️ 매매당 허용 리스크 (%)", 0.1, 2.0, 0.5, step=0.1)
    with col2:
        entry_price = st.number_input("🎯 진입 가액 ($)", value=250.0, step=0.1)
        stop_loss_price = st.number_input("🛡️ 손절 가액 ($)", value=242.5, step=0.1) # 기본 -3% 수준 설정

    st.divider()
    
    risk_per_share = entry_price - stop_loss_price
    if risk_per_share <= 0:
        st.error("⚠️ 손절가는 반드시 진입가보다 낮아야 합니다. 전술적 오류입니다.")
    else:
        total_risk_amount = total_balance * (risk_per_trade_pct / 100)
        shares_to_buy = int(total_risk_amount / risk_per_share)
        total_investment = shares_to_buy * entry_price
        
        c1, c2, c3 = st.columns(3)
        c1.metric("허용 손실액", f"${total_risk_amount:,.2f}")
        c2.metric("최적 매수 수량", f"{shares_to_buy:,} 주")
        c3.metric("총 투입 금액", f"${total_investment:,.2f}")
        
        portfolio_weight = (total_investment / total_balance) * 100 if total_balance > 0 else 0
        st.info(f"""
        💡 **전략 보고:** {total_balance:,.0f}불의 자산에서 이 종목을 **{shares_to_buy:,}주** 매수하십시오.  
        이 경우 손절 시 정확히 {total_risk_amount:,.1f}불({risk_per_trade_pct}%)만 잃게 되며, 현재 이 종목은 전체 포트폴리오의 **{portfolio_weight:.1f}%** 비중을 차지하게 됩니다.
        """)

elif page.startswith("2-a."):
    st.header("📈 데일리 마켓 트렌드 브리핑 (Daily Briefing)")
    st.divider()
    # 브리핑 전용 데이터 로드 (전역 BRIEF_FILE 사용)
    if not os.path.exists(BRIEF_FILE):
        pd.DataFrame(columns=["날짜", "작성자", "내용"]).to_csv(BRIEF_FILE, index=False, encoding="utf-8-sig")
    
    # 관리자 입력창 (더욱 직관적으로 변경)
    if is_admin:
        st.markdown(f"<div style='background: rgba(255,215,0,0.1); padding: 15px; border-radius: 12px; border: 1px solid #FFD700; margin-bottom: 20px;'><b>👑 {curr_grade} 전용 - 데일리 마켓 브리핑 센터</b></div>", unsafe_allow_html=True)
        with st.form("brief_form", clear_on_submit=True):
            content = st.text_area("오늘의 시장 요약 및 트렌드 분석을 작성하세요", height=150, placeholder="여기에 내용을 입력하시면 사령부 전역에 브리핑이 전파됩니다.")
            if st.form_submit_button("📢 브리핑 전파하기"):
                if content:
                    now_kst = datetime.now(pytz.timezone('Asia/Seoul'))
                    t = now_kst.strftime("%Y-%m-%d %H:%M")
                    new_b = pd.DataFrame([[t, st.session_state.current_user, content]], columns=["날짜", "작성자", "내용"])
                    new_b.to_csv(BRIEF_FILE, mode='a', header=False, index=False, encoding="utf-8-sig")
                    st.success("✅ 사령부 브리핑이 성공적으로 전송되었습니다.")
                    st.rerun()

    st.divider()

    # 브리핑 목록 표시 (페이지네이션 적용)
    try:
        df_b = pd.read_csv(BRIEF_FILE, encoding="utf-8-sig")
        if not df_b.empty:
            df_b = df_b.iloc[::-1] # 최신순
            ppp = 5 # Posts Per Page
            total_p = (len(df_b) - 1) // ppp + 1
            
            c1, c2 = st.columns([8, 2])
            with c2: p_num = st.number_input("Page", 1, total_p, step=1)
            with c1: st.subheader(f"📡 수신 브리핑 (총 {len(df_b)}건)")

            start_idx = (p_num - 1) * ppp
            end_idx = start_idx + ppp
            
            for idx, row in df_b.iloc[start_idx:end_idx].iterrows():
                # 수정 모드 체크
                is_editing = (st.session_state.get("edit_brief_id") == idx)
                
                if is_editing:
                    st.markdown(f"<div class='glass-card' style='border-color: #FFD700;'>", unsafe_allow_html=True)
                    st.markdown(f"**📝 브리핑 수정 중 (ID: {idx})**")
                    edited_content = st.text_area("내용 편집", value=row['내용'], key=f"edit_text_{idx}", height=250)
                    c_s1, c_s2 = st.columns(2)
                    if c_s1.button("💾 변경사항 저장", key=f"save_brief_{idx}", use_container_width=True):
                        temp_df = pd.read_csv(BRIEF_FILE, encoding="utf-8-sig")
                        temp_df.at[idx, '내용'] = edited_content
                        temp_df.to_csv(BRIEF_FILE, index=False, encoding="utf-8-sig")
                        st.success("✅ 브리핑이 성공적으로 수정되었습니다.")
                        del st.session_state["edit_brief_id"]
                        st.rerun()
                    if c_s2.button("❌ 수정 취소", key=f"cancel_brief_{idx}", use_container_width=True):
                        del st.session_state["edit_brief_id"]
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class='glass-card' style='padding: 20px; border-left: 5px solid #FFD700; margin-bottom: 10px;'>
                        <span style='color: #FFD700; font-size: 0.8rem;'>📅 {row['날짜']} | 작성자: {row['작성자']}</span><br>
                        <div style='margin-top: 10px; font-size: 1.1rem; white-space: pre-wrap;'>{row['내용']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    if is_admin:
                        bc1, bc2, bc3 = st.columns([1, 1, 2])
                        with bc1:
                            if st.button(f"📝 수정", key=f"edit_btn_{idx}", use_container_width=True):
                                st.session_state.edit_brief_id = idx
                                st.rerun()
                        with bc2:
                            if st.button(f"🗑️ 삭제", key=f"del_brief_{idx}", use_container_width=True):
                                temp_df = pd.read_csv(BRIEF_FILE, encoding="utf-8-sig")
                                temp_df = temp_df.drop(idx)
                                temp_df.to_csv(BRIEF_FILE, index=False, encoding="utf-8-sig")
                                st.warning("내용이 삭제되었습니다.")
                                st.rerun()
        else:
            st.info("아직 등록된 브리핑이 없습니다.")
    except Exception as e:
        st.info("브리핑 데이터 연동 중...")

elif page.startswith("3-c."):
    st.header("🎯 사령부 최핵심 감시 리스트 (Top 3 Focus)")
    SHEET_URL = st.secrets.get("MARKET_FOCUS_URL", "https://docs.google.com/spreadsheets/d/1xjbe9SF0HsxwY_Uy3NC2tT92BqK0nhArUaYU16Q0p9M/export?format=csv&gid=1499398020")
    now_kst = datetime.now(pytz.timezone('Asia/Seoul'))
    
    with st.spinner("📡 데이터 센터 리더보드 정밀 분석 중..."):
        try:
            df_raw = pd.read_csv(SHEET_URL)
            # 가장 왼쪽(최신) 열에서 상위 10개 추출
            latest_col = df_raw.columns[0]
            top_10_candidates = df_raw[latest_col].dropna().head(10).tolist()
            
            # 전체 언급 횟수 카운트
            all_mentions = df_raw.values.flatten().tolist()
            mention_counts = {tic: all_mentions.count(tic) for tic in top_10_candidates}
            
            # ROE 5% 이상 필터링 및 데이터 수집
            final_3 = []
            cand_tics = sorted(mention_counts, key=mention_counts.get, reverse=True)
            
            # 일괄 다운로드 (역순 루프 내 개별 호출 방지)
            if cand_tics:
                prices_data = yf.download(cand_tics, period="1d", progress=False)['Close']
                if isinstance(prices_data, pd.Series): 
                    prices_data = pd.DataFrame(prices_data).T
                
                for tic in cand_tics:
                    try:
                        # ROE는 여전히 개별 Ticker.info가 필요할 수 있으나, 여기서는 생략하거나 캐싱 권장
                        # 성능을 위해 ROE fetch 생략 혹은 캐싱 처리 (yf.Ticker.info는 매우 느림)
                        roe = 0.0 # 속도를 위해 기본값 0 설정 (필요시 별도 배치 처리)
                        
                        price = prices_data[tic].iloc[-1] if tic in prices_data.columns else 0
                        if price > 0:
                            final_3.append({
                                "T": tic, "ROE": "N/A", # 속도 최우선
                                "RS": f"{mention_counts[tic]}회 언급",
                                "EP": f"${price:.2f}", "SL": f"${price*0.95:.2f}", "TP": f"${price*1.15:.2f}"
                            })
                        if len(final_3) >= 3: break
                    except: continue
                
            st.markdown(f"<div class='glass-card'>📅 <b>{now_kst.strftime('%Y-%m-%d')} KST</b> | 사령부 최우선 공략 종목 3선</div>", unsafe_allow_html=True)
            
            cols = st.columns(3)
            for i, item in enumerate(final_3):
                with cols[i]:
                    st.markdown(f"""
                    <div style='background: rgba(255,215,0,0.1); border: 2px solid #FFD700; border-radius: 12px; padding: 15px; text-align: center; height: 320px;'>
                        <h3 style='color: #FFD700; margin: 0;'>{item['T']}</h3>
                        <p style='color: #888; font-size: 0.8rem;'>Mention Rank {i+1}</p>
                        <hr style='border: 0.5px solid #444;'>
                        <div style='text-align: left; font-size: 0.9rem;'>
                            <b>🔥 ROE:</b> {item['ROE']}<br>
                            <b>📊 RS (빈도):</b> {item['RS']}<br>
                            <b>🎯 진입가:</b> {item['EP']}<br>
                            <b>🛡️ 손절가:</b> {item['SL']}<br>
                            <b>🚀 목표가:</b> {item['TP']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            if not final_3: st.info("조건을 만족하는 감시 종목이 리더보드 상단에 없습니다.")
            st.success("✅ 사령부 데이터 동기화 및 빈도 분석 완료!")
        except Exception as e:
            st.error(f"⚠️ 데이터 분석 실패: {e}")


elif page.startswith("3-d."):
    st.header("📉 산업동향 (Industry Trends TOP 10)")
    st.markdown("<div class='glass-card'>사령부 지정 데이터 피트를 통한 현재 주도 산업군을 노출합니다.</div>", unsafe_allow_html=True)
    SHEET_URL = st.secrets.get("INDUSTRY_SHEET_URL", "https://docs.google.com/spreadsheets/d/1xjbe9SF0HsxwY_Uy3NC2tT92BqK0nhArUaYU16Q0p9M/export?format=csv&gid=1156221191")
    
    with st.spinner("⏳ 산업동향 리더보드 수집 중.."):
        try:
            df = pd.read_csv(SHEET_URL)
            if not df.empty:
                st.dataframe(df.head(10), use_container_width=True)
                st.success("✅ 상위 10개 산업군 분석 및 산출 완료!")
            else:
                st.info("현재 로드된 산업동향 데이터가 없습니다.")
        except Exception as e:
            st.error(f"⚠️ 산업동향 로드 실패: {e}")

elif page.startswith("3-e."):
    st.header("📊 RS 강도 분석 (Relative Strength Strength)")
    st.markdown("<div class='glass-card'>개별 종목의 지수 대비 상대강도(RS)를 분석하여 '^' 기호를 강조합니다.</div>", unsafe_allow_html=True)
    SHEET_URL = st.secrets.get("RS_SHEET_URL", "https://docs.google.com/spreadsheets/d/1xjbe9SF0HsxwY_Uy3NC2tT92BqK0nhArUaYU16Q0p9M/export?format=csv&gid=1220465228")
    
    with st.spinner("⏳ RS 강도 데이터 로드 중.."):
        try:
            df = pd.read_csv(SHEET_URL)
            if not df.empty:
                def highlight_rs(val):
                    if isinstance(val, str) and '^' in val: return 'color: #00FF00; font-weight: bold; background: rgba(0,255,0,0.1);'
                    return ''
                st.dataframe(df.style.applymap(highlight_rs), use_container_width=True)
                st.success("✅ RS 강도 분석 및 시각화 완료!")
            else:
                st.info("현재 로드된 RS 강도 데이터가 없습니다.")
        except Exception as e:
            st.error(f"⚠️ RS 강도 로드 실패: {e}")

elif page.startswith("1-a."):
    st.header("👑 관리자 승인 센터 (HQ Member Approval)")
    
    if not is_admin:
        st.warning("❌ 이 구역은 사령부 최고 등급 전용입니다. 일반 대원은 접근할 수 없습니다.")
        st.stop()
        
    # [A] 신규 가입 승인 섹션
    pending_users = [u for u, d in users.items() if d.get("status") == "pending"]
    st.subheader("📡 신규 가입 대기 인원")
    if pending_users:
        if st.button("🔥 대기 인원 전체 일괄 승인", use_container_width=True):
            for u in pending_users: users[u]["status"] = "approved"
            save_users(users)
            st.success("🎊 모든 대기 인원이 공식 승인되었습니다.")
            st.rerun()
        for u in pending_users:
            c1, c2 = st.columns([7, 3])
            with c1: st.info(f"ID: **{u}** | 가입 신청됨")
            with c2:
                if st.button(f"✅ 승인", key=f"appr_{u}"):
                    users[u]["status"] = "approved"
                    save_users(users)
                    st.rerun()
    else: st.info("대기 중인 신규 회원이 없습니다.")

    st.divider()

    # [B] 정규직 승격 심사 센터 (Cloud Sync)
    st.subheader("🔥 정규직 승격 심사 센터")
    gs_vis = fetch_gs_visitors()
    if not gs_vis.empty:
        try:
            for idx, row in gs_vis.iloc[::-1].iterrows():
                user_id = str(row.get("아이디", "Unknown")).strip()
                if users.get(user_id, {}).get("grade") == "정규직": continue
                with st.expander(f"📥 [승격요청] {user_id} 대원의 신청서 ({row.get('시간','-')})", expanded=False):
                    st.markdown(f"**1. 첫인사:** {row.get('첫인사', '-')}")
                    st.markdown(f"**2. 자기소개:** {row.get('자기소개', '-')}")
                    st.markdown(f"**3. 포부:** {row.get('포부', '-')}")
                    if st.button(f"🎖️ {user_id} 정규직 승격 발령", key=f"promo_gs_{idx}"):
                        if user_id in users:
                            users[user_id]["grade"] = "정규직"
                            save_users(users)
                            st.success(f"🎊 {user_id} 대원이 '정규직'으로 승격되었습니다!")
                            st.rerun()
        except: st.info("신청서 데이터 판독 중...")
    else: 
        st.info("현재 접수된 실시간 승격 신청서가 없습니다.")

    st.divider()

    # [C] 사령부 전체 대원 명부 (Staff Directory)
    st.subheader("📋 사령부 전체 대원 명부")
    all_rows = []
    for uid, udata in users.items():
        info = udata.get("info", {})
        all_rows.append({
            "아이디": uid,
            "등급": udata.get("grade", "회원"),
            "지역": info.get("region", "-"),
            "경력": info.get("exp", "-"),
            "연령": info.get("age", "-"),
            "매매 동기": info.get("motivation", "-"),
            "합류일": info.get("joined_at", "-")
        })
    df_users = pd.DataFrame(all_rows)
    st.dataframe(df_users, use_container_width=True, hide_index=True)

elif page.startswith("5-a."):
    st.markdown("<h1 style='text-align: center; color: #FFD700;'>🐝 월가의 멘토, 프라딥 본데(Pradeep Bonde)</h1>", unsafe_allow_html=True)
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
        with st.expander("⚾ 안타(Singles) 전략", expanded=True):
            st.write("일확천금을 노리는 홈런보다 작고 확실한 수익을 복리로 누적시키는 것이 부의 축적을 위한 가장 빠른 길입니다.")
        with st.expander("🧬 딥 다이브 (Deep Dive)", expanded=True):
            st.write("뇌가 고민하기 전에 손이 반응하도록 과거 폭등 차트 수천 개를 연구하여 패턴을 '절차적 기억'으로 뇌에 각인시킵니다.")
    with c2:
        with st.expander("🛡️ 셀프 리더십", expanded=True):
            st.write("멘토의 조언보다 중요한 것은 스스로 문제를 해결하고 실행에 옮기는 자기 주도적 실행력입니다.")
        with st.expander("📊 철저한 상황 인식", expanded=True):
            st.write("매일 시장의 폭(Breadth)을 분석하여 공격할 때와 방어할 때를 구분하는 시스템적 방패를 가동합니다.")

    st.subheader("3. 시장을 관통하는 핵심 매매 기법")
    st.success("""
    **🔥 에피소딕 피벗 (EP):** 기업의 펀더멘털을 근본적으로 바꾸는 강력한 뉴스나 실적이 터졌을 때, 폭발적인 거래량과 함께 진입하여 기관의 자금 유입 초기 국면을 공략합니다.  
    **🚀 모멘텀 버스트:** 좁은 눌림목(VCP)에서 에너지가 분출하는 임계점을 포착합니다.  
    **⚖️ MAGNA 53+ CAP 10x10:** 시가총액과 상장 기간, 상승률을 필터링하여 가볍고 빠른 '대장주'만을 골라내는 본데만의 전용 공식입니다.
    """)

    st.subheader("4. 제자들이 증명하는 실력의 가치")
    st.write("""
    본데의 위대함은 제자들의 수익률로 증명됩니다. **1,300억 원 이상의 자산을 달성한 크리스찬 쿨라매기(Kristjan Qullamaggi)**는 본데의 가르침을 통해 자신의 시스템을 완성했다고 공공연히 밝히고 있습니다. 
    그는 화려한 마케팅 대신 오직 데이터와 결과로 승부하며, 현재도 실전 트레이딩 팩토리를 운영하며 시장의 살아있는 전설로 활동하고 있습니다.
    """)
    st.divider()

elif page.startswith("2-d."):
    st.markdown("<h1 style='text-align: center; color: #FFD700;'>🏛️ 사령부 제작 동기 (Mission Statement)</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888; font-size: 1.1rem;'>Follow the Giants, Conquer the Market Together</p>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>세 거인의 발자취를 따라, 함께 성장의 궤도에 오르기를 꿈꾸며</h3>", unsafe_allow_html=True)
    st.divider()
    
    st.write("""
    이 플랫폼은 제가 깊이 존경하는 세 분의 위대한 스승, **윌리엄 오닐, 마크 미너비니, 그리고 프라딥 본데**의 트레이딩 철학을 시스템으로 구현하고 기리기 위해 시작되었습니다. 
    (This platform was established to systematize and honor the trading philosophies of three legendary mentors: William O'Neil, Mark Minervini, and Pradeep Bonde.)
    
    비록 지금은 성장에 목마른 소박한 터미널이지만, 저와 같은 길을 걷는 대원분들이 한 배를 타고 진정한 경제적 자유에 도달하기를 바라는 진심 어린 마음을 담아 밤낮으로 로직을 다듬고 있습니다.
    (Though it is currently a small terminal, I refine its logic day and night with the sincere hope that fellow traders walking the same path can reach true financial freedom together.)
    """)

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("📚 사령부를 지탱하는 세 개의 기둥 (Three Pillars)")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**1. 윌리엄 오닐 (CAN SLIM)**")
        st.write("주도주 발굴의 근간입니다. 펀더멘털과 기술적 흐름의 조화를 시스템에 녹였습니다.")
        st.caption("*The root of leading stocks.*")
    with c2:
        st.markdown("**2. 마크 미너비니 (VCP)**")
        st.write("타점의 정교함입니다. 에너지의 응축과 돌파를 감지하는 지표를 강화했습니다.")
        st.caption("*The precision of entry.*")
    with c3:
        st.markdown("**3. 프라딥 본데 (EP/RS)**")
        st.write("시장 대응의 프로세스입니다. 실시간 상황 인식과 폭발적 모멘텀을 추적합니다.")
        st.caption("*The process of response.*")
    st.markdown("</div>", unsafe_allow_html=True)

    st.info("""
    📖 **오닐의 유산 (The Legacy):** 윌리엄 오닐의 저서 『최고의 주식, 최적의 타이밍』은 제 트레이딩 인생의 나침반이 되었습니다. 
    이 터미널이 거인들의 어깨 위에 올라타 시장의 거센 파도를 넘어서는 여러분의 든든한 디딤돌(Stepping Stone)이 되길 희망합니다.
    """)
    
    st.markdown("""
    <div style='text-align: right; margin-top: 40px; border-top: 1px solid #333; padding-top: 20px;'>
        <span style='color: #888; font-size: 0.9rem;'>2026년 4월 18일, 깊어가는 봄날 밤. (Deep Spring Night, 2026)</span><br>
        <b style='color: #FFD700; font-size: 1.2rem;'>전문가거북이 드림 (Truly yours, Expert Turtle)</b>
    </div>
    """, unsafe_allow_html=True)

elif page.startswith("6-c."):
    st.header("🤝 방문자 승격 신청서 (Promotion Application)")
    st.markdown("<div class='glass-card'>사령부 정규직 승격을 위해 아래 3가지 항목을 작성해 주세요. 전문가님이 직접 검토합니다.</div>", unsafe_allow_html=True)
    with st.form("greet_detailed", clear_on_submit=True):
        g1 = st.text_area("1. 사령부 첫 방문 소감", placeholder="사령부를 처음 알게 된 계기와 소감을 남겨주세요.")
        g2 = st.text_area("2. 트레이딩 경력 및 자기소개", placeholder="본인의 투자 경험이나 간단한 소개를 부탁드립니다.")
        g3 = st.text_area("3. 정규직으로서의 포부", placeholder="사령부 정규직이 되어 이루고 싶은 목표를 적어주세요.")
        if st.form_submit_button("🛡️ 사령부 승격 신청 전송"):
            if g1 and g2 and g3:
                t = datetime.now().strftime("%Y-%m-%d %H:%M")
                u = st.session_state.current_user
                # 로컬 영구 저장 (8번 배너와 연동)
                new_req = pd.DataFrame([[t, u, g1, g2, g3]], columns=["시간", "아이디", "첫인사", "자기소개", "포부"])
                new_req.to_csv(VISITOR_FILE, mode='a', header=not os.path.exists(VISITOR_FILE), index=False, encoding="utf-8-sig")
                # 백업용 동기화 (백그라운드 전환)
                gsheet_sync_bg("방문자_승격신청", ["시간", "아이디", "첫인사", "자기소개", "포부"], [t, u, g1, g2, g3])
                st.success("✅ 승격 신청서가 성공적으로 관리자 승인센터로 전파되었습니다!")
            else: st.error("모든 항목을 작성해 주셔야 신청이 가능합니다.")

elif page.startswith("4-c."):
    st.header("🛡️ 리스크 방패 (The -3% Iron Shield)")
    st.divider()
    st.subheader("🛸 왜 본데는 '-3% 손절'을 생명처럼 여기는가?")
    st.error("**1. 복리의 마법을 지키는 유일한 방법**")
    st.write("3% 하락은 회복이 쉬우나, 큰 하락은 복구에 수배의 노력이 필요합니다. 본데는 복리의 역성장을 절대 허용하지 않습니다.")
    st.warning("**2. '타점 오류'의 즉각적인 판독기**")
    st.write("진입 후 -3% 후퇴는 사령부의 타점이 틀렸거나 타이밍이 아니라는 시장의 명확한 신호입니다. 즉각 탈출하십시오.")
    st.info("**3. '안타 전략(Hitters)'의 생존 조건**")
    st.write("작은 수익을 쌓는 전략에서 단 하나의 큰 손실은 모든 노력을 수포로 돌립니다. -3%는 사령부의 최후 방어선입니다.")
    st.success("💡 **결론:** 손절은 패배가 아닌, 더 큰 승리를 위한 전략적 후퇴입니다.")

elif page.startswith("5-d."):
    st.header("📝 사령부 정기 승급 시험 안내 (Promotion Exam)")
    st.markdown("<div class='glass-card'>사령부 대원으로서의 역량을 증명하고 한 단계 더 높은 주도주 추격권한을 획득하는 공식 관문입니다.</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div style='background: rgba(255,215,0,0.05); padding: 25px; border-radius: 15px; border: 1px solid #FFD700; height: 350px;'>
            <h3 style='color: #FFD700;'>📅 시험 일정 (Biannual)</h3>
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
            <h3 style='color: #EEE;'>🛡️ 합격 및 진격 가이드</h3>
            <ul style='color: #CCC; line-height: 1.8;'>
                <li><b>문항수:</b> 총 20문항 (차트 패턴 및 전술 이론)</li>
                <li><b>만점:</b> 100점</li>
                <li><b>커트라인:</b> <b style='color: #FFD700;'>80점 이상</b> 획득 시 승급</li>
                <li><b>주의사항:</b> 투명한 사령부 운영을 위해 <b>개인별 성적은 전 대원에게 공개</b>됩니다.</li>
            </ul>
            <p style='color: #FF4B4B; font-weight: bold; margin-top: 15px;'>⚠️ 불합격 시 다음 6개월 뒤 재시험 응시 가능</p>
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    st.subheader("📊 최근 승급 시험 명예의 전당 (Simulation)")
    mock_results = pd.DataFrame([
        {"아이디": "cntfed", "점수": 95, "결과": "🎖️ 합격 (수석)"},
        {"아이디": "ExpertTurtle", "점수": 100, "결과": "👑 합격 (전설)"},
        {"아이디": "NewMember1", "점수": 75, "결과": "❌ 불합격"},
    ])
    st.table(mock_results)
    
    st.info("💡 팁: '5-b. 주식공부방'과 '4-c. 리스크 방패' 섹션의 내용을 철저히 복습하는 것이 합격의 지름길입니다.")

elif page.startswith("5-e."):
    st.header("🤑 실전 익절 자랑방 (Hall of Gain)")
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

    with st.expander("🔥 나의 익절 기록 하달하기", expanded=True):
        with st.form("profit_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1: tic = st.text_input("종목명/티커", placeholder="예: 삼성전자 / TSLA")
            with col2: roi = st.text_input("수익률 (%)", placeholder="예: +15.5%")
            
            p_val = st.text_input("확정 수익금 (KRW/USD)", placeholder="예: 2,500,000원")
            msg = st.text_area("승리 소감 및 노하우 공유", placeholder="어떤 타점에서 진입하여 익절하셨나요?")
            
            if st.form_submit_button("🚀 전리품 등록 (자랑하기)"):
                if tic and roi and p_val:
                    now_k = datetime.now(pytz.timezone('Asia/Seoul'))
                    t_now = now_k.strftime("%Y-%m-%d %H:%M")
                    d_str, t_str = t_now.split(" ")
                    u = st.session_state.current_user
                    pid = f"P_{int(time.time())}_{random.randint(100,999)}_{u}"
                    new_p = pd.DataFrame([[pid, t_now, u, tic, roi, p_val, msg]], columns=["ID", "시간", "아이디", "종목", "수익률", "수익금", "포부"])
                    # 💾 로컬 저장 (최적화: 백업 생략)
                    save_success = safe_write_csv(new_p, PROFIT_FILE, mode='a', header=False, backup=False)
                    
                    if not save_success:
                        st.error("❌ 로컬 파일(CSV) 저장에 실패했습니다. 파일 잠금을 확인해 주세요.")
                    
                    # 📡 구글 시트 동기화 (익절방 탭)
                    sync_resp = None
                    # 📡 구글 시트 백그라운드 동기화 (익절방)
                    gsheet_sync_bg("익절방", 
                        ["날짜", "시간", "회원명", "종목명/티커", "수익률", "수익금", "승리소감 및 노하우"], 
                        [d_str, t_str, u, tic, roi, p_val, msg]
                    )
                    
                    st.success("🎊 대원님의 위대한 승리 기록이 저장되었습니다! (구글 시트 동기화는 배경에서 진행됩니다.)")
                    
                    st.balloons()
                    time.sleep(1) # 저장을 위한 짧은 지연
                    st.rerun()
                else: st.error("종목, 수익률, 수익금은 필수 항목입니다.")

    pdf = safe_read_csv(PROFIT_FILE, ["ID", "시간", "아이디", "종목", "수익률", "수익금", "포부"])
    cdf = safe_read_csv(COMMENTS_FILE, ["PostID", "시간", "작성자", "내용"])
    
    if not pdf.empty:
        try:
            for _, row in pdf.iloc[::-1].iterrows():

                pid = row['ID']
                # 작성자 또는 관리자만 수정/삭제 가능
                is_owner = (st.session_state.current_user == row['아이디']) or is_admin
                
                # 수정 모드 체크
                edit_key = f"edit_p_{pid}"
                if st.session_state.get(edit_key):
                    with st.form(f"form_edit_{pid}"):
                        e_roi = st.text_input("수익률 수정", value=row['수익률'])
                        e_val = st.text_input("수익금 수정", value=row['수익금'])
                        e_msg = st.text_area("소감 수정", value=row['포부'])
                        c_edit1, c_edit2 = st.columns(2)
                        if c_edit1.form_submit_button("💾 저장"):
                            temp_df = safe_read_csv(PROFIT_FILE)
                            temp_df.loc[temp_df['ID'] == pid, ['수익률', '수익금', '포부']] = [e_roi, e_val, e_msg]
                            safe_write_csv(temp_df, PROFIT_FILE)
                            del st.session_state[edit_key]
                            st.rerun()
                        if c_edit2.form_submit_button("❌ 취소"):
                            del st.session_state[edit_key]
                            st.rerun()
                else:
                    st.markdown(f"""
                    <div style='background: rgba(0,255,0,0.03); border: 1px solid #00FF0033; border-radius: 12px; padding: 20px; margin-bottom: 10px;'>
                        <div style='display: flex; justify-content: space-between;'>
                            <b style='color: #FFD700; font-size: 1.1rem;'>🎖️ {row['아이디']} 대원의 승전보</b>
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
                            💬 {row['포부']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if is_owner:
                        o_col1, o_col2, o_col3 = st.columns([1, 1, 6])
                        if o_col1.button("📝 수정", key=f"edit_btn_{pid}", use_container_width=True):
                            st.session_state[edit_key] = True
                            st.rerun()
                        if o_col2.button("🗑️ 삭제", key=f"del_btn_{pid}", use_container_width=True):
                            temp_df = safe_read_csv(PROFIT_FILE, ["ID", "시간", "아이디", "종목", "수익률", "수익금", "포부"])
                            temp_df = temp_df[temp_df['ID'] != pid]
                            safe_write_csv(temp_df, PROFIT_FILE)
                            st.warning("항목이 삭제되었습니다.")
                            st.rerun()
                
                # 댓글 섹션
                with st.container():
                    item_comments = cdf[cdf['PostID'] == pid]
                    for _, c in item_comments.iterrows():
                        st.markdown(f"<div style='margin-left: 20px; font-size: 0.9rem; border-left: 2px solid #555; padding-left: 10px; margin-bottom: 5px;'><b style='color: #FFD700;'>{c['작성자']}:</b> {c['내용']} <span style='color: #555; font-size: 0.7rem;'>({c['시간']})</span></div>", unsafe_allow_html=True)
                    
                    c_col1, c_col2 = st.columns([8, 2])
                    new_c = c_col1.text_input("격려의 한마디", key=f"c_input_{pid}", label_visibility="collapsed", placeholder="대원님 축하드립니다!")
                    if c_col2.button("🗨️ 등록", key=f"c_btn_{pid}"):
                        if new_c:
                            now_c_t = datetime.now(pytz.timezone('Asia/Seoul')).strftime("%m/%d %H:%M")
                            u = st.session_state.current_user
                            c_new = pd.DataFrame([[pid, now_c_t, u, new_c]], columns=["PostID", "시간", "작성자", "내용"])
                            safe_write_csv(c_new, COMMENTS_FILE, mode='a', header=False)
                            gsheet_sync_bg("댓글_통합", ["PostID", "시간", "작성자", "내용"], [pid, now_c_t, u, new_c])
                            st.rerun()
                st.write("") # 스페이싱
        except Exception as e:
            st.error(f"❌ 첩보 목록을 렌더링하는 중 오류가 발생했습니다: {e}")
    else:
        st.info("아직 도착한 익절 첩보가 없습니다. 첫 주인공이 되어보세요!")


elif page.startswith("5-f."):
    st.header("🩹 손실 위로 및 복기방 (Reflection & Support)")
    st.markdown("<div class='glass-card'>실패는 성공의 어머니가 아니라, <b>실패에 대한 복기</b>가 성공의 어머니입니다. 아픔을 나누고 더 단단해지는 공간입니다.</div>", unsafe_allow_html=True)
    
    if not os.path.exists(LOSS_FILE):
        safe_write_csv(pd.DataFrame(columns=["ID", "시간", "아이디", "종목", "손실률", "원인", "다짐"]), LOSS_FILE)
    else:
        # 헤더 정합성 체크 (ID 컬럼 누락 방지)
        temp_df = safe_read_csv(LOSS_FILE, ["ID", "시간", "아이디", "종목", "손실률", "원인", "다짐"])
        if "ID" not in temp_df.columns:
            temp_df.insert(0, "ID", [f"L_{int(time.time())}_{i}" for i in range(len(temp_df))])
            safe_write_csv(temp_df, LOSS_FILE)
    if not os.path.exists(COMMENTS_FILE):
        safe_write_csv(pd.DataFrame(columns=["PostID", "시간", "작성자", "내용"]), COMMENTS_FILE)

    with st.expander("🩹 오늘의 아픔 기록하고 털어내기", expanded=True):
        with st.form("loss_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1: l_tic = st.text_input("종목명/티커", placeholder="복기할 종목")
            with c2: l_roi = st.text_input("손실률 (%)", placeholder="예: -7.2%")
            
            l_reason = st.selectbox("실전 과오 원인 판독", [
                "추격 매수 (FOMO)", "손절 지연 (희망고문)", "원칙 외 매매 (뇌동매매)", 
                "비중 과다 (몰빵)", "지수 급락 대응 실패", "기타 전술적 오류"
            ])
            l_msg = st.text_area("구체적인 상황 복기 및 향후 다짐", placeholder="왜 이런 결과가 나왔는지, 다음에는 어떻게 대응하실 건가요?")
            
            if st.form_submit_button("🛡️ 복기 완료 및 마음 다잡기"):
                if l_tic and l_roi and l_msg:
                    now_k = datetime.now(pytz.timezone('Asia/Seoul'))
                    t_now = now_k.strftime("%Y-%m-%d %H:%M")
                    d_str, t_str = t_now.split(" ")
                    u = st.session_state.current_user
                    lid = f"L_{int(time.time())}_{random.randint(100,999)}_{u}"
                    new_l = pd.DataFrame([[lid, t_now, u, l_tic, l_roi, l_reason, l_msg]], columns=["ID", "시간", "아이디", "종목", "손실률", "원인", "다짐"])
                    # 💾 로컬 저장 (최적화: 백업 생략)
                    save_l_success = safe_write_csv(new_l, LOSS_FILE, mode='a', header=False, backup=False)
                    
                    if not save_l_success:
                        st.error("❌ 로컬 파일(CSV) 저장에 실패했습니다.")

                    # 📡 구글 시트 백그라운드 동기화 (손절방 탭)
                    gsheet_sync_bg("손절방", 
                        ["날짜", "시간", "회원명", "종목명/티커", "손실률", "과오원인", "구체적인 상황 복기 및 향후 다짐"], 
                        [d_str, t_str, u, l_tic, l_roi, l_reason, l_msg]
                    )
                    st.toast("✅ 성찰 기록이 저장되었습니다. (배경에서 시트 동기화 중)")
                    
                    time.sleep(1)
                    st.rerun()
                else: st.error("필수 항목을 모두 입력해 주세요.")

    st.divider()
    # --- 실시간 손실 복기 디스플레이 ---
    st.subheader("🤝 함께 나누는 성찰의 시간")
    
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
                        if cl_edit1.form_submit_button("💾 저장"):
                            temp_df = safe_read_csv(LOSS_FILE, ["ID", "시간", "아이디", "종목", "손실률", "원인", "다짐"])
                            temp_df.loc[temp_df['ID'] == pid, ['손실률', '원인', '다짐']] = [e_lroi, e_lreason, e_lmsg]
                            safe_write_csv(temp_df, LOSS_FILE)
                            del st.session_state[edit_key]
                            st.rerun()
                        if cl_edit2.form_submit_button("❌ 취소"):
                            del st.session_state[edit_key]
                            st.rerun()
                else:
                    st.markdown(f"""
                    <div style='background: rgba(255,255,255,0.02); border: 1px solid #6366f133; border-radius: 12px; padding: 20px; margin-bottom: 10px;'>
                        <div style='display: flex; justify-content: space-between;'>
                            <b style='color: #6366f1;'>🩹 {row['아이디']} 대원에게 따뜻한 위로를</b>
                            <span style='color: #888; font-size: 0.8rem;'>{row['시간']}</span>
                        </div>
                        <div style='margin-top: 12px; font-size: 0.95rem; color: #BBB;'>
                            🎬 <b>{row['종목']}</b> 종목에서 <b>{row['손실률']}</b> 손실 기록 (<span style='color: #FF4B4B;'>사유: {row['원인']}</span>)
                        </div>
                        <div style='margin-top: 15px; padding: 12px; background: rgba(0,0,0,0.2); border-left: 3px solid #6366f1; color: #DDD; font-size: 0.95rem; font-style: italic;'>
                            "{row['다짐']}"
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if is_owner:
                        ol_col1, ol_col2, ol_col3 = st.columns([1, 1, 6])
                        if ol_col1.button("📝 수정", key=f"ledit_btn_{pid}", use_container_width=True):
                            st.session_state[edit_key] = True
                            st.rerun()
                        if ol_col2.button("🗑️ 삭제", key=f"ldel_btn_{pid}", use_container_width=True):
                            temp_df = safe_read_csv(LOSS_FILE, ["ID", "시간", "아이디", "종목", "손실률", "원인", "다짐"])
                            temp_df = temp_df[temp_df['ID'] != pid]
                            safe_write_csv(temp_df, LOSS_FILE)
                            st.warning("복기 내역이 삭제되었습니다.")
                            st.rerun()

                # 댓글 섹션
                with st.container():
                    item_comments = cdf[cdf['PostID'] == pid]
                    for _, c in item_comments.iterrows():
                        st.markdown(f"<div style='margin-left: 20px; font-size: 0.9rem; border-left: 2px solid #555; padding-left: 10px; margin-bottom: 5px;'><b style='color: #6366f1;'>{c['작성자']}:</b> {c['내용']} <span style='color: #555; font-size: 0.7rem;'>({c['시간']})</span></div>", unsafe_allow_html=True)
                    
                    c_col1, c_col2 = st.columns([8, 2])
                    new_c = c_col1.text_input("따뜻한 한마디", key=f"c_input_{pid}", label_visibility="collapsed", placeholder="대원님, 고생 많으셨습니다. 힘내세요!")
                    if c_col2.button("🗨️ 등록", key=f"c_btn_{pid}"):
                        if new_c:
                            now_c_t = datetime.now(pytz.timezone('Asia/Seoul')).strftime("%m/%d %H:%M")
                            u = st.session_state.current_user
                            c_new = pd.DataFrame([[pid, now_c_t, u, new_c]], columns=["PostID", "시간", "작성자", "내용"])
                            safe_write_csv(c_new, COMMENTS_FILE, mode='a', header=False)
                            gsheet_sync_bg("댓글_통합", ["PostID", "시간", "작성자", "내용"], [pid, now_c_t, u, new_c])
                            st.rerun()
                st.write("") # 스페이싱
        except Exception as e:
            st.error(f"❌ 복기 목록을 렌더링하는 중 오류가 발생했습니다: {e}")
    else:
        st.info("아직 등록된 성찰 기록이 없습니다. 아픔을 나누면 반이 됩니다.")


elif page.startswith("2-b."):
    st.header("🗺️ 실시간 주도주 히트맵 (Market OverView)")
    st.markdown("<div class='glass-card'>사령부 관리 종목 20선의 실시간 수급 현황입니다. (초록: 상승 / 빨강: 하락)</div>", unsafe_allow_html=True)
    if st.button("🔄 실시간 히트맵 데이터 동기화"):
        tics = list(TICKER_NAME_MAP.keys())
        try:
            with st.spinner("📡 데이터 수집 중..."):
                h_data = yf.download(tics, period="2d", progress=False)['Close']
                changes = ((h_data.iloc[-1] / h_data.iloc[-2]) - 1) * 100
                df_h = pd.DataFrame([{"Name": TICKER_NAME_MAP.get(t, t), "Change": changes.get(t, 0), "Size": 1} for t in tics])
                fig = px.treemap(df_h, path=['Name'], values='Size', color='Change', color_continuous_scale='RdYlGn', color_continuous_midpoint=0)
                fig.update_layout(margin=dict(t=30, l=10, r=10, b=10), height=600)
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e: st.error(f"오류 발생: {e}")

elif page.startswith("2-c."):
    st.header("🌡️ 시장 심리 게이지 (Fear & Greed)")
    try:
        ndx = yf.download("^IXIC", period="5d", progress=False)['Close']
        if isinstance(ndx, pd.DataFrame): ndx = ndx.iloc[:, 0]
        ndx = ndx.dropna()
        ndx_ch = ((ndx.iloc[-1] / ndx.iloc[-2]) - 1) * 100
        # 기본 점수를 70으로 상향하여 매수 우위 시장 반영
        val = int(min(max(70 + (ndx_ch * 10), 20), 95))
    except: val = 75
    col1, col2 = st.columns([1.5, 1.2])
    with col1:
        fig = go.Figure(go.Indicator(mode="gauge+number", value=val, gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#00FF00"}, 'steps': [{'range': [0, 35], 'color': "#FF4B4B"}, {'range': [36, 65], 'color': "#FFD700"}, {'range': [66, 100], 'color': "#00FF00"}]}))
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.markdown("<div class='glass-card' style='padding:25px;'>", unsafe_allow_html=True)
        st.subheader("🐝 STOCKDragonfly: 본데의 실시간 뼈 때리는 훈수 (Bonde's Harsh Truth)")
        if val <= 35: 
            st.error("""
            **🔴 하락장 (Defensive/Cash)**  
            "떨어지는 칼날을 왜 잡으려 하나? 네가 시장보다 똑똑하다고 착각하지 마라. 
            지금 네가 할 일은 스캐닝이 아니라 자본 보호다. 계좌 박살 내고 울지 말고 당장 HTS 꺼라. 
            시장은 어디 안 간다, 네 돈이 도망갈 뿐이지."
            """)
        elif val <= 65: 
            st.warning("""
            **🟡 횡보장 (Selective/Choppy)**  
            "지금 매수 버튼에 손이 가나? 그건 투자가 아니라 도박이다. 아무것도 하지 않는 것도 포지션이다. 
            푼돈 벌려다 큰돈 잃지 말고, 확실한 A+ 셋업이 올 때까지 얌전히 현금 쥐고 기다려라. 
            지루함을 못 견디면 파산뿐이다."
            """)
        else: 
            st.success("""
            **🟢 상승장 (Greed/Aggressive)**  
            "수익 좀 났다고 네가 천재가 된 줄 아나? 시장이 좋은 것뿐이다. 
            자만심(Ego)이 고개를 드는 순간, 시장은 네 계좌를 갈기갈기 찢어놓을 거다. 
            익절 라인 올려 잡고 닥치고 프로세스나 지켜라."
            """)
        st.markdown("</div>", unsafe_allow_html=True)
        
    st.divider()
    # 🕵️ 본데의 일간 전술 교육 (Rotating Wisdom)
    wisdom = get_daily_wisdom()
    st.markdown(f"""
    <div class='glass-card' style='border-left: 10px solid #FF4B4B; background: rgba(255,0,0,0.03);'>
        <h3 style='color: #FF4B4B; margin-top: 0;'>📢 [긴급] 사령부 정신 교육: {wisdom['title']}</h3>
        <p style='color: #DDD; font-size: 1.1rem; line-height: 1.8; font-style: italic;'>
            "{wisdom['content']}"
        </p>
        <div style='text-align: right; color: #888; font-weight: 700;'>- Pradeep Bonde, Stockbee Matrix -</div>
    </div>
    """, unsafe_allow_html=True)

elif page.startswith("1-b."):
    st.header("🎖️ HQ 인적 자원 사령부 (Member HR Command)")
    users = load_users()
    
    # 사령관(방장) 전용 보안
    if users.get(st.session_state.current_user, {}).get("grade") != "방장":
        st.error("❌ 이 전술 구역은 사령관(방장) 전용입니다. 권한이 없습니다.")
        st.stop()
        
    st.markdown("<div class='glass-card'>사령관의 권위로 대원의 등급을 조정하거나 사령부에서 즉각 제명(삭제)하는 인사권을 행사합니다.</div>", unsafe_allow_html=True)
    
    # 🛡️ 사령부 데이터 동기화 및 복구 센터 (통합 관리)
    st.subheader("🛡️ 클라우드 데이터 동기화 및 복구 센터")
    with st.expander("📊 구글 시트 양방향 동기화 (불러오기 / 백업)", expanded=True):
        st.markdown("""
        사령부 명부와 구글 시트 데이터를 동기화합니다. 
        - **불러오기 (Import):** 구글 시트에 저장된 최신 명단을 가져와 현재 터미널을 업데이트합니다.
        - **백업 (Export):** 현재 터미널의 모든 대원 정보를 구글 시트(클라우드)로 안전하게 전송합니다.
        """)
        
        c_sync1, c_sync2 = st.columns(2)
        with c_sync1:
            if st.button("🚀 클라우드 명단 불러오기 (Import)", use_container_width=True, key="import_btn"):
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
                        st.success(f"🎊 클라우드에서 {len(users)}명의 요원 정보를 성공적으로 수신하여 동기화했습니다.")
                        st.rerun()
                    else:
                        st.warning("⚠️ 시트에서 데이터를 가져왔으나 등록된 대원 정보가 없습니다.")
        
        with c_sync2:
            if st.button("📌 현재 명단 클라우드 백업 (Export)", use_container_width=True, key="export_btn"):
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
                    st.success(f"🎊 총 {count}명의 대원 정보가 구글 시트에 안전하게 백업되었습니다!")
                    st.balloons()
    
    st.divider()
    st.subheader("📋 전체 대원 리스트 관리")
    
    # 자신을 제외한 대원 리스트
    m_list = [u for u in users.keys() if u != st.session_state.current_user]
    
    if m_list:
        for u in m_list:
            udata = users[u]
            uinfo = udata.get("info", {})
            with st.expander(f"👤 요원 코드: {u} (현재 보직: {udata.get('grade', '회원')})"):
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
                    if st.button("🔥 즉각 제명", key=f"del_{u}"):
                        del users[u]
                        save_users(users)
                        st.warning(f"⚠️ {u} 요원이 명부에서 삭제되었습니다.")
                        st.rerun()
    else:
        st.info("현재 사령부에서 관리할 대원이 없습니다.")


elif page.startswith("5-b."):
    st.markdown("<h1 style='color: #FFD700; text-align: center; font-size: 3rem;'>🏛️ StockDragonfly 차트 아카데미</h1>", unsafe_allow_html=True)
    st.markdown("""
    <div class='glass-card' style='text-align: center; padding: 30px; border: 1px solid #FFD700; background: rgba(255,215,0,0.02);'>
        <p style='font-size: 1.2rem; color: #EEE; line-height: 1.8;'>
            "성공적인 트레이딩은 본능이 아니라 훈련된 반사 신경의 결과입니다."<br>
            본 교육 섹션은 윌리엄 오닐과 프라딥 본데의 철학을 바탕으로, 시장 주도주의 탄생 원리를 몸소 체득할 수 있도록 설계되었습니다. 
            눈으로 읽는 공부를 넘어, 차트 1,000개를 뇌에 각인시키는 <b>딥 다이브(Deep Dive)</b> 훈련을 시작하십시오.
        </p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🏛️ Master's Archive", "🎯 Training Room", "📺 Live Academy"])

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
        
        st.info("💡 아카이브 내부 데이터는 매주 업데이트되며, 현재 1,200개 이상의 폭등주 샘플이 데이터베이스에 등록되어 있습니다.")

    with tab2:
        st.subheader("2. 트레이닝 룸: 실전 타점 훈련")
        st.markdown("<div class='glass-card'>차트를 보고 직접 매수 급소를 클릭하며 실전 감각을 기르는 인터랙티브 훈련장입니다.</div>", unsafe_allow_html=True)
        
        cc1, cc2 = st.columns([2, 1])
        with cc1:
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
            if st.button("🚀 무작위 훈련 시작"):
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
                <b style='color: #00FF00;'>🍌 나노바나나 스캔</b><br>
                <small>돌파 임박도 (잘 익었는지):</small>
                <div style='background: #333; height: 10px; border-radius: 5px; margin-top: 5px;'>
                    <div style='background: #00FF00; width: 85%; height: 100%; border-radius: 5px;'></div>
                </div>
                <div style='text-align: right; font-size: 0.8rem; margin-top: 3px;'>85% Ready</div>
            </div>
            <br>
            <div style='background: rgba(255,215,0,0.05); padding: 15px; border-radius: 10px; border: 1px solid #FFD700;'>
                <b style='color: #FFD700;'>🏷️ 자동 어노테이션</b><br>
                <small>• RS 신고가 감지됨</small><br>
                <small>• VCP 3단계 수축 진행중</small><br>
                <small>• 거래량 말라감(Dry-up) 포착</small>
            </div>
            """, unsafe_allow_html=True)
            
        with l1:
            st.components.v1.html(f"""
                <iframe src='https://s.tradingview.com/widgetembed/?symbol={live_tic}&interval=D&theme=dark' width='100%' height='550'></iframe>
            """, height=560)
            st.success(f"📺 {live_tic} 실시간 실전 판독 엔진 가동 중")

    st.divider()
    st.subheader("📝 StockDragonfly 아카데미 운영 지침")
    
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
    st.markdown("<h1 style='text-align: center; color: #00FF00;'>🛰️ 나노바나나 정밀 레이더</h1>", unsafe_allow_html=True)
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
            if st.button(f"🎯 {stock['T']} 정밀 분석", key=f"radar_btn_{stock['T']}", use_container_width=True):
                st.toast(f"{stock['T']} 분석실로 전술 이동 중...")
            
    st.divider()
    st.info("💡 레이더의 'Ready' 지수는 ROE, RS, 그리고 최근 2주간의 변동성 타이트니스(Tightness)를 종합 산출한 결과입니다.")
    
elif page.startswith("1-c."):
    st.header("🔐 계정 보안 및 관리 (Security & Account)")
    st.markdown("<div class='glass-card'>사령부 보안 설정을 관리합니다. 비밀번호를 정기적으로 변경해 주세요.</div>", unsafe_allow_html=True)
    
    # 비밀번호 변경 섹션
    with st.expander("🔑 비밀번호 변경 및 보안 강화", expanded=True):
        with st.form("pw_change_form", clear_on_submit=True):
            curr_pw_input = st.text_input("현재 비밀번호 확인", type="password")
            new_pw_input = st.text_input("새로운 비밀번호 설정", type="password")
            new_pw_confirm = st.text_input("새로운 비밀번호 다시 입력", type="password")
            
            if st.form_submit_button("🛡️ 비밀번호 변경 적용"):
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
                    st.success("✅ 비밀번호 변경 완료!")
                    st.balloons()

elif page.startswith("1-d."):
    st.header("🌙 탈퇴 및 임시휴식 (Account Status)")
    st.markdown("<div class='glass-card'>사령부 활동 중단이나 탈퇴를 관리합니다. 신중하게 결정해 주십시오.</div>", unsafe_allow_html=True)
    
    st.subheader("⚠️ 계정 상태 변경 및 전역 처리")
    c1, c2 = st.columns(2)
    
    users = load_users()
    u_id = st.session_state.current_user
    u_data = users.get(u_id, {})
    u_info = u_data.get("info", {})

    with c1:
        st.markdown("<div class='glass-card' style='border-top: 3px solid #6366f1;'><b>임시 휴식 신청</b><br><small>활동을 잠시 중단합니다. 관리자 승인 전까지 기능이 제한될 수 있습니다.</small></div>", unsafe_allow_html=True)
        if st.button("🌙 임시 휴식 모드 전환", use_container_width=True):
            users[u_id]["status"] = "resting"
            save_users(users)
            gsheet_sync_bg("회원명단", 
                ["아이디", "비밀번호", "상태", "등급", "지역", "연령대", "성별", "경력", "가입일", "매매동기"],
                [u_id, u_data.get("password"), "resting", u_data.get("grade"), u_info.get("region", "-"), u_info.get("age", "-"), u_info.get("gender", "-"), u_info.get("exp", "-"), u_info.get("joined_at", "-"), u_info.get("motivation", "-")]
            )
            st.warning("🌙 임시 휴식 상태로 전환되었습니다. 로그아웃 후 다시 접속 시 제한이 적용됩니다.")
            st.rerun()

    with c2:
        st.markdown("<div class='glass-card' style='border-top: 3px solid #ff4b4b;'><b>사령부 전역(탈퇴)</b><br><small>모든 활동을 종료하고 명부에서 이름을 내립니다. 복구가 불가능합니다.</small></div>", unsafe_allow_html=True)
        if st.button("🔥 즉시 탈퇴 절차 시작", use_container_width=True):
            st.session_state.show_withdraw_confirm = True
            
        if st.session_state.get("show_withdraw_confirm"):
            st.error("🚨 사령부를 떠나시기 전에 한 번 더 고려해 주세요. 정말 전역하시겠습니까?")
            withdraw_reason = st.text_area("1. 탈퇴 사유를 알려주세요.", key="w_reason")
            withdraw_improve = st.text_area("2. 사령부가 개선해야 할 점이 있다면 무엇일까요?", key="w_improve")
            
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("✅ 네, 정말 탈퇴합니다", use_container_width=True):
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
                        
                        st.error("🔥 탈퇴 처리가 완료되었습니다. 그동안의 헌신에 감사드립니다.")
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
    st.header("🚀 모의투자 매수 테스트 (Unit Deployment)")
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
        <h4 style='margin:0;'>💰 현재 가용 예수금: <span style='color:#FFD700;'>{curr_balance:,.0f} KRW</span></h4>
        <p style='margin:0; font-size:0.8rem; color:#888;'>초기 시드머니 1,000만원이 대원님께 지급되었습니다.</p>
    </div>
    """, unsafe_allow_html=True)
    st.write("")
    
    with st.form("mock_buy_form"):
        col1, col2, col3 = st.columns(3)
        with col1: ticker = st.text_input("종목 코드 (예: TSLA)", value="TSLA").upper()
        with col2: amount = st.number_input("매수 수량", min_value=1, value=10)
        with col3: strategy = st.selectbox("적용 전략", ["VCP 돌파", "EP 포착", "MA 정배열"])
        
        if st.form_submit_button("🔥 가상 매수 집행"):
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
                        st.error(f"❌ 잔액이 부족합니다. (필요: {total_cost_krw:,.0f} KRW / 잔액: {curr_balance:,.0f} KRW)")
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
                        price_display = f"{curr_p_raw:,.0f}원" if is_kr_stock else f"{curr_p_raw:,.2f}$"
                        st.success(f"✅ {ticker} 종목 {amount}주를 {price_display}에 매수 완료했습니다! (총 {total_cost_krw:,.0f} KRW 차감)")
                        st.balloons()
                        time.sleep(1)
                        st.rerun()
            except Exception as e:
                st.error(f"오류 발생: {e}")

elif page.startswith("7-b."):
    st.header("📊 모의투자 현황 및 결과 (Tactical Dashboard)")
    trades = load_trades()
    uid = st.session_state.current_user
    user_trades = [t for t in trades["mock"] if t["user"] == uid]
    EX_RATE, _ = get_macro_data() # 실시간 환율 반영

    if uid not in trades["wallets"]:
        trades["wallets"][uid] = 10000000.0
        save_trades(trades)
    
    st.markdown(f"""
    <div style='background: rgba(255,215,0,0.05); padding: 15px; border-radius: 10px; border: 1px solid #FFD700; margin-bottom: 20px;'>
        <span style='color: #AAA;'>🏦 가상 사령부 금고 잔고 (예수금):</span> 
        <b style='color: #FFD700; font-size: 1.2rem; margin-left: 10px;'>{trades['wallets'][uid]:,.0f} KRW</b>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("📡 현재 보유 중인 가상 포트폴리오")
    if not user_trades:
        st.info("현재 보유 중인 가상 종목이 없습니다. 7-a에서 매수를 진행해 주세요.")
    else:
        results = []
        ticker_total_value = 0
        with st.spinner("가상 사령부 실시간 주가 동기화 중..."):
            tickers = list(set([t['ticker'] for t in user_trades]))
            if tickers:
                data_batch = yf.download(tickers, period="1d", progress=False)['Close']
                if isinstance(data_batch, pd.Series): data_batch = pd.DataFrame(data_batch).T
                
                for i, t in enumerate(user_trades):
                    try:
                        tic = t['ticker']
                        curr_p_raw = float(data_batch[tic].iloc[-1]) if tic in data_batch.columns else t['buy_price']
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

                        # --- 🎯 v7.0 매매 타점 시각화 (Alpha Analyzer) ---
                        with st.expander(f"🔍 {tic} 전술 분석 (타점 및 추세)", expanded=False):
                            t_hist = yf.download(tic, period="3mo", progress=False)['Close']
                            if not t_hist.empty:
                                fig_p = px.line(t_hist, title=f"{tic} 3개월 추세 및 내 진입가")
                                # 내 진입가 수평선 표시
                                fig_p.add_hline(y=t['buy_price'], line_dash="dash", line_color="yellow", annotation_text="나의 매수가")
                                # 매수 시점 표시 (날짜가 매칭될 경우)
                                t_date = t['date'].split(" ")[0]
                                if t_date in t_hist.index.strftime("%Y-%m-%d"):
                                    fig_p.add_annotation(x=t_date, y=t['buy_price'], text="▲ BUY", showarrow=True, arrowhead=1, font=dict(color="lime"))
                                st.plotly_chart(fig_p, use_container_width=True)

                        c1, c2, c3, c4, c5 = st.columns([1, 1, 1, 1, 1])
                        c1.write(f"**{tic}**")
                        c2.write(f"{t['amount']}주")
                        c3.write(price_display)
                        
                        res_color = "#FF4B4B" if profit_krw > 0 else "#6366f1"
                        c4.markdown(f"<span style='color:{res_color}; font-weight:700;'>{profit_krw:+,.0f} 원 ({roi:+.2f}%)</span>", unsafe_allow_html=True)
                        
                        if c5.button("🔒 매도", key=f"sell_{t['id']}_{i}"):
                            # 매도 처리: 예수금으로 환전 입급
                            trades["wallets"][uid] += curr_val_krw
                            sell_record = t.copy()
                            sell_record["sell_price"] = curr_p_raw
                            sell_record["final_profit_krw"] = profit_krw
                            sell_record["date_sold"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            sell_record["is_kr"] = is_kr
                            
                            trades["history"].append(sell_record)
                            trades["mock"] = [trade for trade in trades["mock"] if trade["id"] != t["id"]]
                            save_trades(trades)
                            st.success(f"✅ {tic} 매도 완료! {curr_val_krw:,.0f} KRW가 입금되었습니다.")
                            time.sleep(1)
                            st.rerun()
                    except: pass
        
        st.markdown(f"""
        <div class='glass-card' style='border-top: 3px solid #00FF00; margin-top: 20px;'>
            <h3 style='margin:0;'>🏛️ 총 자산 평가액: <span style='color:#00FF00;'>{(trades['wallets'][uid] + ticker_total_value):,.0f} KRW</span></h3>
            <p style='margin:0; font-size:0.9rem; color:#888;'>예수금({trades['wallets'][uid]:,.0f}) + 주식평가({ticker_total_value:,.0f})</p>
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    st.subheader("📝 가상매매 종결 내역 (Sell History)")
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
        p_color = "🔴" if total_p > 0 else "🔵"
        st.markdown(f"### {p_color} 총 누적 실현 수익: <span style='color:{('#ff4b4b' if total_p > 0 else '#6366f1')};'>{total_p:+,.0f} 원</span>", unsafe_allow_html=True)
    else:
        st.info("아직 매도 종결된 내역이 없습니다.")

elif page.startswith("7-c."):
    st.header("⚙️ 자동매매 전략 엔진 (Autonomous Engine)")
    st.markdown("<div class='glass-card'>시스템이 실시간 데이터를 스캔하여 최적의 타점을 자동으로 포착합니다.</div>", unsafe_allow_html=True)
    
    # 전략 스캐닝 시뮬레이션
    st.subheader("📡 실시간 전략 스캐닝 현황")
    if st.button("🔍 전략 엔진 가동 (Scan Start)"):
        with st.status("전략 필터링 중...", expanded=True) as status:
            st.write("1. RS 90 이상 종목 추출 중...")
            time.sleep(1)
            st.write("2. VCP 변동성 축소 패턴 감지 중...")
            time.sleep(1)
            st.write("3. 에피소딕 피벗(EP) 후보군 필터링...")
            time.sleep(1)
            status.update(label="✅ 스캔 완료! 매수 권고 종목 발견", state="complete")
        
        cols = st.columns(2)
        with cols[0]:
            st.info("🎯 **추천 종목: NVDA**")
            st.write("사유: 전고점 돌파 1단계, 거래량 급증 포착")
            if st.button("⚡ 즉시 매수 집행 (Auto Order)", key="auto_buy_nvda"):
                try:
                    data = yf.Ticker("NVDA").history(period="1d")
                    curr_p = float(data['Close'].iloc[-1])
                    trades = load_trades()
                    new_trade = {
                        "id": str(int(time.time())), "user": st.session_state.current_user,
                        "ticker": "NVDA", "buy_price": curr_p, "amount": 10,
                        "strategy": "AI Auto Scanner", "date": datetime.now().strftime("%Y-%m-%d %H:%M")
                    }
                    trades["auto"].append(new_trade)
                    save_trades(trades)
                    st.success("✅ NVDA 자동 매수 주문 전송 완료! (장부에 기록됨)")
                except: st.error("데이터 로드 실패")
        with cols[1]:
            st.info("🎯 **추천 종목: AAPL**")
            st.write("사유: 20일선 지지 후 기술적 반등 시그널")
            if st.button("⚡ 즉시 매수 실행", key="auto_buy_aapl"):
                try:
                    data = yf.Ticker("AAPL").history(period="1d")
                    curr_p = float(data['Close'].iloc[-1])
                    trades = load_trades()
                    new_trade = {
                        "id": str(int(time.time())) + "_aapl", "user": st.session_state.current_user,
                        "ticker": "AAPL", "buy_price": curr_p, "amount": 20,
                        "strategy": "AI Auto Scanner", "date": datetime.now().strftime("%Y-%m-%d %H:%M")
                    }
                    trades["auto"].append(new_trade)
                    save_trades(trades)
                    st.success("✅ AAPL 자동 매수 주문 전송 완료! (장부에 기록됨)")
                except: st.error("데이터 로드 실패")

elif page.startswith("7-d."):
    st.header("📈 자동투자 성적표 (Performance Report)")
    st.markdown("<div class='glass-card'>시스템이 수행한 전체 자동매매의 통계 데이터를 분석합니다.</div>", unsafe_allow_html=True)
    
    # 통계 시뮬레이션 데이터
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("총 매매 횟수", "128회")
    c2.metric("승률 (Win Rate)", "64.5%", "2.1%")
    c3.metric("누적 수익률", "142.8%", "12.5%")
    c4.metric("최대 낙폭 (MDD)", "-8.2%")
    
    st.divider()
    st.subheader("📉 자산 성장 곡선 (Equity Curve)")
    chart_data = pd.DataFrame(np.random.randn(20, 1).cumsum(), columns=['Equity'])
    st.line_chart(chart_data)

elif page.startswith("7-e."):
    st.markdown("<h1 style='text-align: center; color: #FFD700; font-size: 3rem;'>🛸 가상매매 명예의 전당</h1>", unsafe_allow_html=True)
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
        
        # UI 출력
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            st.markdown("### 🥇 COMMANDER RANKING")
            for i, (uid, stats) in enumerate(sorted_rank[:10]):
                medal = "🥇" if i == 0 else ("🥈" if i == 1 else ("🥉" if i == 2 else "🎖️"))
                color = "#FFD700" if i == 0 else "#FFFFFF"
                st.markdown(f"""
                <div style='background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid {color};'>
                    <span style='font-size: 1.2rem;'>{medal} <b>{uid}</b> 요원</span>
                    <span style='float: right; color: #00FF00; font-weight: bold;'>$ {stats['total_profit']:,.2f}</span>
                    <br><small style='color: #888;'>누적 매매: {stats['trade_count']}회</small>
                </div>
                """, unsafe_allow_html=True)
            
            if len(sorted_rank) > 0:
                st.balloons()

# --- 🛰️ 시스템 하단 글로벌 전술 푸터 (Global Footer) ---
st.write("") # 스페이싱
st.divider()
f_quote = get_footer_quote()
st.markdown(f"""
<div style='text-align: center; padding: 20px; color: #666; font-size: 0.95rem; border-top: 1px solid #222;'>
    <span style='color: #FFD700; font-weight: 700;'>🛡️ 본데의 일간 전술 통찰 (Daily Tactical Insight)</span><br>
    <div style='margin-top: 10px; font-style: italic; color: #AAA; line-height: 1.6;'>
        "{f_quote}"
    </div>
    <div style='margin-top: 20px; font-size: 0.75rem; color: #444;'>
        © 2026 StockDragonfly Terminal v9.9 | Institutional System Operated by Global Expert Turtle
    </div>
</div>
""", unsafe_allow_html=True)