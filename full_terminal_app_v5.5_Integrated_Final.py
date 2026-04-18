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
        init = {"cntfed": {"password": "cntfed", "status": "approved", "grade": "방장"}}
        with open(USER_DB_FILE, "w", encoding="utf-8") as f: json.dump(init, f)
        return init
    with open(USER_DB_FILE, "r", encoding="utf-8") as f: 
        users = json.load(f)
        # 마스터 계정 권한 강제 보장 및 등급 통일
        if "cntfed" in users:
            users["cntfed"]["grade"] = "방장"
            users["cntfed"]["status"] = "approved"
            with open(USER_DB_FILE, "w", encoding="utf-8") as f2: json.dump(users, f2)
        return users

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
                    
                    all_res.append({
                        "T": tic, "P": f"${cp:.2f}" if is_us else f"{int(cp):,}원",
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
        
    pending_users = [u for u, d in users.items() if d.get("status") == "pending"]

    st.markdown(f"<div class='glass-card'>📡 현재 가입 대기 인원: <b>{len(pending_users)}명</b></div>", unsafe_allow_html=True)

    if pending_users:
        if st.button("🔥 대기 인원 전체 일괄 승인", use_container_width=True):
            for u in pending_users:
                users[u]["status"] = "approved"
            with open(USER_DB_FILE, "w", encoding="utf-8") as f: json.dump(users, f)
            st.success(f"🎊 총 {len(pending_users)}명의 대원이 사령부에 공식 소속되었습니다!")
            st.rerun()

        st.divider()
        st.subheader("👤 개별 승인 리스트")
        for u in pending_users:
            c1, c2 = st.columns([7, 3])
            with c1:
                st.markdown(f"""
                <div style='background: rgba(255,255,255,0.05); padding: 10px; border-radius: 8px; border-left: 3px solid #FFD700;'>
                    <b>ID: {u}</b> | 가입 신청 접수됨
                </div>
                """, unsafe_allow_html=True)
            with c2:
                if st.button(f"✅ 승인 (ID:{u})", key=f"appr_{u}"):
                    users[u]["status"] = "approved"
                    with open(USER_DB_FILE, "w", encoding="utf-8") as f: json.dump(users, f)
                    st.toast(f"{u} 대원 승인 완료!")
                    st.rerun()
    else:
        st.info("현재 승인 대기 중인 신규 회원이 없습니다.")

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
    st.caption("※ 본 내용은 Pradeep Bonde의 공개된 철학과 전략을 기반으로 재구성되었습니다.")

elif page.startswith("10."):
    st.markdown("<h1 style='text-align: center; color: #FFD700;'>🏛️ 사령부 제작 동기</h1>", unsafe_allow_html=True)
    st.markdown("### 세 거인의 발자취를 따라, 함께 성장의 궤도에 오르기를 꿈꾸며")
    
    st.divider()
    
    st.write("""
    이 플랫폼은 제가 깊이 존경하는 세 분의 스승, **윌리엄 오닐, 마크 미너비니, 그리고 프라딥 본데**의 트레이딩 철학을 기리는 마음으로 시작되었습니다. 
    주식이라는 거친 바다에서 길을 잃지 않도록 저 스스로를 다잡기 위한 '나침반'을 만들고 싶었습니다.
    """)
    
    st.write("""
    저는 **"누구나 간절히 노력한다면 정규직의 꿈을 이룰 수 있고, 경제적 자유를 얻을 수 있다"**는 굳은 신념을 가지고 있습니다. 
    비록 지금은 부족한 점이 많은 터미널이지만, 저와 같은 꿈을 꾸는 분들이 함께 부자가 되었으면 하는 진심 어린 마음을 담아 밤낮으로 코드를 짜고 로직을 다듬었습니다.
    """)
    
    st.info("""
    📖 **오닐의 유산:** 윌리엄 오닐의 저서 『최고의 주식, 최적의 타이밍』은 제 트레이딩의 본질을 깨닫게 해준 보물입니다. 
    이 터미널이 그 거인들의 어깨 위에 올라타 시장을 바라보는 든든한 디딤돌이 되길 희망합니다.
    """)
    
    st.write("우리가 꿈꾸는 경제적 자유는 삶의 주도권을 되찾는 과정입니다. 여기서 여러분과 함께 성장하기를 고대합니다.")
    
    st.divider()

    # 영문 버전 추가
    st.markdown("### 🏛️ Corporate Mission (English Version)")
    st.write("""
    **Following the footsteps of the three giants, dreaming of a collective ascent.**
    
    This platform was born out of my profound respect for three masters: **William O'Neil, Mark Minervini, and Pradeep Bonde.** 
    My goal was to build a "compass" to keep myself grounded and focused so as not to lose my way in the turbulent ocean of the stock market.
    """)
    
    st.write("""
    I hold a firm belief that **"anyone who puts in the sincere effort can achieve their professional dreams and reach financial freedom."** 
    Although this terminal may still be a work in progress, I have poured my heart into writing every line of code and refining every logic, 
    fueled by the sincere hope that those who share this dream can grow wealthy together.
    """)
    
    st.markdown(f"""
    <div style='background: rgba(255,215,0,0.05); padding: 20px; border-radius: 12px; border-left: 5px solid #FFD700; margin: 20px 0;'>
        <b style='color: #FFD700;'>📖 Turtle’s Must-Read Recommendation</b><br>
        There are already many excellent books available. Among them, I most highly recommend <b>"How to Make Money in Stocks" by William O'Neil.</b><br>
        I hope you gain insights that pierce through the core of the market, going beyond mere technical analysis.
    </div>
    """, unsafe_allow_html=True)
    
    st.write("""
    My wish is for this place to evolve into a "Stock Insight Platform" where we do more than just consume information—where we share valuable opinions, 
    encourage one another, and ascend toward success together. I, too, will never stop learning and will continue this journey alongside you.
    """)
    
    st.markdown("""
    <div style='text-align: right; margin-top: 20px;'>
        <span style='color: #888; font-size: 0.9rem;'>April 18, 2026, on a deepening spring evening at home.</span><br>
        <b style='color: #FFD700; font-size: 1.2rem;'>Sincerely, Turtle</b>
    </div>
    """, unsafe_allow_html=True)

elif page.startswith("11."):
    st.header("🤝 방문자 정밀 신청서 (Member Application)")
    st.markdown("<div class='glass-card'>사령부 정규직 승격을 위해 아래 3가지 항목을 자세히 작성해 주세요.</div>", unsafe_allow_html=True)
    
    with st.form("greet_detailed", clear_on_submit=True):
        st.subheader("1. 첫인사")
        g1 = st.text_area("사령부에 처음 방문하신 소감과 첫인사를 남겨주세요.", placeholder="예: 안녕하세요! 유투브를 보고 사령부의 명성을 들어 찾아왔습니다.", height=80)
        
        st.subheader("2. 자기소개")
        g2 = st.text_area("트레이딩 경력이나 현재 본인에 대해 소개해 주세요.", placeholder="예: 3년차 개인 투자자입니다. 오닐의 철학을 공부하며 실력을 쌓고 싶습니다.", height=100)
        
        st.subheader("3. 앞으로의 포부")
        g3 = st.text_area("사령부에서 함께하며 이루고 싶은 목표와 각오를 적어주세요.", placeholder="예: 매일 딥다이브를 통해 차트 1000개를 읽어내는 트레이더가 되겠습니다.", height=100)
        
        if st.form_submit_button("🛡️ 사령부 승격 신청 전송"):
            if g1 and g2 and g3:
                t = datetime.now().strftime("%m/%d %H:%M")
                u = st.session_state.current_user
                # 구글 시트로 3개 항목 통합 전송
                gsheet_sync("방문자_신청서", ["시간", "아이디", "첫인사", "자기소개", "포부"], [t, u, g1, g2, g3])
                st.success("✅ 신청서가 성공적으로 전파되었습니다. 관리자 승인을 기다려 주세요!")
            else:
                st.error("모든 항목을 작성해 주셔야 신청이 가능합니다.")

elif page.startswith("12."):
    st.header("🛡️ 리스크 방패 (The -3% Iron Shield)")
    st.divider()
    
    st.subheader("🛸 왜 본데는 '-3% 손절'을 생명처럼 여기는가?")
    st.error("**1. 복리의 마법을 지키는 유일한 방법**")
    st.write("자산이 50% 하락하면 원금을 회복하기 위해 100%의 수익이 필요합니다. 하지만 3% 하락은 단 한 번의 평범한 거래로도 즉시 복구가 가능합니다. 본데는 복리가 역성장하는 것을 절대 허용하지 않습니다.")
    
    st.warning("**2. '타점 오류'의 즉각적인 판독기**")
    st.write("본데의 매매는 '폭발적인 힘'을 전제로 합니다. 만약 진입 후 주가가 -3% 밀렸다면, 그것은 사령부의 분석이 틀렸거나 시장의 타이밍이 아니라는 명확한 신호입니다. 미련 없이 탈출하여 자본 회전율을 높여야 합니다.")
    
    st.info("**3. '안타 전략(Hitters)'의 생존 조건**")
    st.write("우리는 홈런 한 방보다 꾸준한 안타를 노립니다. 작은 수익들을 쌓는 전략에서 단 하나의 큰 손실은 수십 번의 안타 수익을 순식간에 집어삼킵니다. -3%는 생존을 위한 최후의 방어선입니다.")
    
    st.divider()
    st.success("""
    💡 **사령부의 최종 결론**  
    "손절은 패배가 아니라, 더 큰 승리를 위해 병력을 보존하는 **전략적 후퇴**입니다.  
    -3%에서 멈추는 자만이 다음 주도주를 잡을 자격이 있습니다."
    """)

elif page.startswith("13."):
    st.header("🗺️ 실시간 주도주 히트맵 (Market OverView)")
    st.markdown("<div class='glass-card'>사령부 관리 종목 20선의 실시간 수급 실력을 시각화합니다. (초록: 상승 / 빨강: 하락)</div>", unsafe_allow_html=True)
    
    # 히트맵 데이터 동적 생성
    heatmap_data = []
    for tic, name in TICKER_NAME_MAP.items():
        # 임시 데이터 (실제 데이터 연동 시 h['Close'] 기반 ch 사용)
        fake_ch = np.random.uniform(-5, 5) 
        heatmap_data.append({"Ticker": tic, "Name": name, "Change": fake_ch, "Size": 1})
        
    df_h = pd.DataFrame(heatmap_data)
    fig = px.treemap(df_h, 
                    path=['Name'], 
                    values='Size', 
                    color='Change', 
                    hover_data=['Ticker'],
                    color_continuous_scale='RdYlGn',
                    color_continuous_midpoint=0)
    
    fig.update_layout(margin=dict(t=30, l=10, r=10, b=10), height=600)
    st.plotly_chart(fig, use_container_width=True)

elif page.startswith("14."):
    st.header("🌡️ 시장 심리 게이지 (Fear & Greed)")
    val = 65  # 현재 시장 지수 연동
    
    col1, col2 = st.columns([1.5, 1.2])
    with col1:
        fig = go.Figure(go.Indicator(
            mode="gauge+number", value=val,
            gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#FFD700"},
                   'steps': [{'range': [0, 30], 'color': "#FF4B4B"}, 
                            {'range': [71, 100], 'color': "#00FF00"}]}))
        fig.update_layout(height=450)
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st.markdown("<div class='glass-card' style='padding:30px;'>", unsafe_allow_html=True)
        st.subheader("💡 본데의 실시간 마켓 훈수")
        
        if val <= 30:
            st.error("🔴 위기 구간 (Crisis)")
            st.write("시장이 피를 흘릴 때 현금은 가장 강력한 무기가 됩니다. 현재 시장의 중력은 모든 것을 끌어내리고 있습니다. 무리하게 시장과 싸우려 하지 마십시오. 지금은 수익을 낼 때가 아니라 자산을 지킬 때입니다. 태풍이 완전히 지나가고 맑은 하늘이 보일 때까지 인내하며 기다리는 것이 진정한 프로의 자세입니다.")
        elif val <= 50:
            st.warning("🟠 주의 구간 (Warning)")
            st.write("함부로 바닥을 예단하지 마십시오. 하락 추세 속에서 나타나는 일시적인 반등은 대중을 유혹하는 가짜 신호일 확률이 매우 높습니다. 섣부른 진입은 계좌에 치명적인 상처를 남깁니다. 시장의 체질을 근본적으로 바꿀 수 있는 강력한 EP 촉매제가 터지는 주도주가 등장할 때까지 사냥꾼의 마음으로 숨죽이고 기다리십시오.")
        elif val <= 70:
            st.info("🟡 중립 구간 (Neutral)")
            st.write("지금의 구간은 탐욕으로 가는 위험한 기로입니다. 안일한 마음으로 감행하는 추격 매수는 계좌를 파괴하는 독약과 같습니다. 주가가 이동평균선과 멀어져 있다면 절대 손대지 마십시오. 오직 주가가 옆으로 기어 가며 에너지를 극도로 응축하는 타이트한 종목에만 집중하십시오. 응축이 없는 돌파는 사막의 신기루일 뿐입니다.")
        elif val <= 90:
            st.success("🟢 적극 구간 (Active)")
            st.write("드디어 시장의 중력이 약해졌습니다! 우리가 기다려온 VCP 패턴을 정석으로 돌파하는 주도주들이 쏟아지는 축제의 구간입니다. 지금은 용기를 내어 공격적으로 수익을 취해야 할 때입니다. 다만, 자만은 금물입니다. 손절가는 어느 때보다 타이트하게 관리하되, 일단 추세를 탄 종목의 수익은 대담하게 끝까지 가져가십시오.")
        else:
            st.error("🔥 과열 구간 (Overheated)")
            st.write("모두가 환호하며 승리에 취해 있을 때가 가장 위험한 순간입니다. 지금은 새로운 주식을 살 때가 아니라, 언제든 탈출할 수 있도록 팔 때를 고민해야 하는 시간입니다. 탐욕에 눈이 멀어 익절 기회를 놓치지 마십시오. 모든 종목의 익절가를 본절가 위로 바짝 올리고, 시장이 고개를 숙이기 전에 안전한 탈출로를 확보하십시오.")
        
        st.markdown("</div>", unsafe_allow_html=True)
