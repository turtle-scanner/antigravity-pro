# 작업 일자: 2026-04-18 | 작업 시간: 17:24 | 버전: v2.0 (G-Drive Final)
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
        data = yf.download(sample_tickers, period="5d", progress=False)['Close']
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
        initial_users = {
            "cntfed": {"password": "cntfed", "exp": "Master", "profit": "N/A", "status": "approved"}
        }
        with open(USER_DB_FILE, "w") as f:
            json.dump(initial_users, f)
        return initial_users
    with open(USER_DB_FILE, "r") as f:
        return json.load(f)

def save_user(user_id, password, exp, profit):
    users = load_users()
    if user_id in users: return False, "이미 존재하는 아이디입니다."
    users[user_id] = {"password": password, "exp": exp, "profit": profit, "status": "pending"}
    with open(USER_DB_FILE, "w") as f: json.dump(users, f)
    return True, "가입 신청 완료! 관리자의 승인 후 로그인이 가능합니다."

def update_user_status(user_id, status):
    users = load_users()
    if user_id in users:
        users[user_id]["status"] = status
        with open(USER_DB_FILE, "w") as f: json.dump(users, f)
        return True
    return False

# 0. 페이지 설정
st.set_page_config(page_title="Bonde-Turtle Terminal", page_icon="🐢", layout="wide")

# 1. 암호 보안 설정
def check_password():
    if "password_correct" not in st.session_state: st.session_state["password_correct"] = False
    if st.session_state["password_correct"]: return True

    st.markdown("<div style='text-align: center; padding: 40px 0;'>", unsafe_allow_html=True)
    st.markdown("<h1 style='color: #FFD700; text-shadow: 0 0 15px rgba(255, 215, 0, 0.4);'>🏛️ ANTI-GRAVITY TERMINAL</h1>", unsafe_allow_html=True)
    
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
                    else: st.warning("⏳ 승인 대기 중입니다.")
                else: st.error("❌ Invalid ID or Password.")
        with tab_signup:
            new_id = st.text_input("NEW ID", key="reg_id")
            new_pw = st.text_input("NEW PASSWORD", type="password", key="reg_pw")
            if st.button("가입 신청하기", use_container_width=True):
                success, msg = save_user(new_id, new_pw, "N/A", "N/A")
                if success: st.success(msg)
                else: st.error(msg)
    st.markdown("</div>", unsafe_allow_html=True)
    return False

if check_password():
    # --- 사이드바 헤더 및 시계 ---
    kst = pytz.timezone('Asia/Seoul'); est = pytz.timezone('US/Eastern')
    now_kst = datetime.now(kst); now_est = datetime.now(est)
    
    st.sidebar.markdown("<h2 style='color: #FFFF00;'>🐢 Bonde-Turtle</h2>", unsafe_allow_html=True)
    st.sidebar.markdown(f"""
        <div style='background-color: #111111; padding: 15px; border-radius: 10px; border: 1px solid #FFFF00; margin-bottom: 20px;'>
            <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;'>
                <span style='font-size: 11px; color: #FFFF00;'>🇰🇷 KOREA (KST)</span>
                <span style='font-size: 9px; color: #4ade80;'>LIVE</span>
            </div>
            <div style='font-size: 18px; color: #FFFF00; font-family: monospace; font-weight: bold;'>{now_kst.strftime('%H:%M:%S')}</div>
            <hr style='margin: 10px 0; border: none; border-top: 1px solid #333;'>
            <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;'>
                <span style='font-size: 11px; color: #FFFF00;'>🇺🇸 USA (ET)</span>
                <span style='font-size: 9px; color: #4ade80;'>MARKET</span>
            </div>
            <div style='font-size: 18px; color: #FFFF00; font-family: monospace; font-weight: bold;'>{now_est.strftime('%H:%M:%S')}</div>
        </div>
    """, unsafe_allow_html=True)

    # --- BGM 플레이어 (이름 변경 반영) ---
    st.sidebar.markdown("<p style='font-size: 11px; color: #4ade80; margin-bottom: 5px;'>🎵 BGM SELECTOR</p>", unsafe_allow_html=True)
    bgm_files = {
        "OFF": None,
        "나의 아저씨": "mypapa.mp3",
        "싱그러운": "petty.mp3",
        "You Raise Me Up": "YouRaise.mp3",
        "귀여운": "cute.mp3",
        "설렘 Piano": "hope.mp3",
        "기분좋은": "happy.mp3"
    }
    selected_bgm = st.sidebar.selectbox("음악 선택", list(bgm_files.keys()), key="bgm_selector", label_visibility="collapsed")
    
    if bgm_files[selected_bgm]:
        import base64
        file_path = bgm_files[selected_bgm]
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            vol = st.sidebar.slider("🔊 볼륨", 0.0, 1.0, 0.5, 0.05)
            audio_html = f"""
                <audio id="bgm-player" autoplay loop><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>
                <script>var audio = window.parent.document.getElementById("bgm-player"); if (audio) {{ audio.volume = {vol}; }}</script>
            """
            st.components.v1.html(audio_html, height=0)
            st.sidebar.caption(f"Playing: {selected_bgm}")
        else:
            st.sidebar.error(f"❌ '{file_path}' 파일을 찾을 수 없습니다.")

    # --- 시장 심리 게이지 ---
    score, _, _, _, _ = get_market_sentiment()
    gauge_color = "#4ade80" if score >= 70 else "#fbbf24" if score >= 40 else "#ff4b4b"
    st.sidebar.markdown(f"""
        <div style='background-color: #111111; padding: 15px; border-radius: 10px; border: 1px solid {gauge_color}; margin-top: 15px;'>
            <div style='font-size: 11px; color: {gauge_color}; font-weight: bold; margin-bottom: 10px;'>🔥 MARKET SENTIMENT</div>
            <div style='height: 6px; width: 100%; background: #333; border-radius: 3px; overflow: hidden;'>
                <div style='height: 100%; width: {score}%; background: {gauge_color};'></div>
            </div>
            <div style='display: flex; justify-content: space-between; margin-top: 5px; font-size: 10px; color: #888;'>
                <span>Fear</span>
                <span style='color: {gauge_color};'>{score}%</span>
                <span>Greed</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # --- 메뉴 설정 ---
    menu = ["1. 🎯 주도주 타점 스캐너", "2. 👑 관리자 승인 센터"]
    st.sidebar.radio("Go to", menu)
    st.header("🎯 Bonde-Turtle Terminal v2.0")
    st.write("작업 공간 이동 및 BGM 명칭 변경이 모두 완료되었습니다.")
