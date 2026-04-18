# 작업 일자: 2026-04-18 | 작업 시간: 16:33
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import os
import json
import pytz
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots


# --- 전역 변수 및 유틸리티 함수 ---
ticker_map = {
    "NVDA": "엔비디아", "TSLA": "테슬라", "AAPL": "애플", "MSFT": "마이크로소프트", "AMD": "AMD",
    "SMCI": "슈퍼마이크로", "CELH": "셀시어스", "PLTR": "팔란티어", "HOOD": "로빈후드", "CRWD": "크라우드스트라이크",
    "005930.KS": "삼성전자", "000660.KS": "SK하이닉스", "196170.KQ": "알테오젠", "042700.KS": "한미반도체",
    "007660.KS": "이수페타시스", "003230.KS": "삼양식품", "015860.KS": "일진홀딩스", "322000.KS": "씨앤씨인터",
    "035420.KS": "NAVER", "035720.KS": "카카오", "005380.KS": "현대차", "000270.KS": "기아",
    "068270.KS": "셀트리온", "105560.KS": "KB금융", "055550.KS": "신한지주", "000810.KS": "삼성화재",
    "028260.KS": "삼성물산", "012330.KS": "현대모비스", "051910.KS": "LG화학", "032830.KS": "삼성생명"
}

name_to_ticker = {v: k for k, v in ticker_map.items()}

def resolve_ticker(input_val):
    input_val = input_val.strip()
    if input_val in name_to_ticker:
        return name_to_ticker[input_val]
    for name, ticker in name_to_ticker.items():
        if input_val in name:
            return ticker
    return input_val

@st.cache_data(ttl=300)
def get_market_sentiment():
    sample_tickers = ["SPY", "QQQ", "IWM", "NVDA", "AAPL", "MSFT", "TSLA", "AMD", "005930.KS", "000660.KS", "196170.KQ", "042700.KS", "003230.KS"]
    try:
        data = yf.download(sample_tickers, period="10d", progress=False)['Close']
        if isinstance(data.columns, pd.MultiIndex): data.columns = data.columns.get_level_values(1)
        
        today_ret = (data.iloc[-1] / data.iloc[-2] - 1) * 100
        gainers_4 = (today_ret >= 4.0).sum()
        losers_4 = (today_ret <= -4.0).sum()
        
        return_5d = (data.iloc[-1] / data.iloc[-6] - 1) * 100
        rockets = (return_5d >= 20.0).sum()
        
        is_uptrend = (data.iloc[-1] > data.rolling(5).mean().iloc[-1]).sum()
        breadth_ratio = (is_uptrend / len(sample_tickers)) * 100
        
        score = 0
        if gainers_4 > losers_4: score += 30
        if rockets >= 1: score += 30
        if breadth_ratio >= 60: score += 40
        
        return score, gainers_4, losers_4, rockets, breadth_ratio
    except:
        return 50, 0, 0, 0, 50


# --- 사용자 DB 관리 함수 ---
USER_DB_FILE = "users_db.json"

def load_users():
    if not os.path.exists(USER_DB_FILE):
        # 초기 기본 계정 설정 (cntfed는 자동 승인 상태)
        initial_users = {
            "cntfed": {
                "password": "cntfed", 
                "exp": "Master", 
                "profit": "N/A", 
                "status": "approved"
            }
        }
        with open(USER_DB_FILE, "w") as f:
            json.dump(initial_users, f)
        return initial_users
    with open(USER_DB_FILE, "r") as f:
        return json.load(f)

def save_user(user_id, password, exp, profit):
    users = load_users()
    if user_id in users:
        return False, "이미 존재하는 아이디입니다."
    # 신규 회원은 무조건 'pending' 상태로 저장
    users[user_id] = {
        "password": password,
        "exp": exp,
        "profit": profit,
        "status": "pending"
    }
    with open(USER_DB_FILE, "w") as f:
        json.dump(users, f)
    return True, "가입 신청 완료! 관리자의 승인 후 로그인이 가능합니다."

def update_user_status(user_id, status):
    users = load_users()
    if user_id in users:
        users[user_id]["status"] = status
        with open(USER_DB_FILE, "w") as f:
            json.dump(users, f)
        return True
    return False


# --- 메시지 DB 관리 함수 ---
MESSAGE_DB_FILE = "messages_db.json"

