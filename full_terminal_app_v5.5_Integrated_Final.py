# 🛸 Antigravity Pro Terminal v10.6 Apex Edition (FINAL RESTORED)
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import os
import json
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import requests
import time

# --- 🛰️ 시스템 기초 설정 ---
MASTER_GAS_URL = "https://script.google.com/macros/s/AKfycbyp31pP_T4nVi0rEoeOu-kc6t_ynofxRYnnYZTTO1kxOcQWinBfyhEeDjTRZXzp1eCo/exec"
USERS_SHEET_URL = "https://docs.google.com/spreadsheets/d/1HbC_U1I78HAdV99X6qS1hmY_RiRGPrHX92AYbBPrIpU/export?format=csv&gid=1180564490"
CHAT_SHEET_URL = "https://docs.google.com/spreadsheets/d/1HbC_U1I78HAdV99X6qS1hmY_RiRGPrHX92AYbBPrIpU/export?format=csv&gid=2147147361"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USER_DB_FILE = os.path.join(BASE_DIR, "users_db.json")
TRADES_DB = os.path.join(BASE_DIR, "trades_db.json")

def gsheet_sync(sheet_name, headers, values):
    try: requests.post(MASTER_GAS_URL, json={"sheetName": sheet_name, "headers": headers, "values": values}, timeout=5)
    except: pass

@st.cache_data(ttl=60)
def load_users():
    users = {}
    if os.path.exists(USER_DB_FILE):
        try:
            with open(USER_DB_FILE, "r", encoding="utf-8") as f: users = json.load(f)
        except: pass
    try:
        df_u = pd.read_csv(USERS_SHEET_URL)
        for _, row in df_u.iterrows():
            u_id = str(row.get('아이디', '')).strip()
            if u_id: users[u_id] = {"password": str(row.get('비밀번호', u_id)), "status": str(row.get('상태', 'approved')), "grade": str(row.get('등급', '회원')), "info": {}}
    except: pass
    users["cntfed"] = {"password": "cntfed", "status": "approved", "grade": "방장"}
    return users

def save_users(users):
    with open(USER_DB_FILE, "w", encoding="utf-8") as f: json.dump(users, f, ensure_ascii=False, indent=4)
    load_users.clear()

def sync_user_to_cloud(uid, udata):
    return gsheet_sync("회원명단", ["아이디", "비밀번호", "상태", "등급"], [uid, udata.get("password"), udata.get("status"), udata.get("grade")])

def run_fast_scanner():
    try:
        tics = ["AAPL", "NVDA", "TSLA", "PLTR", "MSFT"]
        data = yf.download(tics, period="1d", progress=False)['Close']
        perf = ((data.iloc[-1] / data.iloc[0]) - 1) * 100
        return pd.DataFrame([{"Ticker": t, "Perf": f"{p:.2f}%"} for t, p in perf.items()])
    except: return pd.DataFrame()

def track_smart_money(t):
    try:
        inst = yf.Ticker(t).info.get('heldPercentInstitutions', 0) * 100
        return {"inst": inst, "status": "🟢 강력" if inst > 60 else "🟡 보통"}
    except: return None

