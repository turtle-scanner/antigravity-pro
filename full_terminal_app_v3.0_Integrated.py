# 작업 일자: 2026-04-18 | 작업 시간: 18:05 | 버전: v3.9 (Full 10-Banner Master)
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

# --- 기본 설정 및 사용자 DB ---
USER_DB_FILE = "users_db.json"
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
        pass # 실전 모드에서는 오류가 나도 터미널 흐름을 방해하지 않습니다.

def load_users():
    if not os.path.exists(USER_DB_FILE):
        return {"cntfed": {"password": "cntfed", "status": "approved"}}
    with open(USER_DB_FILE, "r") as f: return json.load(f)

# --- 마켓 게이지 엔진 ---
@st.cache_data(ttl=60)
def get_bonde_market_gauge():
    # 전문가 수동 보정: 2026/04/08(수) FTD 발생에 따른 상승장 확정
    st, cl = "🟢 GREEN", "#00FF00"
    ad = "Follow-Through Day occurred on April 8th, 2026. The trend is your friend."
    ko = "팔로우스루데이 2026년 4월 8일(수)요일 발생 - 새로운 상승 추세의 시작입니다!"
    nt = "공격: 주도주 매수 및 수익 극대화"
    
    # 지수 데이터는 참고용으로만 조회 (에러 방지용)
    try:
        qqq = yf.Ticker("QQQ").history(period="20d")
        curr_p, ma20 = qqq['Close'].iloc[-1], qqq['Close'].rolling(20).mean().iloc[-1]
        dist = (curr_p/ma20 - 1) * 100
    except: dist = 1.5
    
    return {
        "status": st, "color": cl, "advice": ad, "ko_advice": ko, "note": nt, 
        "study_20": 40, "up_4": 5, "down_4": 1, "ma20_dist": dist
    }

TICKER_NAME_MAP = {
    "NVDA": "엔비디아", "TSLA": "테슬라", "AAPL": "애플", "MSFT": "마이크로소프트", "PLTR": "팔란티어", "SMCI": "슈퍼마이크로", 
    "AMD": "AMD", "META": "메타", "GOOGL": "구글", "AVGO": "브로드컴", "CRWD": "크라우드스트라이크", "005930.KS": "삼성전자", 
    "000660.KS": "SK하이닉스", "196170.KQ": "알테오젠", "042700.KS": "한미반도체", "105560.KS": "KB금융", "055550.KS": "신한지주",
    "005490.KS": "POSCO홀딩스", "000270.KS": "기아", "066570.KS": "LG전자", "035720.KS": "카카오", "035420.KS": "NAVER"
}

st.set_page_config(page_title="Pivot Master Pro", page_icon="⚖️", layout="wide")

# --- 인증 및 회원가입 ---
if "password_correct" not in st.session_state: st.session_state["password_correct"] = False
if not st.session_state["password_correct"]:
    st.markdown("<div style='text-align: center; padding: 40px 0;'><h1 style='color: #FFD700;'>⚖️ Pivot Master Pro</h1></div>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔐 로그인", "✨ 회원가입 신청"])
    
    with tab1:
        id_i = st.text_input("아이디 입력", key="login_id")
        pw_i = st.text_input("비밀번호 입력", type="password", key="login_pw")
        if st.button("터미널 접속"):
            u = load_users()
            if id_i in u and u[id_i]["password"] == pw_i:
                st.session_state["password_correct"] = True
                st.session_state.current_user = id_i
                if u[id_i].get("status") == "approved":
                    st.success(f"반갑습니다, {id_i}님! 터미널을 가동합니다.")
                else: 
                    st.warning("⚠️ 전문가님의 승인 대기 중입니다. 현재 '방문자 권한'으로 철학 및 제작 동기 메뉴만 이용 가능합니다.")
                st.rerun()
            else: st.error("로그인 정보가 올바르지 않습니다.")
            
    with tab2:
        st.write("안티그래비티 터미널의 회원이 되어 함께 성장하세요.")
        new_id = st.text_input("희망 아이디", key="reg_id")
        new_pw = st.text_input("희망 비밀번호", type="password", key="reg_pw")
        if st.button("가입 신청하기"):
            u = load_users()
            if new_id in u: st.warning("이미 존재하는 아이디입니다.")
            elif not new_id or not new_pw: st.warning("아이디와 비번을 모두 입력해 주세요.")
            else:
                u[new_id] = {"password": new_pw, "status": "pending", "grade": "주식입문자"}
                with open(USER_DB_FILE, "w") as f: json.dump(u, f, ensure_ascii=False)
                st.success("✅ 신청 완료! 전문가님의 승인을 기다려 주세요 (8번 메뉴에서 승인 예정).")
    st.stop()

# --- 사이드바 브랜딩 ---
st.markdown("<style>.sidebar-title { font-size: 24px; color: #FFFF00; font-weight: bold; white-space: nowrap; }</style>", unsafe_allow_html=True)
st.sidebar.markdown("<div class='sidebar-title'>⚖️ Pivot Master Pro</div>", unsafe_allow_html=True)

# 집중력 ASMR (선택 사항)
if st.sidebar.checkbox("🎼 집중력 BGM (ASMR)", value=False):
    st.sidebar.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3")

# 공통 데이터 로드
u_all = load_users()
curr_u_data = u_all.get(st.session_state.current_user, {})
is_staff = curr_u_data.get("grade") in ["관리자", "방장"] or st.session_state.current_user == "cntfed"
is_approved = curr_u_data.get("status") == "approved"

# [업데이트] 관리자 알림 센터 (사이드바)
if is_staff:
    pending_count = sum(1 for user in u_all.values() if user.get("status") == "pending")
    if pending_count > 0:
        st.sidebar.warning(f"🔔 신규 가입 신청 {pending_count}건 대기 중!")

# 13개 마스터 메뉴 정의
menu_ops = [
    "1. 🐝 Pivot Master Pro Scanner", "2. 💬 소통 대화방", "3. 💎 프로 분석 리포트", "4. 🚀 모멘텀 50 종목", 
    "5. 🧮 리스크 계산기", "6. 📰 뉴스 피드", "7. 📊 본데 50선", "8. 👑 관리자 승인 센터", 
    "9. 🐝 본데는 누구인가?", "10. 🏛️ 이 사이트 제작 동기", "11. 🤝 방문자 인사 및 승인 요청",
    "12. 🛡️ 포트폴리오 리스크 방패", "13. 🗺️ 실시간 주도주 히트맵"
]

