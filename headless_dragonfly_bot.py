import os
import requests
import json
import time
import pandas as pd
import numpy as np
import yfinance as yf
import pytz
import re
from datetime import datetime, timedelta
import concurrent.futures

# --- [ SUPREME CONFIG ] ---
KIS_APP_KEY = os.getenv("KIS_APP_KEY", "")
KIS_APP_SECRET = os.getenv("KIS_APP_SECRET", "")
KIS_ACCOUNT_NO = os.getenv("KIS_ACCOUNT_NO", "")
KIS_MOCK_TRADING = os.getenv("KIS_MOCK_TRADING", "true").lower() == "true"
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
MASTER_GAS_URL = os.getenv("MASTER_GAS_URL", "")

# --- [ UTILS ] ---
def send_telegram_msg(msg):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID: return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try: requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg}, timeout=5)
    except: pass

def log_combat(msg, type="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{type}] {msg}")
    if type == "ERROR" or "성공" in msg or "포착" in msg:
        prefix = "🚨 " if type == "ERROR" else ("🚀 " if "성공" in msg else "🎯 ")
        send_telegram_msg(f"{prefix}[HEADLESS] {msg}")

# --- [ KIS API AUTH ] ---
def get_kis_access_token():
    base_url = "https://openapivts.koreainvestment.com:29443" if KIS_MOCK_TRADING else "https://openapi.koreainvestment.com:9443"
    url = f"{base_url}/oauth2/tokenP"
    body = {"grant_type": "client_credentials", "appkey": KIS_APP_KEY, "appsecret": KIS_APP_SECRET}
    try:
        res = requests.post(url, json=body, timeout=7)
        if res.status_code == 200: return res.json().get("access_token")
    except Exception as e: log_combat(f"토큰 발급 실패: {str(e)}", "ERROR")
    return None

# --- [ DATA FETCH ] ---
def get_bulk_market_data(tickers, period="250d"):
    if not tickers: return pd.DataFrame()
    try:
        data = yf.download(tickers, period=period, interval="1d", group_by='ticker', threads=True, progress=False)
        return data
    except: return pd.DataFrame()

def get_ticker_data_from_bulk(bulk_df, ticker):
    try:
        if isinstance(bulk_df.columns, pd.MultiIndex):
            if ticker in bulk_df.columns.levels[0]: return bulk_df[ticker].dropna()
        else:
            if ticker in bulk_df.columns: return bulk_df.dropna()
    except: pass
    return pd.DataFrame()

# --- [ BONDE STRATEGY ENGINE ] ---
def analyze_bonde_setup(ticker, df):
    """Pradeep Bonde (Stockbee) Strategy v9.0 Headless Implementation"""
    try:
        if len(df) < 150: return {"status": "REJECT", "reason": "Data Short"}
        
        # Prepare Indicators
        df['C1'] = df['Close'].shift(1)
        df['V1'] = df['Volume'].shift(1)
        df['Pct'] = (df['Close'] / df['C1'] - 1) * 100
        df['Gap'] = (df['Open'] / df['C1'] - 1) * 100
        df['SMA50'] = df['Close'].rolling(50).mean()
        df['SMA200'] = df['Close'].rolling(200).mean()
        df['ADR20'] = ((df['High'] / df['Low'] - 1) * 100).rolling(20).mean()
        df['Range_Pos'] = (df['Close'] - df['Low']) / (df['High'] - df['Low'] + 1e-9)
        
        row = df.iloc[-1]
        c, pct, gap, adr20, range_pos = row['Close'], row['Pct'], row['Gap'], row['ADR20'], row['Range_Pos']
        v, p_v = row['Volume'], row['V1']
        sma50, sma200 = row['SMA50'], row['SMA200']
        
        # Stage 2 & Liquidity
        is_stage2 = c > sma50 > (sma200 if not pd.isna(sma200) else 0)
        is_liquid = (c * v) >= 2000000 # Min 2M$ Dollar Volume
        
        if not is_stage2 or not is_liquid: return {"status": "FAIL"}

        # 1. EP (Episodic Pivot)
        vol_surge = v / (p_v + 1e-9)
        is_ep = pct >= 4.0 and vol_surge >= 1.5 and gap >= 1.5 and range_pos >= 0.7
        
        # 2. RS (Relative Strength) - Weighted 6m, 3m, 1m
        rs = ((c/df['Close'].iloc[-126])*0.4 + (c/df['Close'].iloc[-63])*0.4 + (c/df['Close'].iloc[-21])*0.2)*100
        quality = (rs * 0.5) + (adr20 * 4) + (vol_surge * 2)
        if rs >= 90: quality += 20

        if is_ep:
            return {
                "status": "SUCCESS", "ticker": ticker, "type": "EP (Episodic Pivot)",
                "pct": round(pct, 2), "rs": round(rs, 1), "quality": round(quality, 1)
            }
    except: pass
    return {"status": "FAIL"}

