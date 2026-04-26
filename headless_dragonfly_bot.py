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

# --- [ SUPREME CONFIG ] ---
KIS_APP_KEY = os.getenv("KIS_APP_KEY", "")
KIS_APP_SECRET = os.getenv("KIS_APP_SECRET", "")
KIS_ACCOUNT_NO = os.getenv("KIS_ACCOUNT_NO", "").replace("-", "") # 하이픈 자동 제거
KIS_MOCK_TRADING = os.getenv("KIS_MOCK_TRADING", "true").lower() == "true"
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# [ TACTICAL ALLOCATION ]
US_RATIO = 0.7
KR_RATIO = 0.3
SLOTS_PER_REGION = 4
RISK_PER_TRADE = 0.01   # 한 매매당 총 자산의 1% 리스크 (손절 시 손실액)
STOP_LOSS_PCT = 0.05    # 기본 손절 라인 5%
EXCHANGE_RATE = 1400    # 환율 (보수적 적용)

# --- [ UTILS ] ---
def send_telegram_msg(msg):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID: return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try: requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "HTML"}, timeout=5)
    except: pass

def log_combat(msg, type="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{type}] {msg}")
    if type == "ERROR" or "성공" in msg or "포착" in msg or "브리핑" in msg:
        prefix = "🚨 " if type == "ERROR" else ("🚀 " if "성공" in msg else ("🎯 " if "포착" in msg else "📊 "))
        send_telegram_msg(f"{prefix}<b>[HEADLESS]</b> {msg}")

# --- [ KIS API AUTH ] ---
def call_kis_api(method, url, headers, params=None, json_body=None, retries=3):
    """재시도 로직이 포함된 KIS API 공통 호출 함수"""
    for i in range(retries):
        try:
            if method.upper() == 'GET':
                res = requests.get(url, headers=headers, params=params, timeout=12)
            else:
                res = requests.post(url, headers=headers, json=json_body, timeout=12)
            
            data = res.json()
            if res.status_code == 200 and data.get('rt_cd') in ['0', None]:
                return data
            else:
                msg = data.get('msg1', res.text)
                log_combat(f"API 응답 에러 (시도 {i+1}/{retries}): {msg}", "ERROR")
        except Exception as e:
            log_combat(f"네트워크/접속 에러 (시도 {i+1}/{retries}): {str(e)}", "ERROR")
        time.sleep(2)
    return None

def get_kis_access_token():
    base_url = "https://openapivts.koreainvestment.com:29443" if KIS_MOCK_TRADING else "https://openapi.koreainvestment.com:9443"
    url = f"{base_url}/oauth2/tokenP"
    body = {"grant_type": "client_credentials", "appkey": KIS_APP_KEY, "appsecret": KIS_APP_SECRET}
    res = call_kis_api("POST", url, {}, json_body=body)
    return res.get("access_token") if res else None

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

# --- [ BALANCE & ASSET ALLOCATION ] ---
def get_total_assets(token):
    try:
        base_url = "https://openapivts.koreainvestment.com:29443" if KIS_MOCK_TRADING else "https://openapi.koreainvestment.com:9443"
        
        # 국내 자산 조회
        url_kr = f"{base_url}/uapi/domestic-stock/v1/trading/inquire-balance"
        headers_kr = {"Content-Type": "application/json", "authorization": f"Bearer {token}", "appkey": KIS_APP_KEY, "appsecret": KIS_APP_SECRET, "tr_id": "VTTC8434R" if KIS_MOCK_TRADING else "TTTC8434R"}
        params_kr = {"CANO": KIS_ACCOUNT_NO[:8], "ACNT_PRDT_CD": KIS_ACCOUNT_NO[8:], "AFHR_FLG": "N", "OFRT_BLAM_YN": "N", "PRCS_DVSN": "01", "UNPR_DVSN": "01", "CTX_AREA_FK100": "", "CTX_AREA_NK100": ""}
        res_kr = call_kis_api("GET", url_kr, headers_kr, params=params_kr)
        kr_total = 0
        if res_kr:
            out2 = res_kr.get('output2', [])
            if out2: kr_total = float(out2[0].get('tot_evlu_amt', 0))
        
        # 해외 자산 조회
        url_us = f"{base_url}/uapi/overseas-stock/v1/trading/inquire-balance"
        headers_us = {"Content-Type": "application/json", "authorization": f"Bearer {token}", "appkey": KIS_APP_KEY, "appsecret": KIS_APP_SECRET, "tr_id": "VTTS3061R" if KIS_MOCK_TRADING else "TTTS3061R", "custtype": "P"}
        us_total_krw = 0
        for suffix in ["01", "02"]:
            params_us = {"CANO": KIS_ACCOUNT_NO[:8], "ACNT_PRDT_CD": suffix, "WCRC_FRCR_DVS_CD": "02", "NATN_CD": "840", "TR_PACC_CD": ""}
            res_us = call_kis_api("GET", url_us, headers_us, params=params_us)
            if res_us:
                us_total_krw += float(res_us.get('output2', {}).get('tot_asst_amt', 0))
        
        total = kr_total + us_total_krw
        if total <= 0:
            log_combat("자산 조회 결과가 0입니다. 기본값(1,000만원)을 사용합니다.", "WARNING")
            return 10000000
        return total
    except Exception as e:
        log_combat(f"자산 조회 중 치명적 오류: {str(e)}", "ERROR")
        return 10000000

