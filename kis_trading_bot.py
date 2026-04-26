import os
import time
import logging
from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf
import schedule
from pykis import KisApi

# ------------------------------------------------------------
# 1️⃣ 환경 설정 및 인증 (OAuth 2.0 – client_credentials)
# ------------------------------------------------------------
# KIS API 는 앱키/시크릿을 활용한 client_credentials 흐름을 사용합니다.
# 아래 함수는 OAuth2 토큰을 요청하고, 토큰이 만료될 경우 자동 재발급합니다.

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class KisAuth:
    """KIS API 인증 관리 클래스
    - app_key / app_secret 를 환경변수 혹은 Streamlit secrets 에서 읽습니다.
    - 토큰을 캐시하고, 1시간(기본 TTL) 이전에 재발급합니다.
    """
    def __init__(self, mock: bool = False):
        self.app_key = os.getenv("KIS_APP_KEY") or "<YOUR_APP_KEY>"
        self.app_secret = os.getenv("KIS_APP_SECRET") or "<YOUR_APP_SECRET>"
        self.account_no = os.getenv("KIS_ACCOUNT_NO") or "<YOUR_ACCOUNT_NO>"
        self.is_mock = mock
        self._token = None
        self._token_expiry = None
        self.api = None
        self._init_api()

    def _init_api(self):
        self.api = KisApi(
            app_key=self.app_key,
            app_secret=self.app_secret,
            account_no=self.account_no,
            is_mock=self.is_mock,
        )
        self.refresh_token()

    def refresh_token(self):
        """OAuth2 client_credentials 로 토큰 발급 (KIS 전용)"""
        try:
            token = self.api.get_access_token()
            # KIS 토큰은 일반적으로 1시간 유효합니다.
            self._token = token
            self._token_expiry = datetime.now() + timedelta(hours=1) - timedelta(minutes=5)
            logger.info("✅ KIS access token 발급 성공")
        except Exception as e:
            logger.error(f"⚠️ 토큰 발급 실패: {e}")
            self._token = None
            self._token_expiry = None

    @property
    def token(self):
        if not self._token or datetime.now() >= self._token_expiry:
            logger.info("🔄 토큰이 만료되었거나 존재하지 않음, 재발급 시도")
            self.refresh_token()
        return self._token

# ------------------------------------------------------------
# 2️⃣ 핵심 기능 구현 (REST API)
# ------------------------------------------------------------

class KisTrader:
    """KIS API 를 이용한 기본 트레이딩 기능 래퍼"""
    def __init__(self, auth: KisAuth):
        self.auth = auth
        self.api = auth.api

    # ── 시세 조회 (해외 주식) ──────────────────────
    def get_price(self, ticker: str) -> float:
        """실시간 현재가 조회 (예: 'AAPL', 'TSLA')"""
        try:
            quote = self.api.overseas.price(ticker)
            price = float(quote.last) if quote and hasattr(quote, "last") else 0.0
            logger.info(f"📈 {ticker} 현재가: {price}")
            return price
        except Exception as e:
            logger.error(f"❌ 현재가 조회 오류 ({ticker}): {e}")
            return 0.0

    # ── 기간별 시세 조회 (yfinance 활용) ────────
    def get_history(self, ticker: str, period: str = "1mo", interval: str = "1d") -> pd.DataFrame:
        """yfinance 로 기간별 히스토리 데이터 가져오기"""
        try:
            data = yf.download(ticker, period=period, interval=interval, progress=False)
            if data.empty:
                logger.warning(f"🚧 {ticker} 히스토리 데이터가 없습니다.")
            else:
                logger.info(f"✅ {ticker} 히스토리 ({period}) 다운로드 완료")
            return data
        except Exception as e:
            logger.error(f"❌ 히스토리 조회 오류 ({ticker}): {e}")
            return pd.DataFrame()

    # ── 주문 실행 (매수/매도) ───────────────────────
    def place_order(self, ticker: str, qty: int, side: str = "buy") -> dict:
        """해외 주식 매수/매도 주문
        side: 'buy' 또는 'sell'
        반환값: KIS API 응답 dict (성공 여부 포함)
        """
        try:
            if side.lower() == "buy":
                result = self.api.overseas.buy(ticker, qty)
            else:
                result = self.api.overseas.sell(ticker, qty)
            logger.info(f"🛒 주문 전송 ({side.upper()} {ticker} x{qty})")
            return result
        except Exception as e:
            logger.error(f"❌ 주문 실패 ({side} {ticker} x{qty}): {e}")
            return {"error": str(e)}

    # ── 잔고 조회 (해외) ───────────────────────────
    def get_balance(self) -> dict:
        """해외 계좌 잔고 조회 (KRW, USD 총액 및 현금)"""
        try:
            bal = self.api.overseas.balance()
            result = {
                "krw_total": float(bal.krw_total),
                "usd_total": float(bal.usd_total),
                "usd_cash": float(bal.usd_cash),
            }
            logger.info(f"💰 해외 잔고 조회: {result}")
            return result
        except Exception as e:
            logger.error(f"❌ 잔고 조회 오류: {e}")
            return {"krw_total": 0.0, "usd_total": 0.0, "usd_cash": 0.0}

    # ── 미체결 주문 조회 ───────────────────────────
    def get_unfilled_orders(self) -> list:
        try:
            orders = self.api.overseas.unfilled_orders()
            logger.info(f"📂 미체결 주문 {len(orders)} 건 조회")
            return orders
        except Exception as e:
            logger.error(f"❌ 미체결 주문 조회 오류: {e}")
            return []

