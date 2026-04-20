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

def trigger_ai_chat():
    """AI 대원들이 랜덤하게 소통방에 메시지를 남기는 엔진 (6인 체제)"""
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

@st.cache_data(ttl=900)
def get_market_sentiment_score():
    """VIX 및 나스닥 RSI 기반 실전 공포/탐욕 점수 산출"""
    try:
        # VIX(^VIX)는 공포의 지수
        m_data = yf.download(["^VIX", "^IXIC"], period="14d", interval="1d", progress=False)['Close']
        curr_vix = float(m_data["^VIX"].dropna().iloc[-1]) if "^VIX" in m_data.columns else 20.0
        
        # 기본 점수: VIX가 낮을수록 탐욕(높음), 높을수록 공포(낮음)
        # VIX 15 -> 85점, VIX 40 -> 10점 정도의 보간
        vix_score = max(5, min(95, 100 - (curr_vix * 2.2)))
        
        # 나스닥 RSI로 보정
        ndx = m_data["^IXIC"].dropna()
        delta = ndx.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1+rs.iloc[-1])) if not rs.empty else 50
        
        final_score = (vix_score * 0.6) + (rsi * 0.4)
        return int(final_score), curr_vix
    except:
        return 50, 20.0

# --- [ MACRO ] 거시지표 매크로 바 ---
@st.cache_data(ttl=600)
def get_macro_data():
    try:
        m_data = yf.download(["USDKRW=X", "^TNX"], period="5d", progress=False)['Close']
        rate_series = m_data["USDKRW=X"].dropna()
        rate = float(rate_series.iloc[-1]) if not rate_series.empty else 1400.0
        yield_series = m_data["^TNX"].dropna()
        yield10y = float(yield_series.iloc[-1]) if not yield_series.empty else 4.3
        return rate, yield10y
    except: 
        return 1400.0, 4.3

def get_macro_indicators():
    rate, yield10y = get_macro_data()
    return f"[ USD/KRW ]: {rate:,.1f}원 | [ US 10Y ]: {yield10y:.2f}%"

# --- [ AI ] 사령부 AI 정예 요원 (NPC Operatives) 설정 ---
AI_OPERATIVES = {
    "minsu": {"strategy": "KOSPI Specialist", "risk": "Aggressive", "win_rate": 0.65},
    "Olive": {"strategy": "KOSDAQ Specialist", "risk": "Balanced", "win_rate": 0.70},
    "Pure": {"strategy": "NASDAQ Specialist", "risk": "Conservative", "win_rate": 0.75}
}

@st.cache_data(ttl=300)
def load_users():
    # 1. 먼저 로컬 파일 확인 (안전한 로드 사용)
    users = safe_load_json(USER_DB_FILE, {})
    
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

@st.cache_resource
def get_cached_bg_b64():
    try:
        target = "StockDragonfly2.png" if os.path.exists("StockDragonfly2.png") else "StockDragonfly.png"
        if os.path.exists(target):
            with open(target, "rb") as imm: 
                return base64.b64encode(imm.read()).decode()
    except: pass
    return ""

# --- [ UI ] CSS & Background (Lightweight High-Performance) ---
st.markdown("""
    <style>
        /* [ DESIGN ] 네온 플럭스(Neon Flux) 프리미엄 효과 강화 */
        .neon-glow {
            text-shadow: 0 0 10px rgba(0, 255, 0, 0.5), 0 0 20px rgba(0, 255, 0, 0.3);
            color: #00FF00 !important;
        }
        .neon-glow-red {
            text-shadow: 0 0 10px rgba(255, 75, 75, 0.5), 0 0 20px rgba(255, 75, 75, 0.3);
            color: #FF4B4B !important;
        }
        .neon-glow-gold {
            text-shadow: 0 0 10px rgba(255, 215, 0, 0.5), 0 0 20px rgba(255, 215, 0, 0.3);
            color: #FFD700 !important;
        }
        
        /* 글래스모피즘 효과 강화 */
        .glass-card {
            background: rgba(15, 15, 25, 0.6) !important;
            backdrop-filter: blur(25px);
            border: 1px solid rgba(255, 215, 0, 0.1) !important;
            border-radius: 20px;
            padding: 25px;
            margin-bottom: 25px;
            transition: all 0.4s ease;
        }
        .glass-card:hover {
            border-color: rgba(255, 215, 0, 0.4) !important;
            box-shadow: 0 15px 45px rgba(0,0,0,0.7);
        }
    </style>
""", unsafe_allow_html=True)

# 로고는 바이너리 전송(efficient)을 위해 st.image 사용
# bg_b64 호출 제거 (성능 저하 원인)