# --- [ MARKET HEALTH ] ---
def analyze_market_health():
    indices = {"^IXIC": "NASDAQ", "^KS11": "KOSPI"}
    report = "<b>[전술 시장 브리핑]</b>\n"
    is_defense = False
    try:
        data = yf.download(list(indices.keys()), period="100d", interval="1d", group_by='ticker', progress=False)
        for sym, name in indices.items():
            df = data[sym].dropna()
            if df.empty: continue
            curr_p = df['Close'].iloc[-1]; ma50 = df['Close'].rolling(50).mean().iloc[-1]
            status = "🟢 HEALTHY" if curr_p > ma50 else "🔴 BEARISH"
            if curr_p <= ma50: is_defense = True
            report += f"- {name}: {curr_p:,.1f} ({status})\n"
        report += f"\n💰 <b>자산 배분:</b> 미국 {int(US_RATIO*100)}% : 한국 {int(KR_RATIO*100)}%"
        report += "\n" + ("⚠️ <b>방어 모드:</b> 비중 축소" if is_defense else "⚡ <b>공격 모드:</b> 비중 정상")
        log_combat(report, "INFO")
    except: pass
    return is_defense

# --- [ STRATEGY ] ---
def analyze_bonde_setup(ticker, df):
    try:
        if len(df) < 150: return {"status": "FAIL"}
        df['C1'] = df['Close'].shift(1); df['V1'] = df['Volume'].shift(1)
        df['Pct'] = (df['Close'] / df['C1'] - 1) * 100
        df['Gap'] = (df['Open'] / df['C1'] - 1) * 100
        df['SMA50'] = df['Close'].rolling(50).mean(); df['SMA200'] = df['Close'].rolling(200).mean()
        df['ADR20'] = ((df['High'] / df['Low'] - 1) * 100).rolling(20).mean()
        df['Range_Pos'] = (df['Close'] - df['Low']) / (df['High'] - df['Low'] + 1e-9)
        c, pct, gap, adr20, range_pos = df['Close'].iloc[-1], df['Pct'].iloc[-1], df['Gap'].iloc[-1], df['ADR20'].iloc[-1], df['Range_Pos'].iloc[-1]
        v, p_v = df['Volume'].iloc[-1], df['V1'].iloc[-1]
        is_stage2 = c > df['SMA50'].iloc[-1] > (df['SMA200'].iloc[-1] if not pd.isna(df['SMA200'].iloc[-1]) else 0)
        is_liquid = (c * v) >= 1000000 
        if not is_stage2 or not is_liquid: return {"status": "FAIL"}
        vol_surge = v / (p_v + 1e-9)
        is_ep = pct >= 4.0 and vol_surge >= 1.5 and gap >= 1.5 and range_pos >= 0.7
        rs = ((c/df['Close'].iloc[-126])*0.4 + (c/df['Close'].iloc[-63])*0.4 + (c/df['Close'].iloc[-21])*0.2)*100
        quality = (rs * 0.5) + (adr20 * 4) + (vol_surge * 2)
        if rs >= 90: quality += 20
        if is_ep: return {"status": "SUCCESS", "ticker": ticker, "type": "EP", "pct": round(pct, 2), "rs": round(rs, 1), "quality": round(quality, 1), "close": c}
    except: pass
    return {"status": "FAIL"}

