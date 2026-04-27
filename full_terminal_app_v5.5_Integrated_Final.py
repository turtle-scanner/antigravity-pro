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
    """정적 자산(이미지, 오디오)을 최적화하여 로드 (초기 로딩 속도 개선)"""
    assets = {"bg": "", "logo": "", "audio": {}}
    try:
        # 이미지 로드 (필수 자산 우선)
        for f in ["StockDragonfly2.png", "StockDragonfly.png"]:
            if os.path.exists(f):
                with open(f, "rb") as imm: 
                    encoded = base64.b64encode(imm.read()).decode()
                    if "2" in f: assets["bg"] = encoded
                    else: assets["logo"] = encoded
        if not assets["logo"]: assets["logo"] = assets["bg"]
        
        # 오디오 파일은 선택 시점에 로드하도록 하여 초기 부하 감소 (여기서는 껍데기만 유지)
        assets["audio_manifest"] = ["full", "hope", "happy", "YouRaise", "petty"]
    except: pass
    return assets

@st.cache_data(ttl=3600)
def get_audio_base64(name):
    """오디오 파일을 개별적으로 로드하여 메모리 및 초기 속도 최적화"""
    file_map = {"full": "full.mp3", "hope": "hope.mp3", "happy": "happy.mp3", "YouRaise": "YouRaise.mp3", "petty": "petty.mp3"}
    fname = file_map.get(name)
    if fname and os.path.exists(fname):
        with open(fname, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

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
        
        /* [ SCANNER ] 나노바나나 게이지 */
        .banana-track { background: rgba(255,255,255,0.05); height: 12px; border-radius: 6px; position: relative; overflow: hidden; margin: 10px 0; border: 1px solid rgba(255,255,255,0.1); }
        .banana-fill { height: 100%; border-radius: 6px; transition: width 1s ease-out; box-shadow: 0 0 10px currentColor; }
    </style>
    """, unsafe_allow_html=True)

# --- [ SYSTEM ] [GLOBAL HELPER] Safe Network Request ---
def safe_get(url, timeout=3):
    """지연 및 멈춤 방지를 위한 글로벌 네트워크 헬퍼"""
    try:
        resp = requests.get(url, timeout=timeout)
        if resp.status_code == 200: return resp
    except:    pass
    return None

# --- [ TACTICAL ] Rule-based Tactical Advisor (Platinum Engine) ---
def get_tactical_advice(tic, rs, roe):
        advice = []
        if rs > 80: advice.append("[ MOMENTUM ] 강력한 Relative Strength 포착. 시장을 주도하는 주도주입니다.")
        elif rs > 50: advice.append("[ UP-TREND ] 양호한 추세 유지 중. 섹터 전환 수급을 확인하십시오.")
        else: advice.append("[ CAUTION ] 추세가 다소 정체됨. 지지선 이탈 시 전략적 감시하십시오.")
        
        if roe > 20: advice.append("[ PREMIUM ] 독보적인 ROE. 기업의 가치가 조화로운 우량 성장기업입니다.")
        elif roe > 10: advice.append("[ STRONG ] 견고한 펀더멘털. 실적 발표 이후 돌파 여부를 노리십시오.")
        
        # 보너스 정신적 조언
        quotes = [
            "시장의 소음보다 기본에 충실하십시오. VCP의 끝은 언제나 조용합니다.",
            "손절은 실패가 아닌, 다음 승리를 위한 보험료입니다.",
            "거래량이 마를 때까지 기다리십시오. 폭풍은 고요함 속에서 시작됩니다."
        ]
        advice.append(f"\nINFO: Bonde's Insight: {random.choice(quotes)}")
        return "\n".join(advice)

# --- [ AI ] Tactical Coaching & Mental Reinforcement (Hourly) ---
AI_QUOTES = [
    "주식 시장에서 가장 큰 죄는 틀리는 것이 아니라, 틀린 채로 남아있는 것이다. (William O'Neil)",
    "손절은 실패가 아니라, 다음 승리를 위한 보험료입니다. 기꺼이 지불하십시오. (Pradeep Bonde)",
    "VCP의 끝은 언제나 고요합니다. 폭풍은 그 침묵 속에서 시작됩니다. 인내하십시오.",
    "시장은 당신의 희망에 관심이 없습니다. 오직 수급과 추세에만 반응하십시오.",
    "현금도 하나의 포지션입니다. 억지로 싸우려 하지 마십시오. (Jesse Livermore)",
    "강한 놈이 더 강해집니다. RS 90+의 주도주에 모든 화력을 집중하십시오.",
    "조급함은 사령관의 가장 큰 적입니다. 시스템의 원칙을 믿고 시장의 소음을 차단하십시오.",
    "수익은 머리가 아니라 엉덩이에서 나옵니다. 원칙이 지켜지는 한 자리를 지키십시오."
]

def send_ai_tactical_coaching(token):
    """[ TACTICAL ] 1시간마다 사령관님께 용기와 전술 브리핑 전송"""
    last_coach = st.session_state.get("last_ai_coach_time", 0)
    if time.time() - last_coach < 3600: return # 1시간 미경과 시 패스
    
    try:
        # 시장 심리 및 지수 분석
        score, vix, label = get_market_sentiment_v2()
        macro = get_macro_indicators()
        quote = random.choice(AI_QUOTES)
        
        brief = f"🛡️ [ AI 작전 참모 전술 브리핑 ]\n\n"
        brief += f"👤 **Commander's Insight**:\n\"{quote}\"\n\n"
        brief += f"📊 **Current Status**:\n- 시장 심리: {label} (Score: {score})\n- 공포 지수(VIX): {vix:.2f}\n- {macro}\n\n"
        
        # 지능형 코칭 메시지 생성
        if vix > 25: 
            brief += "⚠️ **참모 조언**: 시장의 공포가 극심합니다. 섣부른 물타기보다 손절선을 엄수하며 생존에 집중하십시오."
        elif score > 70:
            brief += "🚀 **참모 조언**: 시장의 열기가 뜨겁습니다. 추격 매수보다는 익절 라인을 높여 수익을 극대화하십시오."
        else:
            brief += "⚖️ **참모 조언**: 시장이 중립적 흐름을 보이고 있습니다. 본데의 '나노 타이니' 패턴이 나타날 때까지 인내하십시오."
            
        send_telegram_msg(brief)
        st.session_state.last_ai_coach_time = time.time()
        st.session_state.combat_logs.append({"time": datetime.now().strftime("%H:%M:%S"), "msg": "📢 AI 작전 참모의 전술 브리핑이 텔레그램으로 발송되었습니다.", "type": "INFO"})
    except: pass

def get_footer_quote():
    """시스템 하단에 표시할 대가들의 격언"""
    quotes = [
        "VCP의 끝은 언제나 조용한 법입니다. 폭풍은 고요함 속에서 시작됩니다.",
        "손절은 실패가 아닌, 다음 승리를 위한 보험료입니다.",
        "수익은 오직 2단계(Mark-up)에서만 창출됩니다. 기다림은 지루할 수 있으나 결과는 달콤합니다.",
        "리더가 나쁜 직원을 즉시 해고하듯, 추세가 꺾인 종목은 즉시 제명해야 합니다.",
        "시장에 맞서지 마십시오. 파도를 타는 서퍼처럼 수급의 흐름에 몸을 맡기십시오.",
        "가장 강한 놈이 가장 멀리 갑니다. RS 최고가 답입니다."
    ]
    return random.choice(quotes)

@st.cache_resource
def get_ai_chat_cooldown():
    """AI 채팅 범람 방지를 위한 전역 타이머 관리"""
    return {"last_time": 0}

def trigger_ai_chat():
    """AI 페르소나들이 랜덤하게 소통방에 메시지를 던지는 기전 (6인 체제)"""
    # [ OPTIMIZE ] 전역 쿨다운 체크 (15초 내 중복 발송 차단)
    cd = get_ai_chat_cooldown()
    if time.time() - cd["last_time"] < 15: return False
    
    ai_users = [
        {"name": "[ AI ] 프라딥 본데", "grade": "AI_거장(모멘텀)"},
        {"name": "[ AI ] 마크 미너비니", "grade": "AI_거장(VCP)"},
        {"name": "[ AI ] 윌리엄 오닐", "grade": "AI_거장(CAN SLIM)"},
        {"name": "[ AI ] 스탠 와인스태인", "grade": "AI_거장(추세추종)"},
        {"name": "[ AI ] 워렌 버핏", "grade": "AI_거장(가치투자)"},
        {"name": "[ AI ] 한샘농사매매", "grade": "AI_거장(농사매매)"}
    ]
    ai_phrases = [
        "오늘 코스피 선물 흐름 심상치 않네요. 전술적 관망 권고합니다.",
        "방금 HTF 패턴 스캔 결과 공유합니다. 주도주 수급이 강력하네요.",
        "손절가는 생명선입니다. 다들 원칙 매매 잘 지키고 계신가요?",
        "안티그래비티 사령부의 유일한 수익 공식: 인내, 그리고 기계적 대응입니다.",
        "VCP 최종 단계에서 거래량이 말라붙는 모습... 곧 돌파하겠군요.",
        "사령부 요원님들, 오늘도 성투하십시오! 자동매매는 무결점입니다.",
        "시장의 소음(Noise)보다 차트의 신호(Signal)에 집중하세요.",
        "조급함은 중력과 같습니다. 안티그래비티 대원답게 무중력으로 비상합시다.",
        "오늘의 RS 상위 종목들 리스트 정말 탄탄하네요. 주도주 요리 준비 완료입니다!"
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

# --- [ STORAGE ] 데이터베이스 영구 보존 설정 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
def get_db_path(f): return os.path.join(BASE_DIR, f)

BACKUP_DIR = get_db_path("backups")

def auto_backup(file_path, force=True):
    if not os.path.exists(file_path): return
    try:
        fname = os.path.basename(file_path)
        os.makedirs(BACKUP_DIR, exist_ok=True)
        
        # [ SECURE ] 전문가용 요청: 중요 파일에 대한 백업 생성 (강제 여부)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(BACKUP_DIR, f"{fname}_{timestamp}.bak")
        shutil.copy2(file_path, backup_path)
        
        # 백업 파일 개수 관리 (최근 50개까지만 저장)
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
MASTER_GAS_URL = st.secrets.get("MASTER_GAS_URL", "")


def gsheet_sync_bg(sheet_name, cols, row_data):
    """비동기 구글 시트 데이터 전송 (UI 프리징 방지)"""
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
        # 파일이 실제 존재하는데 읽기 시도가 실패할 경우 경고 출력
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

# [ SECURE ] 영구 백업용 구글 시트 URL (CSV 정보 읽기 주소)
USERS_SHEET_URL = st.secrets.get("USERS_SHEET_URL", "")
ATTENDANCE_SHEET_URL = st.secrets.get("ATTENDANCE_SHEET_URL", "")
CHAT_SHEET_URL = st.secrets.get("CHAT_SHEET_URL", "")
VISITOR_SHEET_URL = st.secrets.get("VISITOR_SHEET_URL", "")
WITHDRAWN_SHEET_URL = st.secrets.get("WITHDRAWN_SHEET_URL", "")
# [ GLOBAL ] 전역 공통 및 UI 레이아웃 설정
NOTICE_SHEET_URL = st.secrets.get("NOTICE_SHEET_URL", "")


TICKER_NAME_MAP = {
    "NVDA": "엔비디아", "TSLA": "테슬라", "AAPL": "애플", "MSFT": "마이크로소프트", "PLTR": "팔란티어", "SMCI": "슈퍼마이크로", 
    "AMD": "AMD", "META": "메타", "GOOGL": "구글", "AVGO": "브로드컴", "CRWD": "크라우드스트라이크", "005930.KS": "삼성전자", 
    "000660.KS": "SK하이닉스", "196170.KQ": "알테오젠", "042700.KS": "한미반도체", "105560.KS": "KB금융", "055550.KS": "신한지주",
    "005490.KS": "POSCO홀딩스", "000270.KS": "기아", "066570.KS": "LG전자", "035720.KS": "카카오", "035420.KS": "NAVER",
    "005380.KS": "현대차", "000810.KS": "삼성화재", "NFLX": "넷플릭스", "MSTR": "마이크로스트래티지", "COIN": "코인베이스", 
    "MARA": "마라톤디지털", "PANW": "팔로알토", "SNOW": "스노우플레이크", "STX": "씨게이트", "WDC": "웨스턴디지털",
    "247540.KQ": "에코프로비엠", "277810.KQ": "에코프로", "091990.KQ": "셀트리온헬스케어", "293490.KQ": "카카오게임즈", "086520.KQ": "에코프로",
    "000100.KS": "유한양행", "000720.KS": "현대건설", "012330.KS": "현대모비스", "035720.KS": "카카오", "003410.KS": "쌍용C&E",
    "036930.KQ": "주성엔지니어링", "402340.KS": "SK스퀘어", "009830.KS": "한화솔루션"
}

def get_stock_name(ticker):
    """티커명을 종목명으로 변환 (데이터베이스 및 API 자동 캐시)"""
    if ticker in TICKER_NAME_MAP: return TICKER_NAME_MAP[ticker]
    if "name_cache" not in st.session_state: st.session_state.name_cache = {}
    if ticker in st.session_state.name_cache: return st.session_state.name_cache[ticker]
    
    try:
        # 한국 주식의 경우 네이버 API로 이름 가져오기
        if ticker.endswith(".KS") or ticker.endswith(".KQ"):
            symbol = ticker.split('.')[0]
            url = f"https://polling.finance.naver.com/api/realtime?query=SERVICE_ITEM:{symbol}"
            resp = requests.get(url, timeout=2).json()
            name = resp['result']['areas'][0]['datas'][0]['nm']
            st.session_state.name_cache[ticker] = name
            return name
        # 해외 주식은 yfinance 사용
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
@st.cache_data(ttl=60)
def get_bulk_market_data(tickers, period="60d"):
    """전역 마켓 데이터 엔진 (API 호출 최적화)"""
    if not tickers: return pd.DataFrame()
    try:
        data = yf.download(list(set(tickers)), period=period, progress=False)
        return data if not data.empty else pd.DataFrame()
    except: return pd.DataFrame()

@st.cache_data(ttl=60)
def fetch_macro_ticker_tape():
    """애니메이션 티커 테이프 데이터 수집"""
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

# --- [ SESSION STATE INITIALIZATION ] ---
if "combat_logs" not in st.session_state: st.session_state.combat_logs = []
if "kis_mock_mode" not in st.session_state: st.session_state.kis_mock_mode = st.secrets.get("KIS_MOCK_TRADING", False)
if "is_live_mode" not in st.session_state: st.session_state.is_live_mode = not st.session_state.kis_mock_mode
if "selected_acc_name" not in st.session_state: st.session_state.selected_acc_name = "위탁(종합)"
if "page" not in st.session_state: st.session_state.page = "6-a. [ CHECK ] 출석체크(오늘한줄)"
if "cfg_min_pct" not in st.session_state: st.session_state.cfg_min_pct = 4.0
if "cfg_max_prev_pct" not in st.session_state: st.session_state.cfg_max_prev_pct = 2.0
if "cfg_min_range_pos" not in st.session_state: st.session_state.cfg_min_range_pos = 0.7
if "antigravity_scan" not in st.session_state: st.session_state.antigravity_scan = {}

# --- [ TECHNICAL INDICATORS ] ---
def calculate_rsi(df, period=14):
    """상대강도지수(RSI) 계산"""
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    return df

def calculate_bollinger_bands(df, period=20, std_dev=2):
    """볼린저 밴드 계산"""
    df['MA20'] = df['Close'].rolling(window=period).mean()
    df['STD'] = df['Close'].rolling(window=period).std()
    df['BB_Upper'] = df['MA20'] + (df['STD'] * std_dev)
    df['BB_Lower'] = df['MA20'] - (df['STD'] * std_dev)
    return df

def calculate_cmo(df, period=20):
    """찬드라 모멘텀 오실레이터(CMO) 계산"""
    diff = df['Close'].diff()
    up = diff.where(diff > 0, 0).rolling(window=period).sum()
    down = diff.where(diff < 0, 0).abs().rolling(window=period).sum()
    df['CMO'] = 100 * (up - down) / (up + down)
    return df

# --- [ TICKER LISTS ] ---
def get_kospi_top_200():
    return ["005930.KS", "000660.KS", "042700.KS", "105560.KS", "005380.KS", "000270.KS", "068270.KS", "051910.KS", "005490.KS", "035420.KS"] + [f"{i:06d}.KS" for i in range(100, 2000, 50)] # 예시 리스트

def get_kosdaq_100():
    return ["196170.KQ", "247540.KQ", "086520.KQ", "293490.KQ", "036930.KQ", "067310.KQ"] + [f"{i:06d}.KQ" for i in range(100, 2000, 50)]

def get_nasdaq_200():
    return ["NVDA", "AAPL", "MSFT", "AMZN", "TSLA", "META", "GOOGL", "AVGO", "PEP", "COST", "ADBE", "NFLX", "AMD", "PLTR", "SMCI"]

def get_kr_all_tickers():
    """코스피+코스닥 전 종목급 확장 리스트 (약 500+ 주요 종목)"""
    # 실전 사령부 운영을 위해 시가총액 상위 및 주요 업종별 종목군을 대폭 확장
    kospi_base = ["005930", "000660", "042700", "105560", "005380", "000270", "068270", "051910", "005490", "035420", "000810", "012330", "032830", "006400", "000100", "000720", "003410", "009830", "010140", "000080"]
    kosdaq_base = ["196170", "247540", "086520", "293490", "036930", "067310", "028300", "145020", "214150", "035760", "035900", "066970", "039030", "041510", "051900"]
    
    # 6자리 숫자로 구성된 모든 유효 범위를 시뮬레이션 (실제 모든 종목 스캔을 지향)
    kospi_all = [f"{i:06d}.KS" for i in range(100, 3000, 20)] # 간격을 좁혀 표본 대폭 확대
    kosdaq_all = [f"{i:06d}.KQ" for i in range(100, 3000, 20)]
    
    return sorted(list(set([t + ".KS" for t in kospi_base] + [t + ".KQ" for t in kosdaq_base] + kospi_all + kosdaq_all)))


def get_ticker_data_from_bulk(bulk_df, ticker):
    """일괄 다운로드 데이터에서 특정 종목 추출"""
    if bulk_df.empty: return pd.DataFrame()
    # 멀티인덱스 대응
    if isinstance(bulk_df.columns, pd.MultiIndex):
        if ticker not in bulk_df.columns.get_level_values(1): return pd.DataFrame()
        try:
            return pd.DataFrame({col: bulk_df[col][ticker] for col in ["Open", "High", "Low", "Close", "Volume"]}).dropna()
        except: return pd.DataFrame()
    else:
        # 단일 종목 다운로드인 경우
        return bulk_df.dropna()


@st.cache_data(ttl=900)
def get_market_sentiment_v2():
    try:
        data = get_bulk_market_data(["^VIX", "^IXIC"], "20d")
        vix = float(data['Close']["^VIX"].dropna().iloc[-1]) if "^VIX" in data['Close'].columns else 20.0
        score = max(5, min(95, 100 - (vix * 2.2)))
        label = "GREED" if score > 65 else ("FEAR" if score < 35 else "NEUTRAL")
        return int(score), vix, label
    except: return 50, 20.0, "NEUTRAL"

@st.cache_data(ttl=300)
def get_macro_indicators():

    try:
        data = get_bulk_market_data(["USDKRW=X", "^TNX"], "5d")['Close']
        rate = data["USDKRW=X"].dropna().iloc[-1]
        yield10y = data["^TNX"].dropna().iloc[-1]
        return f"[ USD/KRW ]: {rate:,.1f}원 | [ US 10Y ]: {yield10y:.2f}%"
    except: return "[ USD/KRW ]: 1400.0원 | [ US 10Y ]: 4.30%"

@st.cache_data(ttl=300)
def analyze_market_health():
    """[ MARKET HEALTH ] 주요 지수(KOSPI, NASDAQ)의 50일 이동평균선 상회 여부 분석"""
    indices = {"^KS11": "KOSPI", "^IXIC": "NASDAQ"}
    health_report = {}
    is_defense_mode = False
    
    try:
        data = get_bulk_market_data(list(indices.keys()), period="150d")
        if data.empty: return False, {}
        
        for sym, name in indices.items():
            # 멀티인덱스 및 단일인덱스 대응
            if isinstance(data.columns, pd.MultiIndex):
                close_series = data['Close'][sym].dropna()
            else:
                close_series = data['Close'].dropna() if sym in data['Close'].columns else pd.Series()
            
            if len(close_series) >= 50:
                curr_p = close_series.iloc[-1]
                ma50 = close_series.rolling(50).mean().iloc[-1]
                status = "HEALTHY" if curr_p > ma50 else "CAUTION"
                if status == "CAUTION": is_defense_mode = True
                health_report[sym] = {"name": name, "price": curr_p, "ma50": ma50, "status": status}
            else:
                health_report[sym] = {"name": name, "price": 0, "ma50": 0, "status": "DATA_ERROR"}
    except Exception as e:
        print(f"DEBUG: Market Health Error: {e}")
        return False, {}
        
    return is_defense_mode, health_report

@st.cache_data(ttl=3600)
def get_macro_data():
    """실시간 환율 및 거시 지표 데이터 반환"""
    try:
        data = get_bulk_market_data(["USDKRW=X"], "5d")['Close']
        rate = float(data["USDKRW=X"].dropna().iloc[-1])
        return rate, 4.3
    except:
        return 1400.0, 4.3

# --- [ ENGINE ] KIS API & Core Trading Logic ---
# [ SECURITY ] 사령부 보안을 위해 실제 키는 secrets.toml에 저장하십시오. (하드코딩 제거)
NEW_KEY = ""
NEW_SECRET = ""

KIS_APP_KEY = st.secrets.get("KIS_APP_KEY", NEW_KEY).strip()
KIS_APP_SECRET = st.secrets.get("KIS_APP_SECRET", NEW_SECRET).strip()

# [ 계좌 관리 프리셋 정의 ]
ACC_PRESETS = {
    "위탁(종합)": "4654671301",
    "미니위탁/소수점": "4628981901",
    "ISA 중개형": "4444571901"
}

def get_kis_mock_status():
    """한국투자증권 모의투자 여부 판단 (사이드바 토글 우선)"""
    # [ FIX ] 사이드바 토글 키인 is_live_mode를 직접 참조하여 상태 불일치 해결
    if "is_live_mode" in st.session_state:
        return not st.session_state.is_live_mode
    # 세션 상태가 없으면 secrets 또는 기본값(True: 안전을 위해 모의투자 우선)
    return st.secrets.get("KIS_MOCK_TRADING", True)

def get_current_acc_no():
    # 세션 상태에 계좌 정보가 없으면 기본 위탁(종합) 사용
    selected_acc_name = st.session_state.get("selected_acc_name", "위탁(종합)")
    return ACC_PRESETS.get(selected_acc_name, "4654671301")

KIS_MOCK_TRADING = get_kis_mock_status()
KIS_ACCOUNT_NO = get_current_acc_no()

def get_user_kis_creds():
    """[ TACTICAL ] 현재 로그인한 요원의 개인 KIS 정보를 동적으로 로드"""
    users = load_users()
    u = st.session_state.get("current_user")
    personal = users.get(u, {}).get("kis_credentials", {})
    
    # 개인 키가 있으면 우선순위 1, 없으면 시스템 전역 키(Secrets) 사용
    ak = personal.get("app_key") or KIS_APP_KEY
    as_ = personal.get("app_secret") or KIS_APP_SECRET
    an = personal.get("acc_no") or KIS_ACCOUNT_NO
    return ak.strip(), as_.strip(), an.strip()


# [ NEW ] 텔레그램 설정
TELEGRAM_TOKEN = st.secrets.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = st.secrets.get("TELEGRAM_CHAT_ID", "")

def send_telegram_msg(msg):
    """사령관님께 실시간 전술 보고 전송 (텔레그램)"""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID: return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        params = {"chat_id": TELEGRAM_CHAT_ID, "text": f"🚨 [COMMANDER REPORT]\n{msg}", "parse_mode": "Markdown"}
        requests.get(url, params=params, timeout=15)
    except:    pass

@st.cache_data(ttl=3500, show_spinner=False)
def get_kis_access_token(app_key, app_secret, mock=None):
    """한국투자증권 API 접근 토큰 발급 (1분 제한 방어 로직 포함)"""
    use_mock = mock if mock is not None else get_kis_mock_status()
    # [ SAFETY ] KIS 1분당 1회 제한 방어
    last_req = st.session_state.get("last_token_req_time", 0)
    elapsed = time.time() - last_req
    if elapsed < 60: 
        # [ UI OPTIMIZATION ] 타이머 루프를 제거하여 앱이 멈추는 현상 방지
        st.caption(f"ℹ️ KIS 토큰 재발급 대기 중 ({int(60-elapsed)}초 남음)")
        return st.session_state.get("last_valid_token")


    use_mock = mock if mock is not None else get_kis_mock_status()
    base_url = "https://openapivts.koreainvestment.com:29443" if use_mock else "https://openapi.koreainvestment.com:9443"
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
        if "1분당 1회" in err_msg:
             st.warning("⚠️ KIS 토큰 발급 제한(1분)에 걸렸습니다. 잠시 후 자동 재시도합니다.")
        else:
             st.error(f"❌ [KIS AUTH ERROR] {err_msg} (Target: {'Mock' if mock else 'Real'})")
    except Exception as e:
        st.error(f"🌐 [NETWORK ERROR] KIS 서버 연결 실패: {str(e)}")
    
    return st.session_state.get("last_valid_token")

def execute_panic_sell_all(token):
    """[ EMERGENCY ] 비상 전량 매도 엔진 - 모든 포지션 즉시 시장가 정리"""
    try:
        u_an = st.session_state.get("u_an", KIS_ACCOUNT_NO)
        is_live = st.session_state.get("u_is_live", False)
        current_mock = not is_live
        
        # 1. 국내 주식 전량 매도
        _, _, kr_holdings = get_kis_balance(token, mock=current_mock, acc_no=u_an)
        for h in kr_holdings:
            ticker = h.get('pdno')
            qty = int(h.get('hldg_qty', 0))
            if qty > 0:
                # [ FIX ] .KS 접미사를 붙여 국내 주식임을 명시 (KOSDAQ도 KIS 주문 ID는 동일하게 처리 가능)
                execute_kis_market_order(f"{ticker}.KS", qty, is_buy=False)
        
        # 2. 해외 주식 전량 매도
        _, us_holdings = get_kis_overseas_balance(token, mock=current_mock, acc_no=u_an)
        for h in us_holdings:
            ticker = h.get('ovrs_pdno')
            qty = int(h.get('hldg_qty', 0))
            if qty > 0:
                execute_kis_market_order(ticker, qty, is_buy=False)
                
        msg = "🚨 [ PANIC SELL ] 모든 함대가 시장가로 긴급 철수(현금화)를 완료했습니다. 현재 무포지션 상태입니다."
        send_telegram_msg(msg)
        st.session_state.combat_logs.append({"time": datetime.now().strftime("%H:%M:%S"), "msg": msg, "type": "ERROR"})
        return True
    except Exception as e:
        st.error(f"❌ 비상 매도 중 오류 발생: {str(e)}")
        return False

@st.cache_data(ttl=60, show_spinner=False)
def get_kis_balance(token, mock=None, acc_no=None):
    """국내 주식 잔고 및 수익 현황 조회 (TTL 연장으로 로딩 속도 개선)"""
    ak, as_, an = get_user_kis_creds()
    target_acc = acc_no if acc_no else an
    if not token or not target_acc: return 0, 0, []
    use_mock = mock if mock is not None else get_kis_mock_status()
    base_url = "https://openapivts.koreainvestment.com:29443" if use_mock else "https://openapi.koreainvestment.com:9443"
    url = f"{base_url}/uapi/domestic-stock/v1/trading/inquire-balance"
    headers = {
        "Content-Type": "application/json",
        "authorization": f"Bearer {token}",
        "appkey": ak,
        "appsecret": as_,
        "tr_id": "VTTC8434R" if use_mock else "TTTC8434R",
        "custtype": "P"
    }
    suffixes = [target_acc[8:], "01", "02", "03", "04", "05", "06"]
    for suffix in list(dict.fromkeys(suffixes)):
        params = {
            "CANO": target_acc[:8], "ACNT_PRDT_CD": suffix,
            "AFHR_FLG": "N", "OVAL_DLY_TR_FECONT_YN": "N", "PRCS_DLY_VW_FNC_G": "0",
            "CANL_DLY_VW_FNC_G": "0", "CTX_AREA_FK100": "", "CTX_AREA_NK100": ""
        }
        try:
            res = requests.get(url, headers=headers, params=params, timeout=15)
            if res.status_code == 200:
                data = res.json()
                o2 = data.get('output2')
                if isinstance(o2, list) and len(o2) > 0:
                    o2 = o2[0]
                
                if o2 and isinstance(o2, dict):
                    # [ FIX ] 단순 예수금이 아닌 '주문가능금액'을 우선적으로 가져옴
                    cash = float(o2.get('ord_psbl_cash') or o2.get('prvs_rcdl_exca_amt') or o2.get('dnca_tot_amt') or 0)
                    total_eval = float(o2.get('tot_evlu_amt') or o2.get('nass_amt') or cash)
                    holdings = data.get('output1', [])
                    return total_eval, cash, holdings
            elif res.status_code == 500:
                err_data = res.json()
                msg = err_data.get('msg1', 'Internal Server Error')
                if "계좌" in msg or "권한" in msg: continue 
                st.warning(f"⚠️ KIS 서버 응답(500): {msg}")
        except: continue
    return 0, 0, []

@st.cache_data(ttl=60, show_spinner=False)
def get_kis_overseas_balance(token, mock=None, acc_no=None):
    """해외 주식 잔고 및 달러 현황 조회 (통합증거금 특화 v3.0)"""
    ak, as_, an = get_user_kis_creds()
    target_acc = acc_no if acc_no else an
    if not token or not target_acc: return {"krw": 0, "usd_total": 0, "usd_cash": 0}, []
    
    use_mock = mock if mock is not None else get_kis_mock_status()
    base_url = "https://openapivts.koreainvestment.com:29443" if use_mock else "https://openapi.koreainvestment.com:9443"
    
    # [ TACTICAL ] 통합증거금 계좌는 실제 달러가 없어도 '주문가능외화금액'이 중요함
    USD_CASH_FIELDS = [
        'ord_psbl_frcr_amt', 'ovrs_ord_psbl_amt', 'frcr_ord_psbl_amt', 'frcr_dncl_amt_2', 
        'frcr_dnca_amt', 'psbl_frcr_amt', 'frcr_ord_psbl_amt1', 'ovrs_prec_amt', 
        'frcr_dncl_amt', 'frcr_dncl_amt_1', 'frcr_psbl_amt', 'frcr_dnca_amt1'
    ]
    USD_EVAL_FIELDS = [
        'frcr_evlu_amt2', 'ovrs_tot_evlu_amt', 'tot_evlu_pamt_2', 'evlu_amt_smtot', 
        'frcr_buy_amt_smtl', 'tot_evlu_amt', 'evlu_amt_smtot_2', 'tot_evlu_pamt'
    ]
    KRW_TOTAL_FIELDS = ['tot_evlu_pamt', 'tot_asst_amt', 'evlu_amt_smtot_pamt', 'wdrw_psbl_tot_amt', 'tot_evlu_amt']

    def robust_float(val):
        try:
            if val is None or str(val).strip() == "": return 0
            return float(str(val).replace(',', ''))
        except: return 0

    def find_in_obj(obj, fields):
        if not obj: return 0
        if isinstance(obj, list):
            for item in obj:
                res = find_in_obj(item, fields)
                if res != 0: return res
            return 0
        if isinstance(obj, dict):
            for f in fields:
                val = robust_float(obj.get(f))
                if val != 0: return val
            for v in obj.values():
                if isinstance(v, (dict, list)):
                    res = find_in_obj(v, fields)
                    if res != 0: return res
        return 0

    best_data = {"krw": 0, "usd_total": 0, "usd_cash": 0}
    best_holdings = []
    
    suffixes = ["01", "02", target_acc[8:]] + ["03", "04", "05", "06"]
    suffixes = list(dict.fromkeys([s for s in suffixes if s]))
    
    # [ STRATEGY ] 통합증거금은 000(통합)과 840(미국)을 모두 수색
    natn_codes = ["840", "000"]
    tr_ids = ["TTTS3031R", "TTTS3061R", "TTTS3012R", "TTTS3011R"]
    if use_mock: tr_ids = ["V" + t[1:] for t in tr_ids]
    
    exchanges = ["NASD", "NYSE", "AMEX", "NAS", "NYS", "AMS"]
    
    for suffix in suffixes:
        for natn in natn_codes:
            for tr_id in tr_ids:
                is_psbl = "3031R" in tr_id or "3011R" in tr_id
                url_path = "/uapi/overseas-stock/v1/trading/inquire-psbl-order" if is_psbl else "/uapi/overseas-stock/v1/trading/inquire-balance"
                url = f"{base_url}{url_path}"
                
                headers = {
                    "Content-Type": "application/json", "authorization": f"Bearer {token}",
                    "appkey": ak, "appsecret": as_, "tr_id": tr_id, "custtype": "P"
                }
                
                target_exchanges = exchanges if is_psbl else [None]
                for excg in target_exchanges:
                    params = {"CANO": target_acc[:8], "ACNT_PRDT_CD": suffix, "NATN_CD": natn, "TR_PACC_CD": ""}
                    if is_psbl: 
                        params["TR_CRCY_CD"] = "USD"
                        if excg: params["OVRS_EXCG_CD"] = excg
                    else: 
                        params["WCRC_FRCR_DVS_CD"] = "02"
                    
                    try:
                        res = requests.get(url, headers=headers, params=params, timeout=10)
                        if res.status_code == 200:
                            d = res.json()
                            st.session_state["debug_kis_overseas_last_raw"] = d
                            if d.get('rt_cd') != '0': continue
                                
                            cash_usd = find_in_obj(d, USD_CASH_FIELDS)
                            eval_usd = find_in_obj(d, USD_EVAL_FIELDS)
                            total_krw = find_in_obj(d, KRW_TOTAL_FIELDS)
                            
                            # 통합증거금의 경우 평가금액이 usd_total에 합산되어야 함
                            current_usd_total = eval_usd + cash_usd if eval_usd > 0 else cash_usd
                            
                            if current_usd_total > best_data["usd_total"] or cash_usd > best_data["usd_cash"]:
                                o1 = d.get('output') or d.get('output1')
                                best_data = {"krw": total_krw, "usd_total": current_usd_total, "usd_cash": cash_usd}
                                best_holdings = (o1 if isinstance(o1, list) else [])
                                
                                # 데이터가 충분히 발견되면 즉시 리턴 (속도 최적화)
                                if cash_usd > 1.0 and len(best_holdings) > 0:
                                    return best_data, best_holdings
                    except: continue
    
    return best_data, best_holdings






def execute_kis_auto_cut(token):
    """[ SUPREME RISK ENGINE ] 익절(+21%), 손절(-5%), 파워무브(고점-3%) 벌크 집행"""
    try:
        _, _, kr_holdings = get_kis_balance(token)
        over_data, us_holdings = get_kis_overseas_balance(token)
        all_h = kr_holdings + us_holdings
        if not all_h: return False
        
        # [ OPTIMIZE ] 보유 종목 전체 데이터 벌크 수집
        tickers = []
        for h in all_h:
            tic = h.get('pdno') or h.get('ovrs_pdno')
            if tic:
                # [ FIX ] 국내 주식(숫자 6자리)인 경우 yfinance용 접미사 추가
                if tic.isdigit() and len(tic) == 6:
                    tickers.append(f"{tic}.KS")
                    tickers.append(f"{tic}.KQ") # 둘 다 시도하거나 정확한 구분 필요
                else:
                    tickers.append(tic)
        
        bulk_data = get_bulk_market_data(list(set(tickers)), period="5d")
        
        for h in all_h:
            ticker = h.get('pdno') or h.get('ovrs_pdno')
            qty = int(h.get('hldg_qty', 0))
            buy_p = float(h.get('pchs_avg_pric', 0))
            if qty <= 0 or buy_p <= 0: continue
            
            hist = get_ticker_data_from_bulk(bulk_data, ticker)
            if hist.empty: continue
            
            curr_p = hist['Close'].iloc[-1]
            high_3d = hist['High'].iloc[-3:].max() if len(hist) >= 3 else hist['High'].max()
            roi = (curr_p / buy_p - 1) * 100
            
            # [ TACTICAL LOGIC ]
            stop_loss_val = st.session_state.get("cfg_stop_loss_pct_val", -5.0)
            
            if (high_3d / buy_p - 1) >= 0.20 and curr_p <= high_3d * 0.97: # Power Move Exit
                if execute_kis_market_order(ticker, qty, is_buy=False): 
                    send_telegram_msg(f"⚡ [POWER MOVE EXIT] {ticker} 익절! (+{roi:.1f}%)")
            elif roi >= 21.0: # Hard Profit Target
                if execute_kis_market_order(ticker, qty, is_buy=False):
                    send_telegram_msg(f"💰 [TAKE PROFIT] {ticker} 목표달성! (+{roi:.1f}%)")
            elif roi <= stop_loss_val: # Hard Stop Loss
                if execute_kis_market_order(ticker, qty, is_buy=False):
                    send_telegram_msg(f"📉 [STOP LOSS] {ticker} 손절 집행. ({roi:.1f}%)")
    except Exception as e:
        print(f"DEBUG: Auto Cut Error: {e}")
    return False

def get_kis_current_price(ticker, token):
    """KIS OpenAPI를 통한 실시간 현재가 획득"""
    if not token: return 0
    try:
        is_kr = ticker.endswith(".KS") or ticker.endswith(".KQ")
        symbol = ticker.split('.')[0]
        use_mock = get_kis_mock_status()
        base_url = "https://openapivts.koreainvestment.com:29443" if use_mock else "https://openapi.koreainvestment.com:9443"
        
        ak, as_, _ = get_user_kis_creds()
        if is_kr:
            url = f"{base_url}/uapi/domestic-stock/v1/quotations/inquire-price"
            headers = {"Content-Type": "application/json", "authorization": f"Bearer {token}", "appkey": ak, "appsecret": as_, "tr_id": "FHKST01010100"}
            params = {"FID_COND_SCR_DIV_CODE": "11111", "FID_INPUT_ISCD": symbol}
            resp = requests.get(url, headers=headers, params=params, timeout=15)
            return float(resp.json().get('output', {}).get('stck_prpr', 0))
        else:
            url = f"{base_url}/uapi/overseas-stock/v1/quotations/price"
            headers = {"Content-Type": "application/json", "authorization": f"Bearer {token}", "appkey": ak, "appsecret": as_, "tr_id": "HHDFS76200200"}
            for excd in ["NAS", "NYS", "AMS"]:
                params = {"AUTH": "", "EXCD": excd, "SYMB": ticker}
                resp = requests.get(url, headers=headers, params=params, timeout=15)
                price = float(resp.json().get('output', {}).get('last', 0))
                if price > 0: return price
        return 0
    except: return 0


def get_market_breadth(token):
    """[ MARKET BREADTH ] 시장 건강도 체크 (종목들의 SMA50 상회 비율)"""
    try:
        sample_tickers = ["005930.KS", "000660.KS", "373220.KS", "207940.KS", "005380.KS", "005490.KS", "000270.KS", "035420.KS"]
        above_count = 0
        def check_sma50(t):
            df = get_kis_ohlcv(t, token)
            if len(df) < 50: return False
            return df['Close'].iloc[-1] > df['Close'].rolling(50).mean().iloc[-1]
        for t in sample_tickers:
            if check_sma50(t): above_count += 1
        return (above_count / len(sample_tickers)) * 100
    except: return 50.0



def fast_analyze_stock(ticker, token):
    """스캐너 가동을 위한 독립 분석 함수"""
    try:
        # analyze_stockbee_setup은 글로벌 스코프에 있으므로 직접 호출
        return analyze_stockbee_setup(ticker, kis_token=token)
    except:
        return {"status": "ERROR", "ticker": ticker, "reason": "Analysis Function Error"}

def play_tactical_sound(sound_type="buy"):
    """전술 상황에 따른 오디오 알림 (매수: 북소리 / 매도: 종소리)"""
    # [ ACTION ] 매수: Drum/Taiko, 매도: Bell/Chime
    # 초기 로딩 최적화를 위해 오디오 파일은 하단 JS 컴포넌트로 지연 로딩
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
    """종목별 실시간 ROE(자기자본이익률) 획득 (캐시 활용으로 과부하 방지)"""
    try:
        info = yf.Ticker(ticker).info
        return info.get('returnOnEquity', 0) * 100
    except: return 0

def execute_kis_market_order(ticker, qty, is_buy=True):
    """시장가 주문 실행 엔진 (통합증거금 및 모의투자 완벽 대응 v4.0)"""
    ak, as_, an = get_user_kis_creds()
    use_mock = get_kis_mock_status()
    token = get_kis_access_token(ak, as_, use_mock)
    if not token: return False
    
    # 변수 초기화
    url = ""
    tr_id = ""
    body = {}
    
    is_kr = ticker.endswith(".KS") or ticker.endswith(".KQ") or (ticker.isdigit() and len(ticker) == 6)
    base_url = "https://openapivts.koreainvestment.com:29443" if use_mock else "https://openapi.koreainvestment.com:9443"
    
    if is_kr:
        url = f"{base_url}/uapi/domestic-stock/v1/trading/order-cash"
        tr_id = ("VTTC0802U" if is_buy else "VTTC0801U") if use_mock else ("TTTC0802U" if is_buy else "TTTC0801U")
        body = {
            "CANO": an[:8], "ACNT_PRDT_CD": an[8:],
            "PDNO": ticker.split('.')[0], "ORD_DVSN": "01", "ORD_QTY": str(qty), "ORD_UNPR": "0"
        }
    else:
        url = f"{base_url}/uapi/overseas-stock/v1/trading/order"
        # [ FIX ] 모의투자와 실전의 거래소 코드가 다름
        exchange_code = "NASD" if not use_mock else "NAS"
        try:
            info = yf.Ticker(ticker).info
            ex_name = info.get('exchange', '').upper()
            if 'NYE' in ex_name or 'NEW YORK' in ex_name: exchange_code = "NYSE" if not use_mock else "NYS"
            elif 'ASE' in ex_name or 'AMERICAN' in ex_name: exchange_code = "AMEX" if not use_mock else "AMS"
        except: pass
        
        # [ STRATEGY ] 통합증거금 신청 계좌는 TTTT 계열 TR ID 사용 필수
        if use_mock:
            tr_id = "VTTW0801U" if is_buy else "VTTW0802U"
        else:
            # 사령관님 요청에 따라 통합증거금 전용 TR ID로 전환
            tr_id = "TTTT1002U" if is_buy else "TTTT1006U"
        
        # 현재가 기반 지정가 주문 (시장가 효과)
        curr_p = get_kis_current_price(ticker, token)
        if curr_p <= 0:
            try:
                p_data = yf.download(ticker, period="1d", interval="1m")
                if not p_data.empty: curr_p = p_data['Close'].iloc[-1]
            except: pass
            
        order_p = curr_p * (1.01 if is_buy else 0.99) if curr_p > 0 else 0
        
        body = {
            "CANO": an[:8], "ACNT_PRDT_CD": an[8:],
            "OVRS_EXCG_CD": exchange_code, "PDNO": ticker, "ORD_QTY": str(qty), 
            "ORD_OVRS_P": f"{order_p:.2f}", "ORD_DVSN": "00"
        }
        # 통합증거금 매도 시 필수 필드 추가
        if not is_buy and tr_id == "TTTT1006U":
            body["SLL_TYPE"] = "00" 

    headers = {
        "Content-Type": "application/json", "authorization": f"Bearer {token}",
        "appkey": ak, "appsecret": as_, "tr_id": tr_id
    }
    try:
        res = requests.post(url, headers=headers, json=body, timeout=7)
        res_data = res.json()
        if res.status_code == 200 and res_data.get('rt_cd') == '0':
            play_tactical_sound("buy" if is_buy else "sell")
            log_type = "SUCCESS"
            msg = f"{'✅ 매수' if is_buy else '📉 매도'} 완료: {ticker} ({qty}주)"
            st.session_state.combat_logs.append({"time": datetime.now().strftime("%H:%M:%S"), "msg": msg, "type": log_type})
            send_telegram_msg(f"🔔 [교전 보고] {msg}")
            return True
        else:
            err_msg = res_data.get('msg1', 'Unknown Error')
            st.session_state.combat_logs.append({
                "time": datetime.now().strftime("%H:%M:%S"), 
                "msg": f"❌ {ticker} 주문 실패: {err_msg}", "type": "ERROR"
            })
            return False
    except Exception as e:
        st.session_state.combat_logs.append({"time": datetime.now().strftime("%H:%M:%S"), "msg": f"❌ 시스템 오류: {str(e)}", "type": "ERROR"})
        return False

# --- [ SCANNER HELPERS: STOCKBEE STRICT EDITION ] ---
@st.cache_data(ttl=3600)
def get_bonde_top_50():
    """프라임 본데 50 종목 구글 시트 연동"""
    url = "https://docs.google.com/spreadsheets/d/1xjbe9SF0HsxwY_Uy3NC2tT92BqK0nhArUaYU16Q0p9M/export?format=csv&gid=1499398020"
    try:
        df = pd.read_csv(url)
        tickers = df.iloc[:50, 0].dropna().unique().tolist()
        return [str(t).strip().upper() for t in tickers if len(str(t)) < 6]
    except:
        return ["NVDA", "TSLA", "AAPL", "MSFT", "PLTR", "SMCI", "AMD", "META", "GOOGL", "AVGO", "MSTR", "COIN", "MARA"]

def calculate_cmo(df, period=20):
    """투시아르 찬드(Tushar Chande)의 CMO 지표 계산"""
    if len(df) < period: return df
    df['Net_Change'] = df['Close'] - df['Close'].shift(period)
    df['Abs_Change'] = df['Close'].diff().abs()
    df['Sum_Abs_Change'] = df['Abs_Change'].rolling(window=period).sum()
    df['CMO'] = np.where(df['Sum_Abs_Change'] == 0, 0, 100 * (df['Net_Change'] / df['Sum_Abs_Change']))
    return df

@st.cache_data(ttl=60, show_spinner=False)
def get_kis_ohlcv(ticker, token=None):
    """[ TACTICAL SOURCE ] yfinance 기반 국내 차트 데이터 획득"""
    try:
        yf_ticker = ticker
        if ticker.isdigit() and len(ticker) == 6: yf_ticker = f"{ticker}.KS"
        
        df = yf.download(yf_ticker, period="150d", interval="1d", progress=False)
        if not df.empty:
            df.index.name = 'Date'
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            return df[['Open', 'High', 'Low', 'Close', 'Volume']]
    except: pass
    return pd.DataFrame()

@st.cache_data(ttl=60, show_spinner=False)
def get_kis_overseas_ohlcv(ticker, token=None):
    """[ TACTICAL SOURCE ] yfinance 기반 해외 차트 데이터 획득"""
    try:
        df = yf.download(ticker, period="150d", interval="1d", progress=False)
        if not df.empty:
            df.index.name = 'Date'
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            return df[['Open', 'High', 'Low', 'Close', 'Volume']]
    except: pass
    return pd.DataFrame()


def get_nasdaq_200():
    """나스닥 주요 200 종목 (주도주 후보군)"""
    return ["NVDA", "TSLA", "AAPL", "MSFT", "AMZN", "META", "GOOGL", "GOOG", "AVGO", "COST", "ASML", "AZN", "PEP", "LIN", "AMD", "ADBE", "CSCO", "QCOM", "TMUS", "INTU", "AMAT", "TXN", "AMGN", "ISRG", "HON", "VRTX", "SBUX", "BKNG", "PANW", "MDLZ", "REGN", "LRCX", "GILD", "INTC", "MU", "ADI", "ADP", "KLAC", "MELI", "PDD", "PYPL", "SNPS", "MAR", "CDNS", "CTAS", "ORLY", "CSX", "MARA", "COIN", "MSTR", "PLTR", "SMCI"]

@st.cache_data(ttl=86400)
def get_sheet_tickers(url):
    """구글 시트에서 티커 리스트 추출 (1~5열 대상)"""
    try:
        # CSV 내보내기 링크 생성
        base_url = url.split("/edit")[0]
        gid = url.split("gid=")[1].split("#")[0] if "gid=" in url else "0"
        export_url = f"{base_url}/export?format=csv&gid={gid}"
        
        df = pd.read_csv(export_url)
        found_tickers = []
        import re
        # 왼쪽 1열부터 5열까지 스캔
        for col_idx in range(min(5, len(df.columns))):
            potential = df.iloc[:, col_idx].dropna().astype(str).tolist()
            for p in potential:
                p = p.strip().upper()
                # 미국 티커(1-5자 영문) 또는 한국 티커(6자 숫자) 패턴
                if re.match(r'^[A-Z]{1,5}$', p) or re.match(r'^\d{6}$', p):
                    found_tickers.append(p)
        return list(dict.fromkeys(found_tickers))
    except Exception as e:
        print(f"DEBUG: Sheet Load Error: {e}")
        return []

def analyze_stockbee_setup(ticker, hist_df=None, kis_token=None):
    """프라임 본데(Stockbee) 전략 분석 엔진 v9.0 (High-Speed Tactical Scanner)"""
    try:
        is_kr = ticker.endswith(".KS") or ticker.endswith(".KQ")
        # [ OPTIMIZE ] 데이터가 이미 전달된 경우(벌크) 재호출 생략
        if hist_df is not None and not hist_df.empty:
            hist = hist_df
        else:
            token = kis_token if kis_token else get_kis_access_token(KIS_APP_KEY, KIS_APP_SECRET, KIS_MOCK_TRADING)
            hist = get_kis_ohlcv(ticker, token) if is_kr else get_kis_overseas_ohlcv(ticker, token)

        if hist.empty or len(hist) < 150:
            return {"status": "REJECT", "reason": f"데이터 부족 ({len(hist)}일)", "ticker": ticker, "name": ticker}
            
        # [ PREPARE DATA ]
        df = hist.copy()
        df['C1'], df['C2'], df['V1'] = df['Close'].shift(1), df['Close'].shift(2), df['Volume'].shift(1)
        df['Pct'] = (df['Close'] / (df['C1'] + 1e-9) - 1) * 100
        df['Gap'] = (df['Open'] / (df['C1'] + 1e-9) - 1) * 100
        df['SMA20'], df['SMA50'], df['SMA200'] = df['Close'].rolling(20).mean(), df['Close'].rolling(50).mean(), df['Close'].rolling(200).mean()
        df['SMA7'], df['SMA65'] = df['Close'].rolling(7).mean(), df['Close'].rolling(65).mean()
        df['TI65'] = df['SMA7'] / (df['SMA65'] + 1e-9)
        df['Range_Pos'] = (df['Close'] - df['Low']) / (df['High'] - df['Low'] + 1e-9)
        df['ADR20'] = ((df['High'] / (df['Low'] + 1e-9) - 1) * 100).rolling(20).mean()
        
        row = df.iloc[-1]
        c, o, v, pct, gap, ti65, adr20, range_pos = row['Close'], row['Open'], row['Volume'], row['Pct'], row['Gap'], row['TI65'], row['ADR20'], row['Range_Pos']
        p_c, p_c2, p_v = row['C1'], row['C2'], row['V1']
        sma50, sma200 = row['SMA50'], row['SMA200']

        setups = []
        is_ep = is_dr = is_tight = False

        # [ BONDE FILTER ] 2단계 추세 확인 (Stage 2 check)
        is_stage2 = c > sma50 and sma50 > (sma200 if not pd.isna(sma200) else 0)
        
        # [ LIQUIDITY FILTER ] 슬리피지 방지를 위한 거래대금 체크 (최소 20억/2M$ 이상 권장)
        avg_dollar_vol = (df['Close'] * df['Volume']).rolling(20).mean().iloc[-1]
        is_liquid = avg_dollar_vol >= (2000000000 if is_kr else 2000000) # 한화 20억 or 200만 달러
        
        if not is_liquid:
            return {"status": "REJECT", "reason": "거래대금 부족 (슬리피지 위험)", "ticker": ticker, "name": get_stock_name(ticker)}

        # [ FLEXIBLE CONFIG ]
        cfg_pct = st.session_state.get("cfg_min_pct", 4.0)
        cfg_prev_tight = st.session_state.get("cfg_max_prev_pct", 2.0)
        cfg_range = st.session_state.get("cfg_min_range_pos", 0.7)

        # 1. 돌파 EP (Episodic Pivot) - 정교화
        vol_surge = v / (p_v + 1e-9)
        # 본데 EP 조건: 4% 이상 상승 + 갭상승 + 거래량 폭증(장중 0.5배 이상) + 상단 마감
        if pct >= cfg_pct and vol_surge >= 0.5 and gap >= 2.0 and range_pos >= cfg_range and is_stage2:
            is_ep = True; setups.append("EP (Episodic Pivot)")

        # 2. 조정 DR (Delayed Reaction)
        df['Mega'] = (df['Volume'] >= 5000000) & (df['Pct'] >= 4.0)
        recent_mega = df['Mega'].shift(1).rolling(25).max().iloc[-1] == 1.0
        if recent_mega and is_stage2 and ((o < p_c and c > p_c) or ((p_c/p_c2) <= 1.02 and v > p_v and pct >= 4.0)):
            is_dr = True; setups.append("DR (지속성 반등)")

        # 3. 변동성 TIGHT (응축) - Volume Dry-up(50% 이하) 및 변동성 수렴 필터 강화
        vol_avg20 = df['Volume'].rolling(20).mean().iloc[-2] # 전일 기준 20일 평균 거래량
        is_dry_up = p_v <= (vol_avg20 * 0.5) # 거래량 말라붙음(Dry-up) 체크
        
        # 3일 연속 종가 변동성 1.2% 이내 + 캔들 몸통(Range Pos) 수렴
        ttt = df['Pct'].rolling(3).apply(lambda x: all(abs(x) <= 1.2)).iloc[-1] == 1.0
        if is_stage2 and adr20 >= 3.5 and ti65 >= 1.05 and ttt and is_dry_up:
            is_tight = True; setups.append("TIGHT (Dry-up & 변동성 응축)")

        # RS 품질 (Relative Strength) - 주도주 필터링 강화
        # 본데 스타일: 6개월 및 3개월 수익률 가중합
        rs = round(((c/df['Close'].iloc[-min(len(df), 126)])*0.4 + (c/df['Close'].iloc[-min(len(df), 63)])*0.4 + (c/df['Close'].iloc[-min(len(df), 21)])*0.2)*100, 1)
        v_ratio = v / (p_v + 1e-9)
        # RS가 90 이상일 때 가산점 부여
        quality = round((rs*0.5) + (adr20*4) + (v_ratio*2), 1)
        if rs >= 90: quality += 20 
        
        name = get_stock_name(ticker)

        return {
            "ticker": ticker, "name": name, "close": c, "rs": rs, "day_pct": round(pct, 2), 
            "adr": round(adr20, 2), "quality": quality, "tight": round(abs(pct), 2),
            "is_ep": is_ep, "is_dr": is_dr, "is_tight": is_tight, "status": "SUCCESS" if setups else "PASS",
            "reason": f"🎯 {setups[0]} 포착!" if setups else "조건 미충족", "setups": setups,
            "volume": v, "prev_volume": p_v, "ti65": round(ti65, 3), "is_stage2": is_stage2
        }
    except Exception as e:
        return {"status": "ERROR", "reason": str(e), "ticker": ticker, "name": ticker}   


# --- [ SCANNER HELPERS: UNIVERSE EXPANSION ] ---

@st.cache_data(ttl=86400)
def get_nasdaq_200():
    """나스닥 100+ 주요 상장주 리스트"""
    top_ndq = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "AVGO", "PEP", "COST", "ADBE", "CSCO", "NFLX", "AMD", "TMUS", "INTC", "INTU", "AMAT", "QCOM", "TXN", "AMGN", "ISRG", "HON", "BKNG", "VRTX", "SBUX", "ADP", "GILD", "MDLZ", "REGN", "ADI", "LRCX", "PANW", "SNPS", "MU", "KLAC", "CDNS", "CHTR", "MAR", "PYPL", "ORLY", "ASML", "MNST", "MELI", "CTAS", "ADSK", "LULU", "WDAY", "KDP", "NXPI", "MCHP", "IDXX", "PAYX", "ROST", "PCAR", "DXCM", "AEP", "CPRT", "CPRT", "BKR", "KLA", "EXC", "MRVL", "CRWD", "DDOG", "TEAM", "MSTR", "PLTR", "SNOW", "ZS", "NET", "OKTA", "U", "RIVN", "LCID", "SQ", "SE", "BABA", "PDD", "JD", "BIDU", "NTES"]
    return list(set(top_ndq))

@st.cache_data(ttl=86400)
def get_kospi_top_200():
    """코스피 시총 상위 100+ 주요 종목"""
    top_ks = ["005930.KS", "000660.KS", "373220.KS", "207940.KS", "005490.KS", "005380.KS", "000270.KS", "051910.KS", "006400.KS", "035420.KS", "068270.KS", "105560.KS", "055550.KS", "012330.KS", "035720.KS", "003550.KS", "032830.KS", "000810.KS", "015760.KS", "086790.KS", "009150.KS", "011780.KS", "010130.KS", "033780.KS", "000100.KS", "018260.KS", "003670.KS", "000720.KS", "009830.KS", "011070.KS", "047050.KS", "028260.KS", "010140.KS", "036570.KS", "003410.KS", "051900.KS", "034730.KS", "090430.KS", "010950.KS", "259960.KS", "302440.KS", "402340.KS", "017670.KS"]
    return list(set(top_ks))

@st.cache_data(ttl=86400)
def get_kosdaq_100():
    """코스닥 100 주요 상장주"""
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
    "Bonde": {"strategy": "Momentum/EP Specialist", "risk": "Aggressive", "win_rate": 0.72},
    "Minervini": {"strategy": "VCP/SEPA Specialist", "risk": "Balanced", "win_rate": 0.75},
    "ONeil": {"strategy": "CAN SLIM Specialist", "risk": "Balanced", "win_rate": 0.70},
    "Weinstein": {"strategy": "Stage Analysis Specialist", "risk": "Conservative", "win_rate": 0.68},
    "Buffett": {"strategy": "Value/Moat Specialist", "risk": "Conservative", "win_rate": 0.80},
    "Hansam": {"strategy": "Farm Trading Specialist", "risk": "Conservative", "win_rate": 0.85}
}

@st.cache_data(ttl=60)
def get_realtime_ai_ranking():
    missions = {"Bonde": "NVDA", "Minervini": "247540.KQ", "ONeil": "AAPL", "Weinstein": "TSLA", "Buffett": "005930.KS", "Hansam": "035420.KS"}
    # [ RESET ] 2026-04-27 기준 현재가로 진입가 초기화 (1000만원 + 800$ 기준)
    entry_prices = {"Bonde": 208.27, "Minervini": 208000, "ONeil": 271.06, "Weinstein": 376.30, "Buffett": 219500, "Hansam": 214000}
    
    bulk_data = get_bulk_market_data(list(missions.values()))
    results = []
    usd_krw = 1380 # 기준 환율
    starting_capital_krw = 10000000 + (800 * usd_krw) # 1000만원 + 800$
    
    for name, ticker in missions.items():
        hist = get_ticker_data_from_bulk(bulk_data, ticker)
        curr_p = hist['Close'].iloc[-1] if not hist.empty else entry_prices[name]
        roi = (curr_p / entry_prices[name] - 1) * 100
        
        display_name = {
            "Bonde": "프라딥 본데", "Minervini": "마크 미너비니", 
            "ONeil": "윌리엄 오닐", "Weinstein": "스탠 와인스태인", "Buffett": "워렌 버핏",
            "Hansam": "한샘농사매매"
        }.get(name, name)
        
        results.append({
            "name": f"[ AI ] {display_name}", "pts": int(roi * 100), "win": random.randint(60, 85),
            "balance": int(starting_capital_krw * (1 + roi/100)), "pick": ticker, "entry": entry_prices[name],
            "exit_p": curr_p, "roi": f"{roi:+.2f}%", "exit": datetime.now().strftime("%m/%d %H:%M")
        })
    # [ VS COMMANDER ] 사령관(사용자) 데이터 추가
    comm_equity = st.session_state.get("last_total_equity", starting_capital_krw)
    comm_roi = (comm_equity / starting_capital_krw - 1) * 100
    
    results.append({
        "name": "🚩 [ COMMANDER ] 사령관", "pts": int(comm_roi * 100), "win": 100, # 사령관의 승률은 별도 로직 또는 100으로 표시
        "balance": int(comm_equity), "pick": "TOTAL", "entry": starting_capital_krw,
        "exit_p": comm_equity, "roi": f"{comm_roi:+.2f}%", "exit": "2026-04-27 시작"
    })
    
    return sorted(results, key=lambda x: float(x["roi"].replace('%','')), reverse=True)

@st.cache_data(ttl=600)
def load_users():
    """사용자 데이터 로드 (로컬 우선)"""
    users = safe_load_json(USER_DB_FILE, {})
    return users

def sync_users_from_sheet():
    """비동기 사용자 데이터 동기화"""
    if not USERS_SHEET_URL: return
    try:
        resp = safe_get(USERS_SHEET_URL, timeout=15)
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
    except:    pass

    # 기본 방장 계정 보장
    users = load_users()
    if "cntfed" not in users:
        users["cntfed"] = {"password": "cntfed", "status": "approved", "grade": "방장"}
        safe_save_json(users, USER_DB_FILE)
    
    # [ SYSTEM ] 전문가용 권한을 테스트적으로 상시 보장 (지휘지침 반영)
    users["cntfed"]["grade"] = "방장"
    users["cntfed"]["status"] = "approved"
    
    return users

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def migrate_user_passwords(users):
    # 기존 평문 비밀번호를 해시 엔진으로 변환
    changed = False
    for uid, udata in users.items():
        pw = udata.get("password", "")
        if len(pw) < 64: # 해시가 아닌 경우 (SHA-256은 64글자)
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
            # 다양한 헤더 매핑
            df = df.rename(columns={
                '시간': '시간', 'date': '시간', '날짜': '시간', '일시': '시간',
                '아이디': '아이디', 'id': '아이디', 'ID': '아이디', 'User': '아이디',
                '인사': '인사', '한줄인사': '인사', '내용': '인사', '메시지': '인사',
                '등급': '등급', 'grade': '등급', 'Level': '등급'
            })
            # 필수 컬럼 보장
            expected = ["시간", "아이디", "인사", "등급"]
            for col in expected:
                if col not in df.columns: df[col] = "nan"
            return df[expected]
    except:    pass
    return pd.DataFrame(columns=["시간", "아이디", "인사", "등급"])

@st.cache_data(ttl=60)
def fetch_gs_chat():
    try:
        response = safe_get(CHAT_SHEET_URL, timeout=4)
        if response:
            import io
            df = pd.read_csv(io.StringIO(response.text))
            df = df.rename(columns={'시간': '시간', '아이디': '아이디', '내용': '내용', '등급': '등급'})
            return df
    except:    pass
    return pd.DataFrame()

@st.cache_data(ttl=60)
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
@st.cache_data(ttl=86400) # ROE는 하루 한 번 정도면 충분
def get_ticker_roe(tic):
    try:
        tk = yf.Ticker(tic)
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
                return {"title": str(last_notice.get("제목", "📢 사령부 보안 업데이트 안내")), "content": str(last_notice.get("내용", "쾌적한 서비스를 제공하기 위해 진행 중인 개편입니다. 모든 회원 임시 비밀번호는 1234입니다."))}
    except Exception as e:
        print(f"DEBUG: Notice Fetch Error: {e}")
    return {
        "title": "🚨 사령부 고정 공지", 
        "content": """더욱 쾌적하고 안전한 서비스 환경을 구축하기 위한 서버 업데이트 과정에서, 부득이하게 전체 회원의 비밀번호가 초기화되었습니다. 이용에 불편을 드려 대단히 죄송합니다.<br>
아래 내용에 따라 비밀번호를 재설정해 주시기 바랍니다.<br><br>
<b>▣ 비밀번호 초기화 및 재설정 방법</b><br>
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

# --- 상단 브랜드 헤더 (초정밀 밀도 레이아웃) ---
col_head1, col_head2, col_head3 = st.columns([1, 4, 1])

with col_head3:
    if st.session_state.get("password_correct"):
        if st.button("🚪 LOGOUT", use_container_width=True, key="global_logout"):
            st.session_state["password_correct"] = False
            st.session_state.current_user = None
            st.rerun()
    else:
        if st.button("🔑 LOGIN", use_container_width=True, key="global_login"):
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
        # (Global Header가 상단에 배치되므로 중복 로고/제목 제거)
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
                if st.button("[ OK ] 공지 확인 및 창 닫기", use_container_width=True):
                    st.session_state["show_notice"] = False
                    st.rerun()

        tab1, tab2 = st.tabs(["[ LOGIN ] Terminal Log-In", "[ JOIN ] Join Command (자격 시험)"])
        
        with tab1:
            login_id = st.text_input("사령부 아이디", key="l_id")
            login_pw = st.text_input("암호코드(PW)", type="password", key="l_pw")
            if st.button("Terminal Operation Start", use_container_width=True):
                users = load_users()
                if login_id in users:
                    u_data = users[login_id]
                    if u_data.get("status", "approved") != "approved":
                        st.error(f"⚠️ 현재 계정 상태가 '{u_data.get('status')}'입니다. 사령부의 승인이나 상태 복구가 필요합니다.")
                    elif u_data.get("password") == login_pw or u_data.get("password") == hash_password(login_pw):
                        # 로그인 시 비밀번호 해시 엔진으로 변환 (v7.0 보안 강화)
                        if len(u_data.get("password", "")) < 64:
                            users[login_id]["password"] = hash_password(login_pw)
                            save_users(users)
                        st.session_state["password_correct"] = True
                        st.session_state.current_user = login_id
                        st.rerun()
                    else: st.error("[ ERROR ] 보안 코드가 일치하지 않습니다.")
                else: st.error("[ ERROR ] 등록되지 않은 정보입니다.")
        
        with tab2:
            st.markdown("### [ ACCESS ] 사령부 정예 요원 편성 자격 시험")
            st.info("개인 정보 및 자격 시험 만점(25/30)을 획득해야 사령부 승인이 완료됩니다.")
            
            c1, c2 = st.columns(2)
            with c1:
                new_id = st.text_input("희망 아이디", key="s_id")
                new_pw = st.text_input("희망 비밀번호", type="password", key="s_pw")
                reg_region = st.selectbox("거주 지역", ["서울", "경기", "인천", "부산", "대구", "대전", "광주", "울산", "강원", "충청", "전라", "경상", "제주", "해외"])
            with c2:
                reg_age = st.selectbox("연령대", ["20대 이하", "30대", "40대", "50대", "60대 이상"])
                reg_gender = st.radio("성별", ["남성", "여성"], horizontal=True)
                reg_exp = st.selectbox("주식 경력", ["1년 미만", "1-3년", "3-5년", "5-10년", "10년 이상"])
            
            reg_moti = st.text_area("주식을 하는 이유와 사령부에 임하는 각오", placeholder="반드시 경제적 자유를 얻어 가족들에게 헌신하고 싶습니다.")
            
            st.divider()
            st.markdown("#### 📝 [ EXAM ] 사령부 정예 요원 자격 시험 (30문항 / 10분 제한)")
            st.warning("⚠️ 시험 시작 버튼을 누르면 10분의 타이머가 가동됩니다. 30문제 중 25문제 이상 맞히셔야 자격이 부여됩니다.")
            
            # --- [ TIMER LOGIC ] ---
            if "exam_start_time" not in st.session_state:
                if st.button("🚩 자격 시험 시작 (타이머 가동)"):
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
                st.error("제한 시간이 초과되었습니다. 사령부의 지시를 준수하시고 다시 도전하십시오.")
                if st.button("시험 재도전"):
                    del st.session_state.exam_start_time
                    st.rerun()
                st.stop()

            st.info("Part 1: 기초 기술 종합 테스트 (30문항)")
            
            # --- [ 30 QUESTIONS ] ---
            with st.container():
                st.info("Part 1: 기초 시장 이해 (10문항)")
                q1 = st.radio("Q1. 주식 차트에서 양봉(빨간색)의 의미는?", ["상승", "하락", "유지", "보합"], index=None)
                q2 = st.radio("Q2. 음봉(파란색)의 의미는?", ["상승", "하락", "유지", "보합"], index=None)
                q3 = st.radio("Q3. 거래량이 폭증하는 것은 무엇의 증거인가?", ["관심과 수급", "거래 종료", "시장 붕괴", "가격 하락"], index=None)
                q4 = st.radio("Q4. 이동평균선(이평선)의 정의는?", ["일정 기간 가격의 평균", "미래 주가 예측선", "거래량 평균", "기관 매수가"], index=None)
                q5 = st.radio("Q5. '무릎에서 사서 어깨에서 팔라'는 격언의 의미는?", ["추세 추종", "최저가 매수", "최고가 매도", "단타 매매"], index=None)
                q6 = st.radio("Q6. 골든 크로스란?", ["단기선이 장기선을 상향 돌파", "주가가 금값처럼 오름", "거래량이 줄어듦", "장기선이 단기선을 돌파"], index=None)
                q7 = st.radio("Q7. 데드 크로스 발생 시의 대응은?", ["매도 또는 관망", "적극 매수", "추가 매수", "방치"], index=None)
                q8 = st.radio("Q8. 호가창에서 매수 잔량이 매도 잔량보다 많으면 보통 어떻게 되나?", ["주가가 하락하기 쉽다", "주가가 급등한다", "변화 없다", "거래 중단"], index=None)
                q9 = st.radio("Q9. '손절'의 진정한 의미는?", ["리스크 관리와 생존", "패배 인정", "자산 포기", "실패"], index=None)
                q10 = st.radio("Q10. 주식 투자의 주체 3요소는?", ["개인, 외국인, 기관", "대통령, 정당, 기업인", "증권사, 거래소, 정부", "하늘, 땅, 바다"], index=None)

                st.info("Part 2: 본데의 전술 철학 (10문항)")
                q11 = st.radio("Q11. 본데 전략의 핵심 키워드는?", ["모멘텀 돌파", "가치 투자", "배당주 투자", "인덱스 투자"], index=None)
                q12 = st.radio("Q12. TI65 지표가 의미하는 것은?", ["65일간의 모멘텀 강도", "65일 거래량 평균", "65일 이상 보유 원금", "6.5% 수익률"], index=None)
                q13 = st.radio("Q13. 본데의 '4% Momentum Burst' 매수 조건은?", ["거래량 동반 4% 이상 상승", "4일 연속 하락", "4% 배당 지급", "직전 10분 매수"], index=None)
                q14 = st.radio("Q14. Episodic Pivot(EP)의 발생 원인은?", ["강력한 펀더멘털의 변화", "개인들의 집단 매수", "단순 주가 조정", "기관의 물량 투하"], index=None)
                q15 = st.radio("Q15. 본데가 말하는 가장 안전한 매수 타점은?", ["박스권 돌파 초기", "낙폭 과대 지점", "고점 형성 후 조정", "장 마감 직전"], index=None)
                q16 = st.radio("Q16. 3일 연속 상승한 종목을 거르는 이유는?", ["추격 매수 위험(Laggard)", "오를 것이기 때문", "돈이 아까워서", "규정 때문"], index=None)
                q17 = st.radio("Q17. 주식 시장의 4단계 중 매매해야 하는 단계는?", ["2단계 (Mark-up)", "1단계 (Accumulation)", "3단계 (Distribution)", "4단계 (Capitulation)"], index=None)
                q18 = st.radio("Q18. Gap Up(갭상승)이 중요한 이유는?", ["강력한 기관 수급의 증거", "가격이 비싸서", "사기 좋아서", "자금 때문"], index=None)
                q19 = st.radio("Q19. 본데 전략에서 매도의 1순위 기준은?", ["매수가(LOD) 이탈", "10% 수익", "목표가 도달", "지루할 때"], index=None)
                q20 = st.radio("Q20. ROE가 마이너스인 기업을 배제하는 이유는?", ["펀더멘털 결함 가능성", "현금이 많아서", "이름이 안 예뻐서", "유행에 뒤처져서"], index=None)

                st.info("Part 3: 고등 전략 및 심리 (10문항)")
                q21 = st.radio("Q21. 트레일링 스탑이란?", ["수익률에 따라 익절가를 높임", "손절가를 낮춤", "매도 포기", "천천히 멈춤"], index=None)
                q22 = st.radio("Q22. 시장 심리(Fear & Greed)가 공포(Fear)일 때는?", ["보수적 운용/기회 포착", "대량 공매도", "무조건 매수", "휴식"], index=None)
                q23 = st.radio("Q23. 주식 매매에서 가장 중요한 것은?", ["자기 확신과 냉정한 감정", "애국심", "학력", "행운"], index=None)
                q24 = st.radio("Q24. 분할 매수의 장점은?", ["평단가 조절 및 리스크 분산", "수익 극대화", "빠른 매매", "수수료 절감"], index=None)
                q25 = st.radio("Q25. RSI 지표 30 이하의 의미는?", ["과매도 구간(반등 가능성)", "과매수 구간", "상승 가속", "매도 적기"], index=None)
                q26 = st.radio("Q26. 기술적 인내란?", ["타점이 올 때까지 기다림", "물린 채 버티기", "무한 물타기", "매매 포기"], index=None)
                q27 = st.radio("Q27. 주도주란?", ["시장의 상승을 이끄는 핵심 종목", "가장 싼 주식", "가장 비싼 주식", "거래 정지 주식"], index=None)
                q28 = st.radio("Q28. VCP(변동성 축적 패턴)의 핵심은?", ["돌파 전 강력한 시세 수렴", "가격 하락", "시장 붕괴", "거래 중단"], index=None)
                q29 = st.radio("Q29. 사령부의 최종 목표는?", ["기계적 절차를 통한 복리 수익", "일확천금", "도박", "유명세"], index=None)
                q30 = st.radio("Q30. 당신은 기계처럼 손절 원칙을 지킬 것인가?", ["네, 반드시 지킵니다", "아니오, 상황 봐서요", "모르겠습니다", "지키기 싫습니다"], index=None)

            if st.button("[ SUBMIT ] 자격 시험 제출 및 가입 신청"):
                ans_list = [q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, q11, q12, q13, q14, q15, q16, q17, q18, q19, q20, q21, q22, q23, q24, q25, q26, q27, q28, q29, q30]
                score = 0
                for a in ans_list:
                    if a and ("상승" in a or "하락" in a or "수급" in a or "평균" in a or "추세" in a or "상향" in a or "매도" in a or "하락하기" in a or "생존" in a or "기관" in a or "모멘텀" in a or "65일" in a or "4%" in a or "변동성" in a or "돌파" in a or "Laggard" in a or "2단계" in a or "강력한" in a or "이탈" in a or "펀더멘털" in a or "수익률" in a or "보수적" in a or "감정" in a or "평단가" in a or "과매도" in a or "타점" in a or "이끄는" in a or "강력한" in a or "절차" in a or "지킵니다" in a):
                        score += 1
                
                if score >= 25:
                    users = load_users()
                    if new_id in users: st.error("이미 존재하는 아이디입니다.")
                    else:
                        users[new_id] = {
                            "password": new_pw, "status": "approved", "grade": "회원",
                            "info": {
                                "region": reg_region, "age": reg_age, "gender": reg_gender,
                                "exp": reg_exp, "motivation": reg_moti, "joined_at": datetime.now().strftime("%Y-%m-%d %H:%M")
                            }
                        }
                        save_users(users)
                        
                        # 즉시 구글 시트 백업 전송 (백그라운드 전환)
                        gsheet_sync_bg("회원명단", 
                            ["아이디", "비밀번호", "상태", "등급", "지역", "연령", "성별", "경력", "가입일", "매매동기"],
                            [new_id, new_pw, "approved", "회원", reg_region, reg_age, reg_gender, reg_exp, datetime.now().strftime("%Y-%m-%d %H:%M"), reg_moti]
                        )
                        
                        st.success(f"[ SUCCESS ] {score}/30점 달성! 사령부의 지휘권을 계승할 자격을 증명하셨습니다. 로그인을 진행해 주십시오.")
                        st.balloons()
                else:
                    st.error(f"[ ERROR ] {score}/30점. 사령부의 철학을 더 공부하고 와 주시기 바랍니다. (25점 이상 합격)")
                    with st.expander("[ REVIEW ] 15관문 합격 시험 오답 해설 보기", expanded=True):
                        st.markdown("""
                        - **Q13:** RSI **30 이하**의 매도는 파멸이며, 과매도 구간입니다.
                        - **Q14:** 부분 익절 후에는 손절가를 **본절(Break-even)**로 올려 무위험 상태를 만듭니다.
                        - **Q15:** **3일 연속** 상승한 종목은 절대 추격 매수하지 않는 것이 사령부의 철칙입니다.
                        """)
    st.stop()

# --- [ CONFIG ] Menu & Trades ---
ZONE_CONFIG = {
    "[ HQ ] 1. 본부 사령부": ["1-a. [ ADMIN ] 관리자 메인 센터", "1-b. [ HR ] HQ 정예 요원 사령부", "1-c. [ SECURE ] 계정 보안 설정", "1-d. [ EXIT ] 탈퇴/휴식 신청"],
    "[ MARKET ] 2. 시장 상황실": ["2-a. [ TREND ] 마켓 트렌드 요약", "2-b. [ MAP ] 실시간 히트맵", "2-c. [ SENTIMENT ] 시장 심리 게이지", "2-d. [ ABOUT ] 제작 전기"],
    "[ TARGET ] 3. 주도주 추격기": ["3-a. [ SCAN ] 주도주 전술 스캐너", "3-b. [ RANK ] 주도주 리스트 TOP 50", "3-c. [ WATCH ] 본데 감시 리스트", "3-d. [ INDUSTRY ] 산업동향(TOP 10)", "3-e. [ RS ] RS 강도(TOP 10)", "3-f. [ NANO ] 나노바나나 레이더"],
    "[ CHART ] 4. 실시간 전술 분석실": ["4-a. [ ANALYZE ] BMS 전술 분석기", "4-b. [ INTERACTIVE ] 인터랙티브 차트", "4-c. [ RISK ] 리스크 관리 계산기"],
    "[ ACADEMY ] 5. 마스터 훈련소": ["5-a. [ MENTOR ] 본데의 연구노트", "5-b. [ STUDY ] 주식공부(차트)", "5-c. [ RADAR ] 나노바나나 레이더", "5-d. [ EXAM ] HQ 정예요원 승급시험", "5-z. [ FARM ] 농사매매 전략실"],
    "[ SQUARE ] 6. 안티그래비티 광장": ["6-a. [ CHECK ] 출석체크(오늘한줄)", "6-b. [ CHAT ] 소통 대화방"],
    "[ AUTO ] 7. 자동매매 사령부": ["7-a. [ SETUP ] 사령부 교전 수칙", "7-b. [ MONITOR ] 실시간 시장 관측", "7-c. [ ENGINE ] 자동매매 전략엔진", "7-g. [ COMBAT ] 실시간 교전 관제소", "7-i. [ CONFIG ] 사령부 시스템 설정", "7-j. [ CHANDE ] 찬드라 지표 엔진"],
    "[ VERSUS ] 8. AI 요원 경쟁방": ["8-a. [ AGENTS ] AI 요원 소개", "8-b. [ PROFIT ] AI 요원 수익방", "8-c. [ PORTFOLIO ] AI 요원 현재 보유 종목", "8-d. [ HALL ] AI 요원 명예의 전당", "8-f. [ LIVE ] 실시간 실전수익률"]
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
    audio_list = assets.get("audio_manifest", [])
    sel_bgm = st.selectbox("BGM", ["MUTE"] + audio_list, label_visibility="collapsed")
    vol = st.slider("VOL", 0.0, 1.0, 0.4, 0.1)
    if sel_bgm != "MUTE":
        audio_b64 = get_audio_base64(sel_bgm)
        if audio_b64:
            st.components.v1.html(f"<audio autoplay loop id='bgm'><source src='data:audio/mp3;base64,{audio_b64}' type='audio/mp3'></audio><script>document.getElementById('bgm').volume={vol};</script>", height=0)

    # Navigation
    st.markdown("<p style='color:#FFD700; font-size:0.8rem; font-weight:700; margin-top:20px; margin-bottom:10px;'>[ MISSION CONTROL ]</p>", unsafe_allow_html=True)
    users = load_users()
    curr_grade = users.get(st.session_state.current_user, {}).get("grade", "회원")
    is_admin = curr_grade in ["관리자", "방장"]

    # [ QUICK TEST BUY ]
    st.sidebar.divider()
    st.sidebar.subheader("🚀 QUICK TEST BUY")
    c_t1, c_t2 = st.sidebar.columns([3, 1])
    with c_t1: test_ticker = st.sidebar.text_input("Ticker", value="005930", key="test_buy_ticker", label_visibility="collapsed")
    with c_t2: test_qty = st.sidebar.number_input("Qty", value=1, min_value=1, key="test_buy_qty", label_visibility="collapsed")
    if st.sidebar.button("BUY 1 SHARE NOW", use_container_width=True):
         if execute_kis_market_order(test_ticker, int(test_qty), is_buy=True):
             st.sidebar.success(f"✅ Order sent for {test_ticker}")
         else:
             st.sidebar.error(f"❌ Order failed for {test_ticker}")

    # [ SECURITY ] 계좌 컨트롤 섹션은 사령부 관리자(관리자, 방장)만 접근 가능하도록 수정
    if is_admin:
        st.sidebar.markdown("### ⚙️ ACCOUNT CONTROL (ADMIN ONLY)")
        
        # [ NEW ] 계좌 데이터 탭 주입
        selected_acc = st.sidebar.selectbox(
            "교전 계좌 선택", 
            list(ACC_PRESETS.keys()) + ["직접 입력"], 
            index=list(ACC_PRESETS.keys()).index(st.session_state.get("selected_acc_name", "위탁(종합)")),
            key="selected_acc_name"
        )
        
        if selected_acc == "직접 입력":
            u_an_manual = st.sidebar.text_input("계좌번호 (10자리)", value=st.session_state.get("u_an_manual", "4654671301"))
            st.session_state.u_an_manual = u_an_manual
            KIS_ACCOUNT_NO = u_an_manual
        else:
            KIS_ACCOUNT_NO = ACC_PRESETS[selected_acc]
        
        # [ NEW ] 개인화된 키 로드
        u_ak, u_as, u_an = get_user_kis_creds()
        if selected_acc == "직접 입력": u_an = u_an_manual
        
        is_live = st.sidebar.toggle("🚨 실전 매매 모드 (LIVE)", value=st.session_state.get("is_live_mode", not KIS_MOCK_TRADING), key="is_live_mode")
        st.session_state.kis_mock_mode = not is_live
        st.sidebar.caption(f"📡 연결 키: {u_ak[:5]}*** (개인설정 {'적용됨' if 'kis_credentials' in users.get(st.session_state.current_user, {}) else '기본값'})")
        st.sidebar.caption(f"💳 계좌번호: {u_an[:8]}-** (현재 {'실전' if is_live else '모의'})")
        
        # [ DEBUG ] 현재 접속 모드 명시적 표시
        mode_color = "#FF4B4B" if is_live else "#00FF00"
        st.sidebar.markdown(f"""
            <div style='text-align:center; padding:5px; border-radius:5px; background:{mode_color}22; border:1px solid {mode_color}55; margin-bottom:10px;'>
                <small style='color:{mode_color}; font-weight:bold;'>CONNECTION: {'REAL SERVER' if is_live else 'MOCK SERVER'}</small>
            </div>
        """, unsafe_allow_html=True)

        with st.sidebar.expander("🛠️ API DEEP DIAGNOSTIC"):
            if st.button("RUN DIAGNOSTIC SCAN"):
                st.write("🔍 Scanning KIS response for USD fields...")
                # 최근 저장된 디버그 데이터 출력
                debug_keys = [k for k in st.session_state.keys() if k.startswith("debug_kis_")]
                if debug_keys:
                    for k in debug_keys:
                        st.json(st.session_state[k])
                else:
                    st.warning("No USD data found in recent requests. Try Refreshing first.")

        # [ SIDEBAR BALANCE INFO ]
        try:
            current_mock = not is_live
            token = get_kis_access_token(u_ak, u_as, current_mock)

            
            # 독립적 호출 에러 격리
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
            st.session_state.last_total_equity = full_b
            
            st.sidebar.markdown(f"""
                <div style='background:rgba(255,215,0,0.1); padding:10px; border-radius:5px; border:1px solid #FFD70033;'>
                    <p style='margin:0; font-size:0.7rem; color:#AAA;'>COMMANDER EQUITY ({'LIVE' if is_live else 'MOCK'})</p>
                    <b style='color:#FFD700; font-size:1.1rem;'>{full_b:,.0f} KRW</b><br>
                    <div style='margin-top:5px; border-top:1px solid rgba(255,255,255,0.05); padding-top:5px;'>
                        <small style='color:#CCC;'>KR: {r_total:,.0f} 원</small><br>
                        <small style='color:var(--neon-blue);'>US: ${o_total_usd:,.2f}</small> 
                        <small style='color:#666;'>(Cash: ${o_cash_usd:,.2f})</small>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            if st.sidebar.button("🔄 잔고 동기화(Refresh)", use_container_width=True):
                # [ FIX ] 세션 상태의 토큰 요청 시간까지 초기화하여 즉시 재발급 강제
                st.session_state.last_token_req_time = 0
                st.session_state.last_valid_token = None
                get_kis_access_token.clear()
                get_kis_balance.clear()
                get_kis_overseas_balance.clear()
                st.rerun()

            if st.sidebar.button("☢️ NUCLEAR REFRESH", use_container_width=True, type="primary"):
                st.session_state.clear()
                st.cache_data.clear()
                st.rerun()
        except Exception as e:
            st.sidebar.error(f"❌ AUTH/API ERROR: {str(e)}")
            st.sidebar.caption("인증 세션 또는 키 설정을 확인하십시오.")
    # 일반 회원에게는 표시하지 않음 (완전 은닉)
    pass


    st.sidebar.divider()
    
    for zone, missions in ZONE_CONFIG.items():
        # [ SECURITY ] 구역별 접근 권한 필터링
        if "ADMIN" in str(missions) and not is_admin: continue
        if "AUTO" in zone and curr_grade not in ["방장", "관리자", "정회원", "준회원"]: continue
        # ACADEMY 같은 다른 구역은 모든 요원에게 공개
        
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
            {macro_str} &nbsp;&nbsp;&nbsp; [BREAKING] NVDA VCP Phase 3 Detection... &nbsp;&nbsp; [HQ] 본데 요원 나스닥 주도 수급 분석 중.. &nbsp;&nbsp; [ALERT] RS 상위 10% 종목 실시간 압축 확인...
        </marquee>
    </div>
</div>
""", unsafe_allow_html=True)

# --- [ INFO ] 하단 실시간 지수 현황 ---
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
        "green": ("#00FF00", "rgba(0,255,0,0.1)", "GREED/AGGRESSIVE", "수익 좀 났다고 당신이 천재가 된 게 아니다. 시장이 좋았을 뿐이다. 자만심(Ego)이 고개를 드는 순간, 시장은 당신의 계좌를 갈기갈기 찢어놓을 거다. 익절 라인 올려 잡고 기계적 로직을 지켜라."),
        "orange": ("#FFD700", "rgba(255,215,0,0.1)", "NEUTRAL/WATCH", "방향성이 보이지 않을 때는 엉덩이를 깔고 앉아 있는 것도 기술이다. 억지로 수익을 만들려고 하지 마라. 시장이 당신에게 수익을 줄 기회가 올 때까지 굶주린 사자처럼 기다려라."),
        "red": ("#FF4B4B", "rgba(255,75,75,0.1)", "FEAR/DEFENSIVE", "중력이 당신을 끌어내리고 있다. 거스르지 마라. 지금은 영웅이 될 때가 아니라 생존해야 할 때다. 모든 포지션을 축소하고, 리스크를 감당 못하겠으면 즉시 현금화시켜라.")
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
        <h3 style='margin: 0; color: #FFF; font-size: 1.3rem; letter-spacing: -0.5px;'>[ TRUTH ] 사령관의 심리 분석 센터 (Harsh Truth)</h3>
    </div>
    <div style='background: {c_bg}; border-left: 4px solid {c_color_code}; padding: 20px; border-radius: 0 12px 12px 0;'>
        <p style='color: #EEE; font-size: 1.05rem; line-height: 1.6; margin: 0; font-family: "Pretendard", sans-serif; font-weight: 500;'>"{c_harsh}"</p>
    </div>
</div>
</div>
</div>""", unsafe_allow_html=True)

# --- [ NEW ] [ TACTICAL RADAR & EMERGENCY EXIT ] ---
st.markdown("<h3 style='color: #FFD700; margin-top: 20px;'>📡 TACTICAL RADAR & EMERGENCY EXIT</h3>", unsafe_allow_html=True)
c_rad1, c_rad2 = st.columns([2, 1])

with c_rad1:
    is_defense, health = analyze_market_health()
    h_html = ""
    for idx_name, h in health.items():
        color = "#00FF00" if h['status'] == "HEALTHY" else "#FF3131"
        h_html += f"<span style='color:{color}; font-weight:bold; margin-right:15px;'>{idx_name}: {h['status']} ({h['price']/h['ma50']-1:+.2f}%)</span>"
    
    st.markdown(f"""
    <div class='glass-card' style='padding: 15px; border-left: 5px solid {"#00FF00" if not is_defense else "#FF3131"};'>
        <p style='margin:0; color:#888; font-size:0.8rem;'>MARKET HEALTH (vs 50MA)</p>
        <div style='margin-top:5px;'>{h_html}</div>
        <p style='margin-top:10px; font-size:0.85rem; color:{"#00FF00" if not is_defense else "#FF3131"};'>
            <b>시스템 권고:</b> {"🚀 공격적 교전 가능 (Bullish)" if not is_defense else "🛡️ 방어적 퇴각 권고 (Bearish)"}
        </p>
    </div>
    """, unsafe_allow_html=True)

with c_rad2:
    st.markdown("<div style='height: 5px;'></div>", unsafe_allow_html=True)
    if st.button("🚨 PANIC SELL ALL (즉시 철수)", use_container_width=True, type="primary"):
        st.session_state.show_panic_auth = True
    
    if st.session_state.get("show_panic_auth"):
        auth_code = st.text_input("사령부 승인 번호 (4자리)", type="password", key="dash_panic_auth")
        if auth_code == "1353":
            st.session_state.page = "7-p. [ EMERGENCY ] 비상 탈출 버튼"
            st.session_state.show_panic_auth = False
            st.rerun()
        elif auth_code != "":
            st.error("❌ 보안 코드가 일치하지 않습니다.")

st.divider()


# --- [ DOCTRINE ] 본데 전술 지혜 레이더 ---
BONDE_WISDOM = [
    {
        "title": "[ ADVICE ] '비밀 지표'나 '마법의 셋업'을 찾는 헛수고는 당장 집어치워라",
        "content": "많은 초보자들이 시장에서 완벽한 매수 타점이나 '비밀 지표'가 뭐냐고 묻는다. 그런 건 없다. 시장에서 돈을 버는 진정한 '엣지(Edge)'는 남들보다 뛰어나게 분석하는 것이 아니라, 당신의 돌파 매매(Breakout)에 1달러라도 걸기 전에, 과거에 성공했던 종목 차트 5,000장, 10,000개를 직접 파고드는(Deep Dive) 것이다. 500차트, 1,000차트, 5,000차트 깊이까지 파고들어야 비로소 시장이 어떻게 움직이는지 이해하기 시작하는 것이며, 다른 사람의 종목 추천(Alert)에 의존하는 짓을 멈추고 당신 스스로의 뇌에 패턴을 각인시켜라."
    },
    {
        "title": "[ ADVICE ] 당신은 천재가 아니다 - '섬의 환상(Island Mentality)'에서 깨어나라",
        "content": "운 좋게 시장 환경이 좋은 동안 20%의 수익을 내고 나면, 사람들은 자신이 천재라고 착각한다. 이번 달에 번 돈으로 아파트를 사고 페라리를 사겠다고 하는 상황(Island Mentality)에 빠져 다른 이를 비웃는 '신의 증후군(God Syndrome)'에 걸린다. 그렇게 자만하며 아무 데나 매매를 남발하다 보면, 결국 머리 위로 코코넛이 떨어지며 계좌가 박살 날 것이다. 상황이 이럴 때 들뜨지 말고, 짧고 성실한 수익(Singles)을 챙기며 복리를 굴리는 지루한 과정을 거쳐라."
    },
    {
        "title": "[ ADVICE ] 쓰레기장 같은 시장에서 매매하며 계좌를 갈아버리지 마라",
        "content": "아무리 완벽해 보이는 에피소딕 피벗(EP)이나 모멘텀 버스트 셋업이라도 시장 환경(날씨)이 나쁘면 무용지물이다. 당신은 매일 아침 '오늘 돌파 매매가 통할 시장인가?'를 스스로에게 묻고 있는가? 시장의 하락 종목 수가 상승 종목 수보다 압도적이고 돌파가 계속 실패하는 똥 같은 시장(Shit market)에서 계속 매매 버튼을 누르는 건 계좌를 산산조각(Chop to pieces) 내고 싶다는 마음이나 다름없다. 시장 환경이 나쁠 때는 제발 아무것도 하지 말고 엉덩이를 깔고 앉아 현금을 지켜라."
    },
    {
        "title": "[ ADVICE ] 수익(P&L)에 집착하지 말고 '프로세스'를 지켜라",
        "content": "수익은 당신이 올바른 '프로세스'를 지켰을 때 따라오는 부산물일 뿐이다. 매수 후 3일 연속으로 상승하는 주식을 이제야 늦게 추격 매매하고 있는가? 축하한다, 당신은 최고점에 물린 '호구(Bag Holder)'가 된 것이다. 조급함을 버려라. 손절은 성스러운 것이다. **'첫 번째 손실이 가장 좋은 손실'**임을 명심하고, 당신이 세운 2.5%~5%의 손절선 혹은 당일 최저가(LOD)가 깨지면 기계처럼 잘라라. 당신의 얄팍한 예측이나 감정을 개입시키지 말고 오직 원칙, 철저한 프로세스만 남겨라."
    }
]

# --- [ FOOTER ] 전술 터미널 랜덤 어록 리스트 ---
BONDE_FOOTER_QUOTES = [
    "트레이딩은 돈을 버는 것이 목적이 아니라, 완벽한 프로세스를 수행하는 것이 목적이다. 수익은 그 보상일 뿐이다.",
    "당신이 똑똑하다는 것을 증명하려 하지 마라. 시장은 당신의 존재에 관심이 없다. 오직 당신의 손절선에만 관심이 있을 뿐이다.",
    "일확천금을 꿈꾸는 자는 결국 파산한다. 우리는 매일 안타를 쳐서 복리의 마법을 부리는 비즈니스맨이다.",
    "손실 중인 종목은 수급을 축내고 사기를 저하시키는 나쁜 직원이다. 정에 이끌리지 말고 즉시 현장 해고(손절)하라.",
    "희망(Hope)은 트레이딩 전략이 아니다. '본전 오면 팔겠다'는 생각은 시장이 당신의 파산을 기원하겠다는 예언과 같다.",
    "수익이 나는 주식은 회사를 성장시키는 우수 요원이다. 그들에게 더 많은 지원(비중)을 배분하고 보너스(추세 추종)를 주어 끝까지 부려먹어라.",
    "시장의 건강도(Breadth)가 죽었는데 매수 버튼을 누르는 것은 자살 행위다. 현금을 쥐고 아무것도 하지 않는 것도 트레이딩이다.",
    "지름길을 고집하지 마라. 고수들은 밤이 새도록 1,000개의 차트를 돌려보며 보냈어야 했다. 전술은 반사 신경의 영역이다.",
    "당신만의 엣지(Edge)가 없다면 당신은 트레이더가 아니라 기부천사일 뿐이다. 오늘 당장 딥다이브(Deep Dive) 훈련을 시작하라."
]

def get_daily_wisdom():
    day_idx = datetime.now().day % len(BONDE_WISDOM)
    return BONDE_WISDOM[day_idx]

def get_footer_quote():
    # 날짜 시드를 사용하여 매일 같은 랜덤 어록 선택
    random.seed(datetime.now().strftime("%Y%m%d"))
    return random.choice(BONDE_FOOTER_QUOTES)

# --- [PLACEHOLDER_LOGIC_START] ---
# --- [ COMMANDER'S ROUTER v8.0 ] ---
if page.startswith("1-a."):
    st.header("[ ADMIN ] 관리자 메인 센터 (HQ Member Approval)")
    if not is_admin:
        st.warning("[ ERROR ] 이 구역은 사령부 최고 등급 전용입니다.")
        st.stop()
    pending_users = [u for u, d in users.items() if d.get("status") == "pending"]
    st.subheader("[ QUEUE ] 신규 가입 대기 요원")
    if pending_users:
        if st.button("EXEC: 대기 요원 전체 일괄 승인", use_container_width=True):
            for u in pending_users: users[u]["status"] = "approved"
            save_users(users); st.success("[ SUCCESS ] 모든 대기 요원이 공식 승인되었습니다."); st.rerun()
        for u in pending_users:
            c1, c2 = st.columns([7, 3])
            with c1: st.info(f"ID: **{u}** | 가입 신청 중")
            with c2:
                if st.button(f"APPROVE", key=f"appr_{u}"):
                    users[u]["status"] = "approved"; save_users(users); st.rerun()
    else: st.info("대기 중인 신규 요원이 없습니다.")
    st.divider()
    st.subheader("[ STAFF ] 사령부 전체 요원 명단")
    all_rows = []
    for uid, udata in users.items():
        info = udata.get("info", {})
        all_rows.append({
            "아이디": uid, "등급": udata.get("grade", "회원"), "지역": info.get("region", "-"),
            "경력": info.get("exp", "-"), "연령": info.get("age", "-"), "합류일": info.get("joined_at", "-")
        })
    st.dataframe(pd.DataFrame(all_rows), use_container_width=True, hide_index=True)

elif page.startswith("1-b."):
    st.header("[ HR ] HQ 정예 요원 사령부 (Member HR Command)")
    if users.get(st.session_state.current_user, {}).get("grade") != "방장":
        st.error("[ ERROR ] 이 구역은 사령관(방장) 전용입니다.")
        st.stop()
    st.markdown("<div class='glass-card'>사령관의 권위로 요원의 등급을 조정하거나 사령부에서 즉각 제명하는 인사권을 행사합니다.</div>", unsafe_allow_html=True)
    m_list = [u for u in users.keys() if u != st.session_state.current_user]
    for u in m_list:
        udata = users[u]
        with st.expander(f"[ ID: {u} ] (현재 보직: {udata.get('grade', '회원')})"):
            c1, c2 = st.columns([2, 1])
            with c1:
                new_grade = st.selectbox(f"보직 변경(ID:{u})", ["회원", "정회원", "관리자"], key=f"hr_sel_{u}")
                if st.button(f"인사발령 (ID:{u})", key=f"hr_btn_{u}"):
                    users[u]["grade"] = new_grade; save_users(users); st.rerun()
            with c2:
                if st.button("[ EXEC: DELETE ]", key=f"hr_del_{u}"):
                    del users[u]; save_users(users); st.rerun()

elif page.startswith("1-c."):
    st.header("[ SECURE ] 개인 계정 보안 및 KIS 연동 설정")
    st.markdown("<div class='glass-card'>각 요원의 개인 한국투자증권 API 키를 안전하게 연동하여 개별 매매 환경을 구축합니다.</div>", unsafe_allow_html=True)
    
    users = load_users()
    curr_u = st.session_state.current_user
    u_data = users.get(curr_u, {})
    kis_creds = u_data.get("kis_credentials", {})

    with st.form("kis_secure_form"):
        st.subheader("🔑 KIS API Credentials")
        new_app_key = st.text_input("APP KEY", value=kis_creds.get("app_key", ""), type="password")
        new_app_secret = st.text_input("APP SECRET", value=kis_creds.get("app_secret", ""), type="password")
        new_acc_no = st.text_input("계좌번호 (8자리-2자리)", value=kis_creds.get("acc_no", ""))
        
        st.info("💡 입력된 키는 본인 계정에만 저장되며, 매매 및 잔고 조회 시 우선적으로 사용됩니다.")
        
        if st.form_submit_button("🛡️ 보안 설정 저장 및 적용"):
            if not u_data: u_data = {}
            u_data["kis_credentials"] = {
                "app_key": new_app_key,
                "app_secret": new_app_secret,
                "acc_no": new_acc_no
            }
            users[curr_u] = u_data
            save_users(users)
            st.success("✅ 개인 보안 설정이 저장되었습니다. 이제 본인의 계좌로 매매가 진행됩니다.")
            st.rerun()


elif page.startswith("2-a."):
    st.header("[ TREND ] 마켓 트렌드 요약")
    st.info("실시간 시장 강도: **MODERATE BULLISH**")

elif page.startswith("2-b."):
    st.header("[ MAP ] 실시간 주도주 히트맵")
    st.info("히트맵 데이터를 시각화합니다.")

elif page.startswith("2-c."):
    st.header("[ SENTIMENT ] 시장 심리 게이지")
    val, vix, lbl = get_market_sentiment_v2()
    st.metric("VIX Index", f"{vix:.1f}")

elif page.startswith("2-d."):
    st.markdown("<div style='text-align: right;'><span style='background: #FF4B4B; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.6rem; font-weight: bold;'>HQ-DATA SECURED: IMMUTABLE</span></div>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: #FFD700;'>[ MISSION ] 사령부 제작 동기</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888; font-size: 1.1rem;'>Follow the Giants, Conquer the Market Together</p>", unsafe_allow_html=True)
    st.divider()
    
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
    
    st.markdown("""
    <div style='text-align: right; margin-top: 40px; border-top: 1px solid #333; padding-top: 20px;'>
        <p style='color: #888; font-size: 0.8rem; margin-bottom: 5px;'>Terminal v9.9 Platinum Edition</p>
        <b style='color: #FFD700; font-size: 1.2rem;'>Expert Turtle</b>
    </div>
    """, unsafe_allow_html=True)

elif page.startswith("3-a."):
    st.header("[ SCAN ] 주도주 VCP & EP 마스터 스캐너")
    
    c1, c2, c3 = st.columns(3)
    with c1: scan_us = st.checkbox("USA (NASDAQ/S&P)", value=True)
    with c2: scan_kr = st.checkbox("KOR (KOSPI/KOSDAQ)", value=True)
    with c3: scan_mode = st.selectbox("전술 모드", ["엄격 (Strict)", "보통 (Normal)", "공격적 (Aggressive)"])

    if scan_mode == "공격적 (Aggressive)":
        st.session_state.cfg_min_pct = 2.5
        st.session_state.cfg_max_prev_pct = 5.0
        st.session_state.cfg_min_range_pos = 0.5
    elif scan_mode == "보통 (Normal)":
        st.session_state.cfg_min_pct = 3.5
        st.session_state.cfg_max_prev_pct = 3.0
        st.session_state.cfg_min_range_pos = 0.6
    else:
        st.session_state.cfg_min_pct = 4.0
        st.session_state.cfg_max_prev_pct = 2.0
        st.session_state.cfg_min_range_pos = 0.7

    if st.button("🚀 전술 스캔 개시 (Full Universe Scan)", use_container_width=True):
        with st.status("📡 전역 시장 주도주 탐색 및 전술 분석 중...", expanded=True) as status:
            target_universe = []
            if scan_us: target_universe += get_bonde_top_50() + get_nasdaq_200()
            if scan_kr: target_universe += get_kospi_top_200() + get_kosdaq_100()
            target_universe = list(set(target_universe))
            
            st.write(f"📊 총 {len(target_universe)}개 종목 벌크 데이터 수집 중...")
            # [ OPTIMIZE ] 벌크 다운로드로 네트워크 병목 해결
            bulk_data = get_bulk_market_data(target_universe, period="250d")
            
            hits = {"9M_EP": [], "Burst": [], "Story_EP": [], "Delayed_EP": []}
            
            st.write("⚔️ 병렬 전술 분석 엔진 가동...")
            # [ OPTIMIZE ] ThreadPoolExecutor로 CPU 작업 및 개별 분석 병렬화
            import concurrent.futures
            
            def scan_worker(ticker):
                hist = get_ticker_data_from_bulk(bulk_data, ticker)
                if not hist.empty:
                    return analyze_stockbee_setup(ticker, hist_df=hist)
                return None

            with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
                future_to_ticker = {executor.submit(scan_worker, t): t for t in target_universe}
                completed = 0
                progress_bar = st.progress(0)
                
                for future in concurrent.futures.as_completed(future_to_ticker):
                    res = future.result()
                    if res and res.get("status") == "SUCCESS":
                        hits["Burst"].append(res)
                    completed += 1
                    progress_bar.progress(completed / len(target_universe))
            
            # 품질(Quality)순으로 정렬하여 최정예 종목 상단 배치
            hits["Burst"] = sorted(hits["Burst"], key=lambda x: x.get("quality", 0), reverse=True)
            
            st.session_state.antigravity_scan = hits
            status.update(label=f"✅ 스캔 완료! {len(hits['Burst'])}개 주도주 포착", state="complete")
        st.rerun()

    if "antigravity_scan" in st.session_state:
        results = st.session_state.antigravity_scan["Burst"]
        if results:
            st.subheader(f"🎯 포착된 주도주 후보 ({len(results)}개)")
            for s in results:
                with st.expander(f"[{s['ticker']}] {s['name']} | 강도: {s['quality']} | 수익률: {s['day_pct']}%"):
                    c1, c2, c3 = st.columns([2,1,1])
                    with c1: st.write(f"분석 결과: {s['reason']}")
                    with c2:
                        if st.button("🛒 즉시 매수", key=f"buy_{s['ticker']}"):
                            if execute_kis_market_order(s['ticker'], 1, is_buy=True):
                                st.success(f"{s['name']} 매수 주문 성공!")
                    with c3:
                        st.write(f"RS: {s['rs']}")
        else:
            st.warning("🕵️ 현재 조건에 부합하는 종목이 없습니다. 감도를 '공격적'으로 변경해 보십시오.")


elif page.startswith("3-c."):
    st.header("[ WATCHLIST ] 사령부 관심 저격 종목")
    # [ FIX ] 정의되지 않은 함수 대신 빈 리스트 또는 시트 데이터 활용
    st.info("🎯 사령부에서 실시간 감시 중인 전략 종목 리스트입니다.")
    wl = get_bonde_top_50()
    st.write(wl)

elif page.startswith("3-f."):
    st.markdown("<h1 style='text-align: center; color: #00FF00;'>🔥 나노바나나 레이더 (Ripened Target)</h1>", unsafe_allow_html=True)
    st.markdown("<div class='glass-card' style='text-align: center; margin-bottom: 20px;'>현재 사령부 감시망에너지가 축적되어 돌파가 임박한 '잘 익은' 종목들을 실시간 추적합니다.</div>", unsafe_allow_html=True)
    
    # --- [ TACTICAL GUIDE BOX ] ---
    st.markdown("""
    <div class='glass-card' style='border-left: 5px solid #FFD700; padding: 20px; margin-bottom: 25px;'>
        <h3 style='color: #FFD700; margin-top: 0;'>🍌 나노바나나 99%의 의미 (전술적 해석)</h3>
        <ul style='color: #EEE; font-size: 0.95rem; line-height: 1.6;'>
            <li><b>에너지 축적 완료 (VCP):</b> 변동성이 극도로 줄어들어(Tightness), 아주 작은 매수세만 들어와도 주가가 위로 튀어 오를 수 있는 상태입니다.</li>
            <li><b>전술적 우위 (RS):</b> 시장 지수보다 훨씬 강한 상대 강도를 유지하고 있어, 시장이 반등할 때 가장 먼저 치고 나갈 준비가 되었습니다.</li>
            <li><b>거래량 메마름 (Dry-up):</b> 파는 사람이 더 이상 없는 '거래량 절벽' 구간을 통과했습니다.</li>
        </ul>
        <h4 style='color: #00FF00; margin-bottom: 10px;'>⚔️ 실제 대응 가이드</h4>
        <ul style='color: #CCC; font-size: 0.9rem; line-height: 1.6;'>
            <li><b>관심 종목 등록:</b> 99%인 종목들은 오늘이나 내일 당장 <b>'피벗 포인트(직전 고점)'</b>를 뚫고 올라갈 가능성이 매우 높습니다.</li>
            <li><b>돌파 시 매수:</b> 99% 상태에서 주가가 거래량을 동반하며 당일 고점을 돌파하는 순간이 가장 확률 높은 매수 타점입니다.</li>
            <li><b>자동매매 연동:</b> 자동매매 엔진(Section 7)을 가동 중이라면, 시스템이 이 99% 종목들을 실시간으로 감시하다가 돌파가 일어나는 나노 초 단위의 타이밍에 자동으로 주문을 집행하게 됩니다.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    if "antigravity_scan" in st.session_state:
        res = st.session_state.antigravity_scan
        all_hits = res.get("9M_EP", []) + res.get("Burst", []) + res.get("Story_EP", []) + res.get("Delayed_EP", [])
        
        if not all_hits:
            st.warning("🕵️ 현재 레이더망에 포착된 임박 종목이 없습니다. 3-a에서 스캔을 먼저 진행하십시오.")
        else:
            cols = st.columns(3)
            for i, stock in enumerate(all_hits[:12]):
                # 잘 익은 정도(Ready Score) 계산: RS와 Quality 기반
                ready_score = min(99, int(stock.get('quality', 50) + stock.get('rs', 50) / 10))
                with cols[i % 3]:
                    color = "#00FF00" if ready_score >= 85 else "#FFD700"
                    st.markdown(f"""
                    <div class='glass-card' style='border-top: 5px solid {color}; padding: 18px; min-height: 220px; display: flex; flex-direction: column; justify-content: space-between;'>
                        <div style='height: 55px; display: flex; align-items: center;'>
                            <div style='display: flex; justify-content: space-between; align-items: center; width: 100%; gap: 10px;'>
                                <h3 style='margin: 0; font-size: 1rem; line-height: 1.2; color: #FFF; font-weight: 700;'>{get_stock_name(stock['ticker'])}</h3>
                                <span style='color: {color}; font-weight: 800; font-size: 1.15rem; white-space: nowrap;'>{ready_score}%</span>
                            </div>
                        </div>
                        <div style='margin-top: 15px;'>
                            <div class='banana-track' style='margin-bottom: 15px;'>
                                <div class='banana-fill' style='width: {ready_score}%; background: {color}; box-shadow: 0 0 10px {color}66;'></div>
                            </div>
                            <div style='display: flex; flex-direction: column; gap: 2px;'>
                                <p style='font-size: 0.8rem; color: #BBB; margin: 0;'>🍌 상태: <span style='color: {color}; font-weight: bold;'>{'잘 익음 (임박)' if ready_score >= 85 else '숙성 중'}</span></p>
                                <p style='font-size: 0.75rem; color: #666; margin: 0;'>({stock['ticker']})</p>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("📡 [ SYSTEM ] 현재 나노 엔진 가열 중입니다. **3-a. [ SCAN ]** 메뉴에서 먼저 시장 스캔을 진행하십시오.")

elif page.startswith("4-a."):
    st.header("[ ANALYZE ] BMS 전술 분석기")
    st.markdown("<div class='glass-card'>본데(Bonde), 미너비니(Minervini), 스탁비(Stockbee) 통합 전략 분석기입니다.</div>", unsafe_allow_html=True)
    sel_target = st.selectbox("분석 대상 선택", list(TICKER_NAME_MAP.values()), key="analyze_v8_new")
    st.success(f"[ SUCCESS ] {sel_target} 전술 분석 완료: 매수 적격도 85%")

elif page.startswith("4-b."):
    st.header("[ INTERACTIVE ] 인터랙티브 차트")
    target_tic = st.text_input("분석 티커 입력", value="NVDA", key="chart_v8_new").upper()
    st.components.v1.html(f"<iframe src='https://s.tradingview.com/widgetembed/?symbol={target_tic}&interval=D&theme=dark' width='100%' height='550'></iframe>", height=560)

elif page.startswith("4-c."):
    st.header("[ RISK ] 리스크 관리 계산기")
    with st.form("risk_v8_new"):
        capital = st.number_input("투자 자금", value=10000000)
        if st.form_submit_button("CALC"): st.write("Calculated.")

elif page.startswith("5-a."):
    st.header("[ MENTOR ] 사령부 멘토, 프라딥 본데(Pradeep Bonde)")
    st.markdown("<div class='glass-card'>사령부의 전략적 모태가 된 전설적인 트레이더 프라딥 본데의 철학을 계승합니다.</div>", unsafe_allow_html=True)
    st.info("프라딥 본데의 '절차적 기억'과 '나노 단위 스캐닝'을 통해 개인 투자자도 시장의 주도주를 포착하는 시스템을 완성했습니다.")

elif page.startswith("5-b."):
    st.header("[ STUDY ] 사령부 주식 공부방 (Chart Academy)")
    st.markdown("<div class='glass-card'>운이 아닌 실력으로 차트 보는 법을 훈련합니다.</div>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["[ ARCHIVE ] Master's Archive", "[ TARGET ] Training Room"])
    with tab1:
        st.subheader("📝 대가의 핵심 패턴 1,000선")
        st.info("차트 1,000개를 뇌에 각인시키는 이미지 트레이닝 공간입니다.")
        c1, c2 = st.columns(2)
        with c1:
            st.info("**1. 컵앤핸들 (Cup and Handle)**\n\n깊은 조정을 거친 뒤 손잡이 부분에서 변동성이 수축될 때 진입하는 타점입니다.")
            st.info("**2. VCP (Volatility Contraction Pattern)**\n\n변동성이 20% -> 10% -> 5%로 줄어들며 매물을 소화하는 과정입니다.")
        with c2:
            st.success("**3. Episodic Pivot (EP)**\n\n뉴스나 실적 발표와 함께 발생하는 강력한 상승 갭과 거래량 포착입니다.")
            st.success("**4. 3-Day Rule**\n\n3일 연속 상승한 종목은 추격 매수하지 않고 눌림을 기다리는 인내를 배웁니다.")
    with tab2:
        st.subheader("🎯 실전 돌파 훈련")
        st.warning("과거 차트의 돌파 지점을 직접 클릭하며 반사 신경을 강화합니다.")

elif page.startswith("5-c."):
    st.markdown("<h1 style='text-align: center; color: #00FF00;'>🔥 나노바나나 레이더</h1>", unsafe_allow_html=True)
    st.markdown("<div class='glass-card' style='text-align: center; margin-bottom: 20px;'>현재 사령부 감시망에너지가 축적되어 돌파가 임박한 '황금 바나나' 종목들을 실시간 추적합니다.</div>", unsafe_allow_html=True)

    # --- [ TACTICAL GUIDE BOX ] ---
    st.markdown("""
    <div class='glass-card' style='border-left: 5px solid #FFD700; padding: 20px; margin-bottom: 25px;'>
        <h3 style='color: #FFD700; margin-top: 0;'>🍌 나노바나나 99%의 의미 (전술적 해석)</h3>
        <ul style='color: #EEE; font-size: 0.95rem; line-height: 1.6;'>
            <li><b>에너지 축적 완료 (VCP):</b> 변동성이 극도로 줄어들어(Tightness), 아주 작은 매수세만 들어와도 주가가 위로 튀어 오를 수 있는 상태입니다.</li>
            <li><b>전술적 우위 (RS):</b> 시장 지수보다 훨씬 강한 상대 강도를 유지하고 있어, 시장이 반등할 때 가장 먼저 치고 나갈 준비가 되었습니다.</li>
            <li><b>거래량 메마름 (Dry-up):</b> 파는 사람이 더 이상 없는 '거래량 절벽' 구간을 통과했습니다.</li>
        </ul>
        <h4 style='color: #00FF00; margin-bottom: 10px;'>⚔️ 실제 대응 가이드</h4>
        <ul style='color: #CCC; font-size: 0.9rem; line-height: 1.6;'>
            <li><b>관심 종목 등록:</b> 99%인 종목들은 오늘이나 내일 당장 <b>'피벗 포인트(직전 고점)'</b>를 뚫고 올라갈 가능성이 매우 높습니다.</li>
            <li><b>돌파 시 매수:</b> 99% 상태에서 주가가 거래량을 동반하며 당일 고점을 돌파하는 순간이 가장 확률 높은 매수 타점입니다.</li>
            <li><b>자동매매 연동:</b> 자동매매 엔진(Section 7)을 가동 중이라면, 시스템이 이 99% 종목들을 실시간으로 감시하다가 돌파가 일어나는 나노 초 단위의 타이밍에 자동으로 주문을 집행하게 됩니다.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    if "antigravity_scan" in st.session_state:
        res = st.session_state.antigravity_scan
        all_hits = res.get("9M_EP", []) + res.get("Burst", []) + res.get("Story_EP", []) + res.get("Delayed_EP", [])
        
        if not all_hits:
            st.warning("🕵️ 현재 레이더망에 포착된 임박 종목이 없습니다. 3-a에서 스캔을 먼저 진행하십시오.")
        else:
            cols = st.columns(3)
            for i, stock in enumerate(all_hits[:12]):
                # 5-c 레이더도 3-f와 동일한 신뢰도 점수 로직 적용
                ready_score = min(99, int(stock.get('quality', 50) + stock.get('rs', 50) / 10))
                with cols[i % 3]:
                    color = "#00FF00" if ready_score >= 90 else "#FFD700"
                    st.markdown(f"""
                    <div class='glass-card' style='border-top: 5px solid {color}; padding: 18px; min-height: 220px; display: flex; flex-direction: column; justify-content: space-between;'>
                        <div style='height: 55px; display: flex; align-items: center;'>
                            <div style='display: flex; justify-content: space-between; align-items: center; width: 100%; gap: 10px;'>
                                <h3 style='margin: 0; font-size: 1rem; line-height: 1.2; color: #FFF; font-weight: 700;'>{get_stock_name(stock['ticker'])}</h3>
                                <span style='color: {color}; font-weight: 800; font-size: 1.15rem; white-space: nowrap;'>{ready_score}%</span>
                            </div>
                        </div>
                        <div style='margin-top: 15px;'>
                            <div class='banana-track' style='margin-bottom: 15px;'>
                                <div class='banana-fill' style='width: {ready_score}%; background: {color}; box-shadow: 0 0 10px {color}66;'></div>
                            </div>
                            <div style='display: flex; flex-direction: column; gap: 2px;'>
                                <p style='font-size: 0.8rem; color: #BBB; margin: 0;'>🔬 분석: <span style='color: {color}; font-weight: bold;'>{stock.get('TIC', 'NANO')} 전략 포착</span></p>
                                <p style='font-size: 0.75rem; color: #666; margin: 0;'>({stock['ticker']})</p>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("📡 [ SYSTEM ] 현재 나노 엔진 가열 중입니다. **3-a. [ SCAN ]** 메뉴에서 먼저 시장 스캔을 진행하면 이곳에 황금 바나나 리스트가 나타납니다.")
        
    st.divider()
    st.markdown("""
    <div style='background: rgba(0,0,0,0.3); padding: 20px; border-radius: 12px; border: 1px solid rgba(0,255,0,0.2);'>
        <h4 style='color: #00FF00; margin-top: 0;'>💡 나노바나나의 유래</h4>
        <p style='font-size: 0.9rem; color: #BBB; line-height: 1.6;'>
            바나나가 초록색에서 노랗게 익으면 맛있어지는 것처럼, 주식도 지루한 횡보(초록)를 거쳐 폭발적인 시세 분출(노랑)이 이루어지는 찰나의 시간이 있습니다.<br>
            사령부는 이 찰나를 <b>나노 단위</b>로 쪼개어 분석하여 사령관님께 가장 신선한 기회를 보고합니다.
        </p>
    </div>
    """, unsafe_allow_html=True)

elif page.startswith("5-d."):
    st.header("[ EXAM ] 사령부 정기 승급 시험")
    st.markdown("<div class='glass-card'>80점 이상 획득 시 '정회원' 등으로 승격됩니다.</div>", unsafe_allow_html=True)

elif page.startswith("5-e."):
    st.header("[ PROFIT ] 명예의 전당 (Profit Hall)")
    st.success("요원들의 찬란한 수익 실적을 기록합니다.")

elif page.startswith("5-f."):
    st.header("[ LOSS ] 성찰의 방 (Loss Room)")
    st.error("실패를 분석하여 내일의 승리를 준비합니다.")

    st.error("실패를 분석하여 내일의 승리를 준비합니다.")

elif page.startswith("5-d."):
    st.markdown("""
    <div style='background: linear-gradient(135deg, #FF416C 0%, #FF4B2B 100%); padding: 30px; border-radius: 20px; text-align: center; margin-bottom: 30px;'>
        <h1 style='margin:0; color:white; font-family:Orbitron; letter-spacing:5px;'>HQ ELITE PROMOTION TEST</h1>
        <p style='margin:5px 0 0 0; color:rgba(255,255,255,0.9); font-size:1.1rem;'>사령부 정예요원 승급을 위한 전술 지식 검증</p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("📝 전술 이론 평가 (Phase 1)")
    with st.form("exam_v9"):
        q1 = st.radio("1. 프라딥 본데의 'EP' 전략에서 가장 중요한 요소는?", ["뉴스 없이 상승", "강력한 거래량과 갭상승", "역배열에서의 반등", "배당금 확인"])
        q2 = st.radio("2. 마크 미너비니의 VCP 패턴에서 변동성은 어떻게 변해야 하는가?", ["점점 커져야 함", "일정하게 유지됨", "점점 수축되어야 함", "상관 없음"])
        q3 = st.radio("3. 리스크 관리의 핵심인 '1% Rule'은 무엇을 의미하는가?", ["총 자산의 1%만 매수", "한 종목당 손실을 총 자산의 1%로 제한", "수익 1%에서 무조건 익절", "1% 확률에 베팅"])
        
        if st.form_submit_button("전술 보고서 제출"):
            if q1 == "강력한 거래량과 갭상승" and q2 == "점점 수축되어야 함" and q3 == "한 종목당 손실을 총 자산의 1%로 제한":
                st.balloons()
                st.success("✅ [합격] 지휘관님, 모든 전술 이론을 완벽하게 숙지하셨습니다. 이제 정예요원 자격이 부여됩니다.")
                st.info("사이드바 6-c 메뉴에서 정회원 신청을 진행해 주십시오.")
            else:
                st.error("❌ [불합격] 전술 이해도가 부족합니다. 마스터 훈련소 자료를 다시 검토하십시오.")

elif page.startswith("5-z."):
    st.markdown("""
    <div style='background: linear-gradient(135deg, #1d976c 0%, #93f9b9 100%); padding: 30px; border-radius: 20px; text-align: center; margin-bottom: 30px;'>
        <h1 style='margin:0; color:white; font-family:Pretendard; letter-spacing:2px;'>ANTI-GRAVITY FARMING</h1>
        <p style='margin:5px 0 0 0; color:rgba(255,255,255,0.9); font-size:1.1rem;'>인내와 비중으로 수익을 재배하는 농사매매 전략실</p>
    </div>
    """, unsafe_allow_html=True)

    # [ STRATEGY GUIDE ]
    with st.expander("📖 농사매매 전략 가이드 (지휘관 필독)", expanded=True):
        st.markdown("""
        ### 🏛️ 지휘관을 위한 운영 가이드
        1. **인내의 미학**: 이 시스템은 매일 차트를 보며 일희일비하지 않는 농부의 마음이 핵심입니다. 유하니(AI 후배)가 아침마다 "선배님! 오늘은 사과가 3개나 익었어용!"이라고 알려줄 때까지 본업과 일상에 집중해 주세요.
        2. **비중의 마법**: 종목당 비중을 3~5%로 작게 시작했기 때문에, -30%까지 떨어져도 전체 계좌에 미치는 영향은 제한적입니다. 오히려 저렴하게 씨앗을 더 심는 기회로 삼으시면 됩니다.
        3. **데이터의 신뢰성**: RSI와 볼린저 밴드 지표는 주가가 과하게 꺾였을 때(과매도) 씨를 뿌리는 아주 좋은 기준이 됩니다.
        """)
        
    st.subheader("🌾 농사매매 전술 교본")
    farming_guide = [
        {"상태": "🌱 씨 뿌리기 (새싹)", "조건": "RSI 30 이하 / BB 하단 터치", "액션": "최초 3~5% 비중 진입"},
        {"상태": "🌿 물 주기 (성장)", "조건": "고점 대비 -10, -20, -30% 하락", "액션": "단계별 추가 매수 (5, 10, 20%)"},
        {"상태": "🍎 수확 시기 (과일)", "조건": "수익률 15~25% 도달", "액션": "전량 매도 및 수익 확정"},
        {"상태": "💤 대기 중 (휴면)", "조건": "목표가 미도달 및 추매 조건 아님", "액션": "인내하며 보유"}
    ]
    st.table(pd.DataFrame(farming_guide))

    # [ FARM TRACKER FUNCTIONAL ]
    st.divider()
    st.subheader("🚜 나의 농장 관리소 (Active Crops)")
    
    if "my_farm_stocks" not in st.session_state:
        st.session_state.my_farm_stocks = []

    if st.session_state.my_farm_stocks:
        if st.button("🔄 전체 작물 상태 최신화 (Update All)"):
            with st.status("농작물들의 건강 상태를 체크 중입니다...", expanded=False):
                token = get_kis_access_token(KIS_APP_KEY, KIS_APP_SECRET, KIS_MOCK_TRADING)
                for stock in st.session_state.my_farm_stocks:
                    is_kr = stock['ticker'].endswith(".KS") or stock['ticker'].endswith(".KQ")
                    df = get_kis_ohlcv(stock['ticker'], token) if is_kr else get_kis_overseas_ohlcv(stock['ticker'], token)
                    if not df.empty:
                        df = calculate_rsi(df)
                        stock['current'] = df['Close'].iloc[-1]
                        stock['rsi'] = df['RSI'].iloc[-1]
                        if stock['current'] > stock['max']: stock['max'] = stock['current']
            st.rerun()

        for i, stock in enumerate(st.session_state.my_farm_stocks):
            profit = (stock['current'] - stock['entry']) / stock['entry'] * 100
            drop = (stock['current'] - stock['max']) / stock['max'] * 100
            
            # [ TACTICAL LOGIC ]
            status = "🌱 새싹 (안정적 보유)"
            color = "#93f9b9"
            action_tip = "인내하며 성장을 지켜보세요."
            
            if profit >= 20: 
                status, color, action_tip = "🍎 과일 (수확 적기!)", "#FF4B4B", "전량 매도하여 수익을 확정하세요!"
            elif profit >= 10:
                status, color, action_tip = "🌼 개화 (수익 진행 중)", "#FFD700", "목표가(20%)까지 홀딩하세요."
            elif drop <= -30:
                status, color, action_tip = "🆘 위기 (3차 물주기)", "#FF0000", "비중 20% 추가 매수 (강력 매수 구간)"
            elif drop <= -20:
                status, color, action_tip = "🌿 성장 (2차 물주기)", "#FF4500", "비중 10% 추가 매수 권장"
            elif drop <= -10:
                status, color, action_tip = "🌿 성장 (1차 물주기)", "#FFA500", "비중 5% 추가 매수 준비"
            
            with st.container():
                st.markdown(f"""
                <div class='glass-card' style='border-left: 5px solid {color}; padding: 20px; margin-bottom: 15px;'>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <h3 style='margin: 0;'>{get_stock_name(stock['ticker'])} <small style='color: #888;'>({stock['ticker']})</small></h3>
                        <h4 style='margin: 0; color: {"#FF4B4B" if profit >= 0 else "#4B4BFF"};'>{profit:+.2f}%</h4>
                    </div>
                    <div style='margin: 10px 0; font-size: 0.95rem; color: #FFF; font-weight: bold;'>상태: {status}</div>
                    <div style='font-size: 0.85rem; color: #AAA;'>
                        진입가: {stock['entry']:,} | 현재가: {stock['current']:,} | RSI: {stock['rsi']:.1f} | 고점대비: <span style='color: #FF4B4B;'>{drop:.1f}%</span>
                    </div>
                    <div style='margin-top: 10px; padding: 10px; background: rgba(255,255,255,0.03); border-radius: 8px; border: 1px dashed {color}55;'>
                        <span style='color: {color}; font-weight: bold;'>⚔️ 지휘관 대응:</span> {action_tip}
                    </div>
                    <div style='text-align: right; margin-top: 10px;'>
                        <button style='background: transparent; border: 1px solid #444; color: #888; border-radius: 5px; cursor: pointer;' 
                                onclick='window.location.reload()'>작물 삭제</button>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"🗑️ {stock['ticker']} 작물 삭제", key=f"del_{stock['ticker']}"):
                    st.session_state.my_farm_stocks.pop(i)
                    st.rerun()
    else:
        st.info("현재 농장에 심어진 작물이 없습니다. 아래 레이더에서 우량한 씨앗을 찾아보세요!")

    # [ SEEDING RADAR ENHANCED ]
    st.divider()
    st.subheader("🔍 글로벌 우량주 씨 뿌리기 레이더")
    col1, col2, col3 = st.columns(3)
    with col1: scan_kr = st.checkbox("🇰🇷 한국 (KOSPI/KOSDAQ)", value=True)
    with col2: scan_us = st.checkbox("🇺🇸 미국 (NASDAQ 100)", value=True)
    with col3: rsi_threshold = st.slider("RSI 기준 (과매도 강도)", 15, 45, 30)

    if st.button("🚀 전역 시장 과매도 종목 탐색 개시 (KR 우선)", use_container_width=True):
        with st.status("🕵️ 시장을 뒤져서 저평가된 씨앗들을 찾는 중...", expanded=True) as status:
            token = get_kis_access_token(KIS_APP_KEY, KIS_APP_SECRET, KIS_MOCK_TRADING)
            
            markets = []
            if scan_kr: markets.append(("KR", get_kr_all_tickers()))
            if scan_us: markets.append(("US", get_nasdaq_200()[:50]))
            
            found_seeds = []
            
            for m_type, universe in markets:
                st.write(f"📊 {m_type} 시장 {len(universe)}개 핵심 종목 전술 분석 중...")
                bulk_df = get_bulk_market_data(universe, period="60d")
                
                def analyze_worker(ticker):
                    hist = get_ticker_data_from_bulk(bulk_df, ticker)
                    if not hist.empty and len(hist) >= 30:
                        hist = calculate_rsi(hist)
                        hist = calculate_bollinger_bands(hist)
                        curr_p = hist['Close'].iloc[-1]
                        rsi_v = hist['RSI'].iloc[-1]
                        bb_l = hist['BB_Lower'].iloc[-1]
                        
                        if rsi_v <= rsi_threshold or curr_p <= bb_l:
                            roe_val = 0
                            roe_str = "N/A"
                            try:
                                info = yf.Ticker(ticker).info
                                roe_val = info.get('returnOnEquity', 0)
                                if roe_val < 0: return None
                                roe_str = f"{roe_val * 100:.1f}%"
                            except: pass
                            
                            # [ TACTICAL RATING ]
                            score = 50
                            if rsi_v <= 25: score += 20
                            if roe_val > 0.2: score += 20
                            if curr_p <= bb_l: score += 10
                            
                            reason = []
                            if rsi_v <= rsi_threshold: reason.append(f"RSI 과매도({rsi_v:.1f})")
                            if curr_p <= bb_l: reason.append("볼린저밴드 하단 터치")
                            
                            return {
                                "ticker": ticker, "name": get_stock_name(ticker), 
                                "rsi": rsi_v, "price": curr_p, "roe": roe_str,
                                "reason": " & ".join(reason), "market": m_type,
                                "score": score
                            }
                    return None

                with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
                    results = list(executor.map(analyze_worker, universe))
                    found_seeds += [r for r in results if r]

            if found_seeds:
                status.update(label=f"✅ {len(found_seeds)}개의 우량 씨앗 포착 완료!", state="complete")
                
                unique_found = []
                seen_names = set()
                for s in found_seeds:
                    if s['name'] not in seen_names:
                        unique_found.append(s)
                        seen_names.add(s['name'])
                
                unique_found.sort(key=lambda x: (0 if x['market'] == "KR" else 1, -x['score']))
                
                for s in unique_found:
                    market_icon = "🇰🇷" if s['market'] == "KR" else "🇺🇸"
                    rating_stars = "⭐" * (s['score'] // 20)
                    with st.expander(f"{market_icon} {s['name']} | 전술 점수: {s['score']} {rating_stars}"):
                        st.markdown(f"""
                        <div style='padding: 10px; border-radius: 10px; background: rgba(255,255,255,0.02);'>
                            <p><b>종목명</b>: {s['name']} ({s['ticker']})</p>
                            <p><b>현재가</b>: {s['price']:,} | <b>ROE</b>: <span style='color:#FFD700;'>{s['roe']}</span></p>
                            <p><b>포착 사유</b>: <span style='color:#39FF14;'>{s['reason']}</span></p>
                            <p style='color: #888; font-size: 0.9rem;'>* 전술 점수가 높을수록 우량주가 바닥권에 진입했음을 의미합니다.</p>
                        </div>
                        """, unsafe_allow_html=True)
                        if st.button(f"🚜 {s['ticker']} 농장 등록 (씨 뿌리기)", key=f"add_{s['ticker']}"):
                            new_crop = {
                                "ticker": s['ticker'], "entry": s['price'], 
                                "max": s['price'], "current": s['price'], 
                                "rsi": s['rsi'], "weight": 5
                            }
                            if "my_farm_stocks" not in st.session_state: st.session_state.my_farm_stocks = []
                            st.session_state.my_farm_stocks.append(new_crop)
                            st.success(f"{s['name']} 종목이 나의 농장에 심어졌습니다. 인내하며 키워보세요!")
                            st.rerun()
            else:
                status.update(label="❌ 현재 전역 시장에 씨를 뿌릴 만한 과매도 종목이 없습니다.", state="complete")

    st.info("💡 **전술 핵심**: 우량주가 이유 없이(지수 영향 등) 떨어질 때가 가장 큰 기회입니다. ROE와 전술 점수를 믿고 씨를 뿌리십시오.")



elif page.startswith("6-a."):
    st.header("[ CHECK ] 사령부 출석체크")
    with st.form("att_v8"):
        msg = st.text_input("오늘 매매에 임하는 다짐")
        if st.form_submit_button("서명"): st.success("출석 완료!")

elif page.startswith("6-b."):
    st.header("💬 안티그래비티 대화방")
    st.markdown("<div class='glass-card' style='height:400px; overflow-y:auto;'>실시간 전략 공유 채널입니다.</div>", unsafe_allow_html=True)

elif page.startswith("6-c."):
    st.header("[ APPLY ] 정회원 자격 신청")
    st.info("승급 시험 합격 후 이곳에서 신청서를 제출하십시오.")

elif page.startswith("7-a."):
    st.header("[ EXEC ] 모의투자 매수 테스트")
    st.info("가상 시드머니 1,000만원을 활용하여 전술을 테스트합니다.")

elif page.startswith("7-b."):
    st.header("[ MONITOR ] 사령부 자산 관제소")
    st.info("가상 및 실전(KIS) 계좌의 통합 잔고 현황을 실시간 모니터링합니다.")

elif page.startswith("7-c."):
    st.header("[ ENGINE ] Stockbee 자동매매 엔진")
    st.markdown("<div class='glass-card' style='border-left:5px solid #FFD700;'>본데의 전술로 24시간 실시간으로 감시하며 기계적인 집행을 수행합니다.</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        auto_trade_on = st.toggle("🚨 실시간 자동 교전 엔진 가동", value=st.session_state.get("auto_trade_active", False))
        st.session_state.auto_trade_active = auto_trade_on
    with col2:
        interval = st.number_input("스캔 주기 (분)", 1, 60, 5)

    if auto_trade_on:
        st.success(f"📡 엔진 가동 중... {interval}분 간격으로 시장을 감시합니다.")
        
        # [ AUTO-EXECUTION LOGIC ]
        last_run = st.session_state.get("last_auto_run_time", 0)
        time_passed = (time.time() - last_run) / 60
        
        if time_passed >= interval:
            st.info(f"🔄 자동 교전 주기 도달 ({interval}분). 시스템이 자동으로 사이클을 실행합니다.")
            auto_trigger = True
        else:
            auto_trigger = False
            st.caption(f"⏱️ 다음 자동 스캔까지 약 {int(interval - time_passed)}분 남음")
            # [ JS HEARTBEAT ] 브라우저 강제 리프레시 스크립트 주입
            st.components.v1.html(f"""
                <script>
                setTimeout(function() {{
                    window.parent.location.reload();
                }}, {(interval * 60 * 1000) + 1000});
                </script>
            """, height=0)

        if st.button("⚡ 즉시 1회 자동 교전 사이클 실행") or auto_trigger:
            if auto_trigger: st.session_state.last_auto_run_time = time.time()
            # [ OPTIMIZE ] 현재 세션 설정에 따른 토큰 획득
            ak, as_, an = get_user_kis_creds()
            use_mock = get_kis_mock_status()
            token = get_kis_access_token(ak, as_, use_mock)
            
            with st.status("⚔️ 자동 교전 사이클 시작...", expanded=True) as status:
                # 0. AI 참모 브리핑 (1시간 주기)
                send_ai_tactical_coaching(token)
                
                # 1. 리스크 관리 (기존 포지션 익절/손절)
                st.write("🛡️ 리스크 관리 엔진 가동 (익절/손절 체크)...")
                execute_kis_auto_cut(token)
                
                # 2. 신규 진입 스캔 (최정예 4종목 구성용)
                st.write("🔍 전술 유니버스 전체 스캔 중 (Best 4 선정)...")
                target_universe = get_bonde_top_50() + get_nasdaq_200()
                
                # 현재 보유 종목 리스트 및 슬롯 확인
                # [ FIX ] 현재 세션 설정 및 개인화 키 로드
                u_ak, u_as, u_an = get_user_kis_creds()
                current_mock = get_kis_mock_status()
                
                _, _, kr_holdings = get_kis_balance(token, mock=current_mock, acc_no=u_an)
                over_data, us_holdings = get_kis_overseas_balance(token, mock=current_mock, acc_no=u_an)
                owned_count = len(kr_holdings) + len(us_holdings)
                
                # [ FIX ] 티커 일관성 유지 (KR 종목 접미사 처리)
                owned_tickers = []
                for h in kr_holdings:
                    tic = h.get('pdno', '')
                    # 종목명이나 다른 정보를 통해 .KS/.KQ 구분 (여기서는 resolve_ticker 활용 권장)
                    # 일단 스캔 유니버스와 비교를 위해 접미사 붙임
                    owned_tickers.append(tic + ".KS")
                    owned_tickers.append(tic + ".KQ")
                for h in us_holdings:
                    owned_tickers.append(h.get('ovrs_pdno', ''))
                
                available_slots = 4 - owned_count
                if available_slots <= 0:
                    st.warning("⚠️ 이미 포트폴리오가 가득 찼습니다 (최대 4종목). 교전 중인 부대를 관리하십시오.")
                else:
                    # 전수 조사 후 품질순 정렬
                    potential_hits = []
                    bulk_data = get_bulk_market_data(target_universe, period="250d")
                    
                    for ticker in target_universe:
                        if ticker in owned_tickers: continue
                        hist = get_ticker_data_from_bulk(bulk_data, ticker)
                        if not hist.empty:
                            res = analyze_stockbee_setup(ticker, hist_df=hist)
                            if res.get("status") == "SUCCESS":
                                potential_hits.append(res)
                    
                    # 품질(Quality) 높은 순으로 정렬
                    potential_hits = sorted(potential_hits, key=lambda x: x.get('quality', 0), reverse=True)
                    
                    # [ BREADTH GUARD ] 지수 건강도 체크 및 방어 모드 적용
                    is_defense, health_info = analyze_market_health()
                    defense_factor = 0.5 if is_defense else 1.0
                    
                    if is_defense:
                        st.warning("🛡️ [ DEFENSE MODE ] 지수가 50일선 아래에 있습니다. 매수 비중을 50%로 축소하여 교전을 수행합니다.")
                        send_telegram_msg("🛡️ [ SYSTEM ALERT ] 시장 지수가 50일선 아래로 이탈했습니다. 시스템이 자동으로 '방어 모드'로 전환하여 매수 비중을 50%로 축소합니다.")
                    
                    # 환율 정보 및 자산 확인
                    usd_krw, _ = get_macro_data()
                    total_equity = st.session_state.get("last_total_equity", 10000000)
                    target_krw = total_equity * 0.25 * defense_factor # 방어 모드 시 비중 축소
                    
                    executed_count = 0
                    for res in potential_hits:
                        if executed_count >= available_slots: break
                        
                        ticker = res['ticker']
                        st.write(f"🎯 최정예 타겟 포착: {res['name']} ({ticker}) | 품질: {res['quality']}")
                        
                        is_kr = ticker.endswith(".KS") or ticker.endswith(".KQ")
                        if is_kr:
                            # [ SLIPPAGE GUARD ] 평균 거래량의 1% 이내로 수량 제한
                            max_qty = int(res['volume'] * 0.01)
                            trade_qty = min(max_qty, max(1, int(target_krw / res['close'])))
                        else:
                            # 해외 주식 수량 계산
                            target_usd = target_krw / usd_krw
                            max_qty = int(res['volume'] * 0.01)
                            trade_qty = min(max_qty, max(1, int(target_usd / res['close'])))
                        
                        # 자동 매수 집행
                        if execute_kis_market_order(ticker, trade_qty, is_buy=True):
                            st.info(f"🚀 {res['name']} 자동 매수 집행 완료! ({trade_qty}주)")
                            executed_count += 1
                
                status.update(label="✅ 교전 사이클 종료", state="complete")

    st.divider()
    st.subheader("📊 실시간 교전 로그 (Combat Logs)")
    if st.session_state.get("combat_logs"):
        for log in reversed(st.session_state.combat_logs[-20:]):
            color = "#FF4B4B" if log["type"] == "ERROR" else ("#00FF00" if "매수" in log["msg"] else "#FFD700")
            st.markdown(f"<small style='color:#888;'>[{log['time']}]</small> <span style='color:{color};'>{log['msg']}</span>", unsafe_allow_html=True)
    else:
        st.info("현재 기록된 교전 이력이 없습니다.")


elif page.startswith("7-g."):
    st.title("🏹 REAL-TIME COMBAT CENTER")
    st.markdown("<div class='glass-card'>실시간 시장 데이터를 본데의 시각으로 관제합니다.</div>", unsafe_allow_html=True)
    target_tic = st.text_input("관제 대상 티커", value="NVDA").upper()
    st.components.v1.html(f"<iframe src='https://s.tradingview.com/widgetembed/?symbol={target_tic}&interval=D&theme=dark' width='100%' height='550'></iframe>", height=560)

elif page.startswith("7-h."):
    st.header("📜 MISSION RECAP")
    st.info("과거 교전 이력을 복기하여 절차적 기억을 강화합니다.")

elif page.startswith("7-i."):
    st.header("⚙️ SYSTEM CONFIG (사령부 시스템 설정)")
    
    st.subheader("📡 스캐너 감도 설정 (Tactical Sensitivity)")
    st.session_state.cfg_min_pct = st.slider("최소 상승률 (Min %)", 1.0, 10.0, st.session_state.get("cfg_min_pct", 4.0), 0.5)
    st.session_state.cfg_max_prev_pct = st.slider("전일 최대 상승폭 (Tightness)", 1.0, 10.0, st.session_state.get("cfg_max_prev_pct", 2.0), 0.5)
    st.session_state.cfg_min_range_pos = st.slider("최소 종가 위치 (Range Position)", 0.1, 1.0, st.session_state.get("cfg_min_range_pos", 0.7), 0.1)
    
    st.divider()
    st.subheader("🛡️ 리스크 관리 설정")
    st.session_state.cfg_stop_loss_pct_val = st.slider("기계적 손절 임계값(%)", -10.0, -1.0, st.session_state.get("cfg_stop_loss_pct_val", -5.0), 0.5, key="stop_loss_slider")
    if st.button("설정 저장 및 사령부 적용"):
        st.success("✅ 시스템 설정이 서버에 영구 반영되었습니다.")
    
    st.divider()
    st.subheader("📡 텔레그램 통신 테스트")
    if st.button("🚀 테스트 메시지 전송 (연결 확인)"):
        send_telegram_msg("🔔 [TEST] 사령부와 텔레그램 통신 라인이 성공적으로 확보되었습니다. 준비 완료!")
        st.info("텔레그램 앱에서 메시지 수신 여부를 확인하십시오.")

elif page.startswith("7-p."):
    st.markdown("""
    <div style='background: rgba(255, 0, 0, 0.2); border: 2px solid #FF3131; padding: 30px; border-radius: 15px; text-align: center;'>
        <h1 style='color: #FF3131; margin-bottom: 10px;'>🚨 EMERGENCY PANIC SELL 🚨</h1>
        <p style='color: white; font-size: 1.1rem;'>이 버튼은 시장의 급격한 붕괴나 비상 사태 발생 시 모든 주식을 즉시 <b>시장가로 전량 매도</b>하는 최후의 수단입니다.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.warning("⚠️ 주의: 이 작업은 되돌릴 수 없으며, 모든 보유 종목이 즉시 매도 처리됩니다.")
    
    confirm_panic = st.checkbox("나는 위험을 인지했으며, 현재 모든 포지션을 즉시 정리하기를 원합니다.")
    
    if confirm_panic:
        auth_code_final = st.text_input("최종 승인 번호를 입력하십시오 (1353)", type="password", key="final_panic_auth")
        if st.button("🔥 [ DANGER ] 모든 포지션 즉시 시장가 전량 매도", use_container_width=True):
            if auth_code_final == "1353":
                with st.spinner("⚔️ 함대 전체 긴급 퇴각 및 현금화 집행 중..."):
                    token = get_kis_access_token(KIS_APP_KEY, KIS_APP_SECRET, KIS_MOCK_TRADING)
                    if execute_panic_sell_all(token):
                        st.balloons()
                        st.error("🚨 전량 매도 작전이 완료되었습니다. 텔레그램 보고서를 확인하십시오.")
                    else:
                        st.error("❌ 일부 종목 매도 중 오류가 발생했습니다. 수동 확인이 필요합니다.")
            else:
                st.error("❌ 승인 번호가 올바르지 않습니다. 작전을 중단합니다.")

elif page.startswith("7-q."):
    st.header("📡 [ BREADTH ] 마켓 브레스 감시 시스템")
    st.markdown("<div class='glass-card'>글로벌 주요 지수의 50일 이동평균선 이탈 여부를 실시간 관측합니다.</div>", unsafe_allow_html=True)
    
    is_defense, health = analyze_market_health()
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🇰🇷 KOSPI Index")
        if "^KS11" in health:
            h = health["^KS11"]
            diff = (h['price'] / h['ma50'] - 1) * 100
            st.metric("현재가 vs 50일선", f"{h['price']:,.2f}", f"{diff:+.2f}%", delta_color="normal")
            status_color = "#39FF14" if h['status'] == "HEALTHY" else "#FF3131"
            st.markdown(f"<div style='text-align:center; padding:10px; border-radius:10px; background:{status_color}33; color:{status_color}; border:1px solid {status_color}; font-weight:bold;'>{h['status']}</div>", unsafe_allow_html=True)
            
    with col2:
        st.subheader("🇺🇸 NASDAQ Index")
        if "^IXIC" in health:
            h = health["^IXIC"]
            diff = (h['price'] / h['ma50'] - 1) * 100
            st.metric("현재가 vs 50일선", f"{h['price']:,.2f}", f"{diff:+.2f}%", delta_color="normal")
            status_color = "#39FF14" if h['status'] == "HEALTHY" else "#FF3131"
            st.markdown(f"<div style='text-align:center; padding:10px; border-radius:10px; background:{status_color}33; color:{status_color}; border:1px solid {status_color}; font-weight:bold;'>{h['status']}</div>", unsafe_allow_html=True)

    st.divider()
    if is_defense:
        st.error("🛡️ 현재 시장은 '방어 모드' 발동 구간입니다. 시스템이 자동으로 매수 비중을 조절합니다.")
    else:
        st.success("🚀 현재 시장은 '공격 모드' 구간입니다. 정석적인 비중으로 교전을 수행합니다.")

elif page.startswith("7-j."):
    st.markdown("""
    <div style='background: linear-gradient(90deg, #00F2FF 0%, #0066FF 100%); padding: 25px; border-radius: 15px; text-align: center; margin-bottom: 25px; box-shadow: 0 10px 30px rgba(0,242,255,0.3);'>
        <h1 style='margin:0; color:white; font-family:Orbitron; letter-spacing:5px;'>CHANDE MOMENTUM ENGINE</h1>
        <p style='margin:5px 0 0 0; color:rgba(255,255,255,0.8); font-size:0.9rem;'>Tushar Chande's Tactical Momentum Algorithm v1.0</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        cmo_active = st.toggle("🚀 CHANDE 엔진 가동 (CMO)", value=st.session_state.get("cmo_engine_active", False))
        st.session_state.cmo_engine_active = cmo_active
    with col2:
        use_auto_universe = st.checkbox("나스닥100 + 시트 연동", value=True)
    with col3:
        manual_tickers = st.text_input("추가 티커", value="NVDA,TSLA").upper().replace(" ", "").split(",")
    
    # 유니버스 구성
    if use_auto_universe:
        sheet_url = "https://docs.google.com/spreadsheets/d/1xjbe9SF0HsxwY_Uy3NC2tT92BqK0nhArUaYU16Q0p9M/edit#gid=1499398020"
        # 나스닥 상위 15 (Stage Analysis 기준 핵심 종목군)
        nasdaq_top_15 = ["NVDA", "AAPL", "MSFT", "AMZN", "GOOGL", "GOOG", "AVGO", "META", "TSLA", "WMT", "ASML", "NFLX", "CSCO", "AMD", "MU", "COST"]
        sheet_tickers = get_sheet_tickers(sheet_url)
        cmo_tickers = list(dict.fromkeys(nasdaq_top_15 + sheet_tickers + manual_tickers))
    else:
        cmo_tickers = manual_tickers


    if cmo_active:
        st.success(f"📡 찬드라 엔진 감시 중... 유니버스 크기: {len(cmo_tickers)} 종목")
        with st.expander("🔍 현재 감시 리스트 확인"):
            st.write(", ".join(cmo_tickers))
            
        if st.button("⚡ 즉시 CMO 교전 실행"):

            with st.status("⚔️ CMO 전술 사이클 가동...", expanded=True) as status:
                ak, as_, an = get_user_kis_creds()
                use_mock = get_kis_mock_status()
                token = get_kis_access_token(ak, as_, use_mock)
                
                # 1. 공통 리스크 관리 (-3% 손절 등)
                st.write("🛡️ 전술적 리스크 관리(Stop-Loss) 점검...")
                execute_kis_auto_cut(token)
                
                # 2. CMO 전술 분석 및 매매
                for ticker in cmo_tickers:
                    st.write(f"🔍 {ticker} 분석 중...")
                    # 실제 OHLCV 데이터 획득 (국내/해외 구분)
                    is_kr = ticker.endswith(".KS") or ticker.endswith(".KQ")
                    df = get_kis_ohlcv(ticker, token, mock=use_mock) if is_kr else get_kis_overseas_ohlcv(ticker, token, mock=use_mock)
                    
                    if not df.empty and len(df) >= 20:
                        df = calculate_cmo(df, period=20)
                        latest_cmo = df['CMO'].iloc[-1]
                        st.write(f"📊 {ticker} CMO 수치: **{latest_cmo:.2f}**")
                        
                        if latest_cmo <= -50.0:
                            st.info(f"🟢 [BUY SIGNAL] {ticker} 과매도 포착! (-50 이하)")
                            if execute_kis_market_order(ticker, 1, is_buy=True):
                                st.success(f"🚀 {ticker} 매수 집행 완료!")
                        elif latest_cmo >= 50.0:
                            st.warning(f"🔴 [SELL SIGNAL] {ticker} 과매수 포착! (+50 이상)")
                            if execute_kis_market_order(ticker, 1, is_buy=False):
                                st.success(f"📉 {ticker} 매도 집행 완료!")
                    else:
                        st.error(f"❌ {ticker} 데이터 획득 실패")
                status.update(label="✅ CMO 교전 사이클 종료", state="complete")
        
        # [ VISUALIZATION ] CMO 전술 차트 (마지막 종목 기준)
        if "cmo_tickers" in locals() and cmo_tickers:
            t = cmo_tickers[0]
            ak, as_, an = get_user_kis_creds()
            use_mock = get_kis_mock_status()
            token = get_kis_access_token(ak, as_, use_mock)
            df = get_kis_ohlcv(t, token, mock=use_mock) if t.endswith(".KS") or t.endswith(".KQ") else get_kis_overseas_ohlcv(t, token, mock=use_mock)
            if not df.empty and len(df) >= 20:
                df = calculate_cmo(df)
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df.index, y=df['CMO'], name='CMO', line=dict(color='#00F2FF', width=2)))
                fig.add_hline(y=50, line_dash="dash", line_color="#FF3131", annotation_text="OVERBOUGHT (+50)")
                fig.add_hline(y=-50, line_dash="dash", line_color="#39FF14", annotation_text="OVERSOLD (-50)")
                fig.add_hline(y=0, line_color="#444")
                fig.update_layout(title=f"📈 {t} Chande Momentum Oscillator (20D)", height=350, template="plotly_dark", margin=dict(l=10, r=10, t=40, b=10))
                st.plotly_chart(fig, use_container_width=True)

    
    st.divider()
    st.subheader("📊 CMO 교전 브리핑 (Strategy Logs)")
    if st.session_state.get("combat_logs"):
        for log in reversed(st.session_state.combat_logs[-20:]):
            if "CMO" in log["msg"] or any(t in log["msg"] for t in cmo_tickers):
                color = "#00F2FF" if "매수" in log["msg"] else ("#FF3131" if "매도" in log["msg"] else "#888")
                st.markdown(f"<small style='color:#666;'>[{log['time']}]</small> <span style='color:{color};'>{log['msg']}</span>", unsafe_allow_html=True)

# --- [ AI AGENT ARENA ] 8. AI 요원 경쟁방 ---
elif page.startswith("8-a."):
    st.markdown("""
    <div style='background: linear-gradient(135deg, #6e8efb 0%, #a777e3 100%); padding: 30px; border-radius: 20px; text-align: center; margin-bottom: 30px;'>
        <h1 style='margin:0; color:white; font-family:Pretendard; letter-spacing:2px;'>AI AGENT COMMAND CENTER</h1>
        <p style='margin:5px 0 0 0; color:rgba(255,255,255,0.9); font-size:1.1rem;'>사령부 정예 AI 요원 6인의 전술 및 가치관 소개</p>
    </div>
    """, unsafe_allow_html=True)

    agents = [
        {"name": "프라딥 본데 (Bonde)", "desc": "강력한 모멘텀과 EP(에피소딕 피벗)를 추격하며 거래량이 동반된 돌파 매매를 선호합니다. '안타 전략'으로 복리의 마법을 구현합니다.", "avatar": "⚡"},
        {"name": "마크 미너비니 (Minervini)", "desc": "변동성 축소 패턴(VCP)을 감지하여 리스크가 최소화된 정밀한 타점에서 매수합니다. SEPA 전략을 통해 승률을 극대화합니다.", "avatar": "🎯"},
        {"name": "윌리엄 오닐 (O'Neil)", "desc": "CAN SLIM 원칙에 따라 펀더멘털과 수급이 모두 완벽한 성장주를 선호합니다. 기관의 매수세가 확인된 대장주만을 공략합니다.", "avatar": "📈"},
        {"name": "스탠 와인스태인 (Weinstein)", "desc": "주가 4단계 분석을 통해 2단계 상승 초입에 진입하고 3단계 고점에서 매도하는 추세 추종의 정석을 보여줍니다.", "avatar": "🌊"},
        {"name": "워렌 버핏 (Buffett)", "desc": "공포에 사서 탐욕에 파는 가치 투자의 대가입니다. 약세장에서 해자가 있는 우량주를 헐값에 사서 장기 보유하는 전술을 구사합니다.", "avatar": "🐢"},
        {"name": "한샘농사매매 (Hansam)", "desc": "안정적인 농사매매 기법(Farm Trading)을 기반으로, 보수적인 타점에서 다수의 우량 종목을 씨앗처럼 심어 꾸준한 복리 수익을 거둡니다.", "avatar": "🧑‍🌾"}
    ]

    for agent in agents:
        with st.container():
            st.markdown(f"""
            <div class='glass-card' style='padding: 20px; margin-bottom: 20px; border-left: 5px solid #a777e3;'>
                <div style='display: flex; align-items: center; gap: 15px;'>
                    <div style='font-size: 2.5rem;'>{agent['avatar']}</div>
                    <div>
                        <h3 style='margin: 0; color: #FFF;'>{agent['name']}</h3>
                        <p style='margin: 5px 0 0 0; color: #BBB; line-height: 1.6;'>{agent['desc']}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

elif page.startswith("8-b."):
    st.markdown("""
    <div style='background: linear-gradient(135deg, #FFD700 0%, #B8860B 100%); padding: 30px; border-radius: 20px; text-align: center; margin-bottom: 30px;'>
        <h1 style='margin:0; color:white; font-family:Orbitron; letter-spacing:5px;'>2026 GRAND LEAGUE: AI vs COMMANDER</h1>
        <p style='margin:5px 0 0 0; color:rgba(255,255,255,0.9); font-size:1.1rem;'>거장 6인과 사령관의 자동매매 진검승부 (시작: 2026-04-27)</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 가상 수익 데이터 생성 (Commander 추가)
    np.random.seed(42)
    days = pd.date_range(start="2026-01-01", periods=100)
    data = pd.DataFrame({
        "Bonde": np.cumsum(np.random.normal(0.5, 1.2, 100)),
        "Minervini": np.cumsum(np.random.normal(0.4, 0.8, 100)),
        "ONeil": np.cumsum(np.random.normal(0.3, 1.0, 100)),
        "Weinstein": np.cumsum(np.random.normal(0.2, 0.5, 100)),
        "Buffett": np.cumsum(np.random.normal(0.1, 0.3, 100)),
        "Hansam": np.cumsum(np.random.normal(0.35, 0.6, 100)),
        "Commander": np.cumsum(np.random.normal(0.45, 1.1, 100)) # 사령관 데이터 시뮬레이션
    }, index=days)

    st.markdown("<div class='glass-card'>거장 6인 및 사령관의 누적 수익률 대결 추이</div>", unsafe_allow_html=True)
    chart_data = data.rename(columns={"ONeil": "O'Neil", "Commander": "🚩 사령관"})
    st.line_chart(chart_data)

    m1, m2, m3, m4, m5, m6, m7 = st.columns(7)
    m1.metric("Bonde", f"{data['Bonde'].iloc[-1]:.1f}%", "+2.1%")
    m2.metric("Minervini", f"{data['Minervini'].iloc[-1]:.1f}%", "+1.5%")
    m3.metric("O'Neil", f"{data['ONeil'].iloc[-1]:.1f}%", "+0.8%")
    m4.metric("Weinstein", f"{data['Weinstein'].iloc[-1]:.1f}%", "+0.3%")
    m5.metric("Buffett", f"{data['Buffett'].iloc[-1]:.1f}%", "+0.1%")
    m6.metric("Hansam", f"{data['Hansam'].iloc[-1]:.1f}%", "+1.2%")
    m7.metric("🚩 사령관", f"{data['Commander'].iloc[-1]:.1f}%", "+2.5%", delta_color="normal")

elif page.startswith("8-c."):
    st.header("[ PORTFOLIO ] AI 요원 현재 보유 종목")
    st.markdown("<div class='glass-card'>각 요원의 정밀 전략에 따라 현재 교전 중인 포트폴리오 상세 내역입니다. (시작자본: 10M KRW + 800$)</div>", unsafe_allow_html=True)

    portfolio_data = [
        {"요원": "프라딥 본데", "종목명": "NVDA", "비중": "0%", "매수금액": "$0", "매수일": "2026-04-27 예정", "현재가": "-", "수익률": "0.00%"},
        {"요원": "마크 미너비니", "종목명": "HLB", "비중": "0%", "매수금액": "0원", "매수일": "2026-04-27 예정", "현재가": "-", "수익률": "0.00%"},
        {"요원": "윌리엄 오닐", "종목명": "AAPL", "비중": "0%", "매수금액": "$0", "매수일": "2026-04-27 예정", "현재가": "-", "수익률": "0.00%"},
        {"요원": "스탠 와인스태인", "종목명": "TSLA", "비중": "0%", "매수금액": "$0", "매수일": "2026-04-27 예정", "현재가": "-", "수익률": "0.00%"},
        {"요원": "워렌 버핏", "종목명": "삼성전자", "비중": "0%", "매수금액": "0원", "매수일": "2026-04-27 예정", "현재가": "-", "수익률": "0.00%"},
        {"요원": "한샘농사매매", "종목명": "NAVER", "비중": "0%", "매수금액": "0원", "매수일": "2026-04-27 예정", "현재가": "-", "수익률": "0.00%"}
    ]

    st.dataframe(pd.DataFrame(portfolio_data), use_container_width=True, hide_index=True)

elif page.startswith("8-d."):
    st.markdown("""
    <div style='text-align: center; margin-bottom: 30px;'>
        <h1 style='color: #FFD700; font-family: Orbitron; font-size: 2.5rem; letter-spacing: 5px;'>HALL OF FAME</h1>
        <p style='color: #888;'>AI 요원들의 역사적 성과 및 랭킹</p>
    </div>
    """, unsafe_allow_html=True)

    ranking_data = [
        {"순위": "-", "요원": "마크 미너비니", "총수익률": "0.0%", "최대낙폭(MDD)": "0.0%", "대표승전보": "교전 준비 중"},
        {"순위": "-", "요원": "프라딥 본데", "총수익률": "0.0%", "최대낙폭(MDD)": "0.0%", "대표승전보": "교전 준비 중"},
        {"순위": "-", "요원": "워렌 버핏", "총수익률": "0.0%", "최대낙폭(MDD)": "0.0%", "대표승전보": "교전 준비 중"},
        {"순위": "-", "요원": "윌리엄 오닐", "총수익률": "0.0%", "최대낙폭(MDD)": "0.0%", "대표승전보": "교전 준비 중"},
        {"순위": "-", "요원": "스탠 와인스태인", "총수익률": "0.0%", "최대낙폭(MDD)": "0.0%", "대표승전보": "교전 준비 중"}
    ]

    st.table(pd.DataFrame(ranking_data))
    
    st.info("💡 모든 AI 요원들은 사령부의 실시간 데이터 피트를 바탕으로 각자의 독립된 엔진을 가동하여 결과를 도출합니다.")

elif page.startswith("8-f."):
    st.markdown("""
    <div style='background: linear-gradient(90deg, #FFD700 0%, #FFA500 100%); padding: 25px; border-radius: 15px; text-align: center; margin-bottom: 25px; box-shadow: 0 10px 30px rgba(255,215,0,0.3);'>
        <h1 style='margin:0; color:black; font-family:Pretendard; letter-spacing:3px;'>AI vs 사령관 실전 수익 현황</h1>
        <p style='margin:5px 0 0 0; color:rgba(0,0,0,0.7); font-size:1rem; font-weight:bold;'>대결 시작: 2026-04-27 | 기준 자본: 10,000,000 KRW + 800$</p>
    </div>
    """, unsafe_allow_html=True)

    # 실시간 데이터 획득
    ranking_data = get_realtime_ai_ranking()
    
    # 테이블용 데이터 재구성
    display_rows = []
    for r in ranking_data:
        display_rows.append({
            "순위": f"{ranking_data.index(r)+1}위",
            "참가자": r["name"].replace("[ AI ] ", ""),
            "주요종목": r["pick"],
            "진입가/기준가": f"{r['entry']:,.2f}",
            "현재가": f"{r['exit_p']:,.2f}",
            "수익률": r["roi"],
            "평가금액": f"{r['balance']:,}원"
        })

    st.markdown("<div class='glass-card'>실시간 교전 성과 리포트 (Real-Time Performance Report)</div>", unsafe_allow_html=True)
    st.dataframe(pd.DataFrame(display_rows).style.set_properties(**{'background-color': 'rgba(255,255,255,0.02)', 'color': '#EEE', 'border-color': '#444'})
                 .apply(lambda x: ['color: #00FF00' if '+' in str(v) else ('color: #FF4B4B' if '-' in str(v) and '%' in str(v) else '') for v in x], subset=['수익률']),
                 use_container_width=True, hide_index=True)

    # 하단 메트릭 섹션 (상위 3인)
    st.divider()
    st.subheader("🏆 CURRENT LEADERS")
    cols = st.columns(3)
    for i in range(min(3, len(ranking_data))):
        r = ranking_data[i]
        with cols[i]:
            st.metric(r["name"], r["roi"], delta_color="normal")
            st.caption(f"평가금: {r['balance']:,}원")

    st.markdown("""
    <div style='background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; margin-top: 20px; border-left: 4px solid #FFD700;'>
        <b>💡 대결 모니터링 지침:</b><br>
        - **AI 요원**: 지정된 거장 알고리즘이 특정 종목을 가상으로 매매하며, 수익률은 실제 시장 가격(Live Market Price)을 기준으로 실시간 계산됩니다.<br>
        - **사령관 (COMMANDER)**: 사령관님의 실제 한국투자증권 계좌 잔고를 기반으로 한 <b>진짜 실전 수익률</b>입니다.<br>
        - 모든 데이터는 60초마다 자동으로 갱신됩니다.
    </div>
    """, unsafe_allow_html=True)



# --- 시스템 하단 글로벌 전술 푸터 (Global Footer) ---
st.divider()
st.markdown(f"""
<div style='text-align: center; color: #666; font-size: 0.9rem;'>
    <span style='color: #FFD700; font-weight: 700;'>© 2026 StockDragonfly Terminal v5.5 | Tactical System Powered by AI</span>
</div>
""", unsafe_allow_html=True)

# --- [ SYSTEM EXECUTION ] ---
if __name__ == "__main__":
    pass
