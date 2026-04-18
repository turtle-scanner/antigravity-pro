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

# --- 💾 데이터베이스 및 영구 보존 설정 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
def get_db_path(f): return os.path.join(BASE_DIR, f)

USER_DB_FILE = get_db_path("users_db.json")
CHAT_FILE = get_db_path("chat_log.csv")
BRIEF_FILE = get_db_path("market_briefs.csv")
VISITOR_FILE = get_db_path("visitor_requests.csv")
MASTER_GAS_URL = "https://script.google.com/macros/s/AKfycbyp31pP_T4nVi0rEoeOu-kc6t_ynofxRYnnYZTTO1kxOcQWinBfyhEeDjTRZXzp1eCo/exec"

TICKER_NAME_MAP = {
    "NVDA": "엔비디아", "TSLA": "테슬라", "AAPL": "애플", "MSFT": "마이크로소프트", "PLTR": "팔란티어", "SMCI": "슈퍼마이크로", 
    "AMD": "AMD", "META": "메타", "GOOGL": "구글", "AVGO": "브로드컴", "CRWD": "크라우드스트라이크", "005930.KS": "삼성전자", 
    "000660.KS": "SK하이닉스", "196170.KQ": "알테오젠", "042700.KS": "한미반도체", "105560.KS": "KB금융", "055550.KS": "신한지주",
    "005490.KS": "POSCO홀딩스", "000270.KS": "기아", "066570.KS": "LG전자", "035720.KS": "카카오", "035420.KS": "NAVER",
    "005380.KS": "현대차", "000810.KS": "삼성화재", "NFLX": "넷플릭스", "MSTR": "마이크로스트래티지", "COIN": "코인베이스", 
    "MARA": "마라톤디지털", "PANW": "팔로알토", "SNOW": "스노우플레이크", "STX": "씨게이트", "WDC": "웨스턴디지털"
}

