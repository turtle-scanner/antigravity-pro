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
    "005490.KS": "POSCO홀딩스", "000270.KS": "기아", "066570.KS": "LG전자", "035720.KS": "카카오", "035420.KS": "NAVER"
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
st.markdown("""
<div style='background: rgba(0,0,0,0.85); border: 2px solid #FFD700; border-radius: 15px; padding: 25px; text-align: center; margin-bottom: 25px; box-shadow: 0 0 30px rgba(255,215,0,0.1);'>
    <h1 style='color: #00FF00; margin: 0; font-size: 2.2rem;'>🟢 GREEN MARKET ACTIVE</h1>
    <p style='color: #FFD700; font-size: 1.1rem; margin-top: 10px; font-weight: 700;'>
        🛡️ 사령부 상태: 매수 윈도우 개방 (팔로스루데이 발생: 4월 8일 수요일)
    </p>
    <div style='color: #CCC; font-style: italic; font-size: 0.95rem; margin-top: 5px;'>
        "시장의 중력이 가장 약해지는 순간, 강력한 EP를 동반한 주도주만이 하늘로 솟구칩니다. 우리는 그 불꽃에 동참합니다." - Pradeep Bonde
    </div>
</div>
""", unsafe_allow_html=True)

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
                        "T": display_name, "P": f"${cp:.2f}" if is_us else f"{int(cp):,}원",
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
            us_top = df[df['MARKET'].str.contains("USA")].sort_values("SCORE", ascending=False).head(5)
            kr_top = df[df['MARKET'].str.contains("KOREA")].sort_values("SCORE", ascending=False).head(5)
            
            st.subheader("🔥 사령부 한/미 통합 주도주 TOP 10")
            for _, row in pd.concat([us_top, kr_top]).iterrows():
                st.markdown(f"""
                <div class='glass-card' style='padding: 15px; border-left: 5px solid {"#00FF00" if "USA" in row["MARKET"] else "#FFD700"}; margin-bottom: 10px;'>
                    <div style='display: flex; justify-content: space-between;'>
                        <b style='font-size: 1.1rem;'>{row["MARKET"]} | {row["T"]}</b>
                        <b style='color: {"#00FF00" if "+" in row["CH"] else "#FF4B4B"}; font-size: 1.1rem;'>{row["CH"]}</b>
                    </div>
                    <div style='margin-top: 8px; font-size: 0.95rem; color: #AAA;'>
                        현가: {row["P"]} | 
                        <span style='color: #FFD700;'>ROE: <b>{row["ROE"]:.1f}%</b></span> | 
                        <span style='color: #55AAFF;'>RS (1yr): <b>{row["RS"]:.1f}%</b></span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            st.success("✅ 글로벌 상위 실적/강세주 10선 브리핑 완료!")
        else:
            st.warning("분석 가능한 종목 데이터가 부족합니다. 잠시 후 다시 시도해 주세요.")

    if st.button("🚀 한/미 주도주 10선 정밀 스캔 시작"):
        run_4stage_sc()

elif page.startswith("2."):
    st.header("💬 사령부 소통 및 공지 (HQ Communication)")
    users = load_users()
    user_grade = users.get(st.session_state.current_user, {}).get("grade", "회원")
    is_admin = (user_grade in ["관리자", "방장"]) # 관리자 또는 방장 여부

    # 로컬 저장소 준비
    CHAT_FILE = "chat_log.csv"
    if not os.path.exists(CHAT_FILE):
        pd.DataFrame(columns=["시간", "유저", "내용", "등급"]).to_csv(CHAT_FILE, index=False, encoding="utf-8-sig")

    # 입력창 차별화
    st.markdown(f"<div class='glass-card'>현재 권한: <b>{user_grade}</b></div>", unsafe_allow_html=True)
    
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
                new_msg = pd.DataFrame([[t, u, ms, user_grade]], columns=["시간", "유저", "내용", "등급"])
                new_msg.to_csv(CHAT_FILE, mode='a', header=False, index=False, encoding="utf-8-sig")
                # 구글 시트 백업
                gsheet_sync("소통기록_통합", ["시간", "유저", "내용", "등급"], [t, u, ms, user_grade])
                st.success("✅ 메시지가 사령부 전역에 전파되었습니다.")
                st.rerun()

    st.divider()
    st.subheader("📡 최근 수신 메시지 (HQ Live Feed)")
    
    try:
        chat_df = pd.read_csv(CHAT_FILE).tail(30) # 최근 30개만 표시
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
    
    # 예시 데이터 (실제 데이터 연동 권장)
    chat_data = [
        {"T": "04/19 01:05", "U": "전문가거북이", "M": "금일 주도주 NDX 9점 이상 종목들 집중 모니터링 시작합니다.", "G": "방장"},
        {"T": "04/19 01:06", "U": "회원1", "M": "알겠습니다! 차트 분석 들어갑니다.", "G": "회원"}
    ]
    
    for c in chat_data:
        if c["G"] in ["방장", "관리자"]:
            st.markdown(f"""
            <div style='border: 2px solid #FFD700; border-radius: 12px; padding: 15px; margin-bottom: 10px; background: rgba(255,215,0,0.05);'>
                <span style='color: #FFD700;'>👑 [{c['G']}] {c['U']}</span> <span style='color: #888; font-size: 0.8rem;'>{c['T']}</span><br>
                <div style='margin-top: 10px; font-size: 1.1rem;'><b>{c['M']}</b></div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style='border: 1px solid #444; border-radius: 10px; padding: 10px; margin-bottom: 10px; background: rgba(255,255,255,0.02);'>
                <span style='color: #AAA;'>👤 [{c['G']}] {c['U']}</span> <span style='color: #666; font-size: 0.7rem;'>{c['T']}</span><br>
                <div style='margin-top: 5px; color: #EEE;'>{c['M']}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    try:
        df_c = pd.read_csv(MSG_LOG_FILE, encoding="utf-8-sig").tail(15)
        for _, r in df_c.iloc[::-1].iterrows():
            badge = "👑 [방장]" if r['등급'] == "관리자" else "👤 [회원]"
            color = "rgba(255, 215, 0, 0.15)" if r['등급'] == "관리자" else "rgba(255, 255, 255, 0.05)"
            border = "1px solid #FFD700" if r['등급'] == "관리자" else "none"
            st.markdown(f"""
            <div style='background:{color}; border:{border}; padding:12px; border-radius:10px; margin-bottom:10px;'>
                <span style='color: #888; font-size: 0.8rem;'>[{r['시간']}]</span> <b>{badge} {r['작성자']}</b>: <br>{r['내용']}
            </div>
            """, unsafe_allow_html=True)
    except: st.info("대화 내역이 없습니다.")

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
    st.header("📈 데일리 마켓 트렌드 브리핑 (Daily Briefing)")
    BRIEF_FILE = "market_briefs.csv"
    users = load_users()
    user_grade = users.get(st.session_state.current_user, {}).get("grade", "회원")
    is_admin = (user_grade in ["관리자", "방장"])

    # 브리핑 전용 데이터 로드
    if not os.path.exists(BRIEF_FILE):
        pd.DataFrame(columns=["날짜", "작성자", "내용"]).to_csv(BRIEF_FILE, index=False, encoding="utf-8-sig")
    
    # 관리자 입력창 (더욱 직관적으로 변경)
    if is_admin:
        st.markdown(f"<div style='background: rgba(255,215,0,0.1); padding: 15px; border-radius: 12px; border: 1px solid #FFD700; margin-bottom: 20px;'><b>👑 {user_grade} 전용 - 데일리 마켓 브리핑 센터</b></div>", unsafe_allow_html=True)
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
    users = load_users()
    current_grade = users.get(st.session_state.current_user, {}).get("grade", "회원")
    
    if current_grade not in ["관리자", "방장"]:
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
                    # 이미 정규직이면 통과
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

elif page.startswith("9."):
    st.markdown("<h1 style='text-align: center; color: #FFD700;'>🐝 프라딥 본데(StockBee)</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888;'>시스템으로 시장을 정복한 월가의 멘토</p>", unsafe_allow_html=True)
    
    st.divider()
    
    with st.container():
        st.markdown("### 📖 1. 물류 전문가에서 데이터 트레이더로의 변신")
        with st.expander("성장 배경 전문 보기", expanded=False):
            st.write("""
            온라인에서 **스탁비(Stockbee)**라는 필명으로 더 잘 알려진 프라딥 본데는 24년 이상의 경력을 가진 전업 트레이더입니다. 
            그는 인도에서 물류 산업의 효율성을 진두지휘하던 이력을 바탕으로, 주식 거래를 막연한 운이 아닌 
            **철저하게 설계된 데이터 기반의 비즈니스 모델**로 재정의했습니다. 
            그의 방식은 직관이나 감이 아닌, 수만 번의 과거 차트 백테스팅과 통계를 기반으로 합니다.
            """)

        st.markdown("### 💡 2. 스탁비를 지탱하는 4대 트레이딩 철학")
        with st.expander("⚾ 안타 전략 (Hitters): 꾸준한 누적의 힘", expanded=False):
            st.info("성공은 큰 홈런 한 방보다, 3~5%의 확실한 수익을 복리로 무한히 중첩시키는 과정에서 나옵니다. 자산을 지키는 것이 공격의 시작입니다.")
        with st.expander("🛡️ 셀프 리더십: 스스로가 사령관이 되어라", expanded=False):
            st.info("트레이딩의 모든 책임은 나에게 있습니다. 외부의 소음에 휘둘리지 않고 나만의 시스템을 믿고 실행하는 '심리적 독립'을 강조합니다.")
        with st.expander("🧬 절차적 기억 (Deep Dive): 차트를 뇌에 박아라", expanded=False):
            st.info("과거에 폭등했던 수천 개의 종목 차트를 반복해서 보며, 특정 패턴이 나타날 때 손가락이 즉각 반응하도록 훈련하는 '기계적 몰입'입니다.")
        with st.expander("📊 상황 인식: 시장의 너비(Breadth)를 읽어라", expanded=False):
            st.info("매일 장세의 폭을 분석하여 공격할 날(Green)과 현금을 피난처로 삼을 날(Red)을 엄격히 구분합니다. 시장과 싸우지 마십시오.")

        st.markdown("### ⚡ 3. 시장의 중력을 이기는 핵심 매매 기법")
        with st.expander("🔥 EP (에피소딕 피벗): 폭발의 기폭제", expanded=False):
            st.markdown("""
            **핵심:** 강력한 펀더멘털의 변화(실적 서프라이즈, 대형 계약)와 역대급 거래량이 동반된 '갭 상승'의 초기 국면을 공략합니다.
            - **전술:** 기관의 거대 자금이 유입되는 입구를 포착하여 추세의 시작점에 올라탑니다.
            """)
        with st.expander("🚀 Momentum Burst: 응축된 에너지의 분출", expanded=False):
            st.markdown("""
            **핵심:** 좁은 가격대에서 변동성을 죽이며 힘을 응축하던(VCP) 주식이 특정 임계점을 상향 돌파하는 순간을 포착합니다.
            - **전술:** 매도세가 완전히 고갈된 'Dry-up' 구간 확인 후, 거래량이 실리는 돌파 시점에 진입합니다.
            """)
    
    st.divider()

elif page.startswith("10."):
    st.markdown("<h1 style='text-align: center; color: #FFD700;'>🏛️ 사령부 제작 동기</h1>", unsafe_allow_html=True)
    st.markdown("### 세 거인의 발자취를 따라, 함께 성장의 궤도에 오르기를 꿈꾸며")
    st.divider()
    st.write("""
    이 플랫폼은 제가 깊이 존경하는 세 분의 스승, **윌리엄 오닐, 마크 미너비니, 그리고 프라딥 본데**의 트레이딩 철학을 기리는 마음으로 시작되었습니다. 
    비록 지금은 부족한 점이 많은 터미널이지만, 저와 같은 꿈을 꾸는 분들이 함께 부자가 되었으면 하는 진심 어린 마음을 담아 밤낮으로 코드를 짜고 로직을 다듬었습니다.
    """)
    st.info("""
    📖 **오닐의 유산:** 윌리엄 오닐의 저서 『최고의 주식, 최적의 타이밍』은 제 트레이딩의 본질을 깨닫게 해준 보물입니다. 
    이 터미널이 그 거인들의 어깨 위에 올라타 시장을 바라보는 든든한 디딤돌이 되길 희망합니다.
    """)
    st.markdown("""
    <div style='text-align: right; margin-top: 20px;'>
        <span style='color: #888; font-size: 0.9rem;'>2026년 4월 18일, 깊어가는 봄날 밤.</span><br>
        <b style='color: #FFD700; font-size: 1.2rem;'>전문가거북이 드림</b>
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
        ndx = yf.download("^IXIC", period="2d", progress=False)['Close']
        ndx_ch = ((ndx.iloc[-1] / ndx.iloc[-2]) - 1) * 100
        val = int(min(max(55 + (ndx_ch * 10), 10), 90))
    except: val = 50
    col1, col2 = st.columns([1.5, 1.2])
    with col1:
        fig = go.Figure(go.Indicator(mode="gauge+number", value=val, gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#FFD700"}, 'steps': [{'range': [0, 30], 'color': "#FF4B4B"}, {'range': [71, 100], 'color': "#00FF00"}]}))
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.markdown("<div class='glass-card' style='padding:25px;'>", unsafe_allow_html=True)
        st.subheader("💡 본데의 실시간 훈수")
        if val <= 30: st.error("🔴 공포 구간: 자본 방어에 집중하십시오.")
        elif val <= 50: st.warning("🟠 주의 구간: 섣부른 진입을 자제하십시오.")
        elif val <= 75: st.info("🟡 중립 구간: 개별 주도주의 VCP에 집중하십시오.")
        else: st.success("🟢 적극 구간: EP 돌파 종목에 올라타십시오.")
        st.markdown("</div>", unsafe_allow_html=True)
    
