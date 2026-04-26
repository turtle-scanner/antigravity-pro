import os
from pykis import KisApi

# 환경 변수 혹은 streamlit secrets 에서 KIS 인증 정보를 읽습니다.
API_KEY = os.getenv("KIS_APP_KEY") or "<YOUR_APP_KEY>"
API_SECRET = os.getenv("KIS_APP_SECRET") or "<YOUR_APP_SECRET>"
ACCOUNT_NO = os.getenv("KIS_ACCOUNT_NO") or "<YOUR_ACCOUNT_NO>"

# KisApi 객체 생성 (모의모드 사용 여부는 필요에 따라 조정)
api = KisApi(app_key=API_KEY, app_secret=API_SECRET, account_no=ACCOUNT_NO, is_mock=False)

def get_overseas_price(ticker: str) -> float:
    """해외 주식 현재가 조회 (예: 'AAPL', 'TSLA')"""
    try:
        quote = api.overseas.price(ticker)
        return float(quote.last) if quote and hasattr(quote, "last") else 0.0
    except Exception as e:
        print(f"[ERROR] 현재가 조회 실패: {e}")
        return 0.0

def get_overseas_balance():
    """해외 계좌 잔고 조회 (KRW 총액, USD 총액, USD 현금)"""
    try:
        bal = api.overseas.balance()
        return {
            "krw_total": float(bal.krw_total),
            "usd_total": float(bal.usd_total),
            "usd_cash": float(bal.usd_cash),
        }
    except Exception as e:
        print(f"[ERROR] 잔고 조회 실패: {e}")
        return {"krw_total": 0.0, "usd_total": 0.0, "usd_cash": 0.0}

def place_order(ticker: str, qty: int, side: str = "buy"):
    """해외 주식 매수/매도 주문
    side: 'buy' 혹은 'sell'
    """
    try:
        if side.lower() == "buy":
            result = api.overseas.buy(ticker, qty)
        else:
            result = api.overseas.sell(ticker, qty)
        return result
    except Exception as e:
        print(f"[ERROR] 주문 실패 ({side} {ticker} {qty}): {e}")
        return None

def get_unfilled_orders():
    """미체결(대기) 주문 리스트 조회"""
    try:
        orders = api.overseas.unfilled_orders()
        return orders
    except Exception as e:
        print(f"[ERROR] 미체결 주문 조회 실패: {e}")
        return []

if __name__ == "__main__":
    # 간단 데모 실행
    sample_ticker = "AAPL"
    print(f"{sample_ticker} 현재가: {get_overseas_price(sample_ticker)}")
    print("해외 잔고:", get_overseas_balance())
    # 예시 주문 (실제 실행 전 반드시 주문 파라미터를 검증하세요)
    # order_result = place_order(sample_ticker, 1, side="buy")
    # print("주문 결과:", order_result)
    print("미체결 주문 리스트:")
    for o in get_unfilled_orders():
        print(o)
