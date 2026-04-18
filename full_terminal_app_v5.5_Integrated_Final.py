# 작업 일자: 2026-04-18 | 작업 시간: 20:15 | 버전: v5.5 (Ultimate SQLite Engine)
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
import os
import json
import pytz
import numpy as np
import plotly.graph_objects as go
import requests
import time
import sqlite3

# --- 💾 강철 엔진 (SQLite) 초기화 로직 ---
DB_FILE = "antigravity_master.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # 1. 회원 테이블
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, password TEXT, status TEXT, grade TEXT)''')
    # 2. 대화 기록 테이블
    c.execute('''CREATE TABLE IF NOT EXISTS messages 
                 (user TEXT, content TEXT, time TEXT)''')
    # 3. 방문자 인사 테이블
    c.execute('''CREATE TABLE IF NOT EXISTS visitors 
                 (user TEXT, content TEXT, time TEXT)''')
    # 4. 포트폴리오 테이블
    c.execute('''CREATE TABLE IF NOT EXISTS portfolio 
                 (name TEXT, qty REAL, entry REAL, stop REAL, risk REAL)''')
    
    # 관리자 계정 기본 생성
    c.execute("SELECT * FROM users WHERE username='cntfed'")
    if not c.fetchone():
        c.execute("INSERT INTO users VALUES ('cntfed', 'cntfed', 'approved', '관리자')")
    
    conn.commit()
    conn.close()

init_db()

def get_db_connection():
    return sqlite3.connect(DB_FILE)

# --- 유저 데이터베이스 함수 교체 ---
def load_users():
    conn = get_db_connection()
    df = pd.read_sql("SELECT * FROM users", conn)
    conn.close()
    return df.set_index('username').to_dict('index')

def save_user_sql(uid, pw, status, grade):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO users VALUES (?, ?, ?, ?)", (uid, pw, status, grade))
    conn.commit()
    conn.close()

# --- 통합 설정 ---
MASTER_GAS_URL = "https://script.google.com/macros/s/AKfycbyp31pP_T4nVi0rEoeOu-kc6t_ynofxRYnnYZTTO1kxOcQWinBfyhEeDjTRZXzp1eCo/exec"

def gsheet_sync(sheet_name, headers, values):
    payload = {"sheetName": sheet_name, "headers": headers, "values": values}
    try:
        with st.status(f"🔄 {sheet_name} 데이터 구글시트 동기화 중...", expanded=False) as status:
            resp = requests.post(MASTER_GAS_URL, json=payload, timeout=12)
            if "success" in resp.text:
                st.toast(f"✅ {sheet_name} 동기화 완료!", icon="📊")
                status.update(label="✅ 구글 시트 저장 완료", state="complete")
            else:
                st.toast(f"⚠️ 시트 응답 지연", icon="⏳")
    except Exception:
        pass

# --- 마켓 게이지 엔진 ---
@st.cache_data(ttl=60)
def get_bonde_market_gauge():
    st_val, cl = "🟢 GREEN", "#00FF00"
    ad = "Follow-Through Day occurred on April 8th, 2026. The trend is your friend."
    ko = "팔로우스루데이 2026년 4월 8일(수)요일 발생 - 새로운 상승 추세의 시작입니다!"
    nt = "공격: 주도주 매수 및 수익 극대화"
    
    try:
        qqq = yf.Ticker("QQQ").history(period="20d")
        curr_p, ma20 = qqq['Close'].iloc[-1], qqq['Close'].rolling(20).mean().iloc[-1]
        dist = (curr_p/ma20 - 1) * 100
    except: dist = 1.5
    
    return {
        "status": st_val, "color": cl, "advice": ad, "ko_advice": ko, "note": nt, 
        "study_20": 40, "up_4": 5, "down_4": 1, "ma20_dist": dist
    }

TICKER_NAME_MAP = {
    "NVDA": "엔비디아", "TSLA": "테슬라", "AAPL": "애플", "MSFT": "마이크로소프트", "PLTR": "팔란티어", "SMCI": "슈퍼마이크로", 
    "AMD": "AMD", "META": "메타", "GOOGL": "구글", "AVGO": "브로드컴", "CRWD": "크라우드스트라이크", "005930.KS": "삼성전자", 
    "000660.KS": "SK하이닉스", "196170.KQ": "알테오젠", "042700.KS": "한미반도체", "105560.KS": "KB금융", "055550.KS": "신한지주",
    "005490.KS": "POSCO홀딩스", "000270.KS": "기아", "066570.KS": "LG전자", "035720.KS": "카카오", "035420.KS": "NAVER"
}

# --- 🌑 강제 다크 모드 및 하이엔드 디자인 주입 ---
st.markdown("""
    <style>
    /* 전체 배경을 칠흑 같은 검정으로 고정 */
    .stApp {
        background-color: #000000 !important;
        color: #FFFFFF !important;
    }
    /* 사이드바도 어둠 속으로 */
    [data-testid="stSidebar"] {
        background-color: #050505 !important;
        border-right: 1px solid #333;
    }
    /* 텍스트 색상 및 강조색(황금) 설정 */
    h1, h2, h3, h4, h5, p, span, div {
        color: #FFFFFF !important;
    }
    .sidebar-title {
        color: #FFD700 !important;
        text-shadow: 0 0 10px rgba(255, 215, 0, 0.5);
    }
    /* 버튼 스타일 통일 */
    .stButton>button {
        background-color: #1a1a1a !important;
        color: #FFD700 !important;
        border: 1px solid #FFD700 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 인증 시스템 ---
if "password_correct" not in st.session_state: st.session_state["password_correct"] = False

if not st.session_state["password_correct"]:
    st.markdown("<div style='text-align: center; padding: 40px 0;'><h1 style='color: #FFD700;'>⚖️ Pivot Master Pro</h1><p style='color: #888;'>Antigravity Trading Terminal</p></div>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔐 로그인", "✨ 회원가입 신청"])
    
    with tab1:
        id_i = st.text_input("아이디", key="login_id")
        pw_i = st.text_input("비번", type="password", key="login_pw")
        if st.button("터미널 접속"):
            u = load_users()
            if id_i in u and u[id_i]["password"] == pw_i:
                st.session_state["password_correct"] = True
                st.session_state.current_user = id_i
                st.rerun()
            else: st.error("정보가 올바르지 않습니다.")
            
    with tab2:
        st.write("안티그래비티 터미널의 회원이 되어 함께 성장하세요.")
        new_id = st.text_input("희망 아이디", key="reg_id")
        new_pw = st.text_input("희망 비밀번호", type="password", key="reg_pw")
        if st.button("가입 신청하기"):
            u = load_users()
            if new_id in u: st.warning("이미 존재합니다.")
            elif not new_id or not new_pw: st.warning("모두 입력해 주세요.")
            else:
                save_user_sql(new_id, new_pw, "pending", "주식입문자")
                st.success("✅ 신청 완료! 전문가님의 승인을 기다려 주세요.")
    st.stop()

# --- 사이드바 및 메뉴 ---
st.sidebar.markdown("<h1 class='sidebar-title'>⚖️ Pivot Master Pro</h1>", unsafe_allow_html=True)

# [고도화] 집중력 BGM 시스템
if st.sidebar.checkbox("🎼 집중력 BGM (ASMR)", value=True):
    st.sidebar.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-8.mp3")
    st.sidebar.caption("💡 재생 버튼을 클릭해야 노래가 흘러나옵니다.")

u_all = load_users()
curr_u_data = u_all.get(st.session_state.current_user, {})
is_staff = curr_u_data.get("grade") in ["관리자", "방장"] or st.session_state.current_user == "cntfed"
is_approved = curr_u_data.get("status") == "approved"

if is_staff:
    pending_count = sum(1 for user in u_all.values() if user.get("status") == "pending")
    if pending_count > 0: st.sidebar.warning(f"🔔 신규 가입 신청 {pending_count}건 대기 중!")

menu_ops = [
    "1. 🐝 Pivot Master Pro Scanner", "2. 💬 소통 대화방", "3. 💎 프로 분석 리포트", "4. 🚀 모멘텀 50 종목", 
    "5. 🧮 리스크 계산기", "6. 📰 뉴스 피드", "7. 📊 본데 50선", "8. 👑 관리자 승인 센터", 
    "9. 🐝 본데는 누구인가?", "10. 🏛️ 이 사이트 제작 동기", "11. 🤝 방문자 인사 및 승인 요청",
    "12. 🛡️ 포트폴리오 리스크 방패", "13. 🗺️ 실시간 주도주 히트맵"
]

if is_staff: display_menu = menu_ops
elif is_approved: display_menu = [o for o in menu_ops if not o.startswith("8.")]
else: display_menu = [o for o in menu_ops if any(o.startswith(x) for x in ["9.", "10.", "11."])]

st.sidebar.markdown("<h2 style='color:#FFFF00;'>⚖️ 사령부 메뉴</h2>", unsafe_allow_html=True)
page = st.sidebar.radio("Master Menu", display_menu)

# --- 글로벌 시간 ---
tz_seoul = pytz.timezone('Asia/Seoul')
tz_ny = pytz.timezone('US/Eastern')
now_seoul = datetime.now(tz_seoul).strftime('%Y-%m-%d %H:%M')
now_ny = datetime.now(tz_ny).strftime('%Y-%m-%d %H:%M')

st.markdown(f"<div style='text-align: right; color: #888; font-size: 0.8rem;'>🇰🇷 {now_seoul} | 🇺🇸 {now_ny}</div>", unsafe_allow_html=True)

# --- 마켓 헤더 (캐시 적용) ---
g = get_bonde_market_gauge()
st.markdown(f"""
    <div style='background: #111; padding: 15px; border-radius: 12px; border: 1px solid #FFD700; margin-bottom: 20px;'>
        <div style='display: flex; justify-content: space-around; align-items: center;'>
            <div style='text-align: center; flex: 1;'><h2 style='color: {g["color"]}; margin: 0;'>{g["status"]}</h2></div>
            <div style='flex: 2; text-align: center; border-left: 1px solid #333;'><p style='color: #FFD700; margin: 0;'>{g["ko_advice"]}</p></div>
            <div style='flex: 1; text-align: center; border-left: 1px solid #333;'><h4 style='color: #00FF00; margin: 0;'>Index: {g["ma20_dist"]:.1f}%</h4></div>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- 추천주 최적화 (캐시 적용) ---
@st.cache_data(ttl=3600)
def get_top_pick_cached():
    try:
        conn = get_db_connection()
        df_m = pd.read_sql("SELECT content FROM messages", conn)
        conn.close()
        if df_m.empty: return None
        all_text = " ".join(df_m['content'].tolist())
        import re
        for tic in TICKER_NAME_MAP.keys():
            if re.search(f"\\b{tic.split('.')[0]}\\b", all_text, re.I):
                inf = yf.Ticker(tic).info
                h = yf.Ticker(tic).history(period="1d")
                cp = h['Close'].iloc[-1]
                return {"name": TICKER_NAME_MAP[tic], "ticker": tic, "roe": inf.get('returnOnEquity',0)*100, "price": cp}
    except: return None

tp = get_top_pick_cached()
if tp:
    st.info(f"💎 **대표 주도주: {tp['name']} ({tp['ticker']})** | ROE: {tp['roe']:.1f}% | 현재가: ${tp['price']:.2f} (진입 대기)")

# --- 각 페이지 상세 로직 ---
if page.startswith("1."):
    st.header("⚖️ Pivot Master Pro Scanner")
    tabs = st.tabs(["[모드 1] EP", "[모드 2] BURST", "[모드 3] TTT"])
    @st.cache_data(ttl=300)
    def run_sc():
        res = {"EP": [], "BURST": [], "TTT": []}
        for tic, name in TICKER_NAME_MAP.items():
            try:
                hk = yf.Ticker(tic).history(period="30d"); inf = yf.Ticker(tic).info
                cp, pp = hk['Close'].iloc[-1], hk['Close'].iloc[-2]
                ch = (cp/pp-1)*100; cv = hk['Volume'].iloc[-1]; va = hk['Volume'].iloc[-20:].mean()
                row = {"종목명": name, "현재가": cp, "ROE": inf.get('returnOnEquity',0)*100, "BMS": int(ch+5)}
                if ch > 2 and cv > va*1.2: res["EP"].append(row)
                if ch > 4: res["BURST"].append(row)
            except: continue
        return res
    data = run_sc()
    for tab, k in zip(tabs, ["EP", "BURST", "TTT"]):
        with tab: st.write(pd.DataFrame(data[k]))

elif page.startswith("2."):
    st.header("💬 소통 대화방")
    with st.form("chat", clear_on_submit=True):
        ms = st.text_input("메시지")
        if st.form_submit_button("전송"):
            conn = get_db_connection(); c = conn.cursor()
            now = datetime.now().strftime("%Y-%m-%d %H:%M")
            c.execute("INSERT INTO messages VALUES (?, ?, ?)", (st.session_state.current_user, ms, now))
            conn.commit(); conn.close()
            gsheet_sync("소통대화방_기록", ["유저", "메시지", "시간"], [st.session_state.current_user, ms, now])
            st.rerun()
    conn = get_db_connection()
    df_m = pd.read_sql("SELECT * FROM messages ORDER BY time DESC LIMIT 100", conn)
    conn.close()
    for _, r in df_m.iterrows():
        st.write(f"**{r['user']}** ({r['time']}): {r['content']}")

elif page.startswith("8."):
    st.header("👑 승인 센터")
    u = load_users()
    for k, v in u.items():
        if k == "cntfed": continue
        c1, c2, c3 = st.columns([2, 2, 1])
        c1.write(f"👤 {k} ({v['status']})")
        if v['status'] == 'pending' and c2.button(f"승인하기", key=k):
            save_user_sql(k, v['password'], "approved", "주식입문자")
            st.rerun()
        if c3.button("추방", key=f"k_{k}"):
            conn = get_db_connection(); c = conn.cursor()
            c.execute("DELETE FROM users WHERE username=?", (k,))
            conn.commit(); conn.close(); st.rerun()

elif page.startswith("12."):
    st.header("🛡️ 리스크 방패")
    conn = get_db_connection()
    pdf = pd.read_sql("SELECT * FROM portfolio", conn)
    conn.close()
    with st.form("port"):
        n = st.text_input("종목"); q = st.number_input("수량", 1); e = st.number_input("매수", 100); s = st.number_input("손절", 95)
        if st.form_submit_button("저장"):
            conn = get_db_connection(); c = conn.cursor()
            r = (e-s)*q
            c.execute("INSERT INTO portfolio VALUES (?, ?, ?, ?, ?)", (n, q, e, s, r))
            conn.commit(); conn.close(); st.rerun()
    st.table(pdf)
    if st.button("포트 초기화"):
        conn = get_db_connection(); c = conn.cursor()
        c.execute("DELETE FROM portfolio")
        conn.commit(); conn.close(); st.rerun()

elif page.startswith("13."):
    st.header("🗺️ 주도주 히트맵")
    @st.cache_data(ttl=600)
    def draw_h():
        tics = list(TICKER_NAME_MAP.keys())
        data = yf.download(tics, period="2d", group_by='ticker')
        res = []
        for t in tics:
            try:
                c = data[t]['Close']
                pc = (c.iloc[-1]/c.iloc[-2]-1)*100
                res.append({"name": TICKER_NAME_MAP[t], "change": pc})
            except: continue
        return pd.DataFrame(res)
    df_h = draw_h()
    import plotly.express as px
    st.plotly_chart(px.treemap(df_h, path=['name'], values=[1]*len(df_h), color='change', color_continuous_scale='RdYlGn'))