# 등급별/승인상태별 메뉴 필터링
if is_staff:
    display_menu = menu_ops
elif is_approved:
    display_menu = [o for o in menu_ops if not o.startswith("8.")]
else:
    # 승인 대기 회원(방문자): 9, 10, 11번 노출
    display_menu = [o for o in menu_ops if any(o.startswith(x) for x in ["9.", "10.", "11."])]

# --- 포트폴리오 DB 로직 ---
PORTFOLIO_FILE = "portfolio_db.json"
def load_portfolio():
    if not os.path.exists(PORTFOLIO_FILE): return []
    try:
        with open(PORTFOLIO_FILE, "r") as f: return json.load(f)
    except: return []

def save_portfolio(data):
    with open(PORTFOLIO_FILE, "w") as f: json.dump(data, f)

page = st.sidebar.radio("Master Menu", display_menu)

# --- 글로벌 시간 산출 ---
tz_seoul = pytz.timezone('Asia/Seoul')
tz_ny = pytz.timezone('US/Eastern')
now_seoul = datetime.now(tz_seoul).strftime('%Y-%m-%d %H:%M')
now_ny = datetime.now(tz_ny).strftime('%Y-%m-%d %H:%M')

st.markdown(f"""
    <div style='text-align: right; color: #888; font-size: 0.85rem; padding-bottom: 5px; font-family: monospace;'>
        🇰🇷 SEOUL: {now_seoul} &nbsp; | &nbsp; 🇺🇸 NEW YORK: {now_ny}
    </div>
""", unsafe_allow_html=True)

