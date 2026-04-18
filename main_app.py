# Project Started: 2026-04-18 15:54
# Antigravity Trader Terminal - Stock Program 🚀
import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# --- [07] Trader Mind Clinic (Emotion Diagnostics) ---
def render_mind_clinic():
    st.markdown("<h1 style='color:#FFD700; text-align:center; font-family:Orbitron;'>🧘 MIND CLINIC</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>Stop Revenge Trading & Maintain Discipline</p>", unsafe_allow_html=True)
    
    with st.form("mind_check"):
        emotion = st.select_slider("현재 감정 상태는 어떠신가요?", ["매우 불안", "불안", "보통", "안정", "매우 안정"])
        loss_today = st.number_input("오늘의 손실액 (혹은 %, 마이너스로 입력)", step=1.0)
        is_revenge = st.checkbox("지금 매수한 종목이 손실을 복구하기 위한 건가요?")
        submit = st.form_submit_button("심리 진단 받기")
        
        if submit:
            if is_revenge:
                st.error("🚨 **위험 경보: 뇌동매매 감지!** 손실 복구 심리는 가장 큰 파산의 원인입니다. 당장 HTS를 끄고 산책을 다녀오세요.")
            elif loss_today < -5:
                st.warning("⚠️ **손실 관리 주의:** 오늘 손실이 큽니다. 본데 전략은 내일도 유효합니다. 오늘은 쉬는 것이 최고의 전략입니다.")
            else:
                st.success("✅ **심리 안정 상태:** 냉철한 판단을 내릴 준비가 되셨습니다. 원칙에 따른 매매를 진행하세요.")
    
    if st.button("🏠 BACK TO DASHBOARD"): st.session_state['page'] = "🏠 대시보드"; st.rerun()

# --- [08] Intelligence Forum v2 (SQLite Based) ---
def render_forum():
    st.markdown("<h1 style='color:#FFD700; text-align:center; font-family:Orbitron;'>💬 INTELLIGENCE FORUM</h1>", unsafe_allow_html=True)
    
    conn = sqlite3.connect('forum.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY, author TEXT, content TEXT, timestamp TEXT)''')
    conn.commit()
    
    # 글쓰기
    with st.expander("📝 새로운 전략 및 뉴스 공유하기"):
        new_post = st.text_area("내용을 입력하세요 (차트 분석, 타점 공유 등)")
        if st.button("게시하기"):
            c.execute("INSERT INTO posts (author, content, timestamp) VALUES (?, ?, ?)", 
                      (st.session_state.get('username', 'Guest'), new_post, datetime.now().strftime("%Y-%m-%d %H:%M")))
            conn.commit()
            st.success("게시되었습니다!")
    
    # 글 목록
    st.markdown("---")
    posts = c.execute("SELECT * FROM posts ORDER BY id DESC").fetchall()
    for p in posts:
        st.markdown(f"**👤 {p[1]}** | _{p[3]}_")
        st.markdown(p[2])
        st.markdown("---")
    
    conn.close()
    if st.button("🏠 BACK TO DASHBOARD"): st.session_state['page'] = "🏠 대시보드"; st.rerun()

# --- [Bottom] Sector Money Flow Heatmap ---
def render_sector_heatmap():
    st.markdown("<h2 style='text-align:center; color:#10b981;'>📊 SECTOR MONEY FLOW</h2>", unsafe_allow_html=True)
    
    data = {"Sector": ["Tech", "Bio", "Energy", "Finance", "Consumer", "AI", "SemiCon", "EV"],
            "Change": [2.4, -0.8, 1.2, 0.5, -1.5, 4.2, 3.8, 1.1]}
    df = pd.DataFrame(data)
    
    fig = px.treemap(df, path=['Sector'], values=[abs(x) for x in df['Change']],
                     color='Change', color_continuous_scale='RdYlGn',
                     title="Global Sector Performance Heatmap")
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"})
    st.plotly_chart(fig, use_container_width=True)

# --- Main Routine ---
def main():
    st.set_page_config(page_title="Antigravity Trader Terminal", page_icon="🚀", layout="wide")
    
    if 'page' not in st.session_state:
        st.session_state['page'] = "🏠 대시보드"

    st.sidebar.title("💎 TRADER TERMINAL")
    
    # --- [BGM Control Section] ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎵 BGM CONTROL")
    bgm_files = {
        "OFF": None,
        "나의 아저씨": "나의 아저씨 [ BGM ].mp3",
        "싱그러운": "싱그러운.mp3",
        "You Raise Me Up": "You Raise Me Up  Lyrics.mp3",
        "귀여운": "귀여운.mp3",
        "설렘 Piano": "설렘Piano.mp3",
        "기분좋은": "기분좋은.mp3"
    }

    selected_bgm_name = st.sidebar.selectbox("노래 선택", list(bgm_files.keys()))
    selected_file = bgm_files[selected_bgm_name]

    if selected_file:
        if os.path.exists(selected_file):
            audio_file = open(selected_file, 'rb')
            audio_bytes = audio_file.read()
            st.sidebar.audio(audio_bytes, format='audio/mp3', start_time=0)
            st.sidebar.caption(f"Currently Playing: {selected_bgm_name}")
        else:
            st.sidebar.error(f"❌ {selected_file} 파일이 폴더에 없습니다.")

    st.sidebar.markdown("---")
    menu = ["🏠 대시보드", "🧘 마인드 클리닉", "💬 인텔리전스 포럼"]
    choice = st.sidebar.radio("Menu", menu, index=menu.index(st.session_state['page']))
    st.session_state['page'] = choice

    if st.session_state['page'] == "🏠 대시보드":
        st.markdown("<h1 style='text-align:center; color:#FFD700;'>🚀 ANTIGRAVITY DASHBOARD</h1>", unsafe_allow_html=True)
        render_sector_heatmap()
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🧘 GO TO MIND CLINIC"): 
                st.session_state['page'] = "🧘 마인드 클리닉"
                st.rerun()
        with col2:
            if st.button("💬 GO TO FORUM"):
                st.session_state['page'] = "💬 인텔리전스 포럼"
                st.rerun()

    elif st.session_state['page'] == "🧘 마인드 클리닉":
        render_mind_clinic()

    elif st.session_state['page'] == "💬 인텔리전스 포럼":
        render_forum()

if __name__ == "__main__":
    main()
