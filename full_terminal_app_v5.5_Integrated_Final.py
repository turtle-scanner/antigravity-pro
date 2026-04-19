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

# --- 🪲 시스템 기초 설정 ---
MASTER_GAS_URL = "https://script.google.com/macros/s/AKfycbyp31pP_T4nVi0rEoeOu-kc6t_ynofxRYnnYZTTO1kxOcQWinBfyhEeDjTRZXzp1eCo/exec"
USERS_SHEET_URL = "https://docs.google.com/spreadsheets/d/1HbC_U1I78HAdV99X6qS1hmY_RiRGPrHX92AYbBPrIpU/export?format=csv&gid=1180564490"
CHAT_SHEET_URL = "https://docs.google.com/spreadsheets/d/1HbC_U1I78HAdV99X6qS1hmY_RiRGPrHX92AYbBPrIpU/export?format=csv&gid=2147147361"
POSTS_SHEET_URL = "https://docs.google.com/spreadsheets/d/1HbC_U1I78HAdV99X6qS1hmY_RiRGPrHX92AYbBPrIpU/export?format=csv&gid=0"

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
            if u_id:
                users[u_id] = {
                    "password": str(row.get('비밀번호', u_id)).strip(),
                    "status": str(row.get('상태', 'approved')).strip(),
                    "grade": str(row.get('등급', '회원')).strip(),
                    "info": {
                        "area": str(row.get('지역', '-')),
                        "age_group": str(row.get('연령대', '-')),
                        "gender": str(row.get('성별', '-')),
                        "exp": str(row.get('경력', '-')),
                        "reg_date": str(row.get('가입일', '-')),
                        "motive": str(row.get('매매동기', '-'))
                    }
                }
    except: pass
    users["cntfed"] = {"password": "cntfed", "status": "approved", "grade": "방장", "info": {}}
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
    body { 
        background-color: var(--bg-dark); 
        color: #e2e8f0; 
        font-family: 'Outfit', sans-serif; 
    }
    .stApp { 
        background-image: linear-gradient(rgba(10, 10, 12, 0.9), rgba(10, 10, 12, 0.9)), url("StockDragonfly2.png");
        background-size: cover;
        background-attachment: fixed;
    }
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
    st.markdown("<h1 style='text-align: center; color: #00FF00; text-shadow: 2px 2px 10px #00FF00; font-family: Outfit; font-weight: 900; margin-bottom: 0px;'>🪲 StockDragonfly Apex 🪲</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888; font-size: 1rem; margin-top: 0px;'>High-Performance Trading Command Center</p>", unsafe_allow_html=True)
    
    users = load_users()
    if "show_signup" not in st.session_state: st.session_state.show_signup = False
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if os.path.exists("StockDragonfly.png"):
            st.image("StockDragonfly.png", use_container_width=True)
            st.write("")
        show_major_announcement()
        if not st.session_state.show_signup:
            st.markdown("<div class='glass-card' style='border: 1px solid #00FF00; margin-top: 20px;'><h2 style='text-align: center; color: #00FF00;'>🛡️ StockDragonfly 사령부 입장</h2></div>", unsafe_allow_html=True)
            with st.form("lg_f"):
                u_id = st.text_input("🎖️ 요원 아이디")
                u_pw = st.text_input("🔐 보안 코드", type="password")
                if st.form_submit_button("🪲 사령부 입장"):
                    if u_id in users and users[u_id]["password"] == u_pw:
                        if users[u_id]["status"] == "approved": st.session_state["password_correct"] = True; st.session_state["current_user"] = u_id; st.session_state["user_grade"] = users[u_id].get("grade", "회원"); st.rerun()
                        else: st.warning("🚷 미승인 계정")
                    else: st.error("❌ 정보 불일치")
            if st.button("🤝 신입 요원 자격 심사 신청"): st.session_state.show_signup = True; st.rerun()
        else:
            st.markdown("<div class='glass-card' style='border: 1px solid #6366f1;'><h2 style='text-align: center; color: #6366f1;'>📝 신입 요원 임관 신청서</h2></div>", unsafe_allow_html=True)
            
            # --- 🛠️ STEP 0: 아이디 사전 검증 ---
            if "id_verified" not in st.session_state: st.session_state.id_verified = None
            
            check_col1, check_col2 = st.columns([3, 1])
            with check_col1:
                check_id = st.text_input("🎖️ 사용하실 요원 아이디를 먼저 입력하세요", value=st.session_state.get("pending_id", ""))
            with check_col2:
                st.write("") # 간격 조절
                if st.button("🔍 중복 확인"):
                    users = load_users()
                    if not check_id: st.warning("ID 입력!")
                    elif check_id in users: 
                        st.error("❌ 이미 사용 중")
                        st.session_state.id_verified = False
                    else: 
                        st.success("✅ 사용 가능!")
                        st.session_state.id_verified = True
                        st.session_state.pending_id = check_id
            
            if st.session_state.get("id_verified"):
                st.info(f"🛡️ **{st.session_state.pending_id}** 아이디로 신청서를 작성합니다.")
                with st.form("sg_f"):
                    st.markdown("### [1단계: 요원 인적 사항 및 전사 프로필]")
                    col_id, col_pw = st.columns(2)
                    with col_id:
                        new_id = st.text_input("🎖️ 요원 아이디 (확인됨)", value=st.session_state.pending_id, disabled=True)
                    with col_pw:
                        new_pw = st.text_input("🔐 희망 보안 코드", type="password", placeholder="비밀번호 설정")
                    
                    st.write("")
                    col_info1, col_info2 = st.columns(2)
                    with col_info1:
                        u_age = st.number_input("🎂 나이", min_value=1, max_value=120, value=30)
                        u_area = st.text_input("🌍 사는 곳 (거주 지역)", placeholder="예: 서울 강남구 / 부산 해운대구")
                    with col_info2:
                        u_gender = st.selectbox("🚻 성별", ["남성", "여성"])
                        u_exp = st.selectbox("🏹 주식 연차 (경력)", ["입문 (1년 미만)", "병사 (1~3년)", "부사관 (3~5년)", "영관급 (5~10년)", "장성급 (10년 이상)"])
                    
                    u_motive = st.text_area("🔥 사령부 임관 및 매매 동기", placeholder="StockDragonfly 사령부에 합류하려는 이유와 투자 목표를 자유롭게 기재하세요.")
                
                    st.divider()
                    st.markdown("### [2단계: 전술 지식 평가 (20 Munhang)]")
                    st.info("⚠️ 위 인적 사항을 모두 기재한 후, 아래 20문제 중 17문제 이상을 맞춰야 임관 신청이 가능합니다.")
                    
                    def get_q(txt, ops): return st.radio(txt, ops, index=None)

                    st.markdown("### [PART 1. 중수용: 돌파 매매 실전 전략]")
                    q1 = get_q("1. 약세장(Defensive Regime)에서 나타나는 현상으로 매매를 중단해야 하는 신호는?", ["주요 지수가 200일 이동평균선 위에서 지지받음", "당일 4% 상승 종목 수가 하락 종목 수보다 많음", "주요 지수가 20일 또는 50일 이동평균선 아래에 위치함", "신고가 경신 종목 수가 전주 대비 20% 증가함"])
                    q2 = get_q("2. VCP 패턴이나 깃발형 패턴 완성 직전의 가장 이상적인 모습은?", ["변동폭이 확대되며 거래량이 평소보다 3배 급증", "변동폭이 좁아지고 거래량이 눈에 띄게 마름(Dry-up)", "주가가 5% 이상 급등락하며 매물을 소화함", "거래량은 많으나 주가는 움직이지 않는 정체 상태"])
                    q3 = get_q("3. 돌파 진입 후 계좌를 지키기 위해 설정하는 '기계적 손절선'의 정석 위치는?", ["매수 진입한 당일의 최저점(LOD)", "매수가 대비 무조건 -10% 지점", "120일 이동평균선이 지나는 자리", "전일 종가보다 1% 낮은 가격"])
                    q4 = get_q("4. 매수 후 3~5일 내에 주가가 8~20% 급등했을 때 취해야 할 행동은?", ["전량 매도하여 수익을 모두 현금화한다.", "추가 매수(불타기)를 통해 비중을 최대화한다.", "물량의 1/3~1/2을 익절하고 손절선을 본절가로 상향한다.", "아무것도 하지 않고 목표가까지 무작정 기다린다."])
                    q5 = get_q("5. 남은 물량으로 큰 수익(홈런)을 노릴 때 사용하는 최종 매도 기준은?", ["당일 고가 대비 5% 하락 시 즉시 매도", "10일 또는 20일 이동평균선을 종가 기준으로 이탈 시", "RSI 지수가 50 이하로 떨어지는 순간", "투자 경고 종목으로 지정되는 날"])
                    q6 = get_q("6. 프라딥 본데가 강조한 '추격 매수 금지'의 기준이 되는 연속 상승 일수는?", ["이미 1일 연속 상승한 종목", "이미 2일 연속 상승한 종목", "이미 3일 연속 상승한 종목", "이미 5일 연속 상승한 종목"])
                    q7 = get_q("7. 돌파 당일 캔들이 어떤 모양으로 마감되어야 신뢰도가 가장 높을까요?", ["윗꼬리가 몸통보다 긴 역망치 모양", "당일 변동폭의 최상단(고가 부근)에서 종가 형성", "시가와 종가가 같은 십자가(도지) 모양", "아래꼬리가 길고 파란색(음봉)으로 마감"])
                    q8 = get_q("8. 강력한 뉴스(촉매제)와 함께 엄청난 거래량으로 갭상승하는 셋업의 명칭은?", ["데드 캣 바운스(Dead Cat Bounce)", "에피소딕 피벗(Episodic Pivot, EP)", "헤드 앤 숄더(Head and Shoulders)", "불 트랩(Bull Trap)"])
                    q9 = get_q("9. 진짜 돌파(True Breakout)로 인정받기 위한 거래량의 조건은?", ["전일 거래량보다 현저히 줄어들어야 함", "평균 거래량의 1.5배~3배 이상 크게 폭발함", "거래량 변화 없이 주가만 빠르게 상승함", "장 시작 직후에만 거래량이 몰리고 사라짐"])
                    q10 = get_q("10. 갭상승 종목의 안전한 진입 타점인 '오프닝 레인지 돌파(ORB)'의 기준은?", ["전일의 종가를 하향 돌파할 때", "장 시작 후 형성된 초기 고점(ORH)을 재돌파할 때", "시가 대비 3% 이상 눌림을 줄 때", "장 마감 10분 전 종가 부근"])

                    st.markdown("### [PART 2. 입문용: 주식 차트 기초]")
                    q11 = get_q("11. 한국 주식 차트에서 '빨간색 양봉' 캔들의 의미는?", ["가격이 시작가보다 낮게 끝났다.", "가격이 시작가보다 높게 끝났다. (상승)", "거래량이 어제보다 줄어들었다.", "주식을 파는 사람이 사는 사람보다 많다."])
                    q12 = get_q("12. 한국 주식 차트에서 '파란색 음봉' 캔들의 의미는?", ["주식 가격이 예전보다 상승했다.", "주식 가격이 예전보다 하락했다.", "주식 시장이 곧 마감된다는 뜻이다.", "외국인이 주식을 많이 샀다는 뜻이다."])
                    q13 = get_q("13. 하루 동안 사람들이 주식을 사고팔았던 '양'을 나타내는 용어는?", ["자본금", "시가총액", "거래량", "유동성"])
                    q14 = get_q("14. 진짜 양초를 닮았다고 해서 붙여진 주식 그래프의 이름은?", ["스틱 차트", "캔들 차트", "바 차트", "라인 차트"])
                    q15 = get_q("15. 주식을 너무 비쌀 때 사지 말라는 의미의 격언은?", ["발바닥에서 사서 정수리에서 팔아라.", "무릎에서 사서 어깨에서 팔아라.", "어깨에서 사서 발바닥에서 팔아라.", "허리에서 사서 머리에서 팔아라."])
                    q16 = get_q("16. 일정 기간 주가 평균을 선으로 이은 것으로, 방향성을 알려주는 지표는?", ["매물대선", "이동평균선(이평선)", "지지저항선", "볼린저밴드"])
                    q17 = get_q("17. 짧은 기간의 평균선이 긴 기간의 평균선을 뚫고 올라가는 '좋은 신호'는?", ["실버크로스", "데드크로스", "골든크로스", "다이아몬드크로스"])
                    q18 = get_q("18. 반대로 짧은 평균선이 긴 평균선 아래로 떨어지는 '나쁜 신호'는?", ["데드크로스", "블랙크로스", "폴링크로스", "다크크로스"])
                    q19 = get_q("19. 주식 시장에서 가격이 가장 낮을 때를 일컫는 말은?", ["고점", "낙점", "하점", "저점"])
                    q20 = get_q("20. 장기적으로 주식 시장의 가격이 점점 우상향하는 주요 원인은?", ["주식 숫자가 줄어들기 때문", "인플레이션으로 인해 화플레이션으로 인해 화폐 가치가 떨어지기 때문", "모든 사람이 주식을 사기 때문", "정부가 주가를 강제로 올리기 때문"])

                    if st.form_submit_button("🪲 임관 신청서 최종 제출"):
                        ans = [q1,q2,q3,q4,q5,q6,q7,q8,q9,q10,q11,q12,q13,q14,q15,q16,q17,q18,q19,q20]
                        final_id = st.session_state.pending_id
                        if not final_id or not new_pw: st.error("정보 입력 필수")
                        elif any(a is None for a in ans): st.warning("모든 문제를 풀어주세요.")
                        else:
                            score = 0
                            corrects = ["주요 지수가 20일 또는 50일 이동평균선 아래에 위치함", "변동폭이 좁아지고 거래량이 눈에 띄게 마름(Dry-up)", "매수 진입한 당일의 최저점(LOD)", "물량의 1/3~1/2을 익절하고 손절선을 본절가로 상향한다.", "10일 또는 20일 이동평균선을 종가 기준으로 이탈 시", "이미 3일 연속 상승한 종목", "당일 변동폭의 최상단(고가 부근)에서 종가 형성", "에피소딕 피벗(Episodic Pivot, EP)", "평균 거래량의 1.5배~3배 이상 크게 폭발함", "장 시작 후 형성된 초기 고점(ORH)을 재돌파할 때", "가격이 시작가보다 높게 끝났다. (상승)", "주식 가격이 예전보다 하락했다.", "거래량", "캔들 차트", "무릎에서 사서 어깨에서 팔아라.", "이동평균선(이평선)", "골든크로스", "데드크로스", "저점", "인플레이션으로 인해 화폐 가치가 떨어지기 때문"]
                            for i in range(20):
                                if ans[i] == corrects[i]: score += 1
                            
                            if score >= 17:
                                users = load_users()
                                if final_id in users: st.error("이미 존재하는 ID")
                                else:
                                    users[final_id] = {
                                        "password": new_pw, "status": "pending", "grade": "회원", "score": score,
                                        "info": {"age": u_age, "gender": u_gender, "area": u_area, "exp": u_exp, "motive": u_motive, "reg_date": datetime.now().strftime("%Y-%m-%d %H:%M")}
                                    }
                                    save_users(users)
                                    gsheet_sync("회원명단", 
                                                ["아이디", "비밀번호", "상태", "등급", "지역", "연령대", "성별", "경력", "가입일", "매매동기"], 
                                                [final_id, new_pw, "pending", "회원", u_area, u_age, u_gender, u_exp, datetime.now().strftime("%Y-%m-%d %H:%M"), u_motive])
                                    st.success(f"축하합니다! {score}점으로 자격 통과. 심사를 기다리세요."); time.sleep(2)
                                    st.session_state.show_signup = False
                                    if "id_verified" in st.session_state: del st.session_state.id_verified
                                    st.rerun()
                            else: st.error(f"💀 점수 미달: {score}/20 (합격 컷: 17). 전술 공부 후 다시 도전하세요.")
            
            with st.expander("💡 🏛️ StockDragonfly 전술 아카데미 (필독 학습 가이드)"):
                hint_html = """
                <div style='color: #FFFFFF; line-height: 1.8; font-size: 1rem; background: rgba(0, 255, 0, 0.05); padding: 25px; border-radius: 15px; border: 1px solid #00FF00;'>
                    <h3 style='color: #00FF00; margin-top: 0;'>🛡️ [PART 1. 마스터 전술 레슨]</h3>
                    <ul style='list-style-type: none; padding-left: 0;'>
                        <li>🚀 <b>시장의 온도(Regime):</b> 지수가 20일/50일선 <b>아래</b>에 있으면 매매 중단!</li>
                        <li>🚀 <b>VCP 패턴:</b> 폭발 전 변동폭 수축과 거래량 <b>마름(Dry-up)</b>은 필수!</li>
                        <li>🚀 <b>손절(Stop-loss):</b> 계좌 사수의 보루는 당일의 <b>최저가(LOD)</b>입니다.</li>
                        <li>🚀 <b>익절과 생존:</b> 8~20% 급등 시 <b>절반 익절</b> 후 손절선을 본절로!</li>
                        <li>🚀 <b>추세 홈런:</b> <b>10일 또는 20일 이동평균선</b> 이탈 전까지 홀딩하십시오.</li>
                        <li>🚀 <b>추격 매수 금지:</b> 이미 <b>3일 연속</b> 상승했다면 절대 사지 마세요.</li>
                        <li>🚀 <b>에피소딕 피벗(EP):</b> 강력한 촉매제와 거래량이 만나는 <b>갭상승</b> 지점!</li>
                        <li>🚀 <b>진짜 돌파:</b> 거래량이 평소보다 <b>1.5배~3배 이상</b> 터져야 가짜가 아닙니다.</li>
                        <li>🚀 <b>ORB 타점:</b> 장 초반의 <b>초기 고점(ORH)</b>을 뚫는 순간이 진입 타점!</li>
                    </ul>
                    <h3 style='color: #00FF00; margin-top: 25px;'>📚 [PART 2. 기초 전술 노하우]</h3>
                    <ul style='list-style-type: none; padding-left: 0;'>
                        <li>💡 <b>캔들의 언어:</b> <b>빨강(양봉)</b>은 상승, <b>파랑(음봉)</b>은 하락입니다.</li>
                        <li>💡 <b>거래량:</b> 장중에 터진 에너지의 총합인 <b>거래량</b>을 항상 보십시오.</li>
                        <li>💡 <b>격언의 지혜:</b> <b>무릎</b>에서 확인하고 <b>어깨</b>에서 내려오세요.</li>
                        <li>💡 <b>이동평균선:</b> 주가의 평균을 이은 선으로 시장의 <b>방향성</b>을 봅니다.</li>
                        <li>💡 <b>크로스:</b> 위로 뚫으면 <b>골든</b>, 아래로 꺾이면 <b>데드</b> 크로스입니다.</li>
                        <li>💡 <b>화폐 가치:</b> 자산 우상향의 근본 원인은 <b>인플레이션</b>입니다.</li>
                    </ul>
                    <p style='color: #FFD700; text-align: center; font-weight: bold; margin-top: 20px;'>⚠️ 가이드를 정독하면 20문항 모두 만점이 가능합니다!</p>
                </div>
                """
                st.markdown(hint_html, unsafe_allow_html=True)
            if st.button("⬅️ 로그인 화면으로 복귀"): st.session_state.show_signup = False; st.rerun()