def load_messages():
    if not os.path.exists(MESSAGE_DB_FILE):
        return []
    try:
        with open(MESSAGE_DB_FILE, "r", encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def save_message(user_id, content):
    messages = load_messages()
    new_msg = {
        "user": user_id,
        "content": content,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    messages.append(new_msg)
    # 최근 100개만 유지
    messages = messages[-100:]
    with open(MESSAGE_DB_FILE, "w", encoding='utf-8') as f:
        json.dump(messages, f, ensure_ascii=False)
    return True


# --- 관심종목 DB 관리 함수 ---
WATCHLIST_FILE = "watchlist_db.json"

def load_watchlist(user_id):
    if not os.path.exists(WATCHLIST_FILE):
        return []
    try:
        with open(WATCHLIST_FILE, "r") as f:
            data = json.load(f)
            return data.get(user_id, [])
    except:
        return []

def save_watchlist(user_id, ticker_list):
    data = {}
    if os.path.exists(WATCHLIST_FILE):
        try:
            with open(WATCHLIST_FILE, "r") as f:
                data = json.load(f)
        except:
            data = {}
    
    data[user_id] = list(set(ticker_list)) # 중복 제거
    with open(WATCHLIST_FILE, "w") as f:
        json.dump(data, f)
    return True


# 0. 페이지 설정
st.set_page_config(page_title="Bonde-Turtle Terminal", page_icon="🐢", layout="wide")

# 1. 암호 보안 설정 (Persistent Auth System)
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if st.session_state["password_correct"]:
        return True

    # 로그인/회원가입 화면 UI
    st.markdown("<div style='text-align: center; padding: 40px 0;'>", unsafe_allow_html=True)
    st.markdown("<h1 style='color: #FFD700; text-shadow: 0 0 15px rgba(255, 215, 0, 0.4);'>🏛️ ANTI-GRAVITY TERMINAL</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #888;'>Authorized Personnel Only</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab_login, tab_signup = st.tabs(["🔐 LOGIN", "👤 SIGN UP"])
        
        with tab_login:
            user_id = st.text_input("USER ID", placeholder="아이디를 입력하세요", key="login_id")
            password = st.text_input("PASSWORD", type="password", placeholder="비밀번호를 입력하세요", key="login_pw")
            
            if st.button("LOGIN ACCESS", use_container_width=True):
                users = load_users()
                if user_id in users and users[user_id]["password"] == password:
                    if users[user_id]["status"] == "approved":
                        st.session_state["password_correct"] = True
                        st.session_state["current_user"] = user_id
                        st.rerun()
                    else:
                        st.warning("⏳ 승인 대기 중입니다. 관리자에게 문의하세요.")
                else:
                    st.error("❌ Invalid ID or Password.")
        
        with tab_signup:
            new_id = st.text_input("NEW ID", placeholder="사용할 아이디", key="reg_id")
            new_pw = st.text_input("NEW PASSWORD", type="password", placeholder="비밀번호", key="reg_pw")
            new_exp = st.selectbox("주식 경력", ["1년 미만", "1~3년", "3~5년", "5~10년", "10년 이상"], key="reg_exp")
            new_profit = st.text_input("평균/목표 수익률 (%)", placeholder="예: 25", key="reg_profit")
            
            if st.button("가입 신청하기", use_container_width=True):
                if not new_id or not new_pw or not new_profit:
                    st.warning("모든 정보를 입력해주세요.")
                else:
                    success, msg = save_user(new_id, new_pw, new_exp, new_profit)
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)
                        
    st.markdown("</div>", unsafe_allow_html=True)
    return False

if check_password():
    # 사이드바 레이아웃 및 페이지 네비게이션
    st.sidebar.markdown("<h2 style='color: #FFFF00;'>🐢 Bonde-Turtle</h2>", unsafe_allow_html=True)
    st.sidebar.title("💎 Master Menu")

    # 실시간 시간 표시 (한국 & 미국)
    kst = pytz.timezone('Asia/Seoul')
    est = pytz.timezone('US/Eastern')
    now_kst = datetime.now(kst)
    now_est = datetime.now(est)

    st.sidebar.markdown(f"""
        <div style='background-color: #111111; padding: 15px; border-radius: 10px; border: 1px solid #FFFF00; margin-bottom: 20px; box-shadow: 0 0 15px rgba(255, 255, 0, 0.2);'>
            <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;'>
                <span style='font-size: 12px; color: #FFFF00;'>🇰🇷 KOREA (KST)</span>
                <span style='font-size: 10px; color: #4ade80;'>LIVE</span>
            </div>
            <div style='font-size: 18px; color: #FFFF00; font-family: monospace; font-weight: bold;'>{now_kst.strftime('%H:%M:%S')}</div>
            <div style='font-size: 12px; color: #FFFF00;'>{now_kst.strftime('%Y-%m-%d')}</div>
            <hr style='margin: 10px 0; border: none; border-top: 1px solid #FFFF00;'>
            <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;'>
                <span style='font-size: 12px; color: #FFFF00;'>🇺🇸 USA (ET)</span>
                <span style='font-size: 10px; color: #4ade80;'>MARKET</span>
            </div>
            <div style='font-size: 18px; color: #FFFF00; font-family: monospace; font-weight: bold;'>{now_est.strftime('%H:%M:%S')}</div>
            <div style='font-size: 12px; color: #FFFF00;'>{now_est.strftime('%Y-%m-%d')}</div>
        </div>
    """, unsafe_allow_html=True)

    # --- BGM Player Section (Moved outside of f-string) ---
    st.sidebar.markdown("""
        <div style='background-color: #111111; padding: 15px 15px 5px 15px; border-radius: 10px; border: 1px solid #555; margin-bottom: 5px;'>
            <p style='font-size: 11px; color: #4ade80; margin: 0;'>🎵 BGM SELECTOR</p>
        </div>
    """, unsafe_allow_html=True)
    
    bgm_files = {
        "OFF": None,
        "나의 아저씨": "나의 아저씨 [ BGM ].mp3",
        "싱그러운": "싱그러운.mp3",
        "You Raise Me Up": "You Raise Me Up  Lyrics.mp3",
        "귀여운": "귀여운.mp3",
        "설렘 Piano": "설렘Piano.mp3",
        "기분좋은": "기분좋은.mp3"
    }
    
    selected_bgm_name = st.sidebar.selectbox("음악 선택", list(bgm_files.keys()), key="bgm_selector", label_visibility="collapsed")
    selected_file = bgm_files[selected_bgm_name]
    
    if selected_file:
        import base64
        base_dir = os.path.dirname(os.path.abspath(__file__)) if "__file__" in locals() else os.getcwd()
        full_path = os.path.join(base_dir, selected_file)
        
        if os.path.exists(full_path):
            with open(full_path, "rb") as f:
                data = f.read()
                b64 = base64.b64encode(data).decode()
            
            # 볼륨 조절 슬라이더 추가
            vol = st.sidebar.slider("🔊 볼륨 조절", 0.0, 1.0, 0.5, 0.05)
            
            # HTML5 오디오 태그와 볼륨 컨트롤 스크립트
            audio_html = f"""
                <audio id="bgm-player" autoplay loop>
                    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                </audio>
                <script>
                    var audio = window.parent.document.getElementById("bgm-player");
                    if (audio) {{
                        audio.volume = {vol};
                    }}
                </script>
            """
            with st.sidebar:
                st.components.v1.html(audio_html, height=0)
            st.sidebar.caption(f"Currently Playing: {selected_bgm_name} (Vol: {int(vol*100)}%)")
        else:
            st.sidebar.error(f"파일을 찾을 수 없습니다: {selected_file}")

    # Market Sentiment Gauge (Dynamic)
    score, _, _, _, _ = get_market_sentiment()
    gauge_color = "#4ade80" if score >= 70 else "#fbbf24" if score >= 40 else "#ff4b4b"
    
    def status_text_map(s):
        if s >= 70: return "Greedy"
        if s >= 40: return "Neutral"
        return "Fearful"

    st.sidebar.markdown(f"""
        <div style='background-color: #111111; padding: 15px; border-radius: 10px; border: 1px solid {gauge_color}; margin-top: 10px; margin-bottom: 20px;'>
            <div style='font-size: 12px; color: {gauge_color}; font-weight: bold; margin-bottom: 10px;'>🔥 MARKET FEAR & GREED</div>
            <div style='height: 8px; width: 100%; background: #333; border-radius: 4px; overflow: hidden;'>
                <div style='height: 100%; width: {score}%; background: {gauge_color};'></div>
            </div>
            <div style='display: flex; justify-content: space-between; margin-top: 5px;'>
                <span style='font-size: 10px; color: #ff4b4b;'>Extreme Fear</span>
                <span style='font-size: 11px; color: {gauge_color}; font-weight: bold;'>{score} ({status_text_map(score)})</span>
                <span style='font-size: 10px; color: #4ade80;'>Extreme Greed</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # --- Watchlist Panel ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("⭐ WATCHLIST PANEL")
    current_user = st.session_state.get("current_user", "Guest")
    if 'user_watchlist' not in st.session_state:
        st.session_state['user_watchlist'] = load_watchlist(current_user)
    
    with st.sidebar.expander("➕ 종목 추가", expanded=False):
        new_ticker = st.text_input("Ticker (예: AAPL, 005930.KS)", key="add_watchlist_input").upper()
        if st.button("ADD"):
            if new_ticker and new_ticker not in st.session_state['user_watchlist']:
                st.session_state['user_watchlist'].append(new_ticker)
                save_watchlist(current_user, st.session_state['user_watchlist'])
                st.success(f"{new_ticker} Added!")
                st.rerun()

    if st.session_state['user_watchlist']:
        for t in st.session_state['user_watchlist']:
            cols = st.sidebar.columns([3, 1])
            # 종목명이 있으면 이름으로, 없으면 티커로 표시
            disp_name = ticker_map.get(t, t)
            cols[0].write(f"🔹 {disp_name}")
            if cols[1].button("X", key=f"del_{t}"):
                st.session_state['user_watchlist'].remove(t)
                save_watchlist(current_user, st.session_state['user_watchlist'])
                st.rerun()
    else:
        st.sidebar.info("추가된 종목이 없습니다.")

    menu_options = [
        "1. 🎯 주도주 타점 스캐너", 
        "2. 💬 안티그래비티 대화방", 
        "3. 💎 프로 분석 리포트", 
        "4. 📈 실시간 분석 차트", 
        "5. 🧮 리스크 관리 계산기", 
        "6. 📰 실시간 뉴스 피드", 
        "7. 📊 본데 주식 50선", 
        "8. 💎 마스터 클래스"
    ]
    if st.session_state.get("current_user") == "cntfed":
        menu_options.append("9. 👑 관리자 승인 센터")
        
    page = st.sidebar.radio("Go to", menu_options)

    # 공통 스타일 설정 (전체 노란색 테마)
    st.markdown("""
        <style>
        /* 전체 배경 */
        .main, .stApp, [data-testid="stSidebar"], [data-testid="stHeader"] { 
            background-color: #000000 !important; 
        }
        
        /* 일반 텍스트 흰색 설정 (가독성 최우선) */
        .stMarkdown, p, li, label {
            color: #FFFFFF !important;
            font-family: 'Courier New', Courier, monospace !important;
            font-weight: 500 !important;
        }

        /* Span이나 Div에 과도한 스타일 부여 방지 (아이콘 깨짐 방지) */
        span[data-testid="stHeaderActionElements"], .stExpander p {
            color: inherit !important;
        }

        /* 중요 정보 노란색 강조 */
        h1, h2, h3, h4, h5, h6, .accent-text {
            color: #FFFF00 !important;
            text-shadow: 0 0 5px rgba(255, 255, 0, 0.3) !important;
        }
        
        /* 메트릭(숫자 정보) 흰색으로 선명하게 */
        [data-testid="stMetricValue"] {
            color: #FFFFFF !important;
            font-size: 2rem !important;
            font-weight: 800 !important;
        }
        [data-testid="stMetricLabel"] {
            color: #AAAAAA !important; /* 라벨은 약간 연하게 */
        }

        /* 입력 위젯 가독성 확보 (배경색과 텍스트 대비) */
        input, select, textarea, [data-baseweb="select"] * {
            color: #000000 !important;
            background-color: #FFFFFF !important;
        }

        /* 표(Table) 가독성 업그레이드 */
        th {
            color: #FFFF00 !important; /* 헤더는 노란색 */
            background-color: #111111 !important;
            font-weight: bold !important;
            border: 1px solid #333 !important;
        }
        td {
            color: #FFFFFF !important; /* 내용은 흰색 */
            border: 1px solid #222 !important;
        }
        
        /* 버튼 스타일 */
        .stButton>button {
            background-color: #000000 !important;
            color: #FFFF00 !important;
            border: 2px solid #FFFF00 !important;
        }
        .stButton>button:hover {
            background-color: #FFFF00 !important;
            color: #000000 !important;
        }

        /* 탭 스타일 */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
        }
        .stTabs [data-baseweb="tab"] {
            color: #FFFF00 !important;
            border: 1px solid #FFFF00 !important;
            padding: 5px 15px !important;
        }

        /* 데이터프레임 */
        [data-testid="stTable"], [data-testid="stDataFrame"] {
            border: 1px solid #FFFF00 !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # --- 페이지 1: 주도주 타점 스캐너 ---
    if page.startswith("1."):
        st.markdown("<h1 style='white-space: nowrap;'>🎯 Bonde-Turtle Terminal</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='color: #FFFF00; opacity: 0.9;'>✨ 실시간 시장 데이터 기반 주도주 포착</h3>", unsafe_allow_html=True)
        
        # --- [STOCKBEE PROTOCOL] Phase 1: Market Monitor Engine ---
        def run_market_monitor():
            score, gainers_4, losers_4, rockets, breadth_ratio = get_market_sentiment()
            
            status = "Risk-ON 🟢" if score >= 70 else "Neutral 🟡" if score >= 40 else "Risk-OFF 🔴"
            color = "#4ade80" if score >= 70 else "#fbbf24" if score >= 40 else "#ff4b4b"
            desc = "돌파 매매 최적기! 공격적 진입 가능" if score >= 70 else "선별적 매매 필요. 비중 조절" if score >= 40 else "폭우 주의보! 현금 비중 극대화 권고"
            
            st.markdown(f"""
                <div style='background: linear-gradient(90deg, #111, #222); padding: 20px; border-radius: 15px; border-left: 10px solid {color}; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.5);'>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <div>
                            <h4 style='margin:0; color: #888; font-size: 14px;'>SITUATIONAL AWARENESS</h4>
                            <h1 style='margin:0; color: {color}; font-size: 32px;'>{status}</h1>
                        </div>
                        <div style='text-align: right;'>
                            <p style='margin:0; color: #fff; font-weight: bold;'>{desc}</p>
                            <p style='margin:0; color: #555; font-size: 11px;'>Breadth: {breadth_ratio:.0f}% | 4% Gainers: {gainers_4} | Rockets: {rockets}</p>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        # --- 메인 대시보드 출력 시작 ---
        run_market_monitor()
        
        @st.cache_data(ttl=600)
        def get_scanner_data(tickers_tuple):
            tickers = list(tickers_tuple)
            results = []
            for ticker in tickers:
                try:
                    stock = yf.Ticker(ticker)
                    hist = stock.history(period="1y")
                    if len(hist) < 2: 
                        continue
                    
                    current_price = hist['Close'].iloc[-1]
                    prev_close = hist['Close'].iloc[-2]
                    change_pct = ((current_price - prev_close) / prev_close) * 100
                    
                    avg_volume = hist['Volume'].iloc[-11:-1].mean() if len(hist) > 10 else hist['Volume'].iloc[:-1].mean()
                    current_volume = hist['Volume'].iloc[-1]
                    vol_ratio = current_volume / avg_volume if avg_volume > 0 else 0
                    
                    high_52w = hist['High'].max()
                    dist_from_high = ((current_price - high_52w) / high_52w) * 100
                    is_kr = ticker.endswith(".KS") or ticker.endswith(".KQ")
                    
                    results.append({
                        "Ticker": ticker,
                        "Name": ticker_map.get(ticker, ticker), # 이름 매핑 필수로 적용
                        "Price": f"{int(current_price):,}원" if is_kr else f"${current_price:.2f}",
                        "Change": f"{change_pct:+.2f}%",
                        "Vol Ratio": f"{vol_ratio:.2f}x",
                        "Position": "신고가" if dist_from_high > -1 else f"{dist_from_high:.1f}%",
                        "_change_val": change_pct,
                        "_vol_val": vol_ratio
                    })
                except Exception as e:
                    continue
            return pd.DataFrame(results)

        us_tickers = ["NVDA", "TSLA", "AAPL", "MSFT", "AMD", "SMCI", "CELH", "PLTR", "HOOD", "CRWD"]
        kr_tickers = ["005930.KS", "000660.KS", "196170.KQ", "042700.KS", "007660.KS", "003230.KS", "015860.KS", "322000.KS"]

        col_scan1, col_scan2 = st.columns([2, 1])
        with col_scan1:
            if st.button("🔍 실시간 주식 스캔 시작"):
                with st.spinner("시장을 분석 중입니다 (yfinance 연동)..."):
                    # 기본 리스트 + 사용자 관심종목 통합
                    user_wl = st.session_state.get('user_watchlist', [])
                    all_tickers = tuple(list(set(us_tickers + kr_tickers + user_wl)))
                    
                    df_scan = get_scanner_data(all_tickers)
                    st.session_state['scanner_df'] = df_scan
                    if df_scan.empty:
                        st.warning("⚠️ 시장 데이터를 불러오지 못했습니다. 잠시 후 다시 시도하거나 네트워크 연결을 확인하세요.")
                    else:
                        st.success(f"✅ 분석 완료! {len(df_scan)}개의 주도주 데이터를 불러왔습니다.")
        with col_scan2:
            st.info("💡 종목명을 클릭하면 차트 분석(준비중)이 가능합니다.")

        st.markdown("---")
        
        market_score = 0
        if 'scanner_df' in st.session_state:
            df = st.session_state['scanner_df']
            if not df.empty and 'Position' in df.columns:
                high_count = len(df[df['Position'] == "신고가"])
                total_count = len(df)
                market_score = (high_count / total_count) * 100 if total_count > 0 else 0
        
        signal_color = "🟢" if market_score > 30 else "🟡" if market_score > 10 else "🔴"
        signal_text = "위험 회피 해제 (공격적 매수)" if market_score > 30 else "관망 및 선별 매매" if market_score > 10 else "위험 관리 (현금 비중 확대)"
        
        col1, col2 = st.columns([1, 4])
        with col1:
            st.markdown(f"<div style='text-align:center;'><h3 style='margin-bottom:0;'>🚦 신호</h3><div style='font-size:60px; margin-top:-10px;'>{signal_color}</div></div>", unsafe_allow_html=True)
        with col2:
            st.write(f"**현재 시장:** {signal_text}")
            st.write(f"신고가 비율: **{market_score:.1f}%**")
            if signal_color == "🟢":
                st.success("👉 **본데의 디렉션:** 돌파 매매(MB)와 에피소딕 피봇(EP)을 가장 공격적으로 노려야 할 시기입니다.")
            elif signal_color == "🟡":
                st.warning("👉 **본데의 디렉션:** 시장 주도주들만 선별적으로 매매하며 비중을 조절하십시오.")
            else:
                st.error("👉 **본데의 디렉션:** 무리한 진입보다는 현금을 확보하고 다음 기회를 기다리십시오.")
        st.markdown("---")

        tab1, tab2, tab3, tab4 = st.tabs(["🔥 1. 모멘텀 버스트 (MB)", "🚀 2. 실적 홈런주 (EP)", "🤫 3. 조용한 눌림목 (Anticipation)", "📈 상세 기술적 분석"])

        if 'selected_ticker' not in st.session_state:
            st.session_state['selected_ticker'] = None

        def render_ticker_report(selected_ticker):
            if not selected_ticker:
                return
            
            selected_name = ticker_map.get(selected_ticker, selected_ticker)
            st.markdown("---")
            st.write(f"### 📊 {selected_name} ({selected_ticker}) 상세 분석 보고서")
            
            try:
                with st.spinner("데이터를 분석 중입니다..."):
                    data = yf.download(selected_ticker, period="1y", progress=False)
                    if data.empty: return
                        
                    if isinstance(data.columns, pd.MultiIndex):
                        data.columns = data.columns.get_level_values(0)
                    
                    data['MA50'] = data['Close'].rolling(window=50).mean()
                    data['MA150'] = data['Close'].rolling(window=150).mean()
                    data['MA200'] = data['Close'].rolling(window=200).mean()
                    
                    curr_price = float(data['Close'].iloc[-1])
                    ma150_curr = float(data['MA150'].iloc[-1])
                    ma150_prev = float(data['MA150'].iloc[-20])
                    
                    if curr_price > ma150_curr and ma150_curr > ma150_prev:
                        stage, stage_color = "2단계 (상승)", "#00FF00"
                    elif curr_price < ma150_curr and ma150_curr < ma150_prev:
                        stage, stage_color = "4단계 (하락)", "#FF0000"
                    elif curr_price > ma150_curr and ma150_curr <= ma150_prev:
                        stage, stage_color = "1단계 (바닥권)", "#FFFF00"
                    else:
                        stage, stage_color = "3단계 (천정권)", "#FFA500"

                    rs_score = ((curr_price - data['Close'].iloc[-126]) / data['Close'].iloc[-126]) * 100 if len(data) > 126 else 0
                    stock_obj = yf.Ticker(selected_ticker)
                    info = stock_obj.info
                    roe = info.get('returnOnEquity', 0) * 100
                    
                    bonde_score = 0
                    if curr_price >= data['High'].max() * 0.97: bonde_score += 40
                    if rs_score > 25: bonde_score += 30
                    if roe > 15: bonde_score += 30
                    
                    is_buy = bonde_score >= 70 and "2단계" in stage
                    final_signal = "매수 적극 권장 (BUY)" if is_buy else "관망 및 대기 (HOLD)" if bonde_score >= 40 else "매수 금지 (AVOID)"
                    signal_icon = "🟢" if is_buy else "🟡" if bonde_score >= 40 else "🔴"
                    
                    is_kr = selected_ticker.endswith(".KS") or selected_ticker.endswith(".KQ")
                    entry_p = f"{int(curr_price):,}원" if is_kr else f"${curr_price:.2f}"
                    stop_p = f"{int(curr_price * 0.93):,}원" if is_kr else f"${(curr_price * 0.93):.2f}"
                    target_p = f"{int(curr_price * 1.25):,}원" if is_kr else f"${(curr_price * 1.25):.2f}"
                    
                    st.markdown(f"""
                        <div style='background-color: #111111; padding: 20px; border-radius: 15px; border: 2px solid {stage_color}; margin-bottom: 25px;'>
                            <div style='display: flex; justify-content: space-between; align-items: center;'>
                                <div>
                                    <span style='font-size: 14px; color: #8a94a6;'>FINAL SIGNAL</span>
                                    <h2 style='margin: 0; color: {stage_color};'>{signal_icon} {final_signal}</h2>
                                </div>
                                <div style='text-align: right;'>
                                    <span style='font-size: 14px; color: #8a94a6;'>BONDE SCORE</span>
                                    <h2 style='margin: 0; color: #FFFF00;'>{bonde_score} / 100</h2>
                                </div>
                            </div>
                            <hr style='border: 0.5px solid #333; margin: 15px 0;'>
                            <div style='display: flex; justify-content: space-around; text-align: center;'>
                                <div><span style='color:#8a94a6;'>매수가</span><br><b style='font-size:18px;'>{entry_p}</b></div>
                                <div><span style='color:#FF4B4B;'>손절가</span><br><b style='font-size:18px;'>{stop_p}</b></div>
                                <div><span style='color:#4ADE80;'>목표가</span><br><b style='font-size:18px;'>{target_p}</b></div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("ROE (수익성)", f"{roe:.1f}%")
                    c2.metric("RS (상대강도)", f"{rs_score:.1f}")
                    c3.metric("Weinstein 단계", stage)
                    c4.metric("52주 최고가 대비", f"{((curr_price - data['High'].max())/data['High'].max()*100):.1f}%")

                    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_width=[0.3, 0.7])
                    fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name='Price'), row=1, col=1)
                    fig.add_trace(go.Scatter(x=data.index, y=data['MA50'], line=dict(color='yellow', width=1), name='MA50'), row=1, col=1)
                    fig.add_trace(go.Scatter(x=data.index, y=data['MA150'], line=dict(color='cyan', width=1.5), name='MA150'), row=1, col=1)
                    fig.add_trace(go.Scatter(x=data.index, y=data['MA200'], line=dict(color='orange', width=1), name='MA200'), row=1, col=1)
                    
                    delta = data['Close'].diff()
                    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                    rs_val = gain / loss
                    data['RSI'] = 100 - (100 / (1+rs_val))
                    fig.add_trace(go.Scatter(x=data.index, y=data['RSI'], line=dict(color='magenta', width=1), name='RSI'), row=2, col=1)
                    fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
                    fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
                    
                    fig.update_layout(template='plotly_dark', height=500, showlegend=True, xaxis_rangeslider_visible=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig, use_container_width=True)
                    
            except Exception as e: pass

        with tab1:
            st.subheader("🔥 모멘텀 버스트 (Momentum Burst) 실시간")
            if 'scanner_df' in st.session_state:
                mb_df = st.session_state['scanner_df'][st.session_state['scanner_df']['_change_val'] >= 4].sort_values(by='_change_val', ascending=False)
                if not mb_df.empty:
                    st.dataframe(mb_df[['Name', 'Price', 'Change', 'Vol Ratio', 'Position']], use_container_width=True, hide_index=True)
                    st.session_state['selected_ticker'] = st.selectbox("상세 분석할 종목 선택 (MB)", mb_df['Ticker'].tolist(), format_func=lambda x: ticker_map.get(x, x))
                    render_ticker_report(st.session_state['selected_ticker'])

        with tab2:
            st.subheader("🚀 실시간 에피소딕 피봇 (EP) 탐색")
            if 'scanner_df' in st.session_state:
                ep_df = st.session_state['scanner_df'][st.session_state['scanner_df']['_vol_val'] >= 2.5].sort_values(by='_vol_val', ascending=False)
                if not ep_df.empty:
                    st.dataframe(ep_df[['Name', 'Price', 'Change', 'Vol Ratio', 'Position']], use_container_width=True, hide_index=True)
                    st.session_state['selected_ticker'] = st.selectbox("상세 분석할 종목 선택 (EP)", ep_df['Ticker'].tolist(), format_func=lambda x: ticker_map.get(x, x))
                    render_ticker_report(st.session_state['selected_ticker'])

        with tab3:
            st.subheader("🤫 조용한 눌림목 (Anticipation)")
            if 'scanner_df' in st.session_state:
                df = st.session_state['scanner_df']
                def parse_pos(x):
                    try: return 0 if x == "신고가" else float(x.replace('%', ''))
                    except: return -99
                df['_pos_val'] = df['Position'].apply(parse_pos)
                anti_df = df[(df['_change_val'].abs() <= 1.5) & (df['_vol_val'] <= 1.0) & (df['_pos_val'] >= -15.0)].sort_values(by='_vol_val', ascending=True)
                if not anti_df.empty:
                    st.dataframe(anti_df[['Name', 'Price', 'Change', 'Vol Ratio', 'Position']], use_container_width=True, hide_index=True)
                    st.session_state['selected_ticker'] = st.selectbox("상세 분석할 종목 선택 (Anti)", anti_df['Ticker'].tolist(), format_func=lambda x: ticker_map.get(x, x))
                    render_ticker_report(st.session_state['selected_ticker'])

        with tab4:
            st.markdown("---")
            st.subheader("🔥 Thematic Momentum Heatmap")
            st.write("모멘텀(TI65)과 수급(Volume)이 집중된 섹터와 주도주를 한눈에 파악합니다.")
            
            try:
                heatmap_tickers = ["NVDA", "AMD", "AVGO", "SMCI", "TSLA", "AAPL", "MSFT", "GOOGL", "META", "CRWD", "PLTR", "005930.KS", "000660.KS", "196170.KQ", "042700.KS", "003230.KS", "007660.KS", "322000.KS"]
                map_data = []
                for t in heatmap_tickers:
                    sk = yf.Ticker(t)
                    h = sk.history(period="60d")
                    if h.empty: continue
                    sector = sk.info.get('sector', 'Others')
                    disp_name = ticker_map.get(t, t)
                    last_vol = h['Volume'].iloc[-1]; avg_vol = h['Volume'].mean()
                    perf_2m = (h['Close'].iloc[-1] / h['Close'].iloc[0] - 1) * 100
                    ti65_val = (h['Close'].rolling(7).mean().iloc[-1] / h['Close'].rolling(60).mean().iloc[-1])
                    label = f"{disp_name}<br>{perf_2m:.1f}%"
                    map_data.append({"Ticker": t, "Name": disp_name, "Sector": sector, "Performance": perf_2m, "Volume_Strength": last_vol / avg_vol, "Label": label, "TI65": ti65_val})
                df_map = pd.DataFrame(map_data)
                fig_map = px.treemap(df_map, path=[px.Constant("Market"), 'Sector', 'Name'], values='Volume_Strength', color='Performance', color_continuous_scale='RdYlGn', color_continuous_midpoint=0, hover_data=['Performance', 'TI65'], custom_data=['Label'])
                fig_map.update_traces(texttemplate="%{customdata[0]}", textposition="middle center")
                fig_map.update_layout(template='plotly_dark', margin=dict(t=30, l=10, r=10, b=10), height=500)
                st.plotly_chart(fig_map, use_container_width=True)
            except Exception as e: pass
            
            st.markdown("---")
            st.subheader("📈 상세 기술적 분석 차트")
            render_ticker_report(st.session_state.get('selected_ticker'))

    elif page.startswith("2."):
        st.header("💬 안티그래비티 전용 대화방")
        with st.form("chat_form", clear_on_submit=True):
            new_msg = st.text_input("메시지 입력")
            if st.form_submit_button("전송") and new_msg:
                save_message(st.session_state.get('current_user'), new_msg)
                st.rerun()
        for m in reversed(load_messages()): st.write(f"**{m['user']}**: {m['content']} ({m['time']})")

    elif page.startswith("3."):
        st.markdown("<h1 style='color: #FFD700; text-shadow: 0 0 15px rgba(255, 215, 0, 0.4);'>🏛️ BMS Analyzer Pro</h1>", unsafe_allow_html=True)
        search_input = st.text_input("분석할 종목명 또는 코드를 입력하세요", "NVDA")
        pro_ticker = resolve_ticker(search_input).upper()

        if pro_ticker:
            try:
                with st.spinner(f"🚀 {pro_ticker} BMS 엔진 분석 중..."):
                    stock_obj = yf.Ticker(pro_ticker); hist_data = stock_obj.history(period="1y"); info = stock_obj.info
                    if len(hist_data) >= 70:
                        if isinstance(hist_data.columns, pd.MultiIndex): hist_data.columns = hist_data.columns.get_level_values(0)
                        curr_v = hist_data['Volume'].iloc[-1]; ma7 = hist_data['Close'].rolling(7).mean(); ma65 = hist_data['Close'].rolling(65).mean(); ti65 = ma7.iloc[-1] / ma65.iloc[-1]
                        if ti65 >= 1.05:
                            p_score = 0; v_score = 0; s_score = 0; penalty = 0
                            change = ((hist_data['Close'].iloc[-1] - hist_data['Close'].iloc[-2]) / hist_data['Close'].iloc[-2]) * 100
                            if change >= 4.0: p_score += 20
                            day_high = hist_data['High'].iloc[-1]; day_low = hist_data['Low'].iloc[-1]; day_close = hist_data['Close'].iloc[-1]
                            close_loc = (day_close - day_low) / (day_high - day_low) if day_high != day_low else 0
                            if close_loc >= 0.7: p_score += 10
                            avg_v50 = hist_data['Volume'].rolling(50).mean()
                            if curr_v > hist_data['Volume'].iloc[-2]: v_score += 15
                            if curr_v > avg_v50.iloc[-1] * 1.4: v_score += 15
                            if curr_v > avg_v50.iloc[-1] * 2.0 or curr_v > 9000000: v_score += 10
                            prev_range = (hist_data['High'].iloc[-2] - hist_data['Low'].iloc[-2]) / hist_data['Close'].iloc[-3] * 100
                            if prev_range < 2.0 or hist_data['Close'].iloc[-2] < hist_data['Open'].iloc[-2]: s_score += 20
                            ma50 = hist_data['Close'].rolling(50).mean()
                            if any(hist_data['Close'].iloc[-10:] > ma50.iloc[-10:]) and hist_data['Close'].iloc[-11] < ma50.iloc[-11]: s_score += 10
                            if (hist_data['Close'].iloc[-1] > hist_data['Close'].iloc[-2] > hist_data['Close'].iloc[-3] > hist_data['Close'].iloc[-4]): penalty -= 30
                            
                            total_score = max(0, min(100, p_score + v_score + s_score + penalty))
                            status_color = "#4ade80" if total_score >= 80 else "#fbbf24" if total_score >= 50 else "#ff4b4b"
                            status_text = "BUY 🟢" if total_score >= 80 else "WATCH 🟡" if total_score >= 50 else "AVOID 🔴"
                            
                            m1, m2 = st.columns([1, 2.5])
                            with m1:
                                st.markdown(f"<div style='background-color: #111; padding: 25px; border: 2px solid {status_color}; border-radius: 20px; text-align: center;'><h1 style='color: {status_color}; font-size: 4rem;'>{total_score}</h1><p>{status_text}</p></div>", unsafe_allow_html=True)
                                st.table(pd.DataFrame({"Item": ["Price", "Volume", "Setup", "Risk"], "Points": [f"{p_score}/30", f"{v_score}/40", f"{s_score}/30", f"{penalty}"]}))
                            with m2:
                                fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1, row_heights=[0.7, 0.3])
                                fig.add_trace(go.Candlestick(x=hist_data.index[-60:], open=hist_data['Open'].iloc[-60:], high=hist_data['High'].iloc[-60:], low=hist_data['Low'].iloc[-60:], close=hist_data['Close'].iloc[-60:], name='Price'), row=1, col=1)
                                fig.add_trace(go.Bar(x=hist_data.index[-60:], y=[total_score]*60, marker_color=status_color, opacity=0.3), row=2, col=1)
                                fig.update_layout(template='plotly_dark', height=600, showlegend=False, xaxis_rangeslider_visible=False)
                                st.plotly_chart(fig, use_container_width=True)
            except Exception as e: pass

    elif page.startswith("4."):
        st.header("📈 실시간 분석 차트 (Interactive)")
        search_ticker = st.text_input("분석할 종목명 또는 티커를 입력하세요", "NVDA")
        chart_ticker = resolve_ticker(search_ticker).upper()
        
        if chart_ticker:
            try:
                with st.spinner(f"🚀 {chart_ticker} 데이터를 불러오는 중..."):
                    data = yf.download(chart_ticker, period="1y", progress=False)
                    
                    if data.empty:
                        st.warning(f"⚠️ {chart_ticker}에 대한 데이터를 찾을 수 없습니다. 티커가 정확한지 확인해 주세요.")
                    else:
                        # 컬럼 정리 (MultiIndex 대응)
                        if isinstance(data.columns, pd.MultiIndex):
                            data.columns = data.columns.get_level_values(0)
                        
                        fig = go.Figure(data=[go.Candlestick(
                            x=data.index,
                            open=data['Open'],
                            high=data['High'],
                            low=data['Low'],
                            close=data['Close'],
                            name=chart_ticker
                        )])
                        
                        # 이동평균선 추가 (가독성 향상)
                        fig.add_trace(go.Scatter(x=data.index, y=data['Close'].rolling(20).mean(), name='MA20', line=dict(color='yellow', width=1)))
                        fig.add_trace(go.Scatter(x=data.index, y=data['Close'].rolling(60).mean(), name='MA60', line=dict(color='cyan', width=1)))
                        
                        fig.update_layout(
                            template='plotly_dark',
                            xaxis_rangeslider_visible=True,
                            height=600,
                            title=f"{ticker_map.get(chart_ticker, chart_ticker)} ({chart_ticker}) - 1 Year Chart",
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)'
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
            except Exception as e:
                st.error(f"차트를 생성하는 중 오류가 발생했습니다: {e}")

    elif page.startswith("5."):
        st.header("🧮 리스크 관리 및 포지션 사이징")
        c1, c2 = st.columns(2)
        capital = c1.number_input("총 투자 자산", value=10000000)
        risk_percent = c1.slider("1회 매매당 최대 리스크 (%)", 0.5, 5.0, 1.0)
        entry_price = c1.number_input("매수 예정가", value=100000)
        stop_loss = c2.number_input("손절가 설정", value=95000)
        target_price = c2.number_input("목표가 설정", value=120000)
        risk_per_share = entry_price - stop_loss
        if risk_per_share > 0:
            pos_size = int((capital * (risk_percent / 100)) / risk_per_share)
            st.metric("권장 매수 수량", f"{pos_size} 주", delta=f"총 {(pos_size*entry_price):,} 원")
            st.metric("손익비 (R/R)", f"{(target_price - entry_price) / risk_per_share:.2f}")

    elif page == "6. 📰 실시간 뉴스 피드":
        st.header("📰 실시간 시장 뉴스 브리핑")
        st.markdown("yfinance 엔진을 통해 실시간 금융 뉴스를 정밀 분석합니다.")
        
        try:
            with st.spinner("최신 뉴스를 불러오는 중..."):
                # yfinance의 Search 기능을 활용하여 뉴스 확보
                import yfinance as yf
                market_news = yf.Search("Market").news
                
                if not market_news:
                    st.warning("현재 표시할 뉴스가 없습니다. 잠시 후 다시 시도해 주세요.")
                else:
                    for item in market_news[:15]: # 상위 15개 출력
                        with st.container():
                            st.markdown(f"### {item.get('title')}")
                            col_news1, col_news2 = st.columns([1, 4])
                            with col_news1:
                                if 'thumbnail' in item and item['thumbnail'].get('resolutions'):
                                    st.image(item['thumbnail']['resolutions'][0]['url'], use_container_width=True)
                                else:
                                    st.markdown("🖼️ No Image")
                            with col_news2:
                                st.markdown(f"**Source:** {item.get('publisher')} | **Type:** {item.get('type')}")
                                st.markdown(f"**Link:** [기사 원문 보기]({item.get('link')})")
                                if 'relatedTickers' in item:
                                    st.markdown(f"**관련 종목:** {', '.join(item['relatedTickers'])}")
                            st.markdown("---")
        except Exception as e:
            st.error(f"뉴스를 불러오는 중 오류가 발생했습니다: {e}")
            st.info("💡 종폭별 상세 분석 탭에서도 해당 종목의 소식을 확인할 수 있습니다.")

    elif page == "7. 📊 본데 주식 50선":
        st.header("📊 본데의 주식 50선 (Google Sheet Sync)")
        try:
            # 구글 시트 데이터 로드
            sheet_url = "https://docs.google.com/spreadsheets/d/1xjbe9SF0HsxwY_Uy3NC2tT92BqK0nhArUaYU16Q0p9M/export?format=csv&gid=1499398020"
            df = pd.read_csv(sheet_url)
            st.dataframe(df, use_container_width=True)
            
            st.markdown("---")
            
            # --- 본데의 전략적 통찰 (Bonde's Strategic Insight) 추가 ---
            st.markdown(f"""
                <div style='background-color: #111111; padding: 30px; border-radius: 15px; border: 1px solid #FFD700; margin-top: 20px;'>
                    <h2 style='color: #FFD700; text-align: center; margin-bottom: 25px;'>🚀 Bonde's Strategic Insight: The Momentum 50 Playbook</h2>
                    
                    <p style='font-size: 1.1rem; line-height: 1.8; color: #EEEEEE;'>
                        주식 시장은 복잡해 보이지만, 본질은 <b>'가속도(Acceleration)'</b>와 <b>'관성(Inertia)'</b>의 법칙을 따르는 물리적 전장입니다. 
                        제가 매일 뽑아내는 '모멘텀 50 리스트'는 단순히 많이 오른 종목의 나열이 아닙니다. 이것은 지금 이 순간, 기관들의 거대한 자금이 어디로 쏠리며 
                        어떤 종목이 중력을 이기고 우주로 나갈 준비를 마쳤는지를 보여주는 <b>'수급의 지도'</b>입니다.
                    </p>
                    
                    <div style='margin-top: 30px;'>
                        <h3 style='color: #FFFF00;'>1. 리스트의 위계: 대장주와 후보주의 역학 관계</h3>
                        <p style='color: #DDDDDD; line-height: 1.7;'>
                            상단에 포진한 종목들은 현재 시장의 주인공들입니다. 이들은 가장 강력한 상대강도(RS)를 내뿜으며 지수보다 앞서 달려 나갑니다. 
                            하지만 영리한 트레이더는 상단 종목의 화려함에 눈이 멀어 무작정 뛰어들지 않습니다. 상단 종목은 현재 시장의 테마와 색깔을 읽는 <b>'지표'</b>로 삼으십시오.
                            <br><br>
                            오히려 기회는 리스트의 <b>하단이나 중위권에서 고개를 드는 종목들</b>에 있습니다. 이들은 이제 막 베이스를 탈출하여 시세의 초입(Young Trend)에 있거나, 
                            강력한 1차 상승 후 에너지를 재응축하는 구간에 있습니다. 상단이 '이미 타오르는 불꽃'이라면, 하단은 '폭발을 기다리는 다이너마이트'입니다.
                        </p>
                    </div>

                    <div style='margin-top: 30px;'>
                        <h3 style='color: #FFFF00;'>2. 인내의 미학: 급등은 구경하고 응축을 매수하라</h3>
                        <p style='color: #DDDDDD; line-height: 1.7;'>
                            기억하십시오. 장대양봉이 솟구치며 모두가 환호할 때 진입하는 것은 투자가 아니라 자살 행위입니다. 급등은 그저 우리가 그 종목을 감시 목록(Watchlist)에 넣어야 할 <b>'신호'</b>일 뿐입니다. 
                            진짜 매수는 폭풍이 지나간 뒤에 시작됩니다.
                            <br><br>
                            주가가 급등 후 옆으로 기어가며 변동성을 죽이는 과정을 반드시 지켜보십시오. 캔들의 몸통이 깨알처럼 작아지고, 윗꼬리와 아랫꼬리조차 사라진 '도지형(Doji)' 캔들이 나타나야 합니다. 
                            이때 가장 중요한 것은 <b>거래량의 실종(Dry-up)</b>입니다. 거래량이 먼지처럼 말라붙었다는 것은 매도세가 완전히 소진되어 작은 불씨만으로도 다시 폭발할 준비가 되었다는 증거입니다. 
                            에너지가 응축될 때까지 거북이처럼 인내하십시오.
                        </p>
                    </div>

                    <div style='margin-top: 30px;'>
                        <h3 style='color: #FFFF00;'>3. 생존의 규율: -3%의 지지선과 3일의 시간 정찰</h3>
                        <p style='color: #DDDDDD; line-height: 1.7;'>
                            매수 버튼을 누르는 순간, 당신은 예측가가 아니라 리스크 관리자가 되어야 합니다. 저는 두 가지 엄격한 지지선을 제안합니다.
                            <br><br>
                            <b>첫째, -3%의 기계적 손절입니다.</b> 가격이 내 진입가 대비 3% 밀린다는 것은 내 시나리오가 틀렸거나 시장의 수급이 꼬였다는 명백한 신호입니다. 
                            미련은 계좌를 갉아먹는 암세포입니다. -3%는 당신의 생명을 지켜주는 마지막 방어선입니다.
                            <br><br>
                            <b>둘째, 3일의 시간 정찰(Time Stop)입니다.</b> 모멘텀 주식은 살아있는 생물과 같습니다. 매수 후 3일 이내에 위로 강한 반응이 나오지 않는다면, 
                            그 종목은 이미 죽은 에너지를 가진 것입니다. 주가가 빠지지 않더라도 옆으로 지지부진하다면 과감히 팔고 나오십시오. 자본은 항상 가장 뜨겁게 타오르는 곳에 머물러야 합니다.
                        </p>
                    </div>
                    
                    <div style='margin-top: 40px; padding: 20px; background-color: #222; border-radius: 10px; border-left: 5px solid #FFD700;'>
                        <h3 style='color: #FFD700; margin-top: 0;'>📝 본데의 핵심 가이드 요점 정리</h3>
                        <ul style='color: #FFFFFF; line-height: 1.8;'>
                            <li><b>관찰:</b> 모멘텀 50 리스트를 통해 시장의 주도 섹터와 대장주를 파악한다.</li>
                            <li><b>대기:</b> 급등 후 옆으로 기며 에너지가 응축(Tightness)될 때까지 기다린다.</li>
                            <li><b>포착:</b> 거래량이 마르고 캔들이 도지형으로 작아지는 '고요한 지점'을 찾는다.</li>
                            <li><b>대응:</b> 진입 즉시 -3% 손절을 설정하고, 3일 내 반응이 없으면 기회비용을 위해 청산한다.</li>
                        </ul>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")

    elif page.startswith("8."):
        st.write("본데와 미너비니의 핵심 전략 강의 요약")

    elif page.startswith("9."):
        st.header("👑 회원 가입 승인 관리 센터")
        users = load_users()
        pending = {k: v for k, v in users.items() if isinstance(v, dict) and v.get("status") == "pending"}
        if not pending: st.info("승인 대기자가 없습니다.")
        else:
            for uid, info in pending.items():
                if st.button(f"✅ 승인: {uid}"):
                    if update_user_status(uid, "approved"): st.rerun()

        for m in reversed(load_messages()): st.write(f"**{m['user']}**: {m['content']} ({m['time']})")

    st.sidebar.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRzI5yZq00eP8vE8XG9-L_9u_vB_W_K7uB6A&s", width=150)