# --- 🌑 프리미엄 스타일 시트 ---
st.set_page_config(page_title="StockDragonfly Apex v10.6", page_icon="🛸", layout="wide")
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;700;900&display=swap');
    :root { --primary-neon: #00FF00; --accent-glow: #6366f1; --bg-dark: #0a0a0c; }
    body { background-color: var(--bg-dark); color: #e2e8f0; font-family: 'Outfit', sans-serif; }
    .stApp { background: linear-gradient(135deg, #0a0a0c 0%, #111118 100%); }
    .glass-card { background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 20px; padding: 25px; margin-bottom: 25px; box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8); }
    .stButton>button { background: rgba(99, 102, 241, 0.1); color: white; border: 1px solid var(--accent-glow); border-radius: 12px; padding: 10px 20px; transition: all 0.3s ease; font-weight: 700; }
    .stButton>button:hover { background: var(--accent-glow); box-shadow: 0 0 20px var(--accent-glow); transform: translateY(-2px); }
</style>
""", unsafe_allow_html=True)

# --- 📢 공지사항/시스템 메인 로직 ---
def show_major_announcement():
    if "hide_major_notice" not in st.session_state: st.session_state.hide_major_notice = False
    if not st.session_state.hide_major_notice:
        st.markdown("""<div class='glass-card' style='border: 2px solid #00FF00; background: rgba(0,0,0,0.8);'><h2 style='color: #00FF00; text-align: center;'>📢 시스템 고도화 및 보안 업데이트 안내</h2><p style='font-size: 1.1rem; line-height: 1.6;'>안녕하세요, 관리자입니다.<br>시스템 엔진 개편 및 보안 강화를 위해 모든 회원의 임시 비밀번호가 <b>1234</b>로 초기화되었습니다.<br>[조치 방법]: 상단 [1-c 계정보안설정]에서 변경하십시오.</p></div>""", unsafe_allow_html=True)
        if st.button("❌ 확인 (다시 열지 않기)"): st.session_state.hide_major_notice = True; st.rerun()

def show_global_notice():
    st.markdown("""<div style='background: rgba(0, 255, 0, 0.05); border-left: 5px solid #00FF00; padding: 15px; border-radius: 10px; margin-bottom: 25px;'><span style='color: #00FF00; font-weight: 800;'>[사령부 긴급 공지]</span> <span style='color: #e2e8f0; margin-left: 10px;'>🚨 보안 지침: 공용 보안 코드가 '1234'로 갱신되었습니다. (1-c)에서 변경하십시오.</span></div>""", unsafe_allow_html=True)

def check_login():
    users = load_users()
    if "show_signup" not in st.session_state: st.session_state.show_signup = False
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if os.path.exists("StockDragonfly.png"):
            st.image("StockDragonfly.png", use_container_width=True)
            st.write("")
        show_major_announcement()
        if not st.session_state.show_signup:
            st.markdown("<div class='glass-card' style='border: 1px solid #00FF00; margin-top: 20px;'><h2 style='text-align: center; color: #00FF00;'>🛡️ 안티그래비티 사령부 입장</h2></div>", unsafe_allow_html=True)
            with st.form("lg_f"):
                u_id = st.text_input("🎖️ 요원 아이디")
                u_pw = st.text_input("🔐 보안 코드", type="password")
                if st.form_submit_button("🚀 사령부 입장"):
                    if u_id in users and users[u_id]["password"] == u_pw:
                        if users[u_id]["status"] == "approved": st.session_state["password_correct"] = True; st.session_state["current_user"] = u_id; st.session_state["user_grade"] = users[u_id].get("grade", "회원"); st.rerun()
                        else: st.warning("🚷 미승인 계정")
                    else: st.error("❌ 정보 불일치")
            if st.button("🤝 신입 요원 자격 심사 신청"): st.session_state.show_signup = True; st.rerun()
        else:
            st.markdown("<div class='glass-card' style='border: 1px solid #6366f1;'><h2 style='text-align: center; color: #6366f1;'>📝 신입 요원 자격 심사 (15 Munhang)</h2></div>", unsafe_allow_html=True)
            with st.form("sg_f"):
                new_id = st.text_input("🎖️ 희망 요원 아이디")
                new_pw = st.text_input("🔐 희망 보안 코드", type="password")
                st.divider()
                st.info("⚠️ 아래 15개 전술 퀴즈를 모두 풀어야 임관 신청이 가능합니다.")
                
                # 15문항 자격 심사 (원본 로직 복구)
                q1 = st.radio("1. 주도주 매매의 창시자, 윌리엄 오닐의 핵심 전략은?", ["CANSLIM", "BUY & HOLD"], index=None)
                q2 = st.radio("2. 마크 미너비니가 강조한 'VCP' 패턴의 핵심은?", ["동동성 수축(Volatility Contraction)", "이동평균선 골든크로스"], index=None)
                q3 = st.radio("3. 본데의 '에피소딕 피벗(EP)' 발생 시 가장 중요한 요소는?", ["역대급 거래량과 펀더멘털의 변화", "보조지표 RSI의 과매도"], index=None)
                q4 = st.radio("4. 손절매의 원칙으로 가장 적절한 것은?", ["기계적으로 -3% 이내 수행", "본전이 올 때까지 인내"], index=None)
                q5 = st.radio("5. 주도주를 찾기 위한 지표 'RS'의 의미는?", ["Relative Strength(상대적 강도)", "Return on Stocks(주식 수익률)"], index=None)
                q6 = st.radio("6. 시장의 온도(Market Breadth)를 체크하는 이유는?", ["공격적 투자 시기를 판별하기 위해", "실적 발표일을 확인하기 위해"], index=None)
                q7 = st.radio("7. 계좌의 총 위험도(Total Heat)는 최대 몇 %를 권장하는가?", ["6% 이내", "50% 이내"], index=None)
                q8 = st.radio("8. 매수 후 3~5일간 반응이 없다면 어떻게 해야 하는가?", ["시간 정지 원칙에 따라 매도 고려", "추가 매수(물타기)"], index=None)
                q9 = st.radio("9. 돌파 매매 시 진입 시점은?", ["긴 횡보 끝에 거래량을 실은 돌파 시", "바닥에서 첫 양봉이 나올 때"], index=None)
                q10 = st.radio("10. 주식 매매를 무엇으로 정의해야 하는가?", ["확률 기반의 비즈니스(Business)", "대박을 노리는 한판 승부"], index=None)
                q11 = st.radio("11. 차트 분석 전 가장 먼저 확인해야 할 요소는?", ["글로벌 시장 레짐(Market Regime)", "최근 뉴스 검색"], index=None)
                q12 = st.radio("12. 본데의 'MAGNA' 필터는 무엇을 판별하는가?", ["기업의 펀더멘털과 성장세", "주가의 변동성"], index=None)
                q13 = st.radio("13. 윌리엄 오닐이 강조한 'L'은 무엇인가?", ["Leader(주도주)", "Low Price(저가주)"], index=None)
                q14 = st.radio("14. 분산 투자에 대한 안티그래비티의 철학은?", ["소수 정예 종목에 집중 투자", "수십 개 종목에 골고루 분산"], index=None)
                q15 = st.radio("15. 당신은 원칙을 목숨처럼 지키겠습니까?", ["예 (I AM A WARRIOR)", "아니오"], index=None)

                if st.form_submit_button("🛰️ 임관 신청서 최종 제출"):
                    if not new_id or not new_pw: st.error("정보 입력 필수")
                    elif any(q is None for q in [q1,q2,q3,q4,q5,q6,q7,q8,q9,q10,q11,q12,q13,q14,q15]): st.warning("모든 퀴즈에 답해야 합니다.")
                    else:
                        users = load_users()
                        if new_id in users: st.error("이미 사용 중인 ID")
                        else:
                            users[new_id] = {"password": new_pw, "status": "pending", "grade": "회원", "quiz": "PASSED"}
                            save_users(users); sync_user_to_cloud(new_id, users[new_id]); st.success("임관 신청 완료! 심사 결과를 기다리세요."); time.sleep(2); st.session_state.show_signup = False; st.rerun()
            if st.button("⬅️ 로그인 화면으로 복귀"): st.session_state.show_signup = False; st.rerun()

if "password_correct" not in st.session_state: st.session_state["password_correct"] = False
if not st.session_state["password_correct"]: check_login(); st.stop()

# --- 🚀 메인 시스템 가동 ---
with st.sidebar:
    st.markdown(f"**{st.session_state.get('user_grade','회원')} {st.session_state['current_user']} 요원**")
    zones = {
        "🏰 1. 본부 사령부": ["1-a. 👑 관리자 승인 센터", "1-b. 🎖️ HQ 인적 자원 사령부", "1-c. 🔐 계정 보안 설정", "1-d. 🌙 탈퇴/휴식 신청", "1-e. 🏅 대원 활동 뱃지 보관함"],
        "📡 2. 시장 상황실": ["2-a. 📈 마켓 트렌드 요약", "2-b. 🗺️ 실시간 히트맵", "2-c. 🌡️ 시장 심리 게이지", "2-d. 🏛️ 제작 동기", "2-e. 🚦 업종별 섹터 로테이션", "2-f. 📢 AI 실시간 시황 브리핑"],
        "🏹 3. 주도주 추격대": ["3-a. 🎯 주도주 타점 스캐너", "3-b. 🚀 주도주 랭킹 TOP 50", "3-c. 📊 본데 감시 리스트", "3-d. 📊 기관 수급 추격 레이더"]
    }
    selected_zone = st.selectbox("전술 구역", list(zones.keys()))
    page = st.radio("세부 작전지", zones[selected_zone])
    if st.button("🚪 로그아웃"): st.session_state["password_correct"] = False; st.rerun()

    # --- 🛸 BGM 전술 사운드 시스템 ---
    st.divider()
    st.markdown("### 🎙️ BGM 커맨드 센터")
    bgm_files = [f for f in os.listdir(BASE_DIR) if f.endswith(".mp3")]
    
    # [Featured] my bonde 시그니처 사운드
    if os.path.exists(os.path.join(BASE_DIR, "my bonde.mp3")):
        st.markdown("<span style='color: #00FF00; font-weight: 800;'>🏆 Theme: my bonde</span>", unsafe_allow_html=True)
        st.audio(os.path.join(BASE_DIR, "my bonde.mp3"))

    # [Featured] bird/burd 전심 전술 사운드
    bird_file = next((f for f in bgm_files if f.lower().startswith("bird") or f.lower().startswith("burd")), None)
    if bird_file:
        st.markdown("<span style='color: #6366f1; font-weight: 800;'>🦅 Combat: bird</span>", unsafe_allow_html=True)
        st.audio(os.path.join(BASE_DIR, bird_file))
        st.divider()

    bgm_files = [f for f in bgm_files if f not in ["my bonde.mp3", bird_file]]
    if bgm_files:
        selected_bgm = st.selectbox("기타 전술 음악 선택", bgm_files)
        st.audio(os.path.join(BASE_DIR, selected_bgm))
    else: st.info("추가 사운드 파일이 없습니다.")

show_global_notice()

if page.startswith("1-a."):
    st.header("👑 신입 요원 임관 심사")
    users = load_users()
    pending = {k: v for k, v in users.items() if v["status"] == "pending"}
    for u, data in pending.items():
        if st.button(f"승인: {u}"): users[u]["status"] = "approved"; save_users(users); sync_user_to_cloud(u, users[u]); st.rerun()

elif page.startswith("2-a."):
    st.markdown("<h2 style='color: #00FF00;'>📈 마켓 트렌드 및 데일리 전술 점검</h2>", unsafe_allow_html=True)
    
    # 📊 주요 지수 실시간 대시보드
    indices = {"NASDAQ": "^IXIC", "S&P 500": "^GSPC", "KOSPI": "^KS11", "KOSDAQ": "^KQ11"}
    cols = st.columns(4)
    try:
        data = yf.download(list(indices.values()), period="5d", progress=False)['Close']
        for i, (name, tic) in enumerate(indices.items()):
            curr = data[tic].iloc[-1]
            prev = data[tic].iloc[-2]
            chg = (curr/prev - 1) * 100
            cols[i].metric(name, f"{curr:,.2f}", f"{chg:.2f}%")
    except: st.warning("지수 데이터 로딩 중...")

    st.divider()
    
    # 📑 데일리 전술 체크리스트 (15개 문항 복구)
    st.markdown("### 📋 오늘의 전술 체크리스트")
    with st.expander("🛡️ 작전 개시 전 반드시 확인 (클릭하여 전술 점검)", expanded=True):
        st.markdown("""
        <div style='background: rgba(0, 255, 0, 0.05); padding: 15px; border-radius: 10px; border: 1px solid #00FF00;'>
            <p>✅ <b>[1] 마켓 레짐:</b> 지수가 20일선 위에 있는가? (GREEN LIGHT?)</p>
            <p>✅ <b>[2] 주도 섹터:</b> 오늘 시장을 이끄는 섹터가 명확한가?</p>
            <p>✅ <b>[3] EP 포착:</b> 어닝 서프라이즈와 함께 갭 상승한 종목이 있는가?</p>
            <p>✅ <b>[4] 거래량:</b> 돌파 시 평균 거래량의 150% 이상이 실렸는가?</p>
            <p>✅ <b>[5] 손절 원칙:</b> 모든 포지션에 -3% 하드 스탑이 걸려 있는가?</p>
            <p>✅ <b>[6] 자금 관리:</b> 한 종목에 자산의 20% 이상을 배정하지 않았는가?</p>
            <p>✅ <b>[7] 펀더멘털:</b> MAGNA 필터(매출/이익 성장)를 통과했는가?</p>
            <p>✅ <b>[8] VCP 패턴:</b> 변동성이 수축되며 매수 타점을 형성했는가?</p>
            <p>✅ <b>[9] RS 점수:</b> 지수 대비 강력한 상대 강도를 유지하고 있는가?</p>
            <p>✅ <b>[10] 시간 지지:</b> 매수 후 3~5일 내에 반응이 오지 않으면 정리할 준비가 되었는가?</p>
            <p>✅ <b>[11] 심리 조절:</b> 포모(FOMO)에 휩싸여 추격 매수하고 있지 않은가?</p>
            <p>✅ <b>[12] 뉴스 필터:</b> 시장의 소음을 제외하고 가격과 거래량에만 집중하는가?</p>
            <p>✅ <b>[13] 기록:</b> 모든 매매 진입 이유를 매매 일지에 기록했는가?</p>
            <p>✅ <b>[14] 루틴:</b> 전날 밤 미리 관심 종목 리스트를 확정했는가?</p>
            <p>✅ <b>[15] 원칙 준수:</b> 오늘 하루도 감정이 아닌 원칙으로 매매할 것인가?</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.info("💡 **전술 지침:** 체크리스트 중 12개 이상이 통과되지 않는다면, 현금을 보유하고 관망하는 것이 가장 훌륭한 전략입니다.")

elif page.startswith("3-a."):
    st.header("🎯 주도주 타점 및 RS 스캐너")
    if st.button("🚀 나노급 스캔"):
        df = run_fast_scanner()
        st.dataframe(df, use_container_width=True)

elif page.startswith("5-f."):
    st.markdown("<h2 style='text-align: center; color: #FFD700;'>📝 정기 요원 승급 시험 (Promotion Exam)</h2>", unsafe_allow_html=True)
    
    def get_exam_status_apex():
        now = datetime.now()
        # 이번 달의 마지막 날 찾기
        next_month = now.replace(day=28) + timedelta(days=4)
        last_day = next_month - timedelta(days=next_month.day)
        # 이번 달의 마지막 토요일 찾기
        last_sat = last_day
        while last_sat.weekday() != 5: # 5 is Saturday
            last_sat -= timedelta(days=1)
        
        exam_start = last_sat.replace(hour=11, minute=0, second=0, microsecond=0)
        exam_end = exam_start + timedelta(hours=2)
        
        is_open = (exam_start <= now <= exam_end)
        return is_open, exam_start.strftime("%Y-%m-%d %H:00")

    is_open, next_exam = get_exam_status_apex()
    
    st.markdown(f"""
    <div class='glass-card' style='border: 1px solid #FFD700;'>
        <h4>📢 시험실 운영 지침</h4>
        <p>본 시험은 사령부 정예 요원(Junior 이상)으로 승급하기 위한 필수 관문입니다.</p>
        <p><b>운영 시간:</b> 매달 마지막 토요일 11:00 ~ 13:00 (2시간)</p>
        <p><b>현재 상태:</b> {"<span style='color: #00FF00;'>✅ 개방됨</span>" if is_open else "<span style='color: #FF4B4B;'>❌ 폐쇄됨</span>"}</p>
        <p><b>다음 예정일:</b> {next_exam}</p>
    </div>
    """, unsafe_allow_html=True)

    if is_open or st.session_state.user_grade == "방장":
        st.write("---")
        if st.session_state.user_grade == "방장":
            st.warning("🛡️ 사령관 권한으로 시험실 강제 입장 중 (테스트 모드)")
            
        with st.form("apex_exam_v10"):
            st.markdown("### [전술 평가 1단계: 이론]")
            q1 = st.radio("1. 프라딥 본데가 강조한 '에피소딕 피벗(EP)'의 핵심 발생 조건은?", 
                         ["어닝 서프라이즈 등 강력한 펀더멘털 변화 + 역대급 거래량", "단순히 전고점을 돌파하는 차트 모양"], index=None)
            
            q2 = st.radio("2. 주식 전사로서 단일 매매에서 반드시 사수해야 할 손절 원칙은?", 
                         ["-3% 이내 칼손절", "본전이 올 때까지 장기 보유"], index=None)
            
            st.markdown("### [전술 평가 2단계: 자금 운용]")
            q3 = st.radio("3. 내 계좌 전체의 '오픈 리스크(Total Heat)'는 최대 몇 %를 넘지 말아야 하는가?", 
                         ["6% 이내", "50% 이내"], index=None)
            
            submitted = st.form_submit_button("🛡️ 답안지 최종 제출")
            
            if submitted:
                if q1 and q2 and q3:
                    score = 0
                    if q1 == "어닝 서프라이즈 등 강력한 펀더멘털 변화 + 역대급 거래량": score += 33
                    if q2 == "-3% 이내 칼손절": score += 33
                    if q3 == "6% 이내": score += 34
                    
                    if score >= 100:
                        st.balloons()
                        st.success(f"🎊 장하십니다! {st.session_state.current_user} 요원, 만점 합격입니다!")
                        gsheet_sync("시험결과", ["시간", "아이디", "점수", "결과"], 
                                    [datetime.now().strftime("%Y-%m-%d %H:%M"), st.session_state.current_user, score, "합격"])
                    else:
                        st.error(f"💀 불합격 (점수: {score}). 전술 공부가 더 필요합니다. 다시 도전하십시오.")
                else:
                    st.warning("모든 문항에 답을 하셔야 사령관님께 제출됩니다.")
    else:
        st.info("현재 시험 기간이 아닙니다. 공부방(5-b)에서 실력을 먼저 쌓으십시오.")

elif page.startswith("1-c."):
    st.header("🔐 계정 보안 설정")
    with st.form("pw_f"):
        c_pw = st.text_input("현재 PW", type="password")
        n_pw = st.text_input("신규 PW", type="password")
        if st.form_submit_button("🛡️ 변경"):
            users = load_users(); u_id = st.session_state.current_user
            if users[u_id]["password"] == c_pw: users[u_id]["password"] = n_pw; save_users(users); st.success("변경 완료")

elif page.startswith("1-d."):
    st.header("🌙 탈퇴 및 휴식 신청")
    if st.button("🔥 전역하기"): st.error("전역 처리 중..."); time.sleep(2); st.session_state["password_correct"] = False; st.rerun()

# --- 🛰️ 시스템 푸터 ---
st.divider()
st.markdown("<div style='text-align: center; color: #666;'>© 2026 StockDragonfly Terminal Apex v10.6</div>", unsafe_allow_html=True)
