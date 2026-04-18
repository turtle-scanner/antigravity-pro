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

# --- 💾 데이터베이스 및 글로벌 설정 ---
USER_DB_FILE = "users_db.json"
MESSAGE_DB_FILE = "messages_db.json"
VISITOR_FILE = "visitor_requests.csv"
MSG_LOG_FILE = "messages_db.csv"
PORTFOLIO_FILE = "portfolio_db.json"
MASTER_GAS_URL = "https://script.google.com/macros/s/AKfycbyp31pP_T4nVi0rEoeOu-kc6t_ynofxRYnnYZTTO1kxOcQWinBfyhEeDjTRZXzp1eCo/exec"

TICKER_NAME_MAP = {
    "NVDA": "엔비디아", "TSLA": "테슬라", "AAPL": "애플", "MSFT": "마이크로소프트", "PLTR": "팔란티어", "SMCI": "슈퍼마이크로", 
    "AMD": "AMD", "META": "메타", "GOOGL": "구글", "AVGO": "브로드컴", "CRWD": "크라우드스트라이크", "005930.KS": "삼성전자", 
    "000660.KS": "SK하이닉스", "196170.KQ": "알테오젠", "042700.KS": "한미반도체", "105560.KS": "KB금융", "055550.KS": "신한지주",
    "005490.KS": "POSCO홀딩스", "000270.KS": "기아", "066570.KS": "LG전자", "035720.KS": "카카오", "035420.KS": "NAVER"
}

def load_users():
    if not os.path.exists(USER_DB_FILE):
        init = {"cntfed": {"password": "cntfed", "status": "approved", "grade": "관리자"}}
        with open(USER_DB_FILE, "w", encoding="utf-8") as f: json.dump(init, f)
        return init
    with open(USER_DB_FILE, "r", encoding="utf-8") as f: return json.load(f)

def gsheet_sync(sheet_name, headers, values):
    payload = {"sheetName": sheet_name, "headers": headers, "values": values}
    try: requests.post(MASTER_GAS_URL, json=payload, timeout=5)
    except: pass

st.set_page_config(page_title="StockDragonfly Pro", page_icon="🛸", layout="wide")

# --- 🌑 프리미엄 스타일 디자인 ---
bg_b64 = ""
if os.path.exists("StockDragonfly2.png"):
    with open("StockDragonfly2.png", "rb") as imm: bg_b64 = base64.b64encode(imm.read()).decode()

st.markdown(f"""
    <style>
    .stApp {{ background-color: #000; {f'background-image: linear-gradient(rgba(0,0,0,0.88), rgba(0,0,0,0.88)), url("data:image/png;base64,{bg_b64}");' if bg_b64 else ""} background-size: cover; background-attachment: fixed; }}
    [data-testid="stSidebar"] {{ background-color: rgba(5,5,5,0.96) !important; border-right: 1px solid #FFD70033; backdrop-filter: blur(25px); }}
    h1, h2 {{ color: #FFD700 !important; font-weight: 900; }}
    .stButton>button {{ background: #1a1a1a !important; color: #FFD700 !important; border: 1px solid #FFD700 !important; border-radius: 10px; font-weight: 800; }}
    .stButton>button:hover {{ background: #FFD700 !important; color: #000 !important; transform: translateY(-3px); box-shadow: 0 8px 25px rgba(255, 215, 0, 0.6); }}
    .glass-card {{ background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 15px; padding: 25px; backdrop-filter: blur(15px); margin-bottom: 30px; }}
    </style>
""", unsafe_allow_html=True)

# --- 인증 & 사이드바 ---
if "password_correct" not in st.session_state: st.session_state["password_correct"] = False
if not st.session_state["password_correct"]:
    c1, m, c2 = st.columns([1, 1.8, 1])
    with m:
        if os.path.exists("StockDragonfly.png"): st.image("StockDragonfly.png", use_container_width=True)
        login_id = st.text_input("아이디"); login_pw = st.text_input("비밀번호", type="password")
        if st.button("Terminal Operation Start", use_container_width=True):
            users = load_users()
            if login_id in users and users[login_id]["password"] == login_pw:
                st.session_state["password_correct"] = True; st.session_state.current_user = login_id; st.rerun()
    st.stop()