if "password_correct" not in st.session_state: st.session_state["password_correct"] = False
if not st.session_state["password_correct"]: check_login(); st.stop()

# --- 🪲 StockDragonfly 메인 시스템 가동 ---
def render_top_banners():
    # 🌍 Live Ops & 지수 대시보드
    cols = st.columns([1.5, 3, 1.5])
    with cols[0]:
        st.markdown(f"""
        <div style='background: rgba(0,255,0,0.05); padding: 10px; border-radius: 10px; border-left: 3px solid #00FF00;'>
            <p style='margin: 0; font-size: 0.7rem; color: #00FF00;'>🟢 LIVE OPS CENTER</p>
            <p style='margin: 0; font-size: 0.85rem; font-weight: 700;'>🇰🇷 {datetime.now().strftime('%H:%M:%S')} | 🇺🇸 { (datetime.now() - timedelta(hours=13)).strftime('%H:%M:%S') }</p>
        </div>
        """, unsafe_allow_html=True)
    
    with cols[1]:
        # 🟢 MARKET REGIME ACTIVE BANNER
        st.markdown("""
        <div style='background: rgba(0, 255, 0, 0.05); padding: 15px; border-radius: 15px; border: 2px solid #FFD700; text-align: center; box-shadow: 0 0 20px rgba(0, 255, 0, 0.2);'>
            <h2 style='color: #00FF00; margin: 0; letter-spacing: 2px;'>🟢 GREEN MARKET ACTIVE</h2>
            <p style='color: #6366f1; font-weight: bold; margin: 5px 0 0 0;'>🔵 사령부 상태: 매수 윈도우 개방 (팔로우스루데이 발생: 실시간 감시 중)</p>
            <p style='color: #888; font-size: 0.75rem; font-style: italic; margin-top: 5px;'>"시장의 동력이 가장 약해지는 순간, 강력한 EP를 동반한 주도주만이 하늘로 솟구칩니다. 우리는 그 불꽃에 동참합니다." - Pradeep Bonde</p>
        </div>
        """, unsafe_allow_html=True)
        
    with cols[2]:
        try:
            indices = yf.download(["^IXIC", "^KS11", "^KQ11"], period="1d", progress=False)['Close']
            nq = indices["^IXIC"].iloc[-1]; kp = indices["^KS11"].iloc[-1]; kd = indices["^KQ11"].iloc[-1]
            st.markdown(f"""
            <div style='text-align: right; background: rgba(255,255,255,0.03); padding: 5px 10px; border-radius: 10px;'>
                <p style='margin: 0; font-size: 0.75rem;'>NASDAQ: <span style='color: #00FF00;'>{nq:,.1f}</span></p>
                <p style='margin: 0; font-size: 0.75rem;'>KOSPI: <span style='color: #FF4B4B;'>{kp:,.1f}</span></p>
                <p style='margin: 0; font-size: 0.75rem;'>KOSDAQ: <span style='color: #00FF00;'>{kd:,.1f}</span></p>
            </div>
            """, unsafe_allow_html=True)
        except: st.write("📡 데이터 싱크 중...")