# ------------------------------------------------------------
# 3️⃣ 자동매매 로직 (기술적 지표 기반)
# ------------------------------------------------------------

class SimpleStrategy:
    """RSI와 이동평균(MA) 기반 매매 전략 예시
    - RSI < 30 인 경우 과매도 → 매수
    - RSI > 70 인 경우 과매도 → 매도
    - 현재가가 20일 MA 위에 있으면 상승 추세로 간주
    """
    def __init__(self, trader: KisTrader, ticker: str, qty: int = 1):
        self.trader = trader
        self.ticker = ticker
        self.qty = qty

    @staticmethod
    def compute_rsi(series: pd.Series, period: int = 14) -> pd.Series:
        delta = series.diff()
        up = delta.clip(lower=0)
        down = -delta.clip(upper=0)
        ma_up = up.ewm(com=period - 1, adjust=False).mean()
        ma_down = down.ewm(com=period - 1, adjust=False).mean()
        rs = ma_up / ma_down
        rsi = 100 - (100 / (1 + rs))
        return rsi

    @staticmethod
    def compute_ma(series: pd.Series, window: int = 20) -> pd.Series:
        return series.rolling(window).mean()

    def evaluate_and_trade(self):
        df = self.trader.get_history(self.ticker, period="60d", interval="1d")
        if df.empty:
            logger.warning("데이터가 없어서 전략을 실행할 수 없음")
            return
        close = df['Close']
        rsi = self.compute_rsi(close)
        ma20 = self.compute_ma(close)
        current_price = close.iloc[-1]
        latest_rsi = rsi.iloc[-1]
        latest_ma = ma20.iloc[-1]
        logger.info(f"🔎 {self.ticker} 현재가: {current_price:.2f}, RSI: {latest_rsi:.1f}, MA20: {latest_ma:.2f}")
        # 매수 조건
        if latest_rsi < 30 and current_price > latest_ma:
            logger.info("⚡ 매수 신호 감지 – 실행합니다")
            self.trader.place_order(self.ticker, self.qty, side="buy")
        # 매도 조건
        elif latest_rsi > 70 and current_price < latest_ma:
            logger.info("⚡ 매도 신호 감지 – 실행합니다")
            self.trader.place_order(self.ticker, self.qty, side="sell")
        else:
            logger.info("🔹 현재 매매 신호 없음")

# ------------------------------------------------------------
# 4️⃣ 스케줄러 설정 (cron 형태) – 24시간 자동 실행
# ------------------------------------------------------------

def start_bot(mock: bool = True):
    """봇 초기화 및 스케줄러 등록
    - mock 모드에서는 실제 체결을 방지합니다.
    - schedule 라이브러리로 5분마다 전략을 실행합니다.
    """
    auth = KisAuth(mock=mock)
    trader = KisTrader(auth)
    # 여기서는 AAPL 을 예시 종목으로 사용합니다.
    strategy = SimpleStrategy(trader, ticker="AAPL", qty=1)

    # 매 5분마다 evaluate_and_trade 실행
    schedule.every(5).minutes.do(strategy.evaluate_and_trade)
    logger.info("🚀 자동매매 봇 시작 – 5분 간격으로 전략 실행")
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    # 가상계좌로 테스트하려면 mock=True 로 실행하세요.
    # 실제 운영 시 mock=False 로 변경 후 충분히 검증하세요.
    start_bot(mock=True)