# --- [ EXECUTION ENGINE ] ---
def execute_kis_market_order(ticker, qty, is_buy, token):
    if qty <= 0: return False
    is_kr = ticker.endswith(".KS") or ticker.endswith(".KQ") or (ticker.isdigit() and len(ticker) == 6)
    base_url = "https://openapivts.koreainvestment.com:29443" if KIS_MOCK_TRADING else "https://openapi.koreainvestment.com:9443"
    url = f"{base_url}/uapi/{'domestic-stock/v1/trading/order-cash' if is_kr else 'overseas-stock/v1/trading/order'}"
    
    tr_id = ""
    body = {"CANO": KIS_ACCOUNT_NO[:8], "ACNT_PRDT_CD": KIS_ACCOUNT_NO[8:], "ORD_QTY": str(qty)}
    
    if is_kr:
        tr_id = ("VTTC0802U" if is_buy else "VTTC0801U") if KIS_MOCK_TRADING else ("TTTC0802U" if is_buy else "TTTC0801U")
        body.update({"PDNO": ticker.split('.')[0], "ORD_DVSN": "01", "ORD_UNPR": "0"})
    else:
        tr_id = ("VTTW0801U" if is_buy else "VTTW0802U") if KIS_MOCK_TRADING else ("TTTW0801U" if is_buy else "TTTW0802U")
        # Fetch current price for US Market-like order
        curr_p = 0
        try:
            p_data = yf.download(ticker, period="1d", interval="1m", progress=False)
            if not p_data.empty: curr_p = p_data['Close'].iloc[-1]
        except: pass
        order_p = curr_p * (1.01 if is_buy else 0.99) if curr_p > 0 else 0
        body.update({"OVRS_EXCG_CD": "NASD", "PDNO": ticker, "ORD_OVRS_P": f"{order_p:.2f}", "ORD_DVSN": "00"})

    headers = {"Content-Type": "application/json", "authorization": f"Bearer {token}", "appkey": KIS_APP_KEY, "appsecret": KIS_APP_SECRET, "tr_id": tr_id}
    try:
        res = requests.post(url, headers=headers, json=body, timeout=12)
        res_data = res.json()
        if res_data.get('rt_cd') == '0':
            log_combat(f"{'✅ 매수' if is_buy else '📉 매도'} 완료: {ticker} ({qty}주)")
            return True
        else:
            log_combat(f"주문 실패 ({ticker}): {res_data.get('msg1')}", "ERROR")
    except Exception as e:
        log_combat(f"주문 시스템 오류: {str(e)}", "ERROR")
    return False

def execute_kis_auto_cut(token):
    """Supreme Risk Management (Stop Loss -5%, Take Profit +21%)"""
    try:
        # Get Overseas Balance
        base_url = "https://openapivts.koreainvestment.com:29443" if KIS_MOCK_TRADING else "https://openapi.koreainvestment.com:9443"
        url = f"{base_url}/uapi/overseas-stock/v1/trading/inquire-balance"
        headers = {"Content-Type": "application/json", "authorization": f"Bearer {token}", "appkey": KIS_APP_KEY, "appsecret": KIS_APP_SECRET, "tr_id": "VTTS3061R" if KIS_MOCK_TRADING else "TTTS3061R", "custtype": "P"}
        
        holdings = []
        for suffix in ["01", "02"]:
            params = {"CANO": KIS_ACCOUNT_NO[:8], "ACNT_PRDT_CD": suffix, "WCRC_FRCR_DVS_CD": "02", "NATN_CD": "840", "TR_PACC_CD": ""}
            res = requests.get(url, headers=headers, params=params, timeout=10)
            if res.status_code == 200: holdings += res.json().get('output1', [])
        
        if not holdings: return
        
        tickers = [h.get('ovrs_pdno') for h in holdings if h.get('ovrs_pdno')]
        bulk_data = get_bulk_market_data(tickers, period="5d")
        
        for h in holdings:
            ticker = h.get('ovrs_pdno')
            qty = int(h.get('hldg_qty', 0))
            buy_p = float(h.get('pchs_avg_pric', 0))
            if qty <= 0 or buy_p <= 0: continue
            
            hist = get_ticker_data_from_bulk(bulk_data, ticker)
            if hist.empty: continue
            
            curr_p = hist['Close'].iloc[-1]
            roi = (curr_p / buy_p - 1) * 100
            
            if roi >= 21.0:
                log_combat(f"💰 [익절] {ticker} 목표 도달 (+{roi:.1f}%)")
                execute_kis_market_order(ticker, qty, False, token)
            elif roi <= -5.0:
                log_combat(f"📉 [손절] {ticker} 리스크 관리 집행 ({roi:.1f}%)")
                execute_kis_market_order(ticker, qty, False, token)
    except: pass

# --- [ MAIN LOOP ] ---
def run_headless_cycle():
    log_combat("📡 교전 사이클 시작 (Bonde Strategy v9.0)")
    token = get_kis_access_token()
    if not token: return

    # 1. 리스크 관리 (Auto-Cut)
    execute_kis_auto_cut(token)

    # 2. 본데 전략 스캔 (Nasdaq 100 & 주요 주도주)
    universe = ["NVDA", "TSLA", "AAPL", "MSFT", "AMD", "PLTR", "SMCI", "META", "AMZN", "GOOGL", "NFLX", "COIN", "MARA", "MSTR"]
    bulk_data = get_bulk_market_data(universe)
    
    hits = []
    for ticker in universe:
        df = get_ticker_data_from_bulk(bulk_data, ticker)
        res = analyze_bonde_setup(ticker, df)
        if res.get("status") == "SUCCESS": hits.append(res)
    
    hits = sorted(hits, key=lambda x: x['quality'], reverse=True)
    
    if hits:
        target = hits[0]
        log_combat(f"🎯 본데 타겟 포착: {target['ticker']} ({target['type']}, RS:{target['rs']})")
        # [ LIVE EXECUTION ] - 실제 매매 집행 (테스트 완료 후 주석 해제 권장)
        # 1주씩 정찰병 파견 (예시)
        execute_kis_market_order(target['ticker'], 1, True, token)
    else:
        log_combat("🕵️ 현재 조건에 부합하는 본데 셋업이 없습니다.")

    log_combat("✅ 사이클 종료")

if __name__ == "__main__":
    run_headless_cycle()