# --- [ EXECUTION ] ---
def calculate_risk_based_qty(total_assets, curr_price, risk_pct=0.01, sl_pct=0.05, exchange_rate=1):
    """
    리스크 기반 포지션 사이징:
    수량 = (총자산 * 리스크비율) / (주당 리스크 금액)
    """
    risk_amount = total_assets * risk_pct
    risk_per_share = (curr_price * exchange_rate) * sl_pct
    if risk_per_share <= 0: return 0
    qty = int(risk_amount / risk_per_share)
    return qty

def execute_kis_market_order(ticker, qty, is_buy, token):
    if qty <= 0: return False
    is_kr = ticker.endswith(".KS") or ticker.endswith(".KQ") or (ticker.isdigit() and len(ticker) == 6)
    base_url = "https://openapivts.koreainvestment.com:29443" if KIS_MOCK_TRADING else "https://openapi.koreainvestment.com:9443"
    url = f"{base_url}/uapi/{'domestic-stock/v1/trading/order-cash' if is_kr else 'overseas-stock/v1/trading/order'}"
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
    res = call_kis_api("POST", url, headers, json_body=body)
    if res and res.get('rt_cd') == '0':
        log_combat(f"{'✅ 매수' if is_buy else '📉 매도'} 성공: {ticker} ({qty}주)")
        return True
    return False

def execute_kis_auto_cut(token):
    try:
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
            ticker = h.get('ovrs_pdno'); qty = int(h.get('hldg_qty', 0)); buy_p = float(h.get('pchs_avg_pric', 0))
            if qty <= 0 or buy_p <= 0: continue
            hist = get_ticker_data_from_bulk(bulk_data, ticker)
            if hist.empty: continue
            curr_p = hist['Close'].iloc[-1]; roi = (curr_p / buy_p - 1) * 100
            if roi >= 21.0:
                log_combat(f"💰 [익절] {ticker} 목표 도달 (+{roi:.1f}%)"); execute_kis_market_order(ticker, qty, False, token)
            elif roi <= -5.0:
                log_combat(f"📉 [손절] {ticker} 리스크 관리 집행 ({roi:.1f}%)"); execute_kis_market_order(ticker, qty, False, token)
    except: pass

# --- [ MAIN LOOP ] ---
def run_headless_cycle():
    log_combat("📡 교전 사이클 개시")
    token = get_kis_access_token()
    if not token: return
    
    total_asst = get_total_assets(token)
    is_defense = analyze_market_health()
    execute_kis_auto_cut(token)

    us_univ = ["NVDA", "TSLA", "AAPL", "MSFT", "AMD", "PLTR", "SMCI", "META", "AMZN", "GOOGL", "NFLX", "COIN"]
    kr_univ = ["005930", "000660", "066570", "035420", "035720", "005380"]
    
    for region, univ, ratio in [("US", us_univ, US_RATIO), ("KR", kr_univ, KR_RATIO)]:
        bulk_data = get_bulk_market_data(univ)
        hits = []
        for ticker in univ:
            df = get_ticker_data_from_bulk(bulk_data, ticker)
            res = analyze_bonde_setup(ticker, df)
            if res.get("status") == "SUCCESS": hits.append(res)
        
        hits = sorted(hits, key=lambda x: x['quality'], reverse=True)
        if hits:
            target = hits[0]
            curr_p = target['close']
            
            # 리스크 기반 수량 계산 (자산의 1% 손실 제한)
            ex_rate = EXCHANGE_RATE if region == "US" else 1
            qty = calculate_risk_based_qty(total_asst, curr_p, RISK_PER_TRADE, STOP_LOSS_PCT, ex_rate)
            
            # 자산 배분 비율에 따른 최대 가용 예산 체크 (Safety Buffer)
            max_budget = (total_asst * ratio) / SLOTS_PER_REGION
            if is_defense: max_budget *= 0.5
            
            # 리스크 기반 수량이 예산을 초과하는지 확인 및 보정
            if qty * curr_p * ex_rate > max_budget:
                qty = int(max_budget / (curr_p * ex_rate))
                
            if qty > 0:
                log_combat(f"🎯 [{region}] 본데 타겟 포착: {target['ticker']} (수량: {qty}주, 리스크:{RISK_PER_TRADE*100}%)")
                execute_kis_market_order(target['ticker'], qty, True, token)
        else: log_combat(f"🕵️ [{region}] 현재 조건에 부합하는 본데 셋업이 없습니다.")
    log_combat("✅ 사이클 종료")

if __name__ == "__main__":
    run_headless_cycle()