with st.sidebar:
    if os.path.exists("StockDragonfly.png"): st.image("StockDragonfly.png")
    st.markdown("<p style='color:#FF914D; font-size:1.5rem; font-weight:900;'>🛸 StockDragonfly v9.9</p>", unsafe_allow_html=True)
    st.divider()
    bgms = {"🔇 OFF": None, "✨ You Raise": "YouRaise.mp3", "😊 Happy": "happy.mp3", "🌅 Hope": "hope.mp3", "🐱 Cute": "cute.mp3", "🎻 Petty": "petty.mp3", "🎙️ Ajussi": "나의아저씨.mp3"}
    sel_bgm = st.selectbox("Radio", list(bgms.keys()), label_visibility="collapsed")
    vol = st.slider("🔊 Volume", 0.0, 1.0, 0.45)
    if bgms[sel_bgm] and os.path.exists(bgms[sel_bgm]):
        with open(bgms[sel_bgm], "rb") as f: b64 = base64.b64encode(f.read()).decode()
        st.components.v1.html(f"<audio id='aud' autoplay loop><source src='data:audio/mp3;base64,{b64}' type='audio/mp3'></audio><script>document.getElementById('aud').volume = {vol};</script>", height=0)

menu_ops = ["1. 🎯 주도주 타점 스캐너", "2. 💬 소통 대화방", "3. 💎 프로 분석 리포트", "4. 🚀 주도주 랭킹 TOP 50", "5. 🧮 리스크 계산기", "6. 📈 마켓 트렌드 요약", "7. 📊 본데 감시 리스트", "8. 👑 관리자 승인 센터", "9. 🐝 본데는 누구인가?", "10. 🏛️ 사이트 제작 동기", "11. 🤝 방문자 인사말 신청", "12. 🛡️ 리스크 방패", "13. 🗺️ 실시간 히트맵", "14. 🌡️ 시장 심리 게이지"]
page = st.sidebar.radio("Mission Control", menu_ops)

# --- 🛰️ 마켓 게이지 헤더 ---
st.markdown("<div style='background: rgba(0,0,0,0.7); border: 2px solid #FFD700; border-radius: 12px; padding: 20px; text-align: center; margin-bottom: 25px;'><h2 style='color: #00FF00; margin: 0;'>🟢 GREEN MARKET ACTIVE</h2></div>", unsafe_allow_html=True)

# --- [PLACEHOLDER_LOGIC_START] ---
if page.startswith("1."):
    st.header("🎯 주도주 타점 스캐너 (Scanner Engine)")
    tabs = st.tabs(["[MAGNA_EP 스캐너]", "[4% 모멘텀 버스트]", "[ANTICIPATION 눌림목]"])
    def run_sc():
        data = {"EP": [], "BURST": [], "TTT": []}
        pb = st.progress(0); st_txt = st.empty()
        for i, (tic, name) in enumerate(TICKER_NAME_MAP.items()):
            try:
                st_txt.text(f"> Analyzing {name}...")
                pb.progress((i+1)/len(TICKER_NAME_MAP))
                tk = yf.Ticker(tic); h = tk.history(period="30d"); inf = tk.info
                if len(h) < 20: continue
                cp, pp = h['Close'].iloc[-1], h['Close'].iloc[-2]
                ch, va, cv = (cp/pp-1)*100, h['Volume'].iloc[-20:].mean(), h['Volume'].iloc[-1]
                roe = inf.get('returnOnEquity', 0) * 100
                score = 0
                if roe >= 10: score += 4
                if ch >= 3.5: score += 3
                if cv > va * 1.5: score += 3
                grade = "💎 S급" if score >= 8 else ("🟢 A급" if score >= 5 else "⚪ B급")
                row = {"종목명": name, "현재가": f"${cp:.2f}", "ROE": f"{roe:.1f}%", "BMS점수": f"{score}점", "등급": grade}
                if (h['Open'].iloc[-1]/pp-1) >= 0.02 and cv > va * 1.5: data["EP"].append(row)
                if ch >= 3.5 and cv > h['Volume'].iloc[-2]: data["BURST"].append(row)
                if h['Close'].iloc[-5:].std()/cp*100 < 2.0 and abs(ch) < 1.5: data["TTT"].append(row)
            except: continue
        pb.empty(); st_txt.empty(); return data
    sc_res = run_sc()
    for tab, k in zip(tabs, ["EP", "BURST", "TTT"]):
        with tab:
            if sc_res[k]: st.dataframe(pd.DataFrame(sc_res[k]), use_container_width=True, hide_index=True)
            else: st.info("대상 종목 없음")

elif page.startswith("2."):
    st.header("💬 소통 대화방")
    with st.form("chat_form", clear_on_submit=True):
        ms = st.text_input("메시지")
        if st.form_submit_button("전송"):
            t = datetime.now().strftime("%Y-%m-%d %H:%M")
            gsheet_sync("소통대화방_기록", ["유저", "시간", "내용"], [st.session_state.current_user, t, ms])
            st.rerun()

