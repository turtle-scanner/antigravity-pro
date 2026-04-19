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
            with st.form("sg_f"):
                new_id = st.text_input("아이디")
                new_pw = st.text_input("비밀번호", type="password")
                if st.form_submit_button("🛰️ 임관 신청"):
                    if new_id in users: st.error("이미 존재")
                    else: users[new_id] = {"password": new_pw, "status": "pending", "grade": "회원"}; save_users(users); sync_user_to_cloud(new_id, users[new_id]); st.success("신청 완료"); time.sleep(2); st.session_state.show_signup = False; st.rerun()
            if st.button("⬅️ 돌아가기"): st.session_state.show_signup = False; st.rerun()

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
    st.header("📈 마켓 트렌드 요약")
    indices = ["^IXIC", "^GSPC", "NVDA", "TSLA"]
    data = yf.download(indices, period="1d", progress=False)['Close']
    cols = st.columns(4)
    for i, idx in enumerate(indices): cols[i].metric(idx, f"{data[idx].iloc[-1]:,.2f}")

elif page.startswith("3-a."):
    st.header("🎯 주도주 타점 및 RS 스캐너")
    if st.button("🚀 나노급 스캔"):
        df = run_fast_scanner()
        st.dataframe(df, use_container_width=True)

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
