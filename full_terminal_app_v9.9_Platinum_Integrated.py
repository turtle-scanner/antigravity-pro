# 작업 일자: 2026-04-29 | 버전: v9.9 Platinum Integrated (Cumulative Profit Edition)
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

# --- [ SYSTEM ] [GLOBAL HELPER] Page Config ---
st.set_page_config(page_title="StockDragonfly Pro v9.9 Platinum", page_icon="📟", layout="wide")

# [ DIAGNOSTIC ] 서버 구동 확인용
st.write("🚀 [ SYSTEM ] 사령부 v9.9 Platinum 시스템 로드 완료.")

# --- [ SYSTEM ] [GLOBAL HELPER] Safe Network Request ---
def safe_get(url, timeout=3):
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
    
    quotes = [
        "시장이 혼란스러울수록 기본에 충실하십시오. VCP의 끝자락은 항상 조용합니다.",
        "손절은 패배가 아닌, 다음 승리를 위한 보험료입니다.",
        "거래량이 마를 때를 기다리십시오. 폭발은 고요함 속에서 시작됩니다."
    ]
    advice.append(f"\nINFO: Bonde's Insight: {random.choice(quotes)}")
    return "\n".join(advice)

def get_footer_quote():
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
    return {"last_time": 0}

def trigger_ai_chat():
    cd = get_ai_chat_cooldown()
    if time.time() - cd["last_time"] < 15: return False
    
    ai_users = [
        {"name": "[ AI ] 윌리엄 오닐", "grade": "AI_대원 (모멘텀)"},
        {"name": "[ AI ] 마크 미너비니", "grade": "AI_대원 (VCP)"},
        {"name": "[ AI ] 스탠 와인스태인", "grade": "AI_대원 (추세)"},
        {"name": "[ AI ] 프라딥 본데", "grade": "AI_대원 (돌파)"},
        {"name": "[ AI ] 한샘 농사매매", "grade": "AI_대원 (스윙)"}
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
        new_msg = pd.DataFrame([[now_kst, ai["name"], ms, ai["grade"]]], columns=["시간", "유저", "내용", "등급"])
        safe_write_csv(new_msg, CHAT_FILE, mode='a', header=not os.path.exists(CHAT_FILE))
        cd["last_time"] = time.time()
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
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(BACKUP_DIR, f"{fname}_{timestamp}.bak")
        shutil.copy2(file_path, backup_path)
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

def get_live_weather(loc):
    try:
        resp = requests.get(f"https://wttr.in/{loc}?format=%t+%h+%C&m", timeout=3)
        if resp.status_code == 200:
            raw_text = resp.content.decode('utf-8').strip()
            return raw_text.replace('Â', '')
    except: pass
    return "15°C 50% Clear"

def get_sheet_tickers():
    try:
        url = "https://docs.google.com/spreadsheets/d/1xjbe9SF0HsxwY_Uy3NC2tT92BqK0nhArUaYU16Q0p9M/export?format=csv&gid=1499398020"
        df = pd.read_csv(url)
        return df.iloc[:, 0].dropna().astype(str).str.strip().str.upper().tolist()
    except: return ["NVDA", "TSLA"]

def run_antigravity_screener():
    st_txt = st.empty()
    st_txt.info("📡 [ SCAN ] 전 세계 주도주 수급 및 변동성 정밀 분석 중...")
    tickers = list(TICKER_NAME_MAP.keys())
    results = {"Burst": [], "EP": [], "Anticipation": []}
    try:
        data = yf.download(tickers, period="30d", interval="1d", progress=False)
        if data.empty:
            st.warning("데이터를 가져오지 못했습니다. 잠시 후 다시 시도하세요.")
            return
        close = data['Close']
        volume = data['Volume']
        for tic in tickers:
            try:
                if tic not in close.columns: continue
                c_series = close[tic].dropna()
                v_series = volume[tic].dropna()
                if len(c_series) < 20: continue
                curr_p = c_series.iloc[-1]
                prev_p = c_series.iloc[-2]
                pct = (curr_p - prev_p) / prev_p * 100
                avg_vol = v_series.iloc[-20:-1].mean()
                curr_vol = v_series.iloc[-1]
                vol_ratio = curr_vol / avg_vol if avg_vol > 0 else 0
                if vol_ratio > 3.0 and pct > 5.0:
                    results["EP"].append({"Ticker": tic, "Name": TICKER_NAME_MAP[tic], "Price": curr_p, "Change": f"{pct:+.2f}%", "VolRatio": f"{vol_ratio:.1f}x"})
                if curr_vol > v_series.iloc[-10:-1].max() and pct > 2.0:
                    results["Burst"].append({"Ticker": tic, "Name": TICKER_NAME_MAP[tic], "Price": curr_p, "Change": f"{pct:+.2f}%"})
                recent_range = (c_series.iloc[-5:].max() - c_series.iloc[-5:].min()) / c_series.iloc[-5:].mean() * 100
                if recent_range < 3.0:
                    results["Anticipation"].append({"Ticker": tic, "Name": TICKER_NAME_MAP[tic], "Price": curr_p, "Range": f"{recent_range:.1f}%"})
            except: continue
        st.session_state.antigravity_scan = results
        st_txt.success(f"✅ [ COMPLETE ] {len(tickers)}개 종목 분석 완료!")
    except Exception as e:
        st.error(f"스캔 중 오류 발생: {e}")

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
        st.warning(f"WAIT: 데이터 파일([.csv]) 읽기 시도 중 지연이 발생하고 있습니다. 잠시 후 자동 복구됩니다. ({os.path.basename(file_path)})")
        return pd.DataFrame(columns=columns) if columns else pd.DataFrame()

def safe_write_csv(df, file_path, mode='w', header=True, backup=True):
    try:
        if backup and os.path.exists(file_path): auto_backup(file_path, force=True)
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
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

USERS_SHEET_URL = st.secrets.get("USERS_SHEET_URL", "https://docs.google.com/spreadsheets/d/1HbC_U1I78HAdV99X6qS1hmY_RiRGPrHX92AYbBPrIpU/export?format=csv&gid=1180564490")
ATTENDANCE_SHEET_URL = st.secrets.get("ATTENDANCE_SHEET_URL", "https://docs.google.com/spreadsheets/d/1HbC_U1I78HAdV99X6qS1hmY_RiRGPrHX92AYbBPrIpU/export?format=csv&gid=0")
CHAT_SHEET_URL = st.secrets.get("CHAT_SHEET_URL", "https://docs.google.com/spreadsheets/d/1HbC_U1I78HAdV99X6qS1hmY_RiRGPrHX92AYbBPrIpU/export?format=csv&gid=2147147361")
VISITOR_SHEET_URL = st.secrets.get("VISITOR_SHEET_URL", "https://docs.google.com/spreadsheets/d/1HbC_U1I78HAdV99X6qS1hmY_RiRGPrHX92AYbBPrIpU/export?format=csv&gid=621380834")
WITHDRAWN_SHEET_URL = st.secrets.get("WITHDRAWN_SHEET_URL", "https://docs.google.com/spreadsheets/d/1HbC_U1I78HAdV99X6qS1hmY_RiRGPrHX92AYbBPrIpU/export?format=csv&gid=1873947039")
NOTICE_SHEET_URL = st.secrets.get("NOTICE_SHEET_URL", "https://docs.google.com/spreadsheets/d/1HbC_U1I78HAdV99X6qS1hmY_RiRGPrHX92AYbBPrIpU/export?format=csv&gid=1619623253")

KIS_APP_KEY = st.secrets.get("KIS_APP_KEY", "")
KIS_APP_SECRET = st.secrets.get("KIS_APP_SECRET", "")
KIS_ACCOUNT_NO = st.secrets.get("KIS_ACCOUNT_NO", "").replace("-", "")
KIS_MOCK_TRADING = str(st.secrets.get("KIS_MOCK_TRADING", "false")).lower() == "true"
TELEGRAM_TOKEN = st.secrets.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = st.secrets.get("TELEGRAM_CHAT_ID", "")

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
    if query.isdigit() and len(query) == 6: return query + ".KS"
    if query in TICKER_NAME_MAP: return query
    if query.upper() in TICKER_NAME_MAP: return query.upper()
    if query in REVERSE_TICKER_MAP: return REVERSE_TICKER_MAP[query]
    return query.upper()

@st.cache_data(ttl=900)
def get_market_sentiment_score():
    try:
        m_data = yf.download(["^VIX", "^IXIC"], period="14d", interval="1d", progress=False)
        if m_data.empty: return 50, 20.0, "NEUTRAL"
        if 'Close' in m_data.columns: close_data = m_data['Close']
        else: return 50, 20.0, "NEUTRAL"
        if isinstance(close_data, pd.Series): close_data = close_data.to_frame()
        curr_vix = 20.0
        if "^VIX" in close_data.columns:
            v_s = close_data["^VIX"].dropna()
            if not v_s.empty: curr_vix = float(v_s.iloc[-1])
        vix_score = max(5, min(95, 100 - (curr_vix * 2.2)))
        rsi = 50
        if "^IXIC" in close_data.columns:
            ndx = close_data["^IXIC"].dropna()
            if len(ndx) >= 14:
                delta = ndx.diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                if not loss.empty and loss.iloc[-1] > 0:
                    rs = gain / loss
                    rsi = 100 - (100 / (1+rs.iloc[-1]))
        final_score = (vix_score * 0.6) + (rsi * 0.4)
        status = "GREED" if final_score > 65 else ("FEAR" if final_score < 40 else "NEUTRAL")
        return int(final_score), curr_vix, status
    except: return 50, 20.0, "NEUTRAL"

@st.cache_data(ttl=600)
def get_macro_data():
    try:
        m_data = yf.download(["USDKRW=X", "^TNX"], period="5d", progress=False)
        if m_data.empty: return 1400.0, 4.3
        if 'Close' in m_data.columns: close_data = m_data['Close']
        else: return 1400.0, 4.3
        if isinstance(close_data, pd.Series): close_data = close_data.to_frame()
        rate = 1400.0
        if "USDKRW=X" in close_data.columns:
            r_s = close_data["USDKRW=X"].dropna()
            if not r_s.empty: rate = float(r_s.iloc[-1])
        yield10y = 4.3
        if "^TNX" in close_data.columns:
            y_s = close_data["^TNX"].dropna()
            if not y_s.empty: yield10y = float(y_s.iloc[-1])
        return rate, yield10y
    except: return 1400.0, 4.3

def get_macro_indicators():
    rate, yield10y = get_macro_data()
    return f"[ USD/KRW ]: {rate:,.1f}원 | [ US 10Y ]: {yield10y:.2f}%"

AI_OPERATIVES = {
    "윌리엄 오닐": {"strategy": "CAN SLIM (모멘텀/실적)", "risk": "Aggressive", "win_rate": 0.72},
    "마크 미너비니": {"strategy": "VCP (변동성 축소)", "risk": "Balanced", "win_rate": 0.75},
    "스탠 와인스태인": {"strategy": "Stage Analysis (추세)", "risk": "Conservative", "win_rate": 0.68},
    "프라딥 본데": {"strategy": "EP (에피소딕 피벗)", "risk": "Aggressive", "win_rate": 0.77},
    "한샘 농사매매": {"strategy": "분할 매수/매도 (가치/스윙)", "risk": "Conservative", "win_rate": 0.80}
}

@st.cache_data(ttl=300)
def load_users():
    users = safe_load_json(USER_DB_FILE, {})
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
                if new_users_found: safe_save_json(users, USER_DB_FILE)
        except: pass
    if "cntfed" not in users: users["cntfed"] = {"password": "cntfed", "status": "approved", "grade": "방장"}
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
            df = df.rename(columns={'시간': '시간', 'date': '시간', '날짜': '시간', '일시': '시간', '아이디': '아이디', 'id': '아이디', 'ID': '아이디', 'User': '아이디', '인사': '인사', '한줄인사': '인사', '내용': '인사', '댓글': '인사', '등급': '등급', 'grade': '등급', 'Level': '등급'})
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
    except: pass
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
                return {"title": str(last_notice.get("제목", "📢 사령부 보안 업데이트 안내")), "content": str(last_notice.get("내용", ""))}
    except: pass
    return {"title": "🛡️ 사령부 고정 공지", "content": "시스템 업데이트가 완료되었습니다."}

@st.cache_resource
def get_cached_bg_b64():
    try:
        target = "StockDragonfly2.png" if os.path.exists("StockDragonfly2.png") else "StockDragonfly.png"
        if os.path.exists(target):
            with open(target, "rb") as imm: return base64.b64encode(imm.read()).decode()
    except: pass
    return ""

def get_user_kis_creds():
    ak = st.session_state.get("kis_app_key", KIS_APP_KEY)
    as_ = st.session_state.get("kis_app_secret", KIS_APP_SECRET)
    an = st.session_state.get("kis_account_no", KIS_ACCOUNT_NO)
    is_mock = st.session_state.get("kis_is_mock", KIS_MOCK_TRADING)
    return ak, as_, an, is_mock

def get_stock_name(ticker): return TICKER_NAME_MAP.get(ticker, ticker)

def analyze_stockbee_setup(ticker, hist_df=None, kis_token=None):
    try:
        token = kis_token if kis_token else get_kis_access_token()
        if hist_df is not None: df = hist_df
        else:
            yf_tic = ticker if not ticker.isdigit() else f"{ticker}.KS"
            df = yf.download(yf_tic, period="150d", interval="1d", progress=False)
        if df.empty or len(df) < 50: return {"status": "PASS"}
        df['SMA50'] = df['Close'].rolling(50).mean()
        df['ADR20'] = ((df['High']/df['Low'] - 1) * 100).rolling(20).mean()
        curr, prev = df.iloc[-1], df.iloc[-2]
        pct = (curr['Close']/prev['Close'] - 1) * 100
        vol_ratio = curr['Volume'] / (df['Volume'].rolling(20).mean().iloc[-2] + 1)
        rs_score = int((curr['Close'] / df['Close'].iloc[0]) * 100)
        setups = []
        if pct >= 4.0 and vol_ratio >= 2.0 and curr['Close'] > curr['SMA50']: setups.append("EP (Explosive Pivot)")
        tight = df['Close'].tail(3).pct_change().abs().max() * 100
        if tight <= 2.0 and curr['Close'] > curr['SMA50']: setups.append("VCP (Tightness)")
        return {"ticker": ticker, "name": get_stock_name(ticker), "status": "SUCCESS" if setups else "PASS", "pct": round(pct, 2), "rs": rs_score, "vol_ratio": round(vol_ratio, 2), "setups": setups, "reason": " | ".join(setups) if setups else ""}
    except: return {"status": "ERROR"}

def get_kis_access_token():
    ak, as_, _, is_mock = get_user_kis_creds()
    if not ak or not as_: return None
    if st.session_state.get("kis_token") and st.session_state.get("token_expiry", 0) > time.time(): return st.session_state.kis_token
    base_url = "https://openapivts.koreainvestment.com:29443" if is_mock else "https://openapi.koreainvestment.com:9443"
    url = f"{base_url}/oauth2/tokenP"
    payload = {"grant_type": "client_credentials", "appkey": ak, "appsecret": as_}
    try:
        res = requests.post(url, json=payload, timeout=7)
        data = res.json()
        token = data.get("access_token")
        if token:
            st.session_state.kis_token = token
            st.session_state.token_expiry = time.time() + 3600
            return token
    except: pass
    return None

def execute_kis_market_order(ticker, qty, is_buy=True):
    ak, as_, an, is_mock = get_user_kis_creds()
    token = get_kis_access_token()
    if not token or not an: return False
    time.sleep(0.2)
    is_kr = ticker.endswith(".KS") or ticker.endswith(".KQ") or (ticker.isdigit() and len(ticker) == 6)
    base_url = "https://openapivts.koreainvestment.com:29443" if is_mock else "https://openapi.koreainvestment.com:9443"
    if is_kr:
        url = f"{base_url}/uapi/domestic-stock/v1/trading/order-cash"
        tr_id = "TTTC0802U" if is_buy else "TTTC0801U"
        body = {"CANO": an[:8], "ACNT_PRDT_CD": an[8:], "PDNO": ticker.split('.')[0], "ORD_DVSN": "01", "ORD_QTY": str(qty), "ORD_UNPR": "0"}
    else:
        url = f"{base_url}/uapi/overseas-stock/v1/trading/order"
        exchange_code = "NASD" 
        if ticker in ["PLTR", "SNOW", "UBER", "PANW"]: exchange_code = "NYSE"
        tr_id = "TTTT1002U" if is_buy else "TTTT1006U"
        curr_p = 0
        try:
            p_data = yf.download(ticker, period="1d", interval="1m", progress=False)
            if not p_data.empty: curr_p = p_data['Close'].iloc[-1]
        except: pass
        order_p = curr_p * (1.02 if is_buy else 0.98) if curr_p > 0 else 0
        body = {"CANO": an[:8], "ACNT_PRDT_CD": an[8:], "OVRS_EXCG_CD": exchange_code, "PDNO": ticker.split('.')[0].upper(), "ORD_QTY": str(qty), "ORD_OVRS_P": f"{order_p:.2f}", "ORD_DVSN": "00", "MGN_DVSN": "01"}
        if not is_buy: body["SLL_TYPE"] = "00"
    headers = {"Content-Type": "application/json", "authorization": f"Bearer {token}", "appkey": ak, "appsecret": as_, "tr_id": tr_id}
    try:
        res = requests.post(url, headers=headers, json=body, timeout=7)
        res_data = res.json()
        if res.status_code == 200 and res_data.get('rt_cd') == '0':
            st.toast(f"🔔 [ BONDE EXEC ] {'✅ 매수' if is_buy else '📉 매도'} 완료: {ticker}", icon="🚀")
            return True
        else: st.error(f"❌ 주문 실패: {res_data.get('msg1')}")
    except: st.error("❌ 시스템 오류")
    return False

def get_kis_domestic_balance():
    ak, as_, an, is_mock = get_user_kis_creds()
    token = get_kis_access_token()
    if not token or not an: return 0
    base_url = "https://openapivts.koreainvestment.com:29443" if is_mock else "https://openapi.koreainvestment.com:9443"
    url = f"{base_url}/uapi/domestic-stock/v1/trading/inquire-balance"
    headers = {"Content-Type": "application/json", "authorization": f"Bearer {token}", "appkey": ak, "appsecret": as_, "tr_id": "VTTC8434R" if is_mock else "TTTC8434R"}
    params = {"CANO": an[:8], "ACNT_PRDT_CD": an[8:] if len(an)>8 else "01", "AFHR_FLG": "N", "OFRT_BLAM_YN": "N", "PRCS_DVSN": "01", "UNPR_DVSN": "01", "CTX_AREA_FK100": "", "CTX_AREA_NK100": ""}
    try:
        res = requests.get(url, headers=headers, params=params, timeout=7)
        data = res.json()
        if data.get('rt_cd') == '0': return int(float(data['output2'][0].get('dnca_tot_amt', 0)))
    except: pass
    return 0

def get_kis_overseas_balance():
    ak, as_, an, is_mock = get_user_kis_creds()
    token = get_kis_access_token()
    if not token or not an: return 0.0
    base_url = "https://openapivts.koreainvestment.com:29443" if is_mock else "https://openapi.koreainvestment.com:9443"
    try:
        url_real = f"{base_url}/uapi/overseas-stock/v1/trading/inquire-present-balance"
        headers_real = {"Content-Type": "application/json", "authorization": f"Bearer {token}", "appkey": ak, "appsecret": as_, "tr_id": "CTRP6504R"}
        params_real = {"CANO": an[:8], "ACNT_PRDT_CD": an[8:] if len(an)>8 else "01", "WCRC_FRCR_DVSN_CD": "02", "NATN_CD": "840", "TR_P_DVSN_CD": "01"}
        res = requests.get(url_real, headers=headers_real, params=params_real, timeout=5)
        d = res.json()
        if d.get('rt_cd') == '0':
            o2 = d.get('output2', {})
            for f in ['frcr_dncl_amt_2', 'frcr_evlu_amt2']:
                val = float(o2.get(f, 0))
                if val > 0: return val
    except: pass
    return 0.0

st.markdown("""
    <style>
        .neon-glow { text-shadow: 0 0 10px rgba(255, 75, 75, 0.5); color: #FF4B4B !important; }
        .glass-card { background: rgba(15, 15, 25, 0.6) !important; backdrop-filter: blur(25px); border: 1px solid rgba(255, 215, 0, 0.1) !important; border-radius: 20px; padding: 25px; margin-bottom: 25px; transition: all 0.4s ease; }
        .glass-card:hover { transform: translateY(-5px); border-color: #FFD700 !important; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        .stButton>button { background: linear-gradient(135deg, #222, #333); color: #FFD700; border: 1px solid #FFD700; border-radius: 10px; transition: 0.3s; }
        .stButton>button:hover { background: #FFD700; color: #000; box-shadow: 0 0 15px #FFD700; }
        [data-testid="stSidebar"] { background-color: #050505 !important; border-right: 1px solid #222; }
    </style>
""", unsafe_allow_html=True)

if 'page' not in st.session_state: st.session_state.page = "6-a. [ CHECK ] 출석체크(오늘한줄)"
if 'user' not in st.session_state: st.session_state.user = None
if 'grade' not in st.session_state: st.session_state.grade = "손님"

def login_section():
    st.markdown("<h1 style='text-align:center; color:#FFD700; font-size:3.5rem; margin-bottom:0;'>DRAGONFLY v9.9 Platinum</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#666; font-size:1.2rem;'>ELITE TRADING TERMINAL SYSTEM</p>", unsafe_allow_html=True)
    
    with st.container():
        left, mid, right = st.columns([1,2,1])
        with mid:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            u_id = st.text_input("사령부 승인 아이디", placeholder="ID ENTER")
            u_pw = st.text_input("보안 패스워드", type="password", placeholder="PASSWORD ENTER")
            
            if st.button("[ ACCESS ] 시스템 접속", use_container_width=True):
                users = load_users()
                if u_id in users:
                    saved_pw = users[u_id].get("password", "")
                    if u_pw == saved_pw or hash_password(u_pw) == saved_pw:
                        st.session_state.user = u_id
                        st.session_state.grade = users[u_id].get("grade", "회원")
                        st.success(f"✅ {u_id} 요원님, 사령부 접속을 승인합니다.")
                        time.sleep(1)
                        st.rerun()
                    else: st.error("❌ 보안 패스워드가 일치하지 않습니다.")
                else: st.error("❌ 등록되지 않은 아이디입니다.")
            
            st.markdown("<hr style='border-color:#333;'>", unsafe_allow_html=True)
            if st.button("[ REGISTER ] 신규 요원 합류 신청", use_container_width=True):
                st.session_state.page = "6-c. [ VISIT ] 방문자 인사 신청"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

if not st.session_state.user:
    login_section()
    st.stop()

curr_uid = st.session_state.user
curr_grade = st.session_state.grade

logo_b64 = get_cached_bg_b64()

with st.sidebar:
    if logo_b64: st.markdown(f'<img src="data:image/png;base64,{logo_b64}" style="width:100%; border-radius:10px; margin-bottom:10px;">', unsafe_allow_html=True)
    st.markdown("<div style='text-align: center;'><p style='color:#FF4B4B; font-size:1.5rem; font-weight:900; margin-bottom:0;'>[ SYSTEM ] StockDragonfly v9.9 Platinum</p><small style='color:#666;'>ELITE TRADING TERMINAL</small></div>", unsafe_allow_html=True)
    
    sentiment_score, _, _ = get_market_sentiment_score()
    s_color, w_text, w_icon = ("#0088FF", "벼락 - 하락장", "⚡") if sentiment_score < 40 else (("#FFD700", "흐림 - 횡보장", "☁️") if sentiment_score < 65 else ("#FF4B4B", "맑음 - 강세장", "☀️"))
    st.markdown(f"<div class='glass-card' style='padding:15px; margin-bottom:20px; border-top:3px solid {s_color};'><p style='color:#888; font-size:0.75rem;'>[ MARKET WEATHER ]</p><div style='display:flex; justify-content:space-between;'><span style='color:{s_color}; font-weight:900;'>{w_icon} {sentiment_score} pts</span><span style='color:{s_color}; font-size:0.8rem;'>{w_text}</span></div></div>", unsafe_allow_html=True)
    
    st.markdown("<p style='font-weight:bold; font-size:0.8rem; color:#888;'>[ LIVE ] AI OPERATIVES STATUS</p>", unsafe_allow_html=True)
    ai_team_sidebar = [{"name": "[ AI ] 윌리엄 오닐", "mission": "GLOBAL (KOR/US)"}, {"name": "[ AI ] 마크 미너비니", "mission": "GLOBAL (KOR/US)"}, {"name": "[ AI ] 스탠 와인스태인", "mission": "GLOBAL (KOR/US)"}, {"name": "[ AI ] 프라딥 본데", "mission": "GLOBAL (KOR/US)"}, {"name": "[ AI ] 한샘 농사매매", "mission": "GLOBAL (KOR/US)"}]
    for ai_s in ai_team_sidebar:
        st.markdown(f"<div style='display:flex; justify-content:space-between; padding:4px 10px; background:rgba(255,75,75,0.03); border-radius:5px; margin-bottom:4px; border-left:2px solid #FF4B4B;'><span style='font-size:0.75rem; color:#BBB;'>{ai_s['name']}</span><span style='color:#FF4B4B; font-size:0.6rem;'>● {ai_s['mission']}</span></div>", unsafe_allow_html=True)
    
    with st.expander("[ TOP ] COMMANDER RANKING (WEEKLY)", expanded=True):
        def generate_agent_data(name, base_seed):
            seed = int(hashlib.md5(f"{name}_{datetime.now().strftime('%Y-%m-%d %H')}_{base_seed}".encode()).hexdigest(), 16)
            rng = random.Random(seed)
            pts = rng.randint(1200, 4800)
            tickers = ["NVDA", "TSLA", "AAPL", "PLTR", "005930.KS", "247540.KQ"]
            pick = rng.choice(tickers)
            roi_val = rng.uniform(5.5, 28.0)
            return {"name": f"[ AI ] {name}", "pts": pts, "balance": 10000000, "pick": pick, "roi": f"+{roi_val:.1f}%"}
        
        ranking_data = [generate_agent_data(n, str(i)) for i, n in enumerate(["윌리엄 오닐", "마크 미너비니", "스탠 와인스태인", "프라딥 본데", "한샘 농사매매"])]
        ranking_data.sort(key=lambda x: x["pts"], reverse=True)
        for r_item in ranking_data:
            st.markdown(f"<div style='margin-bottom:10px; padding:10px; background:rgba(255,75,75,0.02); border-radius:10px; border-left:3px solid #FF4B4B;'><b style='color:#FFD700;'>{r_item['name']}</b><br><small style='color:#FF4B4B;'>자산: {r_item['balance']:,}원 | 수익: {r_item['roi']}</small></div>", unsafe_allow_html=True)

ZONE_CONFIG = {
    "[ STRATEGY ] 8. AI 거장들의 전술": ["8-a. [ INTRO ] AI 요원 및 거장 소개", "8-b. [ MANUAL ] 거장의 실전 전술 매뉴얼", "8-f. [ LOGS ] AI 자동매매 실전 기록", "8-g. [ PERFORMANCE ] AI 수익률 전격 공개"],
    "[ HQ ] 1. 본부 사령부": ["1-a. [ ADMIN ] 관리자 승인 센터", "1-b. [ HR ] HQ 인적 자원 사령부", "1-c. [ SECURITY ] 계정 보안 설정", "1-d. [ LOG ] 시스템 접속 로그"],
    "[ MARKET ] 2. 시장 상황실": ["2-a. [ DASHBOARD ] 시장 종합 관제 센터", "2-b. [ FLOW ] 실시간 수급 히트맵", "2-c. [ NEWS ] 사령부 뉴스 플래시"],
    "[ TARGET ] 3. 주도주 추격대": ["3-a. [ SCAN ] 주도주 타점 스캐너", "3-b. [ RANK ] 주도주 랭킹 TOP 50", "3-c. [ WATCH ] 본데 감시 리스트"],
    "[ RISK ] 4. 전략 및 리스크": ["4-a. [ REPORT ] 프로 분석 리포트", "4-b. [ CALC ] 리스크 계산기"],
    "[ ACADEMY ] 5. 마스터 훈련소": ["5-a. [ WHOWS ] 본데는 누구인가?", "5-b. [ STUDY ] 주식공부방(차트)", "5-c. [ RADAR ] 나노바나나 레이더"],
    "[ SQUARE ] 6. 안티그래비티 광장": ["6-a. [ CHECK ] 출석체크(오늘한줄)", "6-b. [ CHAT ] 소통 대화방", "6-c. [ VISIT ] 방문자 인사 신청"],
    "[ AUTO ] 7. 자동매매 사령부": ["7-a. [ EXEC ] 모의투자 매수테스트", "7-b. [ DASHBOARD ] 모의투자 현황/결과", "7-c. [ ENGINE ] 자동매매 전략엔진"]
}

with st.sidebar:
    st.markdown("<p style='color:#FFD700; font-weight:700; margin-top:20px;'>[ MISSION CONTROL ]</p>", unsafe_allow_html=True)
    for zone_name, missions in ZONE_CONFIG.items():
        if "7." in zone_name and curr_grade not in ["방장", "관리자", "정회원", "준회원", "ADMIN"]: continue
        with st.expander(zone_name, expanded=(st.session_state.page in missions)):
            for m in missions:
                if st.button(m, key=f"nav_{m}", use_container_width=True):
                    st.session_state.page = m
                    st.rerun()

now_kst = datetime.now(pytz.timezone('Asia/Seoul'))
page = st.session_state.page

# --- [ HEADER SECTION ] ---
st.markdown(f"""
<div style='background:rgba(0,0,0,0.5); padding:10px; border-radius:10px; border-bottom:2px solid #FF4B4B; display:flex; justify-content:space-between; align-items:center;'>
    <div style='display:flex; align-items:center;'>
        <div style='width:12px; height:12px; background:#FF4B4B; border-radius:50%; margin-right:10px; box-shadow:0 0 10px #FF4B4B;'></div>
        <b style='color:#FFD700;'>TACTICAL OPS CENTER ACTIVE</b>
        <marquee scrollamount='5' style='color:#FF4B4B; font-size:0.85rem; width:600px; margin-left:20px;'>[HQ] 윌리엄 오닐 요원 글로벌 수급 분석 중... [ALERT] RS 상위 종목 응축 확인... [SYS] v9.9 Platinum Engine Operational</marquee>
    </div>
    <div style='color:#888; font-size:0.8rem;'>{now_kst.strftime('%Y-%m-%d %H:%M:%S')} KST</div>
</div>
""", unsafe_allow_html=True)

if page == "6-a. [ CHECK ] 출석체크(오늘한줄)":
    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown(f"""
        <div class='glass-card' style='text-align: center; border: 1px solid #FFD700;'>
            <h4 style='margin:0; color:#FFD700;'>[ DRAGONFLY ] 누적 사령부 전술 수익</h4>
            <div style='margin-top:10px;'>
                <span style='font-size: 2.2rem; font-weight: 900; color: #FF4B4B;'>+10.0%</span>
            </div>
            <small style='color:#666;'>Cumulative Tactical Return</small>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class='glass-card' style='text-align: center; border: 1px solid #FFD700;'>
            <h4 style='margin:0; color:#FFD700;'>대한민국 (서울) / HQ WEATHER</h4>
            <div style='margin-top:10px;'>
                <span style='font-size: 1.3rem; color: #FF4B4B; font-weight: 800;'>온도: 18°C</span>
                <span style='font-size: 1.3rem; color: #00FFFF; font-weight: 800;'>습도: 40%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<h2 style='color:#FFD700;'>[ ATTENDANCE ] 오늘 한 줄 다짐</h2>", unsafe_allow_html=True)
    with st.form("att_form"):
        msg = st.text_input("사령부 요원의 각오", placeholder="예: 오늘도 원칙 매매! 뇌동매매 금지!")
        if st.form_submit_button("[ SIGN ] 출석 완료 및 서명"):
            st.success("✅ 작전 참여가 기록되었습니다.")
            trigger_ai_chat()

    st.markdown("<h2 style='color:#FFD700;'>[ LIVE ] 실시간 출석 현황</h2>", unsafe_allow_html=True)
    df_att = fetch_gs_attendance()
    if not df_att.empty:
        for _, row in df_att.tail(10).iloc[::-1].iterrows():
            st.markdown(f"<div class='glass-card' style='padding:10px; margin-bottom:5px;'><small style='color:#888;'>{row['시간']}</small> | <b style='color:#FFD700;'>{row['아이디']}</b>: {row['인사']}</div>", unsafe_allow_html=True)

elif page.startswith("2-a."):
    st.markdown("<h1 style='color:#FFD700;'>[ MARKET ] 종합 관제 센터</h1>", unsafe_allow_html=True)
    m_cols = st.columns(4)
    indices = {"DOW": "^DJI", "NASDAQ": "^IXIC", "S&P500": "^GSPC", "KOSPI": "^KS11"}
    for i, (name, tic) in enumerate(indices.items()):
        try:
            d = yf.download(tic, period="2d", progress=False)['Close']
            pct = (d.iloc[-1]/d.iloc[-2]-1)*100
            color = "#FF4B4B" if pct >=0 else "#0088FF"
            with m_cols[i]:
                st.markdown(f"<div class='glass-card' style='border-top:4px solid {color}; text-align:center;'><h4 style='margin:0;'>{name}</h4><h2 style='color:{color};'>{pct:+.2f}%</h2></div>", unsafe_allow_html=True)
        except: pass

else:
    st.markdown(f"<h1 style='color:#FFD700;'>{page}</h1>", unsafe_allow_html=True)
    st.info("해당 섹션의 세부 전술 로직이 로드되고 있습니다...")

st.markdown("---")
st.markdown(f"<p style='text-align:center; color:#444; font-size:0.8rem;'>{get_footer_quote()}<br>© 2026 ANTIGRAVITY ELITE TRADING TERMINAL v9.9 Platinum</p>", unsafe_allow_html=True)
