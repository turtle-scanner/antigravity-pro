import os
import requests
import json
import time
import pandas as pd
import numpy as np
import yfinance as yf
import pytz
from datetime import datetime, timedelta
import concurrent.futures

# --- [ CONFIG ] ---
KIS_APP_KEY = os.getenv("KIS_APP_KEY", "")
KIS_APP_SECRET = os.getenv("KIS_APP_SECRET", "")
KIS_ACCOUNT_NO = os.getenv("KIS_ACCOUNT_NO", "")
KIS_MOCK_TRADING = os.getenv("KIS_MOCK_TRADING", "true").lower() == "true"
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# --- [ UTILS ] ---
def send_telegram_msg(msg):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID: return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try: requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg}, timeout=5)
    except: pass

def log_combat(msg, type="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{type}] {msg}")
    if type == "ERROR": send_telegram_msg(f"❌ [SYSTEM ERROR] {msg}")

# --- [ KIS API AUTH ] ---
def get_kis_access_token():
    url = f"{'https://openapivts.koreainvestment.com:29443' if KIS_MOCK_TRADING else 'https://openapi.koreainvestment.com:9443'}/oauth2/tokenP"
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

# --- [ BALANCE & HOLDINGS ] ---
def get_kis_balance(token):
    base_url = "https://openapivts.koreainvestment.com:29443" if KIS_MOCK_TRADING else "https://openapi.koreainvestment.com:9443"
    url = f"{base_url}/uapi/domestic-stock/v1/trading/inquire-balance"
    headers = {"Content-Type": "application/json", "authorization": f"Bearer {token}", "appkey": KIS_APP_KEY, "appsecret": KIS_APP_SECRET, "tr_id": "VTTC8434R" if KIS_MOCK_TRADING else "TTTC8434R"}
    params = {"CANO": KIS_ACCOUNT_NO[:8], "ACNT_PRDT_CD": KIS_ACCOUNT_NO[8:], "AFHR_FLG": "N", "OFRT_BLAM_YN": "N", "PRCS_DVSN": "01", "UNPR_DVSN": "01", "CTX_AREA_FK100": "", "CTX_AREA_NK100": ""}
    try:
        res = requests.get(url, headers=headers, params=params, timeout=10)
        if res.status_code == 200:
            d = res.json()
            out2 = d.get('output2', [{}])[0]
            return float(out2.get('tot_evlu_amt', 0)), float(out2.get('dnca_tot_amt', 0)), d.get('output1', [])
    except: pass
    return 0, 0, []

def get_kis_overseas_balance(token):
    base_url = "https://openapivts.koreainvestment.com:29443" if KIS_MOCK_TRADING else "https://openapi.koreainvestment.com:9443"
    url = f"{base_url}/uapi/overseas-stock/v1/trading/inquire-balance"
    headers = {"Content-Type": "application/json", "authorization": f"Bearer {token}", "appkey": KIS_APP_KEY, "appsecret": KIS_APP_SECRET, "tr_id": "VTTS3061R" if KIS_MOCK_TRADING else "TTTS3061R", "custtype": "P"}
    for suffix in ["01", "02"]:
        params = {"CANO": KIS_ACCOUNT_NO[:8], "ACNT_PRDT_CD": suffix, "WCRC_FRCR_DVS_CD": "02", "NATN_CD": "840", "TR_PACC_CD": ""}
        try:
            res = requests.get(url, headers=headers, params=params, timeout=10)
            if res.status_code == 200:
                d = res.json()
                o2 = d.get('output2', {})
                if o2:
                    total_krw = float(o2.get('tot_evlu_pamt') or o2.get('tot_asst_amt') or 0)
                    total_usd = float(o2.get('frcr_evlu_amt2') or 0)
                    cash_usd = float(o2.get('frcr_dnca_amt') or 0)
                    if total_krw > 0: return {"krw": total_krw, "usd_total": total_usd + cash_usd, "usd_cash": cash_usd}, d.get('output1', [])
        except: pass
    return {"krw": 0, "usd_total": 0, "usd_cash": 0}, []

# --- [ EXECUTION ] ---
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
        curr_p = 0
        try:
            p_data = yf.download(ticker, period="1d", interval="1m", progress=False)
            if not p_data.empty: curr_p = p_data['Close'].iloc[-1]
        except: pass
        order_p = curr_p * (1.01 if is_buy else 0.99) if curr_p > 0 else 0
        body.update({"OVRS_EXCG_CD": "NASD", "PDNO": ticker, "ORD_OVRS_P": f"{order_p:.2f}", "ORD_DVSN": "00"})
    headers = {"Content-Type": "application/json", "authorization": f"Bearer {token}", "appkey": KIS_APP_KEY, "appsecret": KIS_APP_SECRET, "tr_id": tr_id}
    try:
        res = requests.post(url, headers=headers, json=body, timeout=10)
        if res.json().get('rt_cd') == '0':
            log_combat(f"🚀 [HEADLESS] {'매수' if is_buy else '매도'} 성공: {ticker} ({qty}주)")
            send_telegram_msg(f"🔔 [자동 교전 보고] {'✅ 매수' if is_buy else '📉 매도'} 완료: {ticker} ({qty}주)")
            return True
    except: pass
    return False

def execute_kis_auto_cut(token):
    try:
        _, _, kr_h = get_kis_balance(token)
        _, us_h = get_kis_overseas_balance(token)
        all_h = kr_h + us_h
        if not all_h: return
        tickers = []
        for h in all_h:
            tic = h.get('pdno') or h.get('ovrs_pdno')
            if tic: tickers.append(f"{tic}.KS" if (tic.isdigit() and len(tic)==6) else tic)
        bulk_data = get_bulk_market_data(list(set(tickers)), period="5d")
        for h in all_h:
            ticker = h.get('pdno') or h.get('ovrs_pdno')
            qty = int(h.get('hldg_qty', 0))
            buy_p = float(h.get('pchs_avg_pric', 0))
            if qty <= 0 or buy_p <= 0: continue
            hist = get_ticker_data_from_bulk(bulk_data, ticker if not ticker.isdigit() else f"{ticker}.KS")
            if hist.empty: continue
            curr_p = hist['Close'].iloc[-1]
            roi = (curr_p / buy_p - 1) * 100
            if roi >= 21.0: execute_kis_market_order(ticker, qty, False, token)
            elif roi <= -5.0: execute_kis_market_order(ticker, qty, False, token)
    except: pass

# --- [ MAIN ] ---
def run_headless_cycle():
    log_combat("📡 [HEADLESS] 교전 사이클 시작")
    token = get_kis_access_token()
    if not token: return
    execute_kis_auto_cut(token) # 리스크 관리
    # 24/7 봇은 스캔 로직을 추가하여 신규 진입도 가능하게 할 수 있음
    log_combat("✅ [HEADLESS] 사이클 종료")

if __name__ == "__main__":
    run_headless_cycle()