elif page.startswith("3."):
    st.header("💎 프로 분석 리포트")
    tic_in = st.text_input("분석 티커", value="NVDA").upper()
    if st.button("정밀 분석"):
        with st.spinner("AI 판독 중..."):
            st.markdown(f"<div class='glass-card'><h4>📊 {tic_in} 분석 결과</h4>Weinstein 2단계 정배열 포착. 상대강도(RS) 95점.</div>", unsafe_allow_html=True)
            st.components.v1.html(f"<iframe src='https://s.tradingview.com/widgetembed/?symbol={tic_in}&interval=D' width='100%' height='500'></iframe>", height=510)

elif page.startswith("4."):
    st.header("🚀 주도주 랭킹 TOP 50")
    st.markdown("<div class='glass-card'>본데의 가중치 알고리즘을 통한 매수 우선순위 랭킹입니다.</div>", unsafe_allow_html=True)
    df_rank = pd.DataFrame({"우선순위": ["💎 TOP 1", "🔥 TOP 2"], "종목": ["NVDA", "PLTR"], "ROE": ["120%", "45%"], "Score": [540, 480]})
    st.dataframe(df_rank, use_container_width=True, hide_index=True)

elif page.startswith("5."):
    st.header("🧮 리스크 계산기")
    total_c = st.number_input("총 자산 (USD)", value=10000)
    entry_p = st.number_input("진입 가격 ($)", value=100.0)
    stop_p = entry_p * 0.97
    st.write(f"🛑 손절가 (-3%): **${stop_p:.2f}**")
    if st.button("수량 계산"):
        risk_p = entry_p - stop_p
        shares = int((total_c * 0.01) / risk_p)
        st.success(f"🎯 매수 수량: **{shares}주** (1% 리스크)")

elif page.startswith("6."):
    st.header("📈 마켓 트렌드 요약")
    c1, c2 = st.columns(2)
    with c1: st.metric("NASDAQ", "18,250", "+1.2%")
    with c2: st.metric("KOSPI", "2,650", "-0.3%")
    st.divider()
    st.write("반도체(SOXX) 🟢 | 바이오(XBI) 🔴 | 빅테크(XLK) 🟢")

elif page.startswith("7."):
    st.header("📊 본데 감시 리스트")
    st.write("전문가님이 수동으로 관리하는 50선 리포트입니다.")
    st.table(pd.DataFrame({"No": [1, 2, 3], "Ticker": ["NVDA", "PLTR", "ARM"], "Status": ["공격", "대기", "매수"]}))

elif page.startswith("8."):
    st.header("👑 관리자 승인 센터")
    if st.session_state.current_user == "cntfed":
        st.write("신규 가입 대기 회원 리스트입니다.")
        st.button("신규 회원 일괄 승인")
    else: st.warning("권한이 없습니다.")

elif page.startswith("9."):
    st.header("🐝 본데(Pradeep Bonde)는 누구인가?")
    st.markdown("""
    <div class='glass-card' style='max-width:850px; margin:0 auto;'>
    <h4>시스템으로 시장을 정복한 월가의 멘토</h4>
    <p>본데는 24년 경력의 전업 트레이더로, 물류 전문가 출신답게 주식을 데이터 기반 비즈니스로 정의했습니다. <b>EP, Momentum Burst</b>의 대가입니다.</p>
    </div>
    """, unsafe_allow_html=True)

elif page.startswith("10."):
    st.header("🏛️ 사이트 제작 동기")
    st.markdown("""
    <div class='glass-card' style='max-width:850px; margin:0 auto;'>
    <h4>세 거인의 발자취를 따라, 함께 성장의 궤도에 오르기를 꿈꾸며</h4>
    <p>윌리엄 오닐, 마크 미너비니, 프라딥 본데 마스터를 존경하며 제작했습니다.</p>
    <div style='text-align:right;'><b>거북이 드림</b><br><i>Sincerely, Turtle</i></div>
    </div>
    """, unsafe_allow_html=True)

elif page.startswith("11."):
    st.header("🤝 방문자 인사말 신청")
    with st.form("greet"):
        ins = st.text_area("승합 요청 인사")
        if st.form_submit_button("전송"):
            gsheet_sync("방문자_인사말", ["신청자", "사유"], [st.session_state.current_user, ins])
            st.success("전송 완료!")

elif page.startswith("12."):
    st.header("🛡️ 포트폴리오 리스크 방패")
    st.write("계좌 전체 리스크(Global Heat)를 6% 이내로 관리합니다.")

elif page.startswith("13."):
    st.header("🗺️ 실시간 히트맵")
    fig = px.treemap(pd.DataFrame({"T": ["NVDA", "AAPL"], "C": [4, -1]}), path=['T'], values=[1,1], color='C', color_continuous_scale='RdYlGn')
    st.plotly_chart(fig, use_container_width=True)

elif page.startswith("14."):
    st.header("🌡️ 시장 심리 게이지")
    st.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=65, gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#FF4B4B"}})), use_container_width=True)