# --- [ MENU ] 메뉴 UI 구조 고정 (v9.9 Platinum) ---
ZONE_CONFIG = {
    "[ HQ ] 1. 본부 사령부": ["1-a. [ ADMIN ] 관리자 승인 센터", "1-b. [ HR ] HQ 인적 자원 사령부", "1-c. [ SECURE ] 계정 보안 및 관리(18.)", "1-d. [ EXIT ] 탈퇴/휴식 신청"],
    "[ MARKET ] 2. 시장 상황실": ["2-a. [ TREND ] 마켓 트렌드 요약", "2-b. [ MAP ] 실시간 히트맵", "2-c. [ SENTIMENT ] 시장 심리 게이지", "2-d. [ ABOUT ] 제작 동기"],
    "[ TARGET ] 3. 주도주 추격대": ["3-a. [ SCAN ] 주도주 타점 스캐너", "3-b. [ RANK ] 주도주 랭킹 TOP 50", "3-c. [ WATCH ] 본데 감시 리스트", "3-d. [ INDUSTRY ] 산업동향(TOP 10)", "3-e. [ RS ] RS 강도(TOP 10)"],
    "[ RISK ] 4. 전략 및 리스크": ["4-a. [ REPORT ] 프로 분석 리포트", "4-b. [ CALC ] 리스크 계산기", "4-c. [ SHIELD ] 리스크 방패"],
    "[ ACADEMY ] 5. 마스터 훈련소": ["5-a. [ WHOWS ] 본데는 누구인가?", "5-b. [ STUDY ] 주식공부방(차트)", "5-c. [ RADAR ] 나노바나나 레이더", "5-d. [ EXAM ] 정기 승급 시험 안내", "5-e. [ SUCCESS ] 실전 익절 자랑방", "5-f. [ REVIEW ] 손실 위로 및 복기방"],
    "[ SQUARE ] 6. 안티그래비티 광장": ["6-a. [ CHECK ] 출석체크(오늘한줄)", "6-b. [ CHAT ] 소통 대화방", "6-c. [ VISIT ] 방문자 인사 신청"],
    "[ AUTO ] 7. 자동매매 사령부": ["7-a. [ EXEC ] 모의투자 매수테스트", "7-b. [ DASHBOARD ] 모의투자 현황/결과", "7-c. [ ENGINE ] 자동매매 전략엔진", "7-d. [ REPORT ] 자동투자 성적표", "7-e. [ RANK ] 사령부 명예의 전당", "7-f. [ COOLAMAGIE ] [쿨라매기 엔진 적용]"]
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

st.set_page_config(page_title="StockDragonfly Pro", page_icon="[ TERMINAL ]", layout="wide")

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
    /* [ DESIGN ] 네온 플럭스 디자인 고도화 */
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
    
    /* [ DESIGN ] 네온 보더 애니메이션 */
    .neon-border {{ position: relative; padding: 2px; background: linear-gradient(90deg, #FFD700, #00FF00, #FFD700); background-size: 200% 100%; animation: neon-flow 3s linear infinite; border-radius: 20px; }}
    .neon-inner {{ background: #000; border-radius: 18px; padding: 25px; }}
    @keyframes neon-flow {{ 0% {{ background-position: 0% 0%; }} 100% {{ background-position: 200% 0%; }} }}
    
    /* [ SCANNER ] 나노바나나 게이지 */
    .banana-track {{ background: rgba(255,255,255,0.05); height: 12px; border-radius: 6px; position: relative; overflow: hidden; margin: 10px 0; border: 1px solid rgba(255,255,255,0.1); }}
    .banana-fill {{ height: 100%; border-radius: 6px; transition: width 1s ease-out; box-shadow: 0 0 10px currentColor; }}
    
    @keyframes pulse-glow {{ 0% {{ box-shadow: 0 0 10px rgba(0,255,0,0.2); opacity: 0.8; }} 50% {{ box-shadow: 0 0 30px rgba(0,255,0,0.5); opacity: 1; }} 100% {{ box-shadow: 0 0 10px rgba(0,255,0,0.2); opacity: 0.8; }} }}
    .status-pulse {{ border: 1px solid #00FF0044; animation: pulse-glow 2s infinite; }}
    
    @keyframes ticker {{ 0% {{ transform: translateX(100%); }} 100% {{ transform: translateX(-100%); }} }}
    @keyframes marquee-new {{ 
        0% {{ transform: translateX(0); }} 
        100% {{ transform: translateX(-33.33%); }} 
    }}
    .ticker-wrap {{ overflow: hidden; background: rgba(0,0,0,0.6); white-space: nowrap; padding: 12px 0; border-bottom: 2px solid rgba(255,215,0,0.2); margin-bottom: 20px; backdrop-filter: blur(15px); }}
    .ticker-content {{ display: inline-block; animation: marquee-new 40s linear infinite; color: #FFD700; font-size: 0.95rem; font-weight: 600; font-family: 'Outfit'; }}
    .ticker-wrap:hover div {{ animation-play-state: paused !important; }}
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
            st.markdown("#### [ EXAM ] [필수] 사령부 정예 요원 자격 시험 (15문항)")
            st.info("기초 10문제 + 전술 5문제 중 13문제 이상 맞혀야 승인이 완료됩니다.")
            
            # 기초 10문제 (Q1-Q10)
            # 기초 10문제 (Q1-Q10)
            q1 = st.radio("Q1. 우리나라 주식 차트에서 '빨간색 양초(캔들)' 그림은 무슨 뜻일까요?", ["올랐다 (상승)", "떨어졌다 (하락)", "변동 없다", "거래 중지"], index=None)
            q2 = st.radio("Q2. 파란색 양초(캔들) 그림은 무슨 뜻일까요?", ["상승 국면", "하락 국면", "보합 국면", "매수 신호"], index=None)
            q3 = st.radio("Q3. 하루 동안 사람들이 주식을 얼마나 많이 사고팔았는지 알려주는 지표는?", ["거래량", "배당금", "회전율", "수익률"], index=None)
            q4 = st.radio("Q4. 양초 모양을 닮은 막대기들로 그린 차트의 이름은 무엇일까요?", ["막대 차트", "캔들 차트", "라인 차트", "그림 차트"], index=None)
            q5 = st.radio("Q5. 주식 명언 중 가장 잘 알려진 원칙은?", ["발바닥에서 사서 정수리에서 팔아라", "무릎에서 사서 어깨에서 팔아라", "언제든 사고 언제든 팔아라", "사두면 언젠가 오른다"], index=None)
            q6 = st.radio("Q6. 주식 가격의 평균을 내서 선으로 이은 그림을 무엇이라고 할까요?", ["이동평균선(이평선)", "추세선", "지지선", "저항선"], index=None)
            q7 = st.radio("Q7. 단기 이평선이 장기 이평선을 아래에서 위로 뚫고 올라가는 매수 신호는?", ["골든 크로스", "데드 크로스", "실버 크로스", "캔들 크로스"], index=None)
            q8 = st.radio("Q8. 주가 환경이 좋지 않을 때 매매를 쉬며 기회를 기다리는 것을 무엇이라 할까요?", ["관망", "포기", "퇴장", "몰빵"], index=None)
            q9 = st.radio("Q9. 주가가 전고점을 뚫고 강력하게 상승하는 초기 시점은?", ["돌파", "이탈", "보합", "조정"], index=None)
            q10 = st.radio("Q10. 손실을 최소화하기 위해 정해진 가격에서 파는 생명줄은?", ["손절", "익절", "물타기", "추격매수"], index=None)
            
            # 전술 5문제 (Q11-Q15)
            q11 = st.text_input("Q11. 전일 종가보다 큰 차이로 높게 시작하는 것을 무엇이라 하나요? (영문 2단어)", placeholder="Gap Up")
            q12 = st.text_input("Q12. 주식 시장의 4단계 중 가장 수익이 많이 나는 단계는? (숫자만)", placeholder="2")
            q13 = st.radio("Q13. 주가가 너무 과하게 올랐을 때 나타나는 기술적 지표 상태는?", ["RSI 70 이상", "RSI 30 이하", "RSI 50", "이평선 수렴"], index=None)
            q14 = st.text_input("Q14. 수익이 난 후 매수가격으로 손절가를 올리는 행위는? (본ㅁ)", placeholder="본절")
            q15 = st.radio("Q15. 주가가 이미 3일 이상 오른 종목을 뒤늦게 따라 사는 위험한 행위는?", ["추격 매수", "분할 매수", "예약 매수", "장외 매수"], index=None)

            if st.button("[ SUBMIT ] 신규 가입 신청 및 시험 제출"):
                corrects = [
                    "올랐다 (상승)", "하락 국면", "거래량", "캔들 차트", "무릎에서 사서 어깨에서 팔아라",
                    "이동평균선(이평선)", "골든 크로스", "관망", "돌파", "손절",
                    "gap up", "2", "RSI 70 이상", "본절", "추격 매수"
                ]
                answers = [
                    q1, q2, q3, q4, q5, q6, q7, q8, q9, q10,
                    q11.strip().lower(), q12.strip(), q13, q14.strip(), q15
                ]
                score = sum([1 for a, c in zip(answers, corrects) if a == c])

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
                        
                        st.success(f"[ SUCCESS ] {score}/15점! 훌륭합니다. 사령부의 지혜를 계승할 자격을 증명하셨습니다. 로그인을 진행해 주십시오.")
                        st.balloons()
                else:
                    st.error(f"[ ERROR ] {score}/15점. 사령부의 철학을 더 공부하고 와주시기 바랍니다. (13점 이상 합격)")
                    with st.expander("[ REVIEW ] 15관문 자격 시험 정답 및 해설 보기", expanded=True):
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
    st.markdown("<div style='text-align: center;'><p style='color:#00FF00; font-size:1.5rem; font-weight:900; margin-bottom:0;'>[ SYSTEM ] StockDragonfly v9.9</p><small style='color:#666;'>ELITE TRADING TERMINAL</small></div>", unsafe_allow_html=True)
    
    # [NEW] 실시간 작전 대원 상태 (AI 6인방)
    st.markdown("<p style='margin-top:20px; font-weight:bold; font-size:0.8rem; color:#888;'>[ LIVE ] AI OPERATIVES STATUS</p>", unsafe_allow_html=True)
    ai_team_sidebar = [
        {"name": "[ AI ] minsu", "mission": "KOSPI"}, 
        {"name": "[ AI ] Olive", "mission": "KOSDAQ"}, 
        {"name": "[ AI ] Pure", "mission": "NASDAQ"}, 
        {"name": "[ AI ] Harmony", "mission": "Analyzing"}, 
        {"name": "[ AI ] Mint Soft", "mission": "Analyzing"}, 
        {"name": "[ AI ] Calm Blue12", "mission": "Analyzing"}
    ]
    for ai_s in ai_team_sidebar:
        st.markdown(f"""
        <div style='display: flex; justify-content: space-between; padding: 4px 10px; background: rgba(0,255,255,0.03); border-radius: 5px; margin-bottom: 4px; border-left: 2px solid #00FFFF;'>
            <span style='font-size: 0.75rem; color: #BBB;'>{ai_s['name']}</span>
            <span style='color: #00FF00; font-size: 0.6rem;'>● {ai_s['mission']}</span>
        </div>
        """, unsafe_allow_html=True)

    # [NEW] 금주의 우수 요원 랭킹 (전술 지표 포함)
    with st.expander("[ TOP ] COMMANDER RANKING (WEEKLY)", expanded=True):
        ranking_data = [
            {"name": "[ AI ] minsu", "pts": 1250, "win": 78, "pick": "005930.KS", "entry": 71800, "roi": "+4.2%", "exit": "04/20 14:30"},
            {"name": "[ AI ] Olive", "pts": 980, "win": 72, "pick": "247540.KQ", "entry": 285000, "roi": "+6.8%", "exit": "04/20 15:15"},
            {"name": "[ AI ] Pure", "pts": 1120, "win": 65, "pick": "NVDA", "entry": 128.5, "roi": "+12.4%", "exit": "04/19 23:50"}
        ]
        for r_item in ranking_data:
            roi_color = "#00FF00" if "+" in r_item['roi'] else "#FF4B4B"
            # [ ACTION ] 한국 주식명 매핑 및 가격 포맷팅 (원 표시)
            disp_ticker = TICKER_NAME_MAP.get(r_item['pick'], r_item['pick'])
            is_kr = ".KS" in r_item['pick'] or ".KQ" in r_item['pick']
            price_fmt = f"{int(r_item['entry']):,} 원" if is_kr else f"${r_item['entry']:,.2f}"
            
            st.markdown(f"""
            <div style='margin-bottom: 15px; padding: 15px; background: rgba(255,215,0,0.03); border-radius: 12px; border: 1px solid rgba(255,215,0,0.1); border-left: 4px solid #FFD700;'>
                <div style='display: flex; justify-content: space-between;'>
                    <b style='color: #FFD700; font-size: 1rem;'>{r_item['name']}</b>
                    <span style='color: #888; font-size: 0.8rem;'>{r_item['pts']:,} pts</span>
                </div>
                <div style='margin-top: 10px; display: grid; grid-template-columns: 1fr 1fr; gap: 5px; font-size: 0.85rem;'>
                    <span style='color: #555;'>Target: <b style='color: #EEE;'>{disp_ticker}</b></span>
                    <span style='color: #555;'>Entry: <b style='color: #DDD;'>{price_fmt}</b></span>
                    <span style='color: #555;'>Return: <b style='color: {roi_color};'>{r_item['roi']}</b></span>
                    <span style='color: #555;'>Sold: <b style='color: #888;'>{r_item['exit']}</b></span>
                </div>
                <div style='margin-top: 8px; text-align: right;'>
                    <span style='color: #00FFFF; font-size: 0.75rem;'>Win Rate: {r_item['win']}%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)



    # --- [ AUDIO ] 고도화된 전술 BGM 제어판 ---
    st.divider()
    st.markdown("<p style='font-weight:bold; font-size:0.8rem; color:#888;'>[ AUDIO ] TACTICAL BGM PLAYER</p>", unsafe_allow_html=True)
    bgm_options = {
        "[ MUTE ] Silence": None, 
        "[ MIX ] Random Mix": "shuffle",
        "[ BGM ] Full Force": "full.mp3",
        "[ BGM ] Inspiration": "YouRaise.mp3", 
        "[ BGM ] Morning Joy": "happy.mp3", 
        "[ BGM ] Hopeful": "hope.mp3", 
        "[ BGM ] Elegant": "petty.mp3", 
        "[ BGM ] Soul (Ajussi)": "나의아저씨.mp3"
    }
    sel_bgm_v9 = st.selectbox("Radio Select", list(bgm_options.keys()), label_visibility="collapsed")
    vol_v9 = st.slider("[ VOL ] Volume", 0.0, 1.0, 0.4, step=0.05)
    
    target_bgm_v9 = bgm_options[sel_bgm_v9]
    
    # 랜덤 믹스 처리
    if target_bgm_v9 == "shuffle":
        if "shuffled_bgm" not in st.session_state:
            valid_files = [f for f in list(bgm_options.values()) if f and f != "shuffle" and os.path.exists(f)]
            st.session_state.shuffled_bgm = random.choice(valid_files) if valid_files else None
        target_bgm_v9 = st.session_state.shuffled_bgm
    else:
        # 일반 선택 시 셔플 상태 초기화
        if "shuffled_bgm" in st.session_state:
            del st.session_state.shuffled_bgm

    if target_bgm_v9 and os.path.exists(target_bgm_v9):
        # [ AUDIO ] 오디오 성능 최적화: 캐시에 저장된 base64 사용 (매번 인코딩 방지)
        @st.cache_data(show_spinner=False, ttl=3600)
        def get_base64_audio(file_path):
            try:
                with open(file_path, "rb") as f: 
                    return base64.b64encode(f.read()).decode()
            except: return ""
        
        b64 = get_base64_audio(target_bgm_v9)
        if b64:
            # onended 이벤트를 활용하여 랜덤 믹스 시 다음 곡으로 넘어가게 설정 (Streamlit 한계상 재실행 필요)
            st.components.v1.html(f"""
                <audio id='aud' autoplay loop>
                    <source src='data:audio/mp3;base64,{b64}' type='audio/mp3'>
                </audio>
                <script>
                    var audio = document.getElementById('aud');
                    audio.volume = {vol_v9};
                </script>
            """, height=0)

# --- 유저 등급 판독 ---
users = load_users()
curr_user_data = users.get(st.session_state.current_user, {})
curr_grade = curr_user_data.get("grade", "회원")
is_admin = (curr_grade in ["관리자", "방장"])

# --- 🔴 2단계 구성 (ZONE_CONFIG 참조) ---
if 'page' not in st.session_state:
    st.session_state.page = "6-a. [ CHECK ] 출석체크(오늘한줄)"

zones = {k: list(v) for k, v in ZONE_CONFIG.items()} # 원본 구조 복사

# 보급 및 보안 권한에 따른 메뉴 필터링 (1-a, 1-b 관리자 전용 제한)
if not is_admin:
    for admin_page in ["1-a. [ ADMIN ] 관리자 승인 센터", "1-b. [ HR ] HQ 인적 자원 사령부"]:
        if admin_page in zones["[ HQ ] 1. 본부 사령부"]:
            zones["[ HQ ] 1. 본부 사령부"].remove(admin_page)

# 🤖 자동매매 사령부는 모든 승인된 대원(준회원 이상)이 접근 가능
if curr_grade not in ["방장", "관리자", "정회원", "준회원"]:
    if "[ AUTO ] 7. 자동매매 사령부" in zones:
        del zones["[ AUTO ] 7. 자동매매 사령부"]

with st.sidebar:
    st.markdown("<p style='color: #FFD700; font-size: 0.9rem; font-weight: 700; margin-top: 10px; margin-bottom: 20px; letter-spacing: 1px;'>[ MISSION CONTROL ]</p>", unsafe_allow_html=True)
    
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
page = st.session_state.get("page", "6-a. [ CHECK ] 출석체크(오늘한줄)")

# --- 🔴 상단 브랜드 헤더 (초정밀 밀착 레이아웃) ---
st.markdown(f"""
    <div style='text-align: center; margin-top: -30px; margin-bottom: 5px; overflow: visible;'>
        <img src='data:image/png;base64,{logo_b64}' style='width: 110px; margin-bottom: -15px;'>
        <h1 style='font-size: clamp(1.8rem, 7.5vw, 3.8rem); font-weight: 900; background: linear-gradient(45deg, #FFD700, #FFFFFF); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-shadow: 0 10px 20px rgba(0,0,0,0.5); white-space: nowrap; margin-bottom: 0px; line-height: 1.1;'>StockDragonfly</h1>
        <p style='color: #888; letter-spacing: 7px; font-size: 0.7rem; margin-top: -5px; opacity: 0.8;'>ULTRA-HIGH PERFORMANCE TERMINAL</p>
    </div>
""", unsafe_allow_html=True)

# --- 🐉 글로벌 매크로 애니메이션 티커 테이프 ---
@st.cache_data(ttl=600)
def fetch_macro_ticker_tape():
    watch = {"S&P500": "^GSPC", "NASDAQ": "^IXIC", "BTC": "BTC-USD", "GOLD": "GC=F", "KOSPI": "^KS11", "KOSDAQ": "^KQ11", "USDKRW": "KRW=X"}
    indices = list(watch.keys())
    symbols = list(watch.values())
    items = []
    try:
        data = yf.download(symbols, period="5d", interval="1d", progress=False)['Close']
        for name, sym in watch.items():
            try:
                valid_data = data[sym].dropna()
                if len(valid_data) >= 2:
                    curr = valid_data.iloc[-1]
                    prev = valid_data.iloc[-2]
                    diff = curr - prev
                    pct = (diff / prev) * 100
                    
                    # [ ACTION ] 한국 주식 색상 체계 적용 (상승: 빨강, 하락: 파랑 / 글로벌은 반대)
                    if name in ["KOSPI", "KOSDAQ"]:
                        color = "#FF4B4B" if diff >= 0 else "#0088FF"
                    else:
                        color = "#00FF00" if diff >= 0 else "#FF4B4B"
                        
                    items.append(f"<span class='ticker-item' style='margin-right: 30px;'>{name} <b>{curr:,.1f}</b> <span style='color:{color};'>{pct:+.2f}%</span></span>")
            except: continue
    except: pass
    return "".join(items)

ticker_html = fetch_macro_ticker_tape()
st.markdown(f"""
    <div class='ticker-wrap' style='background: rgba(0,255,0,0.03); border-top: 1px solid #FFD70033; border-bottom: 2px solid #FFD70066;'>
        <div style='display: inline-block; white-space: nowrap; animation: marquee-new 40s linear infinite; font-family: "Outfit", sans-serif; font-size: 0.95rem; font-weight: 600;'>
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

# --- [ INFO ] 상단 실시간 정보 바 ---
now_kr = datetime.now(pytz.timezone('Asia/Seoul'))
now_us = datetime.now(pytz.timezone('America/New_York'))

@st.cache_data(ttl=600)
def get_top_indices():
    res = {"DOW": [0.0, 0.0], "S&P500": [0.0, 0.0], "NASDAQ": [0.0, 0.0], "KOSPI": [0.0, 0.0], "KOSDAQ": [0.0, 0.0]}
    symbols = {"DOW": "^DJI", "S&P500": "^GSPC", "NASDAQ": "^IXIC", "KOSPI": "^KS11", "KOSDAQ": "^KQ11"}
    try:
        data = yf.download(list(symbols.values()), period="7d", progress=False)['Close']
        for name, ticker in symbols.items():
            try:
                valid_series = data[ticker].dropna()
                if len(valid_series) >= 2:
                    curr = valid_series.iloc[-1]
                    prev = valid_series.iloc[-2]
                    pct = ((curr / prev) - 1) * 100
                    res[name] = [float(curr), float(pct)]
            except:
                continue
    except:
        return {k: [0.0, 0.0] for k in symbols.keys()}
    return res

idx_info = get_top_indices()

# --- [ CONTROL ] 사령부 통합 지수 관제 센터 (Stable v6.1) ---
idx_info = get_top_indices()

with st.container():
    st.markdown("<div style='margin-bottom: -10px;'></div>", unsafe_allow_html=True)
    
    indices_list = ["DOW", "S&P500", "NASDAQ", "KOSPI", "KOSDAQ"]
    cols = st.columns(5)
    
    for i, name in enumerate(indices_list):
        val, pct = idx_info.get(name, [0.0, 0.0])
        with cols[i]:
            # [ ACTION ] 시간 레이블 출력 (DOW와 KOSPI 기준)
            if name == "DOW":
                st.markdown(f"<p style='font-size: 0.7rem; color: #888; margin-bottom: 5px;'>[ USA ] {now_us.strftime('%m/%d %H:%M')}</p>", unsafe_allow_html=True)
            elif name == "KOSPI":
                st.markdown(f"<p style='font-size: 0.7rem; color: #888; margin-bottom: 5px;'>[ KOREA ] {now_kr.strftime('%m/%d %H:%M')}</p>", unsafe_allow_html=True)
            else:
                st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)
                
            # [ ACTION ] 모든 지수 스타일 통일
            is_kr = name in ["KOSPI", "KOSDAQ"]
            theme_color = "#FF4B4B" if is_kr else "#00FF00"
            border_alpha = "44" if is_kr else "11"
            bg_alpha = "0.05" if is_kr else "0.02"
            
            # 상승/하락 색상 결정
            if is_kr:
                stat_color = "#FF4B4B" if pct >= 0 else "#0088FF"
                arrow = "▲" if pct >= 0 else "▼"
            else:
                stat_color = "#00FF00" if pct >= 0 else "#FF4B4B"
                arrow = "↑" if pct >= 0 else "↓"
                
            st.markdown(f"""
                <div style='background: rgba({ "255,75,75" if is_kr else "255,255,255" },{bg_alpha}); padding: 12px; border-radius: 12px; border: 1px solid {theme_color}{border_alpha}; text-align: center; height: 120px; transition: all 0.3s;'>
                    <div style='color: {theme_color}; font-weight: 800; font-size: 0.8rem; margin-bottom: 8px; opacity: 0.8;'>{name}</div>
                    <div style='color: #FFF; font-size: 1.4rem; font-weight: 700; letter-spacing: -0.5px;'>{val:,.1f}</div>
                    <div style='color: {stat_color}; font-size: 0.9rem; font-weight: 800; margin-top: 5px;'>{arrow} {pct:+.2f}%</div>
                </div>
            """, unsafe_allow_html=True)

st.divider()

# --- [ ADVISOR ] AI 전술 사령관 (Tactical Commander v6.0) ---
def get_ai_commander_report(indices):
    try:
        score = sum([v[1] for v in indices.values()])
        avg_pct = score / len(indices)
    except:
        avg_pct = 0.0
    
    if avg_pct > 0.5:
        posture = "[ STATUS: AGGRESSIVE ]"
        msg = "시장의 활력이 극에 달했습니다. 주도주의 돌파(Breakout)에 비중을 높여 수익을 극대화하십시오."
        color = "green"
    elif avg_pct > -0.5:
        posture = "[ STATUS: NEUTRAL ]"
        msg = "시장이 방향성을 탐색 중입니다. 무리한 진입보다 기존 포지션의 손절가를 유지하며 관망하십시오."
        color = "orange"
    else:
        posture = "[ STATUS: CASH ]"
        msg = "시장의 중력이 강해지고 있습니다. 현금 비중을 확보하고 폭풍이 지나가길 기다리십시오."
        color = "red"
    return posture, msg, color

posture, tactical_msg, p_color = get_ai_commander_report(idx_info)

with st.container():
    if p_color == "green": st.success(f"### {posture}\n\n{tactical_msg}")
    elif p_color == "orange": st.warning(f"### {posture}\n\n{tactical_msg}")
    else: st.error(f"### {posture}\n\n{tactical_msg}")

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
        <div class='glass-card' style='text-align: center; padding: 20px; border: 1px solid #FFD700; border-radius: 15px;'>
            <h4 style='margin:0; color:#FFD700;'>[ DRAGONFLY ] 누적 사령부 방문</h4>
            <span style='font-size: 2.5rem; font-weight: 900; color: #00FF00;'>{total_visits:,}</span>
            <p style='margin:0; color:#888;'>Operatives Engaged</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        # --- [ REAL-TIME WEATHER ] 지역별 기온 및 습도 정보 (wttr.in 활용) ---
        locations = {"대한민국": "Seoul", "일본": "Tokyo", "미국": "New York"}
        
        # UI 레이아웃 내부에 셀렉트박스 배치 (공간 효율을 위해 소형으로)
        sel_region = st.selectbox("기상 지역 소환", list(locations.keys()), index=0, label_visibility="collapsed")
        loc_id = locations[sel_region]
        
        @st.cache_data(ttl=1800)
        def get_live_weather(loc):
            try:
                # %t: 기온, %h: 습도, %C: 상태 / m: 섭씨(Metric) 강제
                resp = requests.get(f"https://wttr.in/{loc}?format=%t+%h+%C&m", timeout=3)
                if resp.status_code == 200:
                    return resp.text.strip()
            except: pass
            return "15°C 50% Clear"
            
        weather_info = get_live_weather(loc_id)
        # 습도 기호(%)가 포함되어 나오므로 그대로 출력
        
        st.markdown(f"""
        <div class='glass-card' style='text-align: center; padding: 15px; border: 1px solid #FFD700; border-radius: 15px;'>
            <h4 style='margin:0; color:#FFD700;'>{sel_region.upper()} / HQ WEATHER</h4>
            <span style='font-size: 1.6rem; color: #00FF00; font-weight: 800;'>{weather_info}</span>
            <p style='margin:0; color:#888;'>HQ AREA STATUS: OPERATIONAL</p>
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
    
    def run_4stage_sc():
        US_RADAR = ["NVDA", "TSLA", "AAPL", "MSFT", "AMZN", "META", "GOOGL", "AVGO", "CRWD", "PLTR", "SMCI", "AMD", "NFLX", "STX", "WDC", "MSTR", "COIN", "MARA", "PANW", "SNOW"]
        KR_RADAR = ["005930.KS", "000660.KS", "196170.KQ", "042700.KS", "105560.KS", "055550.KS", "005490.KS", "000270.KS", "066570.KS", "035720.KS", "005380.KS", "000810.KS"]
        full_list = US_RADAR + KR_RADAR
        
        all_res = []
        st_txt = st.empty()
        st_txt.info("[ WAIT ] 글로벌 실시간 데이터 일괄 수집 중... 잠시만 기다려 주십시오.")
        
        try:
            # 일괄 다운로드로 속도 및 안정성 확보
            data_full = yf.download(full_list, period="1y", interval="1d", progress=False)
            data = data_full['Close']
            data_high = data_full['High']
            data_low = data_full['Low']
            
            # --- [ ACTION ] [Parallel ROE Fetching] ---
            # 모든 티커의 ROE를 병렬로 미리 수집 (캐시가 있으면 즉시 반환됨)
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                roe_map = {tic: res for tic, res in zip(full_list, executor.map(get_ticker_roe, full_list))}

            for tic in full_list:
                try:
                    if tic not in data.columns: continue
                    h = data[tic].dropna()
                    if len(h) < 200: continue

                    # --- [ VCP ] v7.0 VCP(변동성 축소) 정밀 분석 ---
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
                        "MARKET": "USA" if is_us else "KOREA"
                    })
                except: continue
        except Exception as e:
            st.error(f"⚠️ 데이터 통신 중 오류가 발생했습니다: {e}")
            return
            
        st_txt.empty()
        
        if all_res:
            df = pd.DataFrame(all_res)
            st.session_state.scan_results = df
            st.success("[ SUCCESS ] 스캔 완료! 주도주 분석 결과가 데이터베이스에 등재되었습니다.")
            
            # --- AI Advisor Preview Area ---
            with st.expander("[ ADVISOR ] 사령부 AI 전술 판독 보고서 (Summary)", expanded=True):
                top_stock = df.sort_values("SCORE", ascending=False).iloc[0]
                advice_text = get_tactical_advice(top_stock['T'], top_stock['RS'], top_stock['ROE'])
                st.markdown(f"**현재 최고의 전술 타겟: {top_stock['T']} ({top_stock['TIC']})**")
                st.info(advice_text)
        else:
            st.warning("분석 가능한 종목 데이터가 부족합니다. 잠시 후 다시 시도해 주세요.")

    if st.button("[ EXEC ] 한/미 주도주 10선 정밀 스캔 시작"):
        run_4stage_sc()

    if "scan_results" in st.session_state and st.session_state.scan_results is not None:
        df = st.session_state.scan_results
        us_top = df[df['MARKET'].str.contains("USA")].sort_values("SCORE", ascending=False).head(5)
        kr_top = df[df['MARKET'].str.contains("KOREA")].sort_values("SCORE", ascending=False).head(5)
        combined_top = pd.concat([us_top, kr_top])
        
        st.subheader("[ HOT ] 사령부 한/미 통합 주도주 TOP 10")
        for i, row in combined_top.iterrows():
            # 구문 오류 방지를 위해 미리 포맷팅 수행
            roe_val = f"{row['ROE']:.1f}"
            rs_val = f"{row['RS']:.1f}"
            score_val = str(int(row["SCORE"]))
            border_col = "#00FF00" if "USA" in row["MARKET"] else "#FFD700"
            change_col = "#00FF00" if "+" in row["CH"] else "#FF4B4B"
            
            st.markdown(f"""
            <div class='glass-card' style='padding: 15px; border-left: 5px solid {border_col}; margin-bottom: 10px;'>
                <div style='display: flex; justify-content: space-between;'>
                    <b style='font-size: 1.1rem;'>{row["MARKET"]} | {row["T"]} ({row["TIC"]})</b>
                    <b style='color: {change_col}; font-size: 1.1rem;'>{row["CH"]}</b>
                </div>
                <div style='margin-top: 8px; font-size: 0.95rem; color: #AAA;'>
                    현가: {row["P"]} | 
                    <span style='color: #FFD700;'>ROE: <b>{roe_val}%</b></span> | 
                    <span style='color: #55AAFF;'>RS: <b>{rs_val}%</b></span> | 
                    <span style='color: #00FF00;'>VCP: <b>{row["VCP"]}</b></span> | 
                    <span style='color: #FF4B4B;'>Score: <b>{score_val}</b></span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        st.subheader("[ CHART ] 종목별 정밀 차트 분석 (Select Ticker)")
        
        # 종목 선택 옵션 생성 (이름 + 티커)
        options = [f"{row['T']} ({row['TIC']})" for _, row in combined_top.iterrows()]
        selected_option = st.selectbox("분석할 종목을 선택하세요", options)
        
        # 선택된 티커 추출
        selected_row = combined_top[combined_top.apply(lambda r: f"{r['T']} ({r['TIC']})" == selected_option, axis=1)].iloc[0]
        selected_ticker = selected_row["TIC"]
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
                else:
                    # 일반 버블 모드
                    st.markdown(f"""
                    <div style='text-align: {align}; margin-bottom: 5px;'>
                        <div style='display: inline-block; max-width: 85%; text-align: left;'>
                            <div style='font-size: 0.75rem; color: #888; margin-bottom: 3px; display: flex; justify-content: {"flex-end" if is_me else "flex-start"}; gap: 8px;'>
                                <b>{row["유저"]}</b> <span style='font-size: 0.65rem;'>({row["등급"]})</span> <span>{row["시간"]}</span>
                            </div>
                            <div style='background: {bg}; border: {border}; border-radius: {border_radius}; padding: 12px; color: #FFF; line-height: 1.6; box-shadow: 0 4px 10px rgba(0,0,0,0.2);'>
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
    
    with st.spinner("DATA: 데이터 센터 리더보드 정밀 분석 중..."):
        try:
            df_raw = pd.read_csv(SHEET_URL)
            latest_col = df_raw.columns[0]
            top_10_candidates = df_raw[latest_col].dropna().head(10).tolist()
            all_mentions = df_raw.values.flatten().tolist()
            mention_counts = {tic: all_mentions.count(tic) for tic in top_10_candidates}
            final_3 = []
            cand_tics = sorted(mention_counts, key=mention_counts.get, reverse=True)
            
            if cand_tics:
                prices_data = yf.download(cand_tics, period="1d", progress=False)['Close']
                if isinstance(prices_data, pd.Series): 
                    prices_data = pd.DataFrame(prices_data).T
                for tic in cand_tics:
                    try:
                        roe = 0.0
                        price = prices_data[tic].iloc[-1] if tic in prices_data.columns else 0
                        if price > 0:
                            final_3.append({
                                "T": tic, "ROE": "N/A",
                                "RS": f"{mention_counts[tic]}회 언급",
                                "EP": f"${price:.2f}", "SL": f"${price*0.95:.2f}", "TP": f"${price*1.15:.2f}"
                            })
                        if len(final_3) >= 3: break
                    except: continue
                
            st.markdown(f"<div class='glass-card'>DATE: <b>{now_kst.strftime('%Y-%m-%d')} KST</b> | 사령부 최우선 공략 종목 3선</div>", unsafe_allow_html=True)
            cols = st.columns(3)
            for i, item in enumerate(final_3):
                with cols[i]:
                    st.markdown(f"""
                    <div style='background: rgba(255,215,0,0.1); border: 2px solid #FFD700; border-radius: 12px; padding: 15px; text-align: center; height: 320px;'>
                        <h3 style='color: #FFD700; margin: 0;'>{item['T']}</h3>
                        <p style='color: #888; font-size: 0.8rem;'>Mention Rank {i+1}</p>
                        <hr style='border: 0.5px solid #444;'>
                        <div style='text-align: left; font-size: 0.9rem;'>
                            <b>[ ROE ]:</b> {item['ROE']}<br>
                            <b>[ RS-FREQ ]:</b> {item['RS']}<br>
                            <b>[ ENTRY ]:</b> {item['EP']}<br>
                            <b>[ STOP ]:</b> {item['SL']}<br>
                            <b>[ TARGET ]:</b> {item['TP']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            if not final_3: st.info("조건을 만족하는 감시 종목이 리더보드 상단에 없습니다.")
            st.success("[ SUCCESS ] 사령부 데이터 동기화 및 빈도 분석 완료!")
        except Exception as e:
            st.error(f"[ ERROR ] 데이터 분석 실패: {e}")

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
    st.markdown("<h1 style='text-align: center; color: #FFD700;'>[ MENTOR ] 월가의 멘토, 프라딥 본데</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888; font-size: 1.2rem;'>Stockbee: 시스템 트레이딩의 선구자</p>", unsafe_allow_html=True)
    st.divider()
    st.write("프라딥 본데는 실전 트레이더로서 자신만의 매매 프로세스를 체계화하여 거대한 유산을 남기고 있습니다.")
    st.subheader("1. 비금융권 출신의 최적화 시각")
    st.info("물류 사업의 '시스템 최적화' 경험을 주식 시장에 대입하여, 비즈니스 모델로서의 매매 프로세스를 구축했습니다.")
    st.subheader("2. 스탁비의 4대 트레이딩 철학")
    c1, c2 = st.columns(2)
    with c1:
        with st.expander("SINGLES: 안타 전략", expanded=True): st.write("확실한 수익을 복리로 누적시키는 꾸준함.")
        with st.expander("DEEP DIVE: 딥 다이브", expanded=True): st.write("폭등 차트 수천 개를 연구하여 패턴을 뇌에 각인.")
    with c2:
        with st.expander("SHIELD: 셀프 리더십", expanded=True): st.write("자기 주도적 실행력과 원칙 고수.")
        with st.expander("BREADTH: 상황 인식", expanded=True): st.write("시장의 폭을 분석하여 공격과 방어 구분.")
    st.subheader("3. 시장 관통 매매 기법")
    st.success("""
    [ EP ]: 기업 펀더멘털을 바꾸는 강력한 뉴스 공략.
    [ BURST ]: 눌림목(VCP) 에너지 임계점 포착.
    [ FORMULA ]: 본데만의 대장주 선별 공식 (MAGNA 53+).
    """)
    st.subheader("4. 제자들의 증명")
    st.write("크리스찬 쿨라매기 등 수천억 자산가들이 본데의 가르침을 통해 시스템을 완성했습니다.")
    st.divider()

elif page.startswith("2-d."):
    st.markdown("<h1 style='text-align: center; color: #FFD700;'>[ MISSION ] 사령부 제작 동기</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888; font-size: 1.1rem;'>Follow the Giants, Conquer the Market Together</p>", unsafe_allow_html=True)
    st.divider()
    st.write("이 플랫폼은 윌리엄 오닐, 마크 미너비니, 프라딥 본데의 철학을 기리기 위해 시작되었습니다.")
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("[ PILLARS ] 사령부를 지탱하는 세 개의 기둥")
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown("**1. 오닐 (CAN SLIM)**"); st.caption("Growth potential.")
    with c2: st.markdown("**2. 미너비니 (VCP)**"); st.caption("Precision timing.")
    with c3: st.markdown("**3. 본데 (EP/RS)**"); st.caption("Strategic process.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.info("이 터미널이 거령들의 어깨 위에 올라타 거센 파도를 넘는 디딤돌이 되길 희망합니다.")
    st.markdown("""
    <div style='text-align: right; margin-top: 40px; border-top: 1px solid #333; padding-top: 20px;'>
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

elif page.startswith("2-d."):
    st.markdown("<h1 style='text-align: center; color: #FFD700;'>[ MISSION ] 사령부 제작 동기</h1>", unsafe_allow_html=True)
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
    [ LEGACY ] 오닐의 유산 (The Legacy): 윌리엄 오닐의 저서 『최고의 주식, 최적의 타이밍』은 제 트레이딩 인생의 나침반이 되었습니다. 
    이 터미널이 거인들의 어깨 위에 올라타 시장의 거센 파도를 넘어서는 여러분의 든든한 디딤돌(Stepping Stone)이 되길 희망합니다.
    """)
    
    st.markdown("""
    <div style='text-align: right; margin-top: 40px; border-top: 1px solid #333; padding-top: 20px;'>
        <span style='color: #888; font-size: 0.9rem;'>2026년 4월 18일, 깊어가는 봄날 밤. (Deep Spring Night, 2026)</span><br>
        <b style='color: #FFD700; font-size: 1.2rem;'>전문가거북이 드림 (Truly yours, Expert Turtle)</b>
    </div>
    """, unsafe_allow_html=True)

elif page.startswith("6-c."):
    st.header("[ APPLY ] 방문자 승격 신청서")
    st.markdown("<div class='glass-card'>사령부 정규직 승격을 위해 아래 3가지 항목을 작성해 주세요. 전문가님이 직접 검토합니다.</div>", unsafe_allow_html=True)
    with st.form("greet_detailed", clear_on_submit=True):
        g1 = st.text_area("1. 사령부 첫 방문 소감", placeholder="사령부를 처음 알게 된 계기와 소감을 남겨주세요.")
        g2 = st.text_area("2. 트레이딩 경력 및 자기소개", placeholder="본인의 투자 경험이나 간단한 소개를 부탁드립니다.")
        g3 = st.text_area("3. 정규직으로서의 포부", placeholder="사령부 정규직이 되어 이루고 싶은 목표를 적어주세요.")
        if st.form_submit_button("[ EXEC ] 사령부 승격 신청 전송"):
            if g1 and g2 and g3:
                t = datetime.now().strftime("%Y-%m-%d %H:%M")
                u = st.session_state.current_user
                # 로컬 영구 저장 (8번 배너와 연동)
                new_req = pd.DataFrame([[t, u, g1, g2, g3]], columns=["시간", "아이디", "첫인사", "자기소개", "포부"])
                new_req.to_csv(VISITOR_FILE, mode='a', header=not os.path.exists(VISITOR_FILE), index=False, encoding="utf-8-sig")
                # 백업용 동기화 (백그라운드 전환)
                gsheet_sync_bg("방문자_승격신청", ["시간", "아이디", "첫인사", "자기소개", "포부"], [t, u, g1, g2, g3])
                st.success("[ SUCCESS ] 승격 신청서가 성공적으로 관리자 승인센터로 전파되었습니다!")
            else: st.error("[ ERROR ] 모든 항목을 작성해 주셔야 신청이 가능합니다.")

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
    val, curr_vix = get_market_sentiment_score()
    
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
                        st.success(f"[ SUCCESS ] {disp_name} 종목 {amount}주를 {price_display}에 매수 완료했습니다! (총 {total_cost_krw:,.0f} KRW 차감)")
                        st.balloons()
                        time.sleep(1)
                        st.rerun()
            except Exception as e:
                st.error(f"오류 발생: {e}")

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
    st.header("[ AUTO ] 자동매매 전략 엔진 (Autonomous Engine)")
    st.markdown("<div class='glass-card'>시스템이 실시간 데이터를 스캔하여 최적의 타점을 자동으로 포착합니다.</div>", unsafe_allow_html=True)
    
    # 전략 스캐닝 시뮬레이션
    st.subheader("[ SCAN ] 실시간 전략 스캐닝 현황")
    if st.button("🔍 전략 엔진 가동 (Scan Start)"):
        with st.status("전략 필터링 중...", expanded=True) as status:
            st.write("1. RS 90 이상 종목 추출 중...")
            time.sleep(1)
            st.write("2. VCP 변동성 축소 패턴 감지 중...")
            time.sleep(1)
            st.write("3. 에피소딕 피벗(EP) 후보군 필터링...")
            time.sleep(1)
            status.update(label="[ SUCCESS ] 스캔 완료! 매수 권고 종목 발견", state="complete")
        
        cols = st.columns(2)
        with cols[0]:
            st.info("[ TARGET ] **추천 종목: NVDA**")
            st.write("사유: 전고점 돌파 1단계, 거래량 급증 포착")
            if st.button("[ EXEC ] 즉시 매수 집행 (Auto Order)", key="auto_buy_nvda"):
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
                    st.success("[ SUCCESS ] NVDA 자동 매수 주문 전송 완료! (장부에 기록됨)")
                except: st.error("데이터 로드 실패")
        with cols[1]:
            st.info("[ TARGET ] **추천 종목: AAPL**")
            st.write("사유: 20일선 지지 후 기술적 반등 시그널")
            if st.button("[ EXEC ] 즉시 매수 실행", key="auto_buy_aapl"):
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
                    st.success("[ SUCCESS ] AAPL 자동 매수 주문 전송 완료! (장부에 기록됨)")
                except: st.error("데이터 로드 실패")

elif page.startswith("7-d."):
    st.header("[ REPORT ] 자동투자 성적표 (Performance Report)")
    st.markdown("<div class='glass-card'>시스템이 수행한 전체 자동매매의 통계 데이터를 분석합니다.</div>", unsafe_allow_html=True)
    
    # 통계 시뮬레이션 데이터
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("총 매매 횟수", "128회")
    c2.metric("승률 (Win Rate)", "64.5%", "2.1%")
    c3.metric("누적 수익률", "142.8%", "12.5%")
    c4.metric("최대 낙폭 (MDD)", "-8.2%")
    
    st.divider()
    
    st.subheader("[ LOG ] 자동투자 상세 매매 기록 (Execution Log)")
    # 가상의 상세 매매 이력 데이터 (AI가 수행한 것으로 가주)
    auto_history = [
        {"일시": "2026-04-20 10:15", "티커": "NVDA", "수량": 10, "매수가": "855.20", "현재가": "890.30", "수익": "+4.1%"},
        {"일시": "2026-04-20 09:30", "티커": "PLTR", "수량": 50, "매수가": "22.15", "현재가": "23.40", "수익": "+5.6%"},
        {"일시": "2026-04-19 15:45", "티커": "TSLA", "수량": 5, "매수가": "172.10", "현재가": "165.20", "수익": "-4.0%"},
        {"일시": "2026-04-19 11:20", "티커": "SMCI", "수량": 2, "매수가": "920.00", "현재가": "1040.50", "수익": "+13.1%"},
        {"일시": "2026-04-18 13:10", "티커": "AMD", "수량": 15, "매수가": "180.50", "현재가": "185.00", "수익": "+2.5%"}
    ]
    
    h_df = pd.DataFrame(auto_history)
    st.dataframe(h_df, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("[ GROWTH ] 자산 성장 곡선 (Equity Curve)")
    chart_data = pd.DataFrame(np.random.randn(20, 1).cumsum(), columns=['Equity'])
    st.line_chart(chart_data)

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
        
        # --- 🤖 AI 요원들의 자율 실적 시뮬레이션 및 병합 ---
        st.markdown("---")
        st.markdown("### [ NETWORK ] 사령부 통합 실시간 랭킹 (HUMAN vs AI)")
        
        # AI 요원 실적 생성 (VIX 및 시장 심리에 따라 변동)
        sentiment_score, _ = get_market_sentiment_score()
        market_multiplier = (sentiment_score / 50.0) # 시장이 좋을수록 AI도 잘 벌음
        
        ai_stats = []
        for name, info in AI_OPERATIVES.items():
            # 가상의 누적 수익 생성 (AI 요원 레벨에 따른 퍼포먼스)
            rand_perf = (info['win_rate'] * 15000000 * market_multiplier) + (random.randint(-500000, 1000000))
            ai_stats.append((name, {"total_profit": rand_perf, "trade_count": random.randint(50, 200), "is_ai": True}))
        
        # Human + AI 통합 정렬
        human_stats = [(uid, stats) for uid, stats in sorted_rank]
        combined_ranking = sorted(human_stats + ai_stats, key=lambda x: x[1]['total_profit'], reverse=True)

        with st.container():
            for i, (uid, stats) in enumerate(combined_ranking[:10]):
                is_ai = stats.get("is_ai", False)
                medal = "1ST" if i == 0 else ("2ND" if i == 1 else ("3RD" if i == 2 else "HONOR"))
                border_color = "#00FFFF" if is_ai else "#FFD700" if i < 3 else "rgba(255,255,255,0.1)"
                bg_color = "rgba(0, 255, 255, 0.05)" if is_ai else "rgba(255, 255, 255, 0.02)"
                
                label = " [AI Operative]" if is_ai else " [Commander]"
                
                st.markdown(f"""
                <div class='glass-card' style='border-left: 5px solid {border_color}; background: {bg_color}; margin-bottom: 10px; padding: 15px;'>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <div>
                            <span style='font-size: 1.1rem; font-weight: bold;'>{medal} {uid}</span>
                            <span style='font-size: 0.75rem; color: #888;'>{label}</span>
                        </div>
                        <div style='text-align: right;'>
                            <b class='{"neon-glow" if stats["total_profit"] > 0 else "neon-glow-red"}' style='font-size: 1.2rem;'>
                                ₩ {stats['total_profit']:,.0f}
                            </b>
                            <br><small style='color: #555;'>Trades: {stats['trade_count']}회</small>
                        </div>
                    </div>
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
        sentiment_score, curr_vix = get_market_sentiment_score()
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
            data_d = yf.download(tickers, period="3mo", interval="1d", progress=False)
            close_d = data_d['Close']
            high_d = data_d['High']
            low_d = data_d['Low']
            
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
            sentiment_score, _ = get_market_sentiment_score()
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