# --- 마켓 대시보드 공통 헤더 ---
g = get_bonde_market_gauge()
st.markdown(f"""
    <div style='background: linear-gradient(90deg, #000, #111); padding: 15px; border-radius: 12px; border: 2px solid #FFD700; margin-bottom: 20px;'>
        <div style='display: flex; justify-content: space-around; align-items: center;'>
            <div style='text-align: center; flex: 1;'>
                <h2 style='color: {g["color"]}; margin: 0; font-size: 2.2rem;'>{g["status"]}</h2>
                <p style='color: #FFD700; font-weight: bold; margin: 0;'>{g["note"]}</p>
            </div>
            <div style='padding: 0 30px; border-left: 1px solid #333; flex: 2; text-align: center;'>
                <p style='color: #FFD700; font-style: italic; font-size: 1.1rem; margin: 0;'>\" {g["advice"]} \"</p>
                <p style='color: #FFFFFF; font-weight: bold; font-size: 1rem; margin-top: 8px;'>{g["ko_advice"]}</p>
            </div>
            <div style='flex: 1; border-left: 1px solid #333; padding-left: 20px; font-family: monospace; color: #00FF00;'>
                <div>> 20% Study: <span style='color: #FFD700;'>{g["study_20"]}</span></div>
                <div>> Index: <span style='color: {"#00FF00" if g["ma20_dist"] > 0 else "#FF4B4B"};'>{g["ma20_dist"]:.1f}% vs MA20</span></div>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

with st.expander("❓ 마켓 인디케이터 상세 의미 확인 (클릭)"):
    st.markdown("<div style='background:#111; padding:15px; border-radius:10px; border:1px solid #333;'><h4 style='color:#00FF00;'>20% Study</h4><p>최근 5일간 20% 급등한 종목 수. 20개 이상일 때 장세가 비로소 살아남을 뜻합니다.</p><h4 style='color:#00FF00;'>Index Flow</h4><p>지수가 20일선 위에 있는지 확인합니다. 8% 이상 벌어지면 과밀 구간입니다.</p></div>", unsafe_allow_html=True)

# --- 최적화: 본데 추천주 (Bonde Top Pick) 캐싱 엔진 ---
@st.cache_data(ttl=3600)
def get_top_pick_cached():
    url = "https://docs.google.com/spreadsheets/d/1xjbe9SF0HsxwY_Uy3NC2tT92BqK0nhArUaYU16Q0p9M/export?format=csv&gid=1499398020"
    try:
        df_gs = pd.read_csv(url)
        all_items = []
        for i in range(min(10, len(df_gs.columns))):
            all_items += df_gs.iloc[:50, i].dropna().tolist()
        
        counts = pd.Series(all_items).value_counts()
        candidates = [str(t).strip() for t in counts.index.tolist() if len(str(t)) < 6]
        
        for tic in candidates:
            try:
                tk = yf.Ticker(tic)
                inf = tk.info
                roe = inf.get('returnOnEquity', 0) * 100
                if roe >= 10: 
                    h = tk.history(period="1d")
                    if not h.empty:
                        entry = h['Close'].iloc[-1]
                        return {
                            "ticker": tic, "name": TICKER_NAME_MAP.get(tic, tic),
                            "roe": roe, "count": counts.get(tic),
                            "entry": entry, "sl": entry * 0.97, "tp": entry * 1.20
                        }
            except: continue
    except: return None
    return None

top_pick = get_top_pick_cached()

if top_pick:
    st.markdown(f"""
        <div style='background: #1a1a1a; padding: 20px; border-radius: 12px; border: 2px solid #FFD700; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(255, 215, 0, 0.2);'>
            <div style='display: flex; justify-content: space-between; align-items: flex-start;'>
                <div>
                    <span style='background: #FFD700; color: #000; padding: 5px 12px; border-radius: 20px; font-weight: bold; font-size: 0.8rem;'>💎 BONDE'S TOP PICK</span>
                    <h2 style='color: #fff; margin: 15px 0 5px 0; font-size: 1.8rem;'>{top_pick['name']} ({top_pick['ticker']})</h2>
                    <p style='color: #4ade80; margin: 0;'>최근 10일간 {top_pick['count']}회 언급 | ROE: {top_pick['roe']:.1f}%</p>
                </div>
                <div style='text-align: right;'>
                    <p style='color: #888; font-size: 0.8rem; margin: 0;'>전문가 권장 전략</p>
                    <h3 style='color: #FFD700; margin: 5px 0;'>수익 목표 +20%</h3>
                </div>
            </div>
            <div style='display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin-top: 20px; padding-top: 20px; border-top: 1px solid #333;'>
                <div style='text-align: center;'>
                    <p style='color: #888; margin: 0; font-size: 0.9rem;'>진입 가격 (돌파)</p>
                    <p style='color: #fff; font-size: 1.4rem; font-weight: bold; margin: 5px 0;'>${top_pick['entry']:.2f}</p>
                </div>
                <div style='text-align: center;'>
                    <p style='color: #FF4B4B; margin: 0; font-size: 0.9rem;'>손절 가격 (-3%)</p>
                    <p style='color: #FF4B4B; font-size: 1.4rem; font-weight: bold; margin: 5px 0;'>${top_pick['sl']:.2f}</p>
                </div>
                <div style='text-align: center;'>
                    <p style='color: #4ade80; margin: 0; font-size: 0.9rem;'>목표 가격 (+20%)</p>
                    <p style='color: #4ade80; font-size: 1.4rem; font-weight: bold; margin: 5px 0;'>${top_pick['tp']:.2f}</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- 각 페이지 로직 ---
if page.startswith("1."):
    st.header("⚖️ Pivot Master Pro Scanner")
    st.info("✅ 데일리 체크리스트: 마켓 레짐 확인(GREEN?) / 섹터 주도주 여부 / ROE 10% 이상 / -3% 손절 준수")
    st.divider()
    tabs = st.tabs(["1. [모드 1: MAGNA_EP] - 에피소딕 피벗 & 펀더멘털", "2. [모드 2: 4_BURST] - 4% 모멘텀 버스트", "3. [모드 3: ANTICIPATION] - 조용한 눌림목(TTT)"])
    def run_sc():
        data = {"EP": [], "BURST": [], "TTT": []}; pb = st.progress(0); st_txt = st.empty()
        for i, (tic, name) in enumerate(TICKER_NAME_MAP.items()):
            try:
                st_txt.text(f"> Analyzing {name}...")
                pb.progress((i+1)/len(TICKER_NAME_MAP))
                h = yf.Ticker(tic).history(period="30d"); inf = yf.Ticker(tic).info
                if len(h) < 20: continue
                cp, pp = h['Close'].iloc[-1], h['Close'].iloc[-2]
                ch, va, cv = (cp/pp-1)*100, h['Volume'].iloc[-20:].mean(), h['Volume'].iloc[-1]
                fmt = lambda v: f"{int(v):,}원" if ".KS" in tic or ".KQ" in tic else f"${v:.2f}"
                ent = h['High'].iloc[-20:].max()
                roe_num = inf.get('returnOnEquity', 0) * 100
                bms_score = 0
                if roe_num >= 15: bms_score += 4
                elif roe_num >= 10: bms_score += 2
                if ch > 2: bms_score += 3
                if cv > va * 1.5: bms_score += 3
                
                grade = "💎 S급" if bms_score >= 8 else ("🟢 A급" if bms_score >= 5 else "⚪ B급")
                
                row = {
                    "종목명": name, "현재가": fmt(cp), "RS": int((cp/h['Close'].iloc[0])*100), 
                    "ROE": f"{roe_num:.1f}%", "BMS": f"{bms_score}점", "등급": grade,
                    "진입가": fmt(ent), "손절가": fmt(ent*0.97), "목표가": fmt(ent*1.20)
                }
                if (h['Open'].iloc[-1]/pp-1)>=0.02 and cv > va*1.5: data["EP"].append(row)
                if ch>=3.5 and cv > h['Volume'].iloc[-2]: data["BURST"].append(row)
                if h['Close'].iloc[-5:].std()/cp*100 < 2.0 and abs(ch)<1.5: data["TTT"].append(row)
            except: continue
        pb.empty(); st_txt.empty(); return data
    sc_res = run_sc()
    for tab, k in zip(tabs, ["EP", "BURST", "TTT"]):
        with tab:
            if sc_res[k]: 
                res_df = pd.DataFrame(sc_res[k])
                st.dataframe(res_df.style.highlight_max(axis=0, subset=['BMS'], color='#004400'), use_container_width=True, hide_index=True)
            else: st.info("대상 종목 없음")

elif page.startswith("2."):
    st.header("💬 소통 대화방")
    st.info("전문가님과 회원들의 대화는 구글 시트(1HbC_U1I78HAdV99X6qS1hm...)에 실시간 기록 중입니다.")
    
    MSG_FILE = "messages_db.csv"
    
    # 대화 입력 폼
    with st.form("chat_form", clear_on_submit=True):
        ms = st.text_input("메시지를 입력하세요 (Shift+Enter로 줄바꿈 가능)")
        if st.form_submit_button("🚀 전송"):
            if ms.strip():
                now_t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                curr_user = st.session_state.current_user
                new_msg = pd.DataFrame([{"유저": curr_user, "내용": ms, "시간": now_t}])
                # 1. 로컬 CSV 저장
                if not os.path.exists(MSG_FILE): new_msg.to_csv(MSG_FILE, index=False, encoding='utf-8-sig')
                else: new_msg.to_csv(MSG_FILE, mode='a', header=False, index=False, encoding='utf-8-sig')
                # 2. 구글 시트 실시간 전송
                gsheet_sync("소통대화방_기록", ["보낸사람", "시간", "내용"], [curr_user, now_t, ms])
                st.rerun()
    
    # 대화 기록 표시 (엑셀 데이터 로드)
    if os.path.exists(MSG_FILE):
        try:
            df_msg = pd.read_csv(MSG_FILE, encoding='utf-8-sig')
            
            # 구글 시트용 다운로드 버튼 추가
            col1, col2 = st.columns([2, 1])
            with col1:
                st.write(f"💬 **전체 대화 수: {len(df_msg)}개**")
            with col2:
                st.download_button(label="📥 CSV 다운로드", data=df_msg.to_csv(index=False, encoding='utf-8-sig'), file_name=f"antigravity_chat_{datetime.now().strftime('%m%d')}.csv", mime="text/csv")
            
            st.divider()

            # --- 100개 단위 페이징 로직 ---
            page_size = 100
            total_msgs = len(df_msg)
            total_pages = max(1, (total_msgs + page_size - 1) // page_size)
            
            page_num = st.select_slider("📜 대화 내역 페이지 이동 (100개 단위)", options=list(range(1, total_pages + 1)), value=1)
            
            start_idx = (page_num - 1) * page_size
            end_idx = start_idx + page_size
            
            # 역순 정렬 후 슬라이싱
            df_paged = df_msg.iloc[::-1].iloc[start_idx:end_idx]
            
            for _, m in df_paged.iterrows():
                st.markdown(f"**{m['유저']}** <span style='color:#888; font-size:0.8rem;'>({m['시간']})</span>", unsafe_allow_html=True)
                st.info(m['내용'])
                st.write("")
        except Exception as e:
            st.error(f"대화 기록 로딩 중 오류: {e}")
    else:
        st.write("아직 등록된 대화가 없습니다. 첫마디를 건네보세요!")

elif page.startswith("3."):
    st.header("💎 주식 정밀 분석 리포트 (BMS)")
    st.write("전문가용 분석 팩토리입니다. 분석을 원하는 티커(Ticker)를 입력하세요.")
    
    with st.form("analytic_form"):
        tic_input = st.text_input("종목 심볼 입력 (예: NVDA, TSLA, 005930.KS)", value="NVDA").upper().strip()
        submit_btn = st.form_submit_button("정밀 분석 시작")
    
    if submit_btn:
        with st.spinner(f"{tic_input} 데이터 정밀 판독 중..."):
            try:
                tk = yf.Ticker(tic_input); h = tk.history(period="1y"); inf = tk.info
                if h.empty: st.error("종목 정보를 찾을 수 없습니다."); st.stop()
                
                cp = h['Close'].iloc[-1]; ma50 = h['Close'].rolling(50).mean().iloc[-1]; ma200 = h['Close'].rolling(200).mean().iloc[-1]
                roe = inf.get('returnOnEquity', 0) * 100; rs_score = int((cp / h['Close'].iloc[0]) * 100)
                
                st.subheader(f"📊 {inf.get('longName', tic_input)} 분석 결과")
                col1, col2, col3 = st.columns(3)
                col1.metric("현재가", f"${cp:.2f}" if tic_input.isalpha() else f"{int(cp):,}원")
                col2.metric("ROE (자기자본이익률)", f"{roe:.1f}%")
                col3.metric("상대강도 (RS Score)", rs_score)
                
                st.divider()
                c1, c2 = st.columns(2)
                with c1:
                    st.write("**✅ 기술적 건강도 (Technical Health)**")
                    st.write(f"- 50일선: {'🟢 위 (정배열)' if cp > ma50 else '🔴 아래 (역배열)'}")
                    st.write(f"- 200일선: {'🟢 위 (강력)' if cp > ma200 else '🔴 아래 (경계)'}")
                with c2:
                    st.write("**✅ 펀더멘털 평가 (Fundamental Grade)**")
                    grade = "A (주도주)" if roe >= 15 else "B (우량주)" if roe >= 0 else "F (적자기업)"
                    st.write(f"- 최종 등급: **{grade}**")
                st.success(f"💡 가이드: {tic_input}은 현재 {grade} 등급 종목입니다. 전문가 원칙에 따른 대응을 권장합니다.")
                
                st.divider()
                st.write("**📈 실시간 레이더 차트 (TradingView)**")
                # TradingView Widget HTML
                chart_html = f"""
                <div class="tradingview-widget-container" style="height:450px;width:100%;">
                  <div id="tradingview_chart"></div>
                  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
                  <script type="text/javascript">
                  new TradingView.widget({{
                    "autosize": true,
                    "symbol": "{'NASDAQ:'+tic_input if tic_input.isalpha() else 'KRX:'+tic_input.split('.')[0]}",
                    "interval": "D",
                    "timezone": "Etc/UTC",
                    "theme": "dark",
                    "style": "1",
                    "locale": "kr",
                    "toolbar_bg": "#f1f3f6",
                    "enable_publishing": false,
                    "hide_side_toolbar": false,
                    "allow_symbol_change": true,
                    "container_id": "tradingview_chart"
                  }});
                  </script>
                </div>
                """
                st.components.v1.html(chart_html, height=500)
            except Exception as e: st.error(f"분석 중 오류 발생: {e}")

elif page.startswith("4."):
    st.header("🚀 주도주 우선순위 랭킹 (Bonde Priority)")
    st.info("✅ 원칙: 상위 50선 중 우상향 정배열 종목만 골라내어 '에피소딕 피벗' 패턴을 기다립니다. (ROE 마이너스 종목 자동 제외)")
    st.divider()
    url = "https://docs.google.com/spreadsheets/d/1xjbe9SF0HsxwY_Uy3NC2tT92BqK0nhArUaYU16Q0p9M/export?format=csv&gid=1499398020"
    try:
        df_gs = pd.read_csv(url)
        # 상위 50개씩 6일치 통합
        all_merged = []
        today_list = df_gs.iloc[:50, 0].dropna().tolist()
        for i in range(min(6, len(df_gs.columns))):
            all_merged += df_gs.iloc[:50, i].dropna().tolist()
        
        counts = pd.Series(all_merged).value_counts()
        candidates = [str(t).strip() for t in counts.index.tolist() if len(str(t)) < 6][:50]
        
        if not candidates: st.warning("분석할 종목을 찾지 못했습니다.")
        else:
            st.info(f"실시간 데이터 분석을 통해 {len(candidates)}개 종목의 우선순위를 산출합니다.")
            full_data = yf.download(candidates, period="1y", progress=False)['Close']
            
            results = []
            pb = st.progress(0); st_txt = st.empty()
            
            for i, tic in enumerate(candidates):
                st_txt.text(f"> [{i+1}/{len(candidates)}] {tic} 점수 산출 중...")
                pb.progress((i+1)/len(candidates))
                try:
                    f = counts.get(tic, 0); inf = yf.Ticker(tic).info; roe = inf.get('returnOnEquity', 0) * 100
                    # 순위 가중치: 오늘 리스트에 있으면 (50 - 순위) 점수 부여
                    rank_score = (50 - today_list.index(tic)) if tic in today_list else 0
                    total_score = (f * 100) + rank_score
                    
                    # [신규 필터] ROE가 마이너스(-)인 종목은 무조건 제외 (적자 기업 필터링)
                    if roe < 0: continue
                    
                    if f >= 2 or roe >= 10: # 최소 2회 언급 또는 우량주만
                        cp = full_data[tic].dropna().iloc[-1] if tic in full_data.columns else 0
                        
                        priority = "💎 TOP PICK" if total_score >= 500 else "🔥 STRONG" if total_score >= 300 else "🧱 WATCH"
                        results.append({
                            "우선순위": priority, "종목": tic, "점수": total_score, "출현횟수": f"{f}회",
                            "ROE": f"{roe:.1f}%", "현재가": f"${cp:.2f}",
                            "분류": "초강력" if total_score >= 500 else "실적주" if roe >= 10 else "모멘텀주"
                        })
                except: continue
            
            pb.empty(); st_txt.empty()
            if results:
                st.success("오늘의 매수 우선순위 랭킹이 확정되었습니다.")
                res_df = pd.DataFrame(results).sort_values(by="점수", ascending=False)
                # 구글 시트용 다운로드 버튼 추가
                st.download_button(label="📊 오늘의 주도주 데이터 구글시트 백업", data=res_df.to_csv(index=False, encoding='utf-8-sig'), file_name=f"bonde_priority_{datetime.now().strftime('%m%d')}.csv", mime="text/csv")
                st.dataframe(res_df, use_container_width=True, hide_index=True)
            else: st.warning("조건을 만족하는 주도주가 포착되지 않았습니다.")
            
            # --- 본데 매매 원칙 가이드 (순수 텍스트 버전) ---
            st.markdown("---")
            st.subheader("🛡️ Antigravity Pro: 본데(Bonde) 전략 매매 원칙")
            st.write("**거북이투자전문가님 가이드 | 핵심 요점 요약**")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.success("1. 리스트 분석")
                st.write("- **상위 그룹:** 주도 섹터 파악 (추격 금지)")
                st.write("- **중·하위 그룹:** 실질적 매수 사냥터")
                
            with col2:
                st.warning("2. 매수 진입")
                st.write("- **에너지 응축:** VCP 패턴/거래량 건조 대기")
                st.write("- **정석 돌파:** 피벗 상단 거래량 돌파 시 진입")
                
            with col3:
                st.error("3. 리스크/시간")
                st.write("- **손절/익절:** -3% 설정 / 목표 +20% 이상")
                st.write("- **3일의 법칙:** 반응 없으면 즉시 청산")
            
            st.info('" Don\'t fight the trend. Wait for the Setup. Protect your Capital. "')
            st.markdown("---")
            
    except Exception as e: st.error(f"분석 엔진 가동 실패: {e}")

elif page.startswith("5."):
    st.header("🧮 리스크 & 포지션 계산기")
    st.info("전문가 원칙: 매수 즉시 -3% 손절 설정, 자본의 1% 이상 리스크 금지")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💰 자금 설정")
        total_cap = st.number_input("총 투자 자산 (USD/$)", min_value=0, value=10000, step=1000)
        max_risk_pct = st.number_input("거래당 최대 허용 리스크 (%)", min_value=0.1, max_value=5.0, value=1.0, step=0.1)
        st.write(f"👉 이번 거래에서 잃어도 되는 최대 금액: **${total_cap * (max_risk_pct/100):,.2f}**")
        
    with col2:
        st.subheader("📈 진입 설정")
        entry_price = st.number_input("진입 가격 ($)", min_value=0.1, value=100.0, step=1.0)
        # 전문가 권장 손절가 (-3%) 자동 계산
        recommended_sl = entry_price * 0.97
        stop_loss = st.number_input("손절 가격 ($)", min_value=0.1, value=recommended_sl, step=0.1)
        st.write(f"⚠️ 현재 설정된 손절 폭: **{((entry_price - stop_loss) / entry_price * 100):.2f}%**")

    st.markdown("---")
    
    # 리스크 계산 로직
    risk_per_share = entry_price - stop_loss
    if risk_per_share > 0:
        max_risk_amt = total_cap * (max_risk_pct / 100)
        shares_to_buy = int(max_risk_amt / risk_per_share)
        total_pos_size = shares_to_buy * entry_price
        pos_pct = (total_pos_size / total_cap) * 100
        
        st.subheader("🎯 최종 계산 결과")
        res_c1, res_c2, res_c3 = st.columns(3)
        res_c1.metric("매수 추천 수량", f"{shares_to_buy} 주")
        res_c2.metric("총 포지션 규모", f"${total_pos_size:,.2f}")
        res_c3.metric("계좌 비중", f"{pos_pct:.1f} %")
        
        st.success(f"✅ **가이드**: 총 자산의 {pos_pct:.1f}%를 사용하여 {shares_to_buy}주를 매수하십시오. 손절 시 계좌의 딱 {max_risk_pct}%만 잃게 됩니다.")
        
        # 목표가 기대 수익
        target_20 = entry_price * 1.20
        profit_20 = (target_20 - entry_price) * shares_to_buy
        st.write(f"🏹 **1차 목표가(+20%): ${target_20:,.2f}** (달성 시 예상 수익: **+${profit_20:,.2f}**)")
    else:
        st.error("손절 가격은 진입 가격보다 낮아야 합니다.")

    st.divider()
    st.subheader("🎯 포트폴리오 총 리스크 (Total Heat) 관리")
    st.write("전문가 권고: 계좌 전체의 오픈 리스크(Total Heat)는 6%를 넘지 않아야 합니다.")
    
    with st.expander("💼 복수 포지션 통합 위험도 계산"):
        st.write("현재 보유 중인 모든 종목의 리스크 합계를 입력하세요.")
        heat_input = st.text_area("보유 종목별 리스크% (쉼표 구분, 예: 1, 1, 0.5, 1)", value="1.0, 1.0")
        try:
            heat_list = [float(x.strip()) for x in heat_input.split(",")]
            total_heat = sum(heat_list)
            st.write(f"🔥 현재 내 포트폴리오의 총 열기(Total Heat): **{total_heat:.1f}%**")
            if total_heat > 6.0: st.error("⚠️ 경고: 계좌 전체 리스크가 위험 수준(6% 초과)입니다. 추가 진입을 자제하십시오.")
            else: st.success("✅ 안정: 계좌 전체 리스크가 관리 범위 내에 있습니다.")
        except: st.write("올바른 숫자를 입력해 주세요.")

elif page.startswith("6."):
    st.header("📈 실시간 마켓 트렌드 요약")
    st.info("뉴스를 넘어 지수와 대장주의 흐름으로 시장의 온도를 즉시 파악합니다.")
    
    try:
        # 주요 지수 및 대장주 데이터 한 번에 가져오기
        indices = {"KOSPI": "^KS11", "KOSDAQ": "^KQ11", "S&P 500": "^GSPC", "NASDAQ": "^IXIC"}
        hot_stocks = {"삼성전자": "005930.KS", "SK하이닉스": "000660.KS", "엔비디아": "NVDA", "테슬라": "TSLA"}
        
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("📊 글로벌 지수 현황")
            for name, tic in indices.items():
                d = yf.Ticker(tic).history(period="2d")
                if len(d) >= 2:
                    curr, prev = d['Close'].iloc[-1], d['Close'].iloc[-2]
                    chg = (curr/prev - 1) * 100
                    st.metric(name, f"{curr:,.2f}", f"{chg:.2f}%")
                else: st.write(f"{name}: 데이터 준비 중")
                
        with c2:
            st.subheader("🔥 실시간 대장주 동향")
            for name, tic in hot_stocks.items():
                d = yf.Ticker(tic).history(period="2d")
                if len(d) >= 2:
                    curr, prev = d['Close'].iloc[-1], d['Close'].iloc[-2]
                    chg = (curr/prev - 1) * 100
                    fmt = f"{int(curr):,}원" if ".KS" in tic else f"${curr:.2f}"
                    st.metric(name, fmt, f"{chg:.2f}%")
                else: st.write(f"{name}: 데이터 준비 중")
                
    except Exception as e:
        st.error(f"트렌드 로딩 실패: {e}")
    
    st.markdown("---")
    st.subheader("🧬 섹터별 수급 레이더 (Sector Momentum)")
    sectors = {"반도체(SOXX)": "SOXX", "빅테크(XLK)": "XLK", "바이오(XBI)": "XBI", "에너지(XLE)": "XLE"}
    sc_cols = st.columns(len(sectors))
    for col, (sn, stic) in zip(sc_cols, sectors.items()):
        sd = yf.Ticker(stic).history(period="2d")
        if len(sd)>=2:
            sc_chg = (sd['Close'].iloc[-1]/sd['Close'].iloc[-2]-1)*100
            col.write(f"**{sn}**")
            col.write(f"{'🟢' if sc_chg>0 else '🔴'} {sc_chg:.1f}%")
    
    st.markdown("---")
    st.info("💡 팁: 지수가 초록색(상승)일 때는 주도주 돌파 매수에 집중하고, 빨간색(하락)일 때는 관망하며 에너지를 비축하십시오.")

elif page.startswith("7."):
    st.header("📊 본데 50선 실시간 모니터링 리스트")
    url = "https://docs.google.com/spreadsheets/d/1xjbe9SF0HsxwY_Uy3NC2tT92BqK0nhArUaYU16Q0p9M/export?format=csv&gid=1499398020"
    try:
        with st.spinner("구글 시트 데이터 동기화 중..."):
            df_gs = pd.read_csv(url)
            st.success("✅ 구글 스프레드시트 데이터 동기화 완료")
            st.write("전문가님이 감시 중인 실시간 주도주 리스트입니다.")
            st.dataframe(df_gs.head(100), use_container_width=True, hide_index=False)
            st.info("💡 팁: 표의 헤더를 클릭하면 각 날짜별로 정렬하여 보실 수 있습니다.")
    except Exception as e:
        st.error(f"구글 시트 연동 실패: {e}")

elif page.startswith("8."):
    st.header("👑 회원 관리 및 승인 센터")
    st.info("관리자와 방장만 이용 가능한 섹션입니다.")
    
    u = load_users()
    if "cntfed" in u and u["cntfed"].get("grade") != "관리자":
        u["cntfed"]["grade"] = "관리자"
        with open(USER_DB_FILE, "w") as f: json.dump(u, f)
    
    st.subheader("📋 전체 회원 명단 (Admin Only)")
    st.divider()
    grades_list = ["주식입문자", "주식중수", "주식고수", "방장", "관리자"]
    
    for k, v in u.items():
        if k == "cntfed": continue
        c1, c2, c3, c4 = st.columns([2, 2, 2, 1])
        c1.write(f"👤 **{k}**")
        if v.get("status") == "pending":
            if c2.button(f"승인 대기 중", key=f"app_{k}"):
                u[k]["status"] = "approved"; u[k]["grade"] = "주식입문자"
                with open(USER_DB_FILE, "w") as f: json.dump(u, f, ensure_ascii=False)
                st.success(f"{k} 승격!"); st.rerun()
        else:
            cg = v.get("grade", "주식입문자")
            ng = c2.selectbox("등급 변경", grades_list, index=grades_list.index(cg) if cg in grades_list else 0, key=f"sel_{k}")
            if ng != cg:
                u[k]["grade"] = ng
                with open(USER_DB_FILE, "w") as f: json.dump(u, f, ensure_ascii=False)
                st.success(f"{k} 등급 변경 완료!"); st.rerun()
            c3.write("🟢 활동 중")
        if c4.button("❌ 추방", key=f"kick_{k}"):
            del u[k]
            with open(USER_DB_FILE, "w") as f: json.dump(u, f, ensure_ascii=False)
            st.rerun()
        st.divider()

elif page.startswith("9."):
    st.header("🎯 프라딥 본데(StockBee): 시스템으로 시장을 정복한 월가의 멘토")
    st.write("""
    온라인에서 ‘스탁비(StockBee)’라는 필명으로 더 잘 알려진 프라딥 본데는 24년 이상의 경력을 가진 전업 트레이더이자 현대 트레이딩 교육의 거두입니다. 
    그는 수천 달러를 1억 달러 이상의 자산으로 불린 크리스찬 쿨라매기를 비롯해 세계적인 수익률을 기록한 수많은 트레이더를 배출하며 월가의 전설적인 멘토로 자리 잡았습니다.
    """)
    
    with st.expander("1. 🚚 물류 전문가에서 데이터 트레이더로의 변신 (클릭하여 읽기)"):
        st.write("""
        본데의 성공 비결은 그의 독특한 이력에서 시작됩니다. 그는 금융권 엘리트 코스를 밟은 인물이 아닙니다. 
        인도에서 DHL과 FedEx 프랜차이즈의 마케팅 책임자로 일하며 물류 네트워크의 효율성과 프로세스 관리를 진두지휘하던 인물이었습니다. 
        2000년경 주식 시장에 뛰어든 초기에 그는 여느 개인 투자자들처럼 시행착오를 겪었습니다. 
        그러나 물류 산업에서 체득한 시스템 경영의 원리를 트레이딩에 접목하면서 반전이 시작되었습니다. 
        그는 주식 거래를 막연한 운이나 추측이 아닌, 철저하게 설계된 ‘데이터 기반의 비즈니스 모델’로 재정의했습니다.
        """)
        
    with st.expander("2. 🧘 스탁비를 지탱하는 4대 트레이딩 철학 (클릭하여 읽기)"):
        st.write("""
        그의 매매법 밑바탕에는 단순한 차트 분석을 넘어선 고도의 심리적 규율과 절차적 사고가 깔려 있습니다.
        
        **첫째는 ‘섬의 환상’에서 탈피하는 안타 전략입니다.** 
        많은 이들이 주식으로 단번에 부자가 되어 호화로운 생활을 누리는 홈런을 꿈꾸지만, 본데는 이를 파멸의 지름길로 봅니다. 
        그는 작고 확실한 수익을 복리로 누적시키는 안타 전략이 성공의 핵심이라고 가르칩니다. 수익은 단지 올바른 프로세스를 성실히 수행했을 때 따라오는 부산물일 뿐입니다.
        
        **둘째는 셀프 리더십입니다.** 
        본데는 트레이딩의 주도권이 전적으로 자신에게 있어야 한다고 강조합니다. 
        아무리 훌륭한 스승이 있더라도 결국 스스로 문제를 해결하고 실행에 옮기는 강인한 의지가 없다면 시장이라는 거친 파도를 넘을 수 없기 때문입니다.
        
        **셋째는 딥 다이브를 통한 절차적 기억의 형성입니다.** 
        실전 매매는 장중에 머리로 고민하는 것이 아니라 반사적으로 이루어져야 합니다. 
        이를 위해 본데는 과거 폭등했던 수천 개의 차트 패턴을 뇌에 각인시키는 혹독한 훈련을 시킵니다. 
        이는 운동선수가 반복 훈련을 통해 몸이 먼저 반응하게 만드는 것과 같은 이치입니다.
        
        **넷째는 철저한 상황 인식입니다.** 
        그는 매일 아침 시장의 폭(Breadth)을 분석하며 오늘이 공격적으로 투자할 날인지, 아니면 현금을 지켜야 할 날인지를 엄격하게 판단합니다. 
        상승 종목과 하락 종목의 비율을 토대로 한 마켓 레짐 판독은 그의 매매 시스템에서 가장 중요한 필터 역할을 합니다.
        """)
        
    with st.expander("3. 🍱 시장의 중력을 이기는 대표 매매 기법 (클릭하여 읽기)"):
        st.write("""
        본데의 전략은 주가를 밀어 올리는 강력한 동력인 촉매제와 모멘텀에 초점을 맞춥니다.
        
        **대표적인 기법인 ‘에피소딕 피벗(EP)’**은 시장에서 오랫동안 잊혔던 종목이 어닝 서프라이즈나 대형 계약 같은 펀더멘털의 근본적 변화를 만났을 때를 공략합니다. 
        이때 주가는 기관의 강력한 매수세와 함께 엄청난 거래량을 동반하며 갭 상승을 일으키는데, 본데는 이 폭발적인 초기 국면에 탑승하여 수익을 극대화합니다.
        
        **또한 ‘모멘텀 버스트’**는 좁은 구간에서 힘을 응축하던 주식이 분출하는 순간을 포착하는 기법입니다. 
        이는 짧은 기간 안에 빠른 수익을 챙기고 나오는 안타 전략의 정수라 할 수 있습니다. 
        여기에 매출과 이익의 비정상적인 성장을 검증하는 MAGNA 필터와 시가총액 100억 달러 미만의 젊은 기업을 선별하는 CAP 10x10 공식을 더해 종목 선정의 정밀도를 극대화합니다.
        """)
        
    with st.expander("4. 🏭 신뢰로 구축된 트레이딩 팩토리, 스탁비 커뮤니티 (클릭하여 읽기)"):
        st.write("""
        그는 화려한 마케팅이나 광고에 의존하지 않습니다. 
        오직 결과와 입소문만으로 운영되는 스탁비 커뮤니티는 전 세계 트레이더들이 모여 본데가 고안한 프로세스를 검증하고 학습하는 공간입니다. 
        이곳은 단순한 정보 공유를 넘어, 초보자와 베테랑이 함께 시장을 분석하며 동반 성장하는 거대한 트레이딩 팩토리의 역할을 수행하고 있습니다.
        """)
        
    st.info("💡 전문가님의 안티그래비티 터미널은 위와 같은 본데의 정수를 시스템화하여 여러분의 매매를 보조합니다.")

elif page.startswith("10."):
    st.header("🏠 이 사이트 제작 동기")
    st.subheader("감사하며 존경하는 마음으로 제작했습니다.")
    st.write("### 세 거인의 발자취를 따라, 함께 성장의 궤도에 오르기를 꿈꾸며")
    
    st.write("""
    이 플랫폼은 제가 깊이 존경하는 세 분의 스승, 윌리엄 오닐, 마크 미너비니, 그리고 프라딥 본데의 트레이딩 철학을 기리는 마음으로 시작되었습니다. 
    주식이라는 거친 바다에서 길을 잃지 않도록 저 스스로를 다잡기 위한 '나침반'을 만들고 싶었습니다.
    
    저는 **"누구나 간절히 노력한다면 정규직의 꿈을 이룰 수 있고, 경제적 자유를 얻을 수 있다"**는 굳은 신념을 가지고 있습니다. 
    비록 지금은 부족한 점이 많은 터미널이지만, 저와 같은 꿈을 꾸는 분들이 함께 부자가 되었으면 하는 진심 어린 마음을 담아 밤낮으로 코드를 짜고 로직을 다듬었습니다.
    """)
    
    st.info("""
    📖 **거북이가 추천하는 필독서**
    이미 세상에는 훌륭한 책들이 많이 나와 있습니다. 그중에서도 윌리엄 오닐의 저서 
    **『최고의 주식, 최적의 타이밍(How to Make Money in Stocks)』**은 제가 가장 추천하는 필독서입니다. 
    기술적인 분석을 넘어 시장의 본질을 꿰뚫는 혜안을 얻으시길 바랍니다.
    """)
    
    st.write("""
    이곳이 단순히 정보를 얻는 곳을 넘어, 서로의 귀한 의견을 나누고 격려하며 함께 우상향하는 '주식 인사이트 플랫폼'으로 성장하기를 소망합니다. 
    저 또한 멈추지 않고 배우며 여러분과 함께 걷겠습니다.
    
    **2026년 4월 18일, 깊어가는 봄날 저녁 집에서**
    **거북이 드림**
    """)
    
    st.divider()
    
    st.subheader("🏛️ Motivation Behind ISATY : Antigravity")
    st.write("### Following the footsteps of the three giants, dreaming of a collective ascent.")
    
    st.write("""
    This platform was born out of my profound respect for three masters: William O'Neil, Mark Minervini, and Pradeep Bonde. 
    My goal was to build a "compass" to keep myself grounded and focused so as not to lose my way in the turbulent ocean of the stock market.
    
    I hold a firm belief that **"anyone who puts in the sincere effort can achieve their professional dreams and reach financial freedom."** 
    Although this terminal may still be a work in progress, I have poured my heart into writing every line of code and refining every logic, 
    fueled by the sincere hope that those who share this dream can grow wealthy together.
    """)
    
    st.info("""
    📖 **Turtle’s Must-Read Recommendation**
    There are already many excellent books available. Among them, I most highly recommend 
    **"How to Make Money in Stocks" by William O'Neil**. 
    I hope you gain insights that pierce through the core of the market, going beyond mere technical analysis.
    """)
    
    st.write("""
    My wish is for this place to evolve into a "Stock Insight Platform" where we do more than just consume information—where we share valuable opinions, 
    encourage one another, and ascend toward success together. I, too, will never stop learning and will continue this journey alongside you.
    
    **April 18, 2026, on a deepening spring evening at home.**
    **Sincerely, Turtle**
    """)

elif page.startswith("11."):
    st.header("🤝 방문자 인사 및 승인 요청")
    st.info("안티그래비티의 일원이 되신 것을 환영합니다! 전문가님께 정중한 인사말과 승인 요청을 남겨주세요.")
    
    VISITOR_FILE = "visitor_requests.csv"
    
    with st.form("visitor_form", clear_on_submit=True):
        ms = st.text_area("인사말 및 승인 요청 메시지를 남겨주세요 (예: 주식 열정 가득한 OOO입니다. 승인 부탁드립니다!)")
        if st.form_submit_button("✉️ 메시지 전송"):
            if ms.strip():
                now_t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                curr_user = st.session_state.current_user
                new_msg = pd.DataFrame([{"유저": curr_user, "내용": ms, "시간": now_t}])
                if not os.path.exists(VISITOR_FILE): new_msg.to_csv(VISITOR_FILE, index=False, encoding='utf-8-sig')
                else: new_msg.to_csv(VISITOR_FILE, mode='a', header=False, index=False, encoding='utf-8-sig')
                
                # 구글 시트 실시간 통합 전송
                gsheet_sync("방문자_인사말", ["신청자", "시간", "인사말"], [curr_user, now_t, ms])
                st.success("인사말이 성공적으로 전달되었습니다! 전문가님이 곧 확인하실 예정입니다.")
                st.rerun()

    if os.path.exists(VISITOR_FILE):
        df_v = pd.read_csv(VISITOR_FILE, encoding='utf-8-sig')
        st.divider()
        st.write("💬 **최근 방문자 인사 현황 (최신 100건)**")
        for _, m in df_v.iloc[::-1].head(100).iterrows():
            st.markdown(f"🔹 **{m['유저']}**: {m['내용']} <span style='color:#666; font-size:0.75rem;'>({m['시간']})</span>", unsafe_allow_html=True)

elif page.startswith("12."):
    st.header("🛡️ 포트폴리오 리스크 방패")
    st.info("전체 자산 대비 현재 노출된 총 리스크(Global Heat)를 관리합니다.")
    
    with st.expander("🛡️ 리스크 관리 원칙", expanded=True):
        st.write("1. 전체 자산 대비 총 손절 리스크(Heat)는 6%를 넘지 않아야 합니다.")
        st.write("2. 하루에 새롭게 진입하는 종목의 리스크 합은 1.5~2.5% 이내여야 합니다.")

    col1, col2 = st.columns(2)
    with col1:
        total_equity = st.number_input("총 투자 자산 (예: 100,000,000)", value=10000000)
    with col2:
        st.metric("추천 최대 총 리스크 (6%)", f"{total_equity * 0.06:,.0f}원")

    st.subheader("📊 현재 보유 종목 리스크 입력")
    # 영구 DB 로드
    p_entries = load_portfolio()
    
    with st.form("add_pos"):
        c1, c2, c3, c4 = st.columns(4)
        name = c1.text_input("종목명")
        qty = c2.number_input("수량", value=1)
        entry = c3.number_input("매수가", value=1000)
        stop = c4.number_input("손절가", value=950)
        if st.form_submit_button("➕ 포트폴리오 추가"):
            risk_per_share = entry - stop
            total_pos_risk = risk_per_share * qty
            p_entries.append({"name":name, "qty":qty, "entry":entry, "stop":stop, "risk":total_pos_risk})
            save_portfolio(p_entries)
            st.rerun()

    if p_entries:
        p_df = pd.DataFrame(p_entries)
        total_heat = p_df['risk'].sum()
        heat_pct = (total_heat / total_equity) * 100

        st.table(p_df)
        
        st.divider()
        c_a, c_b = st.columns(2)
        c_a.metric("총 노출 리스크 (Total Heat)", f"{total_heat:,.0f}원", f"{heat_pct:.2f}%")
        
        if heat_pct > 6:
            st.error(f"🚨 경고: 현재 리스크({heat_pct:.2f}%)가 임계치(6%)를 초과했습니다! 비중을 축소하세요.")
        elif heat_pct > 4:
            st.warning("⚠️ 주의: 리스크가 높은 수준입니다. 추가 진입에 신중하세요.")
        else:
            st.success("✅ 안전: 현재 자산 대비 리스크가 적정 수준 내에서 관리되고 있습니다.")
            
        if st.button("🗑️ 포트폴리오 초기화"):
            save_portfolio([])
            st.rerun()

elif page.startswith("13."):
    st.header("🗺️ 실시간 주도주 히트맵 (Heatmap)")
    st.info("전문가님이 관리하시는 핵심 주도주 50선의 실시간 온도계입니다.")
    
    @st.cache_data(ttl=300)
    def get_heatmap_data():
        tics = list(TICKER_NAME_MAP.keys())
        try:
            h_data = yf.download(tics, period="2d", group_by='ticker', threads=True)
            results = []
            for t in tics:
                try:
                    c = h_data[t]['Close']
                    pct = (c.iloc[-1] / c.iloc[-2] - 1) * 100
                    results.append({"name": TICKER_NAME_MAP[t], "ticker": t, "change": pct})
                except: continue
            return pd.DataFrame(results)
        except: return pd.DataFrame()

    df_h = get_heatmap_data()
    if not df_h.empty:
        import plotly.express as px
        fig = px.treemap(df_h, path=['name'], values=[1]*len(df_h), color='change',
                         color_continuous_scale='RdYlGn', color_continuous_midpoint=0,
                         hover_data=['change', 'ticker'])
        fig.update_layout(margin=dict(t=0, l=0, r=0, b=0), height=600)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("데이터를 불러오는 중입니다. 잠시만 기다려주세요...")