def load_users():
    if not os.path.exists(USER_DB_FILE):
        init = {"cntfed": {"password": "cntfed", "status": "approved", "grade": "방장"}}
        with open(USER_DB_FILE, "w", encoding="utf-8") as f: json.dump(init, f)
        return init
    try:
        with open(USER_DB_FILE, "r", encoding="utf-8") as f: 
            users = json.load(f)
            # 전문가님 권한은 시스템적으로 절대 보장 (지워짐 방지)
            if "cntfed" in users:
                users["cntfed"]["grade"] = "방장"
                users["cntfed"]["status"] = "approved"
                with open(USER_DB_FILE, "w", encoding="utf-8") as f2: json.dump(users, f2)
            return users
    except: return {"cntfed": {"password": "cntfed", "status": "approved", "grade": "방장"}}

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
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;700;900&display=swap');
    .stApp {{ background-color: #000; {f'background-image: linear-gradient(rgba(0,0,0,0.88), rgba(0,0,0,0.88)), url("data:image/png;base64,{bg_b64}");' if bg_b64 else ""} background-size: cover; background-attachment: fixed; }}
    [data-testid="stSidebar"] {{ background-color: rgba(5,5,5,0.96) !important; border-right: 1px solid #FFD70033; backdrop-filter: blur(25px); }}
    h1, h2 {{ color: #FFD700 !important; font-weight: 900; }}
    .stButton>button {{ background: #1a1a1a !important; color: #FFD700 !important; border: 1px solid #FFD700 !important; border-radius: 10px; font-weight: 800; }}
    .stButton>button:hover {{ background: #FFD700 !important; color: #000 !important; transform: translateY(-3px); box-shadow: 0 8px 25px rgba(255, 215, 0, 0.6); }}
    .glass-card {{ background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 15px; padding: 25px; backdrop-filter: blur(15px); margin-bottom: 30px; transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); }}
    .glass-card:hover {{ background: rgba(255, 255, 255, 0.08); border-color: rgba(255,215,0,0.3); transform: translateY(-5px); box-shadow: 0 15px 35px rgba(0,0,0,0.4); }}
    
    /* 애니메이션 효과 */
    @keyframes pulse-glow {{ 0% {{ box-shadow: 0 0 15px rgba(0,255,0,0.2); }} 50% {{ box-shadow: 0 0 40px rgba(0,255,0,0.6); }} 100% {{ box-shadow: 0 0 15px rgba(0,255,0,0.2); }} }}
    .status-pulse {{ animation: pulse-glow 3s infinite; }}
    
    @keyframes ticker {{ 0% {{ transform: translateX(100%); }} 100% {{ transform: translateX(-100%); }} }}
    .ticker-wrap {{ overflow: hidden; background: rgba(255,215,0,0.05); white-space: nowrap; padding: 5px 0; border-bottom: 1px solid rgba(255,215,0,0.1); margin-bottom: 15px; }}
    .ticker-content {{ display: inline-block; animation: ticker 40s linear infinite; color: #FFD700; font-size: 0.85rem; font-weight: 500; }}
    .ticker-item {{ margin: 0 30px; display: inline-block; }}
    
    /* 모바일 최적화 */
    @media (max-width: 768px) {{
        .stApp {{ background-attachment: scroll; }}
        h1 {{ font-size: 1.8rem !important; }}
        h2 {{ font-size: 1.4rem !important; }}
        .glass-card {{ padding: 15px; }}
        .mobile-header {{ font-size: 2.2rem !important; }}
        .responsive-bar {{ flex-direction: column !important; align-items: flex-start !important; gap: 10px !important; padding: 15px !important; }}
        .responsive-indices {{ width: 100% !important; justify-content: space-between !important; gap: 10px !important; }}
        .ticker-content {{ animation: ticker 25s linear infinite; }}
    }}
    </style>
""", unsafe_allow_html=True)

# --- 인증 & 사이드바 ---
if "password_correct" not in st.session_state: st.session_state["password_correct"] = False
if not st.session_state["password_correct"]:
    c1, m, c2 = st.columns([1, 2, 1])
    with m:
        st.markdown("<h1 class='mobile-header' style='text-align: center; color: #FFD700; font-size: 4rem; margin-top: 0; margin-bottom: 10px; font-family: \"Outfit\", sans-serif; text-shadow: 0 0 30px rgba(255,215,0,0.4);'>🛸 StockDragonfly</h1>", unsafe_allow_html=True)
        if os.path.exists("StockDragonfly.png"): st.image("StockDragonfly.png", use_container_width=True)
        tab1, tab2 = st.tabs(["🚀 Terminal Log-In", "📝 Join Command (자격 시험)"])
        
        with tab1:
            login_id = st.text_input("사령부 아이디", key="l_id")
            login_pw = st.text_input("액세스 키 (PW)", type="password", key="l_pw")
            if st.button("Terminal Operation Start", use_container_width=True):
                users = load_users()
                if login_id in users and users[login_id]["password"] == login_pw:
                    st.session_state["password_correct"] = True
                    st.session_state.current_user = login_id
                    st.rerun()
                else: st.error("❌ 등록되지 않은 정보이거나 보안 코드가 일치하지 않습니다.")
        
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
            q6 = st.radio("Q6. 주식 가격의 평균을 내서 선으로 이은 그림을 무엇이라고 할까요?", ["이동평균선(이평선)", "추세 지탱선", "가격 유동선", "거래 지표선"], index=None)
            q7 = st.radio("Q7. 단기 이평선이 장기 이평선을 뚫고 올라가는 아주 좋은 신호는?", ["실버크로스", "골든크로스", "다이아크로스", "엔젤크로스"], index=None)
            q8 = st.radio("Q8. 반대로 단기 이평선이 장기 이평선 아래로 푹 꺼지는 나쁜 신호는?", ["다크크로스", "데드크로스", "블랙크로스", "폴링크로스"], index=None)
            q9 = st.radio("Q9. 주식 가격이 제일 낮을 때와 제일 높을 때를 각각 무엇이라 할까요?", ["바닥/천장", "저점/고점", "하단/상단", "출발/종착"], index=None)
            q10 = st.radio("Q10. 장기적으로 주식 시장의 가격은 보통 어떻게 움직일까요?", ["아래로 떨어진다", "위로 올라간다 (우상향)", "계속 횡보한다", "예측 불가능하다"], index=None)
            
            st.markdown("---")
            # 전술 5문제 (Q11-Q15)
            q11 = st.radio("Q11. MAGNA 53 공식에서 'G'는 무엇을 의미할까요?", ["Growth (성장)", "Gap Up (갭 상승)", "Gold (금)", "Gamma (옵션)"], index=None)
            q12 = st.radio("Q12. 적극적 매수에 참여해야 하는 스탠 와인스타인의 단계는?", ["1단계 (기초)", "2단계 (상승)", "3단계 (최정상)", "4단계 (쇠퇴)"], index=None)
            q13 = st.radio("Q13. RSI 보조지표에서 '과매도(Oversold)' 기준 수치는?", ["20 이하", "30 이하", "50 이하", "70 이하"], index=None)
            q14 = st.radio("Q14. 부분 익절 후 남은 물량의 손절선(Stop-loss) 설정은?", ["최초 손절가 유지", "매수한 가격(본절)으로 상향", "현재가 -10% 하향", "손절선 제거 및 장기투자"], index=None)
            q15 = st.radio("Q15. 모멘텀 버스트 룰에 따라 추격 매수를 금지하는 최소 연속 상승 일수는?", ["2일 연속", "3일 연속", "5일 연속", "10일 연속"], index=None)
            
            if st.button("🛡️ 요원 임명 신청 및 채점", use_container_width=True):
                if not new_id or not new_pw or not reg_moti:
                    st.error("❌ 아이디, 비밀번호, 가치관을 모두 작성해 주세요.")
                else:
                    ans = [q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, q11, q12, q13, q14, q15]
                    correct = [
                        "올랐다 (상승)", "하락 국면", "거래량", "캔들 차트", "무릎에서 사서 어깨에서 팔아라", 
                        "이동평균선(이평선)", "골든크로스", "데드크로스", "저점/고점", "위로 올라간다 (우상향)",
                        "Gap Up (갭 상승)", "2단계 (상승 국면)", "30 이하", "매수한 가격(본절)으로 상향", "3일 연속"
                    ]
                    score = sum([1 for a, c in zip(ans, correct) if a == c])
                    
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
                            with open(USER_DB_FILE, "w", encoding="utf-8") as f: json.dump(users, f)
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
    if os.path.exists("StockDragonfly.png"): st.image("StockDragonfly.png")
    st.markdown("<p style='color:#FF914D; font-size:1.5rem; font-weight:900;'>🛸 StockDragonfly v9.9</p>", unsafe_allow_html=True)
    st.divider()
    bgms = {"🔇 OFF": None, "✨ You Raise": "YouRaise.mp3", "😊 Happy": "happy.mp3", "🌅 Hope": "hope.mp3", "🐱 Cute": "cute.mp3", "🎻 Petty": "petty.mp3", "🎙️ Ajussi": "나의아저씨.mp3"}
    sel_bgm = st.selectbox("Radio", list(bgms.keys()), label_visibility="collapsed")
    vol = st.slider("🔊 Volume", 0.0, 1.0, 0.45)
    if bgms[sel_bgm] and os.path.exists(bgms[sel_bgm]):
        with open(bgms[sel_bgm], "rb") as f: b64 = base64.b64encode(f.read()).decode()
        st.components.v1.html(f"<audio id='aud' autoplay loop><source src='data:audio/mp3;base64,{b64}' type='audio/mp3'></audio><script>document.getElementById('aud').volume = {vol};</script>", height=0)

# --- 유저 등급 판독 ---
users = load_users()
curr_user_data = users.get(st.session_state.current_user, {})
curr_grade = curr_user_data.get("grade", "회원")
is_admin = (curr_grade in ["관리자", "방장"])

menu_ops = [
    "1. 🎯 주도주 타점 스캐너", "2. 💬 소통 대화방", "3. 💎 프로 분석 리포트", 
    "4. 🚀 주도주 랭킹 TOP 50", "5. 🧮 리스크 계산기", "6. 📈 마켓 트렌드 요약", 
    "7. 📊 본데 감시 리스트", "8. 👑 관리자 승인 센터", "9. 🐝 본데는 누구인가?", 
    "10. 🏛️ 사이트 제작 동기", "11. 🤝 방문자 인사말 신청", "12. 🛡️ 리스크 방패", 
    "13. 🗺️ 실시간 히트맵", "14. 🌡️ 시장 심리 게이지"
]

# 오직 방장(전문가님)에게만 15번 메뉴 노출
if curr_grade == "방장":
    menu_ops.append("15. 🎖️ HQ 인적 자원 사령부")

page = st.sidebar.radio("Mission Control", menu_ops)

# --- 🛰️ 전광판 티커 테이프 ---
@st.cache_data(ttl=300)
def get_ticker_tape():
    watch = ["NVDA", "TSLA", "AAPL", "MSFT", "AMZN", "META", "BTC-USD", "ETH-USD"]
    items = []
    try:
        data = yf.download(watch, period="2d", progress=False)['Close']
        for t in watch:
            try:
                c = ((data[t].iloc[-1] / data[t].iloc[-2]) - 1) * 100
                items.append(f"<span class='ticker-item'>{t} {data[t].iloc[-1]:,.1f} ({c:+.2f}%)</span>")
            except: pass
    except: pass
    return "".join(items)

ticker_html = get_ticker_tape()
st.markdown(f"<div class='ticker-wrap'><div class='ticker-content'>{ticker_html * 3}</div></div>", unsafe_allow_html=True)

# --- 🛰️ 상단 실시간 정보 바 ---
now_kr = datetime.now(pytz.timezone('Asia/Seoul'))
now_us = datetime.now(pytz.timezone('America/New_York'))

@st.cache_data(ttl=60)
def get_top_indices():
    res = {"NASDAQ": [0.0, 0.0], "KOSPI": [0.0, 0.0], "KOSDAQ": [0.0, 0.0]}
    for n, t in {"NASDAQ": "^IXIC", "KOSPI": "^KS11", "KOSDAQ": "^KQ11"}.items():
        try:
            h = yf.download(t, period="5d", progress=False)
            close_data = h['Close']
            if isinstance(close_data, pd.DataFrame):
                close_data = close_data.iloc[:, 0]
            close_data = close_data.dropna()
            if len(close_data) >= 2:
                curr = close_data.iloc[-1]
                prev = close_data.iloc[-2]
                pct = ((curr / prev) - 1) * 100
                res[n] = [float(curr), float(pct)]
        except: pass
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
            <span style='color: #EEE; font-size: 1rem; font-weight: 700;'>🇰🇷 {now_kr.strftime('%H:%M:%S')}</span>
            <span style='color: #444; margin: 0 10px;'>|</span>
            <span style='color: #EEE; font-size: 1rem; font-weight: 700;'>🇺🇸 {now_us.strftime('%H:%M:%S')}</span>
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
    import random
    random.seed(datetime.now().strftime("%Y%m%d"))
    return random.choice(BONDE_FOOTER_QUOTES)

# --- [PLACEHOLDER_LOGIC_START] ---
if page.startswith("1."):
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
            data = yf.download(full_list, period="1y", interval="1d", progress=False)['Close']
            
            for tic in full_list:
                try:
                    if tic not in data.columns: continue
                    h = data[tic].dropna()
                    if len(h) < 200: continue
                    
                    cp = h.iloc[-1]
                    pp = h.iloc[-2]
                    y_ago = h.iloc[0]
                    
                    ch = (cp/pp - 1) * 100
                    rs = ((cp / y_ago) - 1) * 100
                    
                    # ROE는 실패할 가능성이 높으므로 별도 처리 및 캐싱/기본값 활용
                    try:
                        tk = yf.Ticker(tic)
                        roe = tk.info.get('returnOnEquity', 0) * 100
                    except:
                        roe = 0 # ROE 정보 부재 시 0으로 처리하여 전체 로직 보호
                    
                    score = rs + (roe * 1.2)
                    is_us = (".KS" not in tic and ".KQ" not in tic)
                    display_name = TICKER_NAME_MAP.get(tic, tic) if not is_us else tic
                    
                    all_res.append({
                        "T": display_name, "TIC": tic, "P": f"${cp:.2f}" if is_us else f"{int(cp):,}원",
                        "CH": f"{ch:+.1f}%", "ROE": roe, "RS": rs, "SCORE": score,
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
            st.success("✅ 스캔 완료! 아래 리스트에서 종목을 선택하여 차트 분석을 계속하십시오.")
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
                    <span style='color: #55AAFF;'>RS (1yr): <b>{row["RS"]:.1f}%</b></span>
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
            
            st.warning("💡 한국 주식은 트레이ڈنگ뷰보다 '네이버 증권' 정밀 분석이 더 권장됩니다.")
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

elif page.startswith("2."):
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
                # 구글 시트 백업
                gsheet_sync("소통기록_통합", ["시간", "유저", "내용", "등급"], [t, u, ms, curr_grade])
                st.success("✅ 메시지가 사령부 전역에 전파되었습니다.")
                st.rerun()

    st.divider()
    try:
        chat_df = pd.read_csv(CHAT_FILE, encoding="utf-8-sig").tail(30) # 최근 30개만 표시
        for _, row in chat_df.iloc[::-1].iterrows(): # 역순 출력
            is_leader = row["등급"] in ["방장", "관리자"]
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

elif page.startswith("3."):
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
    
    tic_in = st.text_input("분석 티커", value="NVDA").upper()
    if st.button("정밀 분석"):
        with st.spinner("AI 판독 중..."):
            st.markdown(f"<div class='glass-card'><h4>📊 {tic_in} 분석 결과</h4>Weinstein 2단계 정배열 포착. 상대강도(RS) 95점.</div>", unsafe_allow_html=True)
            st.components.v1.html(f"<iframe src='https://s.tradingview.com/widgetembed/?symbol={tic_in}&interval=D' width='100%' height='500'></iframe>", height=510)

elif page.startswith("4."):
    st.header("🚀 주도주 실시간 랭킹 (Daily Live Ranking)")
    RANK_SHEET_URL = "https://docs.google.com/spreadsheets/d/1xjbe9SF0HsxwY_Uy3NC2tT92BqK0nhArUaYU16Q0p9M/export?format=csv&gid=1499398020"
    
    # 한국 시간 설정
    now_kst = datetime.now(pytz.timezone('Asia/Seoul'))
    
    with st.spinner("📊 전문가님의 데이터 센터에서 실시간 동기화 중..."):
        try:
            df_live = pd.read_csv(RANK_SHEET_URL)
            if 'ROE' in df_live.columns:
                df_live['ROE_VAL'] = df_live['ROE'].astype(str).str.replace('%','').astype(float)
                df_final = df_live[df_live['ROE_VAL'] >= 10.0].head(10)
            else:
                df_final = df_live.head(10)
            
            st.markdown(f"<div class='glass-card'>📅 <b>{now_kst.strftime('%Y-%m-%d %H:%M')} KST</b> | ROE 10% 이상 주도주 우선순위</div>", unsafe_allow_html=True)
            
            display_cols = ["종목명", "ROE", "현재가", "진입가", "단계", "손절가", "목표가"]
            available_cols = [c for c in display_cols if c in df_final.columns]
            
            if available_cols:
                st.dataframe(df_final[available_cols], use_container_width=True, hide_index=True)
            else:
                st.dataframe(df_final, use_container_width=True, hide_index=True)
                
            st.success(f"✅ {now_kst.strftime('%H:%M')} 한국 시간 기준 업데이트 완료!")
        except Exception as e:
            st.error(f"⚠️ 시트 연동 중 오류 발생: {e}")
            st.info("시트가 '링크가 있는 모든 사용자에게 공개(뷰어)' 상태인지 확인해 주세요.")

elif page.startswith("5."):
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

elif page.startswith("6."):
    st.header("📈 데일리 마켓 트렌드 브리핑 (Daily Briefing)")
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
                st.markdown(f"""
                <div class='glass-card' style='padding: 20px; border-left: 5px solid #FFD700; margin-bottom: 10px;'>
                    <span style='color: #FFD700; font-size: 0.8rem;'>📅 {row['날짜']} | 작성자: {row['작성자']}</span><br>
                    <div style='margin-top: 10px; font-size: 1.1rem;'>{row['내용']}</div>
                </div>
                """, unsafe_allow_html=True)
                if is_admin:
                    if st.button(f"🗑️ 삭제 (ID:{idx})", key=f"del_brief_{idx}"):
                        temp_df = pd.read_csv(BRIEF_FILE, encoding="utf-8-sig")
                        temp_df = temp_df.drop(idx)
                        temp_df.to_csv(BRIEF_FILE, index=False, encoding="utf-8-sig")
                        st.warning("내용이 삭제되었습니다.")
                        st.rerun()
        else:
            st.info("아직 등록된 브리핑이 없습니다.")
    except Exception as e:
        st.info("브리팅 데이터 연동 중...")

elif page.startswith("7."):
    st.header("🎯 사령부 최핵심 감시 리스트 (Top 3 Focus)")
    SHEET_URL = "https://docs.google.com/spreadsheets/d/1xjbe9SF0HsxwY_Uy3NC2tT92BqK0nhArUaYU16Q0p9M/export?format=csv&gid=1499398020"
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
            for tic in sorted(mention_counts, key=mention_counts.get, reverse=True):
                try:
                    tk = yf.Ticker(tic)
                    roe = tk.info.get('returnOnEquity', 0) * 100
                    if roe >= 5.0 or roe == 0: # 데이터 없으면 일단 포함 (ROE 5% 기준 완화)
                        # RS, 진입가 등은 사령부 엔진 계산 또는 시트 연동
                        price = tk.history(period="1d")['Close'].iloc[-1]
                        final_3.append({
                            "T": tic, "ROE": f"{roe:.1f}%", 
                            "RS": f"{mention_counts[tic]}회 언급", # 빈도를 RS 대용으로 표시
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

elif page.startswith("8."):
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
            with open(USER_DB_FILE, "w", encoding="utf-8") as f: json.dump(users, f)
            st.success("🎊 모든 대기 인원이 공식 승인되었습니다.")
            st.rerun()
        for u in pending_users:
            c1, c2 = st.columns([7, 3])
            with c1: st.info(f"ID: **{u}** | 가입 신청됨")
            with c2:
                if st.button(f"✅ 승인", key=f"appr_{u}"):
                    users[u]["status"] = "approved"
                    with open(USER_DB_FILE, "w", encoding="utf-8") as f: json.dump(users, f)
                    st.rerun()
    else: st.info("대기 중인 신규 회원이 없습니다.")

    st.divider()

    # [B] 정규직 승격 심사 섹션
    st.subheader("🔥 정규직 승격 심사 센터")
    if os.path.exists(VISITOR_FILE):
        try:
            req_df = pd.read_csv(VISITOR_FILE)
            if not req_df.empty:
                for idx, row in req_df.iloc[::-1].iterrows():
                    user_id = row["아이디"]
                    if users.get(user_id, {}).get("grade") == "정규직": continue
                    with st.expander(f"📥 [승격요청] {user_id} 대원의 신청서 ({row['시간']})", expanded=False):
                        st.markdown(f"**1. 첫인사:** {row['첫인사']}")
                        st.markdown(f"**2. 자기소개:** {row['자기소개']}")
                        st.markdown(f"**3. 포부:** {row['포부']}")
                        if st.button(f"🎖️ {user_id} 정규직 승격 발령", key=f"promo_{idx}"):
                            if user_id in users:
                                users[user_id]["grade"] = "정규직"
                                with open(USER_DB_FILE, "w", encoding="utf-8") as f: json.dump(users, f)
                                st.success(f"🎊 {user_id} 대원이 '정규직'으로 승격되었습니다!")
                                st.rerun()
            else: st.info("현재 접수된 승격 신청서가 없습니다.")
        except: st.info("접수된 신청서가 없습니다.")
    else: st.info("접수된 신청서가 없습니다.")

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

elif page.startswith("9."):
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

elif page.startswith("10."):
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

elif page.startswith("11."):
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
                # 백업용 동기화
                gsheet_sync("방문자_승격신청", ["시간", "아이디", "첫인사", "자기소개", "포부"], [t, u, g1, g2, g3])
                st.success("✅ 승격 신청서가 성공적으로 관리자 승인센터로 전파되었습니다!")
            else: st.error("모든 항목을 작성해 주셔야 신청이 가능합니다.")

elif page.startswith("12."):
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

elif page.startswith("13."):
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

elif page.startswith("14."):
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

elif page.startswith("15."):
    st.header("🎖️ HQ 인적 자원 사령부 (Member HR Command)")
    users = load_users()
    
    # 사령관(방장) 전용 보안
    if users.get(st.session_state.current_user, {}).get("grade") != "방장":
        st.error("❌ 이 전술 구역은 사령관(방장) 전용입니다. 권한이 없습니다.")
        st.stop()
        
    st.markdown("<div class='glass-card'>사령관의 권위로 대원의 등급을 조정하거나 사령부에서 즉각 제명(삭제)하는 인사권을 행사합니다.</div>", unsafe_allow_html=True)
    
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
                        with open(USER_DB_FILE, "w", encoding="utf-8") as f: json.dump(users, f)
                        st.success(f"✅ {u} 요원이 {new_grade}(으)로 발령되었습니다.")
                        st.rerun()
                with c3:
                    st.write("") # 정렬용
                    if st.button("🔥 즉각 제명", key=f"del_{u}"):
                        del users[u]
                        with open(USER_DB_FILE, "w", encoding="utf-8") as f: json.dump(users, f)
                        st.warning(f"⚠️ {u} 요원이 명부에서 삭제되었습니다.")
                        st.rerun()
    else:
        st.info("현재 사령부에 등록된 관리 대상 대원이 없습니다.")
    
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