render_top_banners()
st.write("") # 간격 조절
show_global_notice()
with st.sidebar:
    st.markdown(f"**{st.session_state.get('user_grade','회원')} {st.session_state['current_user']} 요원**")
    zones = {
        "🏰 1. 본부 사령부": ["1-a. 👑 관리자 승인 센터", "1-b. 🎖️ HQ 인적 자원 사령부", "1-c. 🔐 계정 보안 설정", "1-d. 🌙 탈퇴/휴식 신청"],
        "📡 2. 시장 상황실": ["2-a. 📈 마켓 트렌드 요약", "2-b. 🗺️ 실시간 히트맵", "2-c. 🌡️ 시장 심리 게이지", "2-d. 🏛️ 사이트 제작 동기"],
        "🏹 3. 주도주 추격대": ["3-a. 🎯 주도주 타점 스캐너", "3-b. 🚀 주도주 랭킹 TOP 50", "3-c. 📝 본데 감시 리스트"],
        "🛡️ 4. 전략 및 리스크": ["4-a. 🔬 프로 분석 리포트", "4-b. 📐 리스크 관리 계산기", "4-c. 🛡️ 리스크 방패"],
        "🎓 5. 마스터 훈련소": ["5-a. 🐝 본데는 누구인가?", "5-b. 📚 주식공부방(차트분석)", "5-c. 📡 나노바나나 정밀 레이더"],
        "🏢 6. 안티그래비티 광장": ["6-a. ✅ 출석체크", "6-b. 💬 소통 대화방", "6-c. 🤝 방문자 인사말 신청"],
        "🤖 7. 자동매매 사령부": ["7-a. 🧪 주식자동매수프로그램(Mock)", "7-b. 📊 자동매매 현황", "7-c. 🏆 사령부 명예의 전당"]
    }
    selected_zone = st.selectbox("전술 구역", list(zones.keys()))
    page = st.radio("세부 작전지", zones[selected_zone])
    if st.button("🚪 로그아웃"): st.session_state["password_correct"] = False; st.rerun()

    # --- 🪲 BGM 전술 사운드 시스템 ---
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
    st.header("👑 신입 요원 임관 승인 센터")
    users = load_users()
    pending = [u for u in users if users[u].get("status") == "pending"]
    if not pending: st.info("현재 대기 중인 임관 신청서가 없습니다.")
    else:
        for u in pending:
            info = users[u].get("info", {})
            with st.container():
                st.markdown(f"""
                <div class='glass-card' style='border: 1px solid #FFD700;'>
                    <h4>🎖️ 요원 코드: {u}</h4>
                    <p><b>[프로필 정보]</b></p>
                    <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 10px;'>
                        <span>🎂 나이: {info.get('age', info.get('age_group', '-'))}세</span>
                        <span>🚻 성별: {info.get('gender', '-')}</span>
                        <span>🌍 지역: {info.get('area', '-')}</span>
                        <span>🏹 경력: {info.get('exp', '-')}</span>
                    </div>
                    <p style='margin-top: 10px;'><b>🔥 매매 동기</b><br>{info.get('motive', '-')}</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"🛡️ {u} 요원 임관 승인", key=f"app_btn_{u}"):
                    users[u]["status"] = "approved"; save_users(users); sync_user_to_cloud(u, users[u]); st.success(f"{u} 요원 임관 완료!"); time.sleep(1); st.rerun()

elif page.startswith("1-b."):
    st.header("🎖️ HQ 인적 자원 사령부")
    users = load_users()
    approved = [u for u in users if users[u].get("status") == "approved"]
    st.subheader(f"📊 활동 중인 정예 요원: {len(approved)}명")
    for u in approved:
        info = users[u].get("info", {})
        with st.expander(f"👤 {users[u].get('grade','회원')} {u} 요원 상세 프로필"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"🎂 나이: {info.get('age', info.get('age_group', '-'))}")
                st.write(f"🚻 성별: {info.get('gender', '-')}")
                st.write(f"🏹 경력: {info.get('exp', '-')}")
            with col2:
                st.write(f"🌍 거주지: {info.get('area', '-')}")
                st.write(f"📅 가입일: {info.get('reg_date', '-')}")
                st.write(f"🏆 자격 점수: {users[u].get('score', '-')}")
            st.markdown("**🔥 전사 임관 동기**")
            st.write(info.get('motive', '-'))
            if st.session_state.user_grade == "방장" and u != "cntfed":
                if st.button(f"💀 {u} 요원 제명", key=f"kick_{u}"):
                    del users[u]; save_users(users); st.error(f"{u} 요원 제명 완료"); time.sleep(1); st.rerun()

elif page.startswith("2-a."):
    st.header("📈 마켓 트렌드 및 데일리 전술 점검")
    score, gainers_4, losers_4, rockets, breadth_ratio = get_market_sentiment()
    status = "Risk-ON 🟢" if score >= 70 else "Neutral 🟡" if score >= 40 else "Risk-OFF 🔴"
    color = "#00FF00" if score >= 70 else "#fbbf24" if score >= 40 else "#ff4b4b"
    st.markdown(f"""
        <div style='background: rgba(0,255,0,0.05); padding: 25px; border-radius: 15px; border-left: 10px solid {color};'>
            <h1 style='color: {color};'>{status} (Score: {score})</h1>
            <p style='color: #EEE;'>Breadth: {breadth_ratio:.0f}% | 4% Gainers: {gainers_4} | Rockets: {rockets}</p>
        </div>
    """, unsafe_allow_html=True)
    st.info("💡 **본데의 전술 지침:** 지수가 50일 이동평균선 아래에 있다면 매매 비중을 급격히 줄이십시오.")
    
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
    if st.button("🪲 나노급 스캔"):
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

elif page.startswith("2."):
    st.header("📝 주도주 분석 및 전술 게시판")
    try:
        df_p = pd.read_csv(POSTS_SHEET_URL)
        if not df_p.empty:
            # 시간순 역순 정렬 (최신글 상단)
            df_p = df_p.iloc[::-1]
            for _, row in df_p.iterrows():
                sender = str(row.get('보낸사람', '사령관'))
                tm = str(row.get('시간', '-'))
                content = str(row.get('내용', '내용 없음'))
                
                st.markdown(f"""
                <div class='glass-card'>
                    <div style='display: flex; justify-content: space-between; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px; margin-bottom: 10px;'>
                        <span style='color: #00FF00; font-weight: 800;'>🎖️ {sender}</span>
                        <span style='color: #888; font-size: 0.85rem;'>{tm}</span>
                    </div>
                    <div style='font-size: 1.1rem; line-height: 1.6; color: #e2e8f0;'>
                        {content}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else: st.info("아직 등록된 게시물이 없습니다.")
    except: st.error("시트 데이터를 불러오는 데 실패했습니다 (URL/권한 확인 요망)")

elif page.startswith("1-c."):
    st.header("🔐 계정 보안 설정")
    with st.form("pw_f"):
        c_pw = st.text_input("현재 PW", type="password")
        n_pw = st.text_input("신규 PW", type="password")
        if st.form_submit_button("🛡️ 변경"):
            users = load_users(); u_id = st.session_state.current_user
            if users[u_id]["password"] == c_pw: users[u_id]["password"] = n_pw; save_users(users); st.success("변경 완료")

elif page.startswith("4-a."):
    st.header("🏛️ BMS Analyzer Pro (Tactical Insight)")
    search_input = st.text_input("분석할 종목명 또는 코드를 입력하세요", "NVDA")
    pro_ticker = resolve_ticker(search_input).upper()
    if pro_ticker:
        try:
            with st.spinner(f"🚀 {pro_ticker} BMS 엔진 분석 중..."):
                stock_obj = yf.Ticker(pro_ticker); hist_data = stock_obj.history(period="1y")
                if len(hist_data) >= 70:
                    if isinstance(hist_data.columns, pd.MultiIndex): hist_data.columns = hist_data.columns.get_level_values(0)
                    curr_v = hist_data['Volume'].iloc[-1]; ma7 = hist_data['Close'].rolling(7).mean(); ma65 = hist_data['Close'].rolling(65).mean(); ti65 = ma7.iloc[-1] / ma65.iloc[-1]
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
                    status_color = "#00FF00" if total_score >= 80 else "#fbbf24" if total_score >= 50 else "#ff4b4b"
                    st.markdown(f"<div style='background-color: #111; padding: 25px; border: 2px solid {status_color}; border-radius: 20px; text-align: center;'><h1 style='color: {status_color}; font-size: 4rem;'>{total_score}</h1><p>BMS 전술 등급</p></div>", unsafe_allow_html=True)
        except: st.error("엔진 가동 오류")

elif page.startswith("4-b."):
    st.header("🧮 리스크 관리 및 포지션 사이징")
    c1, c2 = st.columns(2)
    capital = c1.number_input("총 투자 자산 (KRW)", value=10000000)
    risk_percent = c1.slider("1회 매매당 최대 허용 리스크 (%)", 0.5, 5.0, 1.0)
    entry_price = c1.number_input("예상 진입가", value=100000)
    stop_loss = c2.number_input("기계적 손절가", value=95000)
    target_price = c2.number_input("1차 목표가", value=120000)
    risk_per_share = entry_price - stop_loss
    if risk_per_share > 0:
        pos_size = int((capital * (risk_percent / 100)) / risk_per_share)
        st.metric("🎯 권장 매수 수량", f"{pos_size} 주", delta=f"총 {(pos_size*entry_price):,} 원")
        st.metric("🔄 예상 손익비 (R/R Ratio)", f"{(target_price - entry_price) / risk_per_share:.2f}")

elif page.startswith("12."):
    st.header("🛡️ 리스크 방패 (Trailing Stop)")
    st.info("자산 보호 전략 및 트레일링 스톱 가이드 구역입니다.")

elif page.startswith("5-a."):
    st.header("🏛️ 본데는 누구인가? (Master Class)")
    st.markdown("### 🏆 Pradeep Bonde의 트레이딩 철학")
    st.write("대가의 마인드셋과 실전 전술을 학습하는 사령부 최고 교육 과정입니다.")

elif page.startswith("6-a."):
    st.header("✅ 오늘의 출석 체크")
    if st.button("🎖️ 출석 도장 찍기"): st.success("오늘도 전우애로 승리하십시오!"); st.balloons()

elif page.startswith("1-d."):
    st.header("🌙 탈퇴 및 휴식 신청")
    if st.button("🔥 전역하기"): st.error("전역 처리 중..."); time.sleep(2); st.session_state["password_correct"] = False; st.rerun()

elif page.startswith("2-b."):
    st.header("🔥 Thematic Momentum Heatmap")
    try:
        heatmap_tickers = ["NVDA", "AMD", "AVGO", "SMCI", "TSLA", "AAPL", "MSFT", "GOOGL", "META", "CRWD", "PLTR", "005930.KS", "000660.KS", "196170.KQ", "042700.KS", "003230.KS", "007660.KS", "322000.KS"]
        map_data = []
        for t in heatmap_tickers:
            sk = yf.Ticker(t); h = sk.history(period="60d")
            if h.empty: continue
            disp_name = ticker_map.get(t, t); perf_2m = (h['Close'].iloc[-1] / h['Close'].iloc[0] - 1) * 100
            map_data.append({"Name": disp_name, "Performance": perf_2m, "Volume": h['Volume'].iloc[-1]})
        df_map = pd.DataFrame(map_data)
        fig_map = px.treemap(df_map, path=['Name'], values='Volume', color='Performance', color_continuous_scale='RdYlGn', color_continuous_midpoint=0)
        fig_map.update_layout(template='plotly_dark', height=400)
        st.plotly_chart(fig_map, use_container_width=True)
    except: st.error("히트맵 생성 중 오류")

elif page.startswith("2-c."):
    st.header("🧠 시장 심리 게이지 (Fear & Greed)")
    score, _, _, _, _ = get_market_sentiment()
    gauge_txt = "탐욕(Greedy)" if score >= 70 else "중립(Neutral)" if score >= 40 else "공포(Fear)"
    st.metric("현재 시장 심리 지수", f"{score} / 100", delta=gauge_txt)
    st.progress(score/100)
elif page.startswith("2-d."):
    st.header("🏛️ 제작 동기: StockDragonfly의 철학과 비전")
    st.markdown("""
        <div style='background: rgba(255, 215, 0, 0.05); padding: 30px; border-radius: 20px; border: 1px solid #FFD700;'>
            <h3 style='color: #00FF00;'>🛡️ 왜 StockDragonfly인가?</h3>
            <p style='color: #EEE; line-height: 1.8;'>안티그래비티는 시장의 무거운 '중력'을 이겨내고 하늘로 솟구치는 주도주를 상징합니다. 
            단순한 매매 도구를 넘어, 사령관님을 중심으로 한 정예 요원들이 시장에서 살아남고, 번영하며, 
            결국 경제적 자유라는 최고 사령부에 안착하는 것이 우리의 목표입니다.</p>
        </div>
    """, unsafe_allow_html=True)
elif page.startswith("3-b."):
    st.header("📊 본데의 주식 50선 (Momentum Playbook)")
    try:
        sheet_url = "https://docs.google.com/spreadsheets/d/1xjbe9SF0HsxwY_Uy3NC2tT92BqK0nhArUaYU16Q0p9M/export?format=csv&gid=1499398020"
        df = pd.read_csv(sheet_url)
        st.dataframe(df, use_container_width=True)
        st.markdown(f"""
            <div style='background-color: #111111; padding: 30px; border-radius: 15px; border: 2px solid #FFD700; margin-top: 20px;'>
                <h2 style='color: #00FF00; text-align: center; margin-bottom: 25px;'>🚀 Bonde's Strategic Insight: The Momentum 50 Playbook</h2>
                <p style='color: #EEE; line-height: 1.8;'>주식 시장은 복잡해 보이지만, 본질은 <b>'가속도'</b>와 <b>'관성'</b>의 법칙을 따르는 물리적 전장입니다. 
                거래량이 먼지처럼 말라붙을 때(Dry-up)까지 거북이처럼 인내하십시오. 에너지가 응축될 때까지 기다리는 자만이 폭발적인 성장을 얻을 수 있습니다.</p>
                <div style='background-color: #222; padding: 15px; border-radius: 10px; border-left: 5px solid #00FF00;'>
                    <h4 style='color: #00FF00; margin-top: 0;'>📝 본데의 핵심 가이드 요점 정리</h4>
                    <ul style='color: #FFF; font-size: 0.9rem; line-height: 1.8;'>
                        <li><b>급등은 구경:</b> 장대양봉은 감시 목록에 넣어야 할 '신호'일 뿐입니다.</li>
                        <li><b>응축을 매수:</b> 거래량이 먼지처럼 마르고 캔들이 작아지는 '고요한 지점'을 찾으세요.</li>
                        <li><b>생존 규율:</b> 진입 즉시 -3% 손절을 설정하고, 3일 내 반응이 없으면 팔고 나오십시오.</li>
                    </ul>
                </div>
            </div>
        """, unsafe_allow_html=True)
    except: st.error("데이터 싱크 오류")
elif page.startswith("3-c."): st.header("📋 본데 감시 리스트"); st.info("피벗 포인트 돌파 전 관심주 구역입니다.")
elif page.startswith("4-c."): st.header("🛡️ 리스크 방패 (Trailing Stop)"); st.info("자산 보호 전략 및 트레일링 스톱 가이드 구역입니다.")
elif page.startswith("6-b."): st.header("💬 소통 대화방"); st.info("실시간 시장 상황 공유 및 회원 간 종목 토론 구역입니다.")

elif page.startswith("7-a."):
    st.header("🧪 주식자동매수프로그램 (Trader Bot Mock)")
    st.markdown("""
        <div style='background: rgba(0,255,0,0.05); padding: 30px; border-radius: 20px; border: 2px solid #00FF00;'>
            <h3 style='color: #00FF00;'>🤖 알고리즘 자동 매수 엔진 가동 중</h3>
            <p style='color: #EEE;'>선택된 주도주가 설정한 피벗 포인트를 돌파하는 순간, 시스템이 기계적으로 매수를 집행합니다.</p>
            <hr style='border: 0.5px solid #333;'>
            <div style='display: flex; justify-content: space-around;'>
                <div><p style='margin:0; color:#888;'>오늘의 매수 집행</p><h3>5건</h3></div>
                <div><p style='margin:0; color:#888;'>평균 체결가 대비</p><h3 style='color:#00FF00;'>+2.45%</h3></div>
                <div><p style='margin:0; color:#888;'>봇 상태</p><h3 style='color:#00FF00;'>ACTIVE</h3></div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    if st.button("🚀 알고리즘 긴급 정지"): st.error("시스템이 중단되었습니다.")

elif page.startswith("7-b."): st.header("📊 자동매매 현황"); st.info("현재 봇이 관리 중인 포지션과 수익률 실시간 현황판입니다.")
elif page.startswith("7-c."): st.header("🏆 사령부 명예의 전당"); st.success("사령부 최고의 수익률을 기록한 요원들의 기록실입니다.")
elif page.startswith("5-b."):
    st.header("📚 주식공부방: 1,000개 폭등주 패턴 딥 다이브")
    st.info("📊 과거 100년간의 폭등주들이 보였던 VCP(변동성 수축)와 컵앤핸들 패턴의 정수를 학습합니다.")
    st.markdown("### 🏹 전술 교본 도서관\n- **교본 1:** 마크 미너비니의 '승자처럼 생각하고 행동하라' 핵심 요약\n- **교본 2:** 윌리엄 오닐의 CANSLIM 원칙 실전 적용")

elif page.startswith("5-c."):
    st.header("📡 나노바나나 정밀 레이더: 숙성도 판독 훈련")
    st.markdown("""
        <div style='background: #111; padding: 25px; border-radius: 15px; border-left: 5px solid #FFFF00;'>
            <h4 style='color: #FFFF00;'>🍌 나노바나나 전술이란?</h4>
            <p style='color: #DDD; line-height: 1.7;'>차트가 마치 잘 익은 바나나처럼 노랗고 부드럽게(Tightness) 숙성되는 과정을 포착하는 안목 훈련입니다. 
            이평선이 수렴하고 거래량이 먼지처럼 마를 때(Dry-up), 바로 그때가 타점입니다.</p>
        </div>
    """, unsafe_allow_html=True)

elif page.startswith("6-c."):
    st.header("🤝 방문자 인사말 신청")
    st.info("새롭게 합류한 전우들에게 따뜻한 환영과 격려의 인사를 남기는 공간입니다. (로딩 중...)")

# --- 🪲 시스템 푸터 및 전술 통찰 ---
def render_footer():
    st.divider()
    # 🕵️ 본데의 일간 전술 통찰 (Daily Tactical Insight)
    st.markdown("""
    <div style='text-align: center; padding: 20px; border-top: 1px solid rgba(255,255,255,0.1); margin-top: 30px;'>
        <p style='color: #6366f1; font-weight: bold; margin: 0;'>🔵 본데의 일간 전술 통찰 (Daily Tactical Insight)</p>
        <p style='color: #FFD700; font-style: italic; font-size: 0.9rem; margin-top: 8px;'>
            "희망(Hope)은 트레이딩 전략이 아니다. 본전 오면 팔겠다는 생각은 시장에 당신의 전 재산을 기부하겠다는 선언과 같다."
        </p>
        <p style='color: #555; font-size: 0.75rem; margin-top: 15px;'>© 2026 StockDragonfly Terminal v10.6 | Institutional System Operated by Global Expert Tactician</p>
    </div>
    """, unsafe_allow_html=True)

render_footer()
