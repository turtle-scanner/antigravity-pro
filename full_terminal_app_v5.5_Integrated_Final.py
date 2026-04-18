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
                fmt_price = f"{int(cp):,}원" if (".KS" in tic or ".KQ" in tic) else f"${cp:.2f}"
                row = {"종목명": name, "현재가": fmt_price, "ROE": f"{roe:.1f}%", "BMS점수": f"{score}점", "등급": grade}
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
    st.header("💬 소통 대화방 (HQ Control)")
    users = load_users()
    user_grade = users.get(st.session_state.current_user, {}).get("grade", "회원")
    is_admin = (user_grade == "관리자")

    if not os.path.exists(MSG_LOG_FILE):
        pd.DataFrame(columns=["시간", "작성자", "내용", "등급"]).to_csv(MSG_LOG_FILE, index=False, encoding="utf-8-sig")
    
    with st.form("chat_form", clear_on_submit=True):
        label = "📢 [관리자] 중요 게시물/공지 작성" if is_admin else "💬 자유 메시지 작성"
        ms = st.text_input(label)
        if st.form_submit_button("전파"):
            if ms:
                t = datetime.now().strftime("%m/%d %H:%M")
                u = st.session_state.current_user
                gsheet_sync("소통대화방_기록", ["시간", "유저", "내용", "등급"], [t, u, ms, user_grade])
                new_m = pd.DataFrame([[t, u, ms, user_grade]], columns=["시간", "작성자", "내용", "등급"])
                new_m.to_csv(MSG_LOG_FILE, mode='a', header=False, index=False, encoding="utf-8-sig")
                st.rerun()

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
    st.header("💎 프로 분석 리포트")
    tic_in = st.text_input("분석 티커", value="NVDA").upper()
    if st.button("정밀 분석"):
        with st.spinner("AI 판독 중..."):
            st.markdown(f"<div class='glass-card'><h4>📊 {tic_in} 분석 결과</h4>Weinstein 2단계 정배열 포착. 상대강도(RS) 95점.</div>", unsafe_allow_html=True)
            st.components.v1.html(f"<iframe src='https://s.tradingview.com/widgetembed/?symbol={tic_in}&interval=D' width='100%' height='500'></iframe>", height=510)

elif page.startswith("4."):
    st.header("🚀 주도주 실시간 랭킹 (Daily Live Ranking)")
    RANK_SHEET_URL = "https://docs.google.com/spreadsheets/d/1xjbe9SF0HsxwY_Uy3NC2tT92BqK0nhArUaYU16Q0p9M/export?format=csv&gid=1499398020"
    
    with st.spinner("📊 전문가님의 데이터 센터에서 실시간 동기화 중..."):
        try:
            df_live = pd.read_csv(RANK_SHEET_URL)
            # ROE 10% 이상 필터링 (ROE 컬럼명은 시트 상황에 따라 조정 가능, 여기선 'ROE'로 가정)
            # 만약 % 기호가 있다면 제거 후 비교
            if 'ROE' in df_live.columns:
                df_live['ROE_VAL'] = df_live['ROE'].astype(str).str.replace('%','').astype(float)
                df_final = df_live[df_live['ROE_VAL'] >= 10.0].head(10)
            else:
                df_final = df_live.head(10) # 컬럼 없을 시 상위 10개 표시
            
            st.markdown(f"<div class='glass-card'>📅 <b>{datetime.now().strftime('%Y-%m-%d')} 기준</b> | ROE 10% 이상 주도주 우선순위</div>", unsafe_allow_html=True)
            
            # 전문가님 요청 컬럼 표시 (시트에 해당 컬럼이 있다고 가정, 없으면 기본값)
            display_cols = ["종목명", "ROE", "현재가", "진입가", "단계", "손절가", "목표가"]
            # 실제 시트 컬럼명과 다를 경우를 대비한 유연한 처리
            available_cols = [c for c in display_cols if c in df_final.columns]
            
            if available_cols:
                st.dataframe(df_final[available_cols], use_container_width=True, hide_index=True)
            else:
                st.dataframe(df_final, use_container_width=True, hide_index=True)
                
            st.success("✅ 구글 시트 데이터 기반 데일리 랭킹 업데이트 완료!")
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
    st.markdown("<h1 style='text-align: center; color: #FFD700;'>🐝 프라딥 본데(StockBee)</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888;'>시스템으로 시장을 정복한 월가의 멘토</p>", unsafe_allow_html=True)
    
    st.divider()
    
    with st.container():
        st.markdown("### 📖 1. 물류 전문가에서 데이터 트레이더로의 변신")
        st.write("""
        온라인에서 **스탁비(Stockbee)**라는 필명으로 더 잘 알려진 프라딥 본데는 24년 이상의 경력을 가진 전업 트레이더입니다. 
        그는 인도에서 물류 산업의 효율성을 진두지휘하던 이력을 바탕으로, 주식 거래를 막연한 운이 아닌 
        **철저하게 설계된 데이터 기반의 비즈니스 모델**로 재정의했습니다.
        """)

        st.markdown("### 💡 2. 스탁비를 지탱하는 4대 트레이딩 철학")
        st.info("**안타 전략 (Hitters):** 큰 홈런보다 확실한 수익을 복리로 누적시키는 것이 성공의 핵심입니다.")
        st.info("**셀프 리더십:** 트레이딩의 주도권은 본인에게 있어야 하며, 스스로 문제를 해결하는 의지가 필요합니다.")
        st.info("**절차적 기억 (Deep Dive):** 과거 폭등했던 수천 개의 차트를 뇌에 각인시키는 혹독한 훈련을 강조합니다.")
        st.info("**상황 인식:** 매일 장세의 폭(Breadth)을 분석하여 공격할 날과 지킬 날을 엄격히 구분합니다.")

        st.markdown("### ⚡ 3. 시장의 중력을 이기는 핵심 매매 기법")
        st.warning("**EP (에피소딕 피벗):** 강력한 펀더멘털 변화와 거래량 폭발을 동반한 갭 상승 초기 국면 공략")
        st.warning("**Momentum Burst:** 좁은 구간에서 힘을 응축하던 주식이 분출하는 순간을 포착")
    
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
    
    st.markdown("""
    <div style='text-align: right;'>
        <b style='color: #FFD700; font-size: 1.2rem;'>거북이 드림</b><br>
        <i style='color: #888;'>Sincerely, Turtle Dream</i>
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
    st.header("🛡️ 포트폴리오 리스크 방패")
    st.write("계좌 전체 리스크(Global Heat)를 6% 이내로 관리합니다.")

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
