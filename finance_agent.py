import logging
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

import numpy as np
import pandas as pd
import yfinance as yf

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FinanceAgent")


@dataclass
class AnalysisConfig:
    rsi_period: int = 14
    short_sma: int = 20
    long_sma: int = 50
    ema_fast: int = 12
    ema_slow: int = 26
    ema_signal: int = 9
    bb_period: int = 20
    bb_std: float = 2.0


def _safe_float(value: Optional[float], default: float = 0.0) -> float:
    if value is None or pd.isna(value):
        return default
    return float(value)


def create_mock_data(days: int = 260, seed: int = 42) -> pd.DataFrame:
    """Dış veri bağlantısı yoksa demo amaçlı sentetik OHLC veri üretir."""
    rng = np.random.default_rng(seed)
    idx = pd.date_range(end=pd.Timestamp.today().normalize(), periods=days, freq="B")
    base = np.cumsum(rng.normal(0.15, 1.8, size=days)) + 100
    close = np.maximum(base, 5)
    open_ = close + rng.normal(0, 0.9, size=days)
    high = np.maximum(open_, close) + np.abs(rng.normal(0.9, 0.5, size=days))
    low = np.minimum(open_, close) - np.abs(rng.normal(0.9, 0.5, size=days))
    volume = rng.integers(900_000, 4_500_000, size=days)

    return pd.DataFrame(
        {
            "Open": open_,
            "High": high,
            "Low": low,
            "Close": close,
            "Volume": volume,
        },
        index=idx,
    )


def _add_indicators(df: pd.DataFrame, config: AnalysisConfig) -> Tuple[pd.DataFrame, float]:
    df = df.dropna(subset=["Open", "High", "Low", "Close"]).copy()

    # Ortalamalar
    df["SMA20"] = df["Close"].rolling(window=config.short_sma, min_periods=config.short_sma).mean()
    df["SMA50"] = df["Close"].rolling(window=config.long_sma, min_periods=config.long_sma).mean()

    # RSI (Wilder)
    delta = df["Close"].diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.ewm(alpha=1 / config.rsi_period, min_periods=config.rsi_period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / config.rsi_period, min_periods=config.rsi_period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    df["RSI"] = 100 - (100 / (1 + rs))
    df["RSI"] = df["RSI"].fillna(50)

    # MACD
    ema_fast = df["Close"].ewm(span=config.ema_fast, adjust=False).mean()
    ema_slow = df["Close"].ewm(span=config.ema_slow, adjust=False).mean()
    df["MACD"] = ema_fast - ema_slow
    df["MACD_SIGNAL"] = df["MACD"].ewm(span=config.ema_signal, adjust=False).mean()
    df["MACD_HIST"] = df["MACD"] - df["MACD_SIGNAL"]

    # Bollinger
    bb_mid = df["Close"].rolling(window=config.bb_period, min_periods=config.bb_period).mean()
    bb_std = df["Close"].rolling(window=config.bb_period, min_periods=config.bb_period).std()
    df["BB_MID"] = bb_mid
    df["BB_UPPER"] = bb_mid + config.bb_std * bb_std
    df["BB_LOWER"] = bb_mid - config.bb_std * bb_std

    # Volatilite
    df["Returns"] = df["Close"].pct_change()
    volatility = _safe_float(df["Returns"].std() * np.sqrt(252) * 100)

    return df, volatility


def get_stock_data(
    symbol: str,
    period: str = "1y",
    config: AnalysisConfig = AnalysisConfig(),
    allow_demo_fallback: bool = False,
) -> Tuple[Optional[pd.DataFrame], float, bool]:
    """Gerçek veriyi indirir; istenirse başarısızlıkta demo veriye düşer."""
    try:
        logger.info("📥 %s için veriler çekiliyor...", symbol)
        df = yf.download(symbol, period=period, interval="1d", auto_adjust=True, progress=False)

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        if df.empty:
            raise ValueError(f"'{symbol}' için veri bulunamadı.")

        df, volatility = _add_indicators(df, config)
        return df, volatility, False

    except Exception as exc:
        logger.error("❌ Veri çekme hatası: %s", exc)
        if allow_demo_fallback:
            logger.warning("🧪 Demo veri moduna geçiliyor.")
            demo_df = create_mock_data()
            demo_df, volatility = _add_indicators(demo_df, config)
            return demo_df, volatility, True
        return None, 0.0, False


def _risk_from_vol(vol: float) -> str:
    if vol >= 38:
        return "Yüksek"
    if vol <= 20:
        return "Düşük"
    return "Orta"


def advanced_analysis(df: Optional[pd.DataFrame], vol: float) -> Dict[str, float | str]:
    if df is None or len(df) < 50:
        return {
            "symbol_name": "Varlık Analizi",
            "last_price": 0.0,
            "change_pct": 0.0,
            "rsi": 50.0,
            "volatility": vol,
            "decision": "VERİ YETERSİZ",
            "comment": "Analiz için en az 50 günlük veri gerekli.",
            "risk_level": "Yüksek",
            "trend_strength": "Zayıf",
            "confidence": 0.0,
        }

    last_close = _safe_float(df["Close"].iloc[-1])
    first_close = _safe_float(df["Close"].iloc[0], last_close)
    rsi = _safe_float(df["RSI"].iloc[-1], 50)
    sma20 = _safe_float(df["SMA20"].iloc[-1], last_close)
    sma50 = _safe_float(df["SMA50"].iloc[-1], last_close)
    macd = _safe_float(df["MACD"].iloc[-1])
    macd_signal = _safe_float(df["MACD_SIGNAL"].iloc[-1])
    bb_upper = _safe_float(df["BB_UPPER"].iloc[-1], last_close)
    bb_lower = _safe_float(df["BB_LOWER"].iloc[-1], last_close)

    change_pct = 0.0 if first_close == 0 else ((last_close - first_close) / first_close) * 100

    score = 0
    reasons = []

    if rsi < 30:
        score += 2
        reasons.append("RSI aşırı satım bölgesinde")
    elif rsi > 70:
        score -= 2
        reasons.append("RSI aşırı alım bölgesinde")

    if last_close > sma20 > sma50:
        score += 2
        reasons.append("fiyat kısa/orta vadeli ortalamaların üzerinde")
    elif last_close < sma20 < sma50:
        score -= 2
        reasons.append("fiyat kısa/orta vadeli ortalamaların altında")

    if macd > macd_signal:
        score += 1
        reasons.append("MACD pozitif bölgede")
    else:
        score -= 1
        reasons.append("MACD momentumu negatif")

    if last_close < bb_lower:
        score += 1
        reasons.append("Bollinger alt bandına yakın (tepki potansiyeli)")
    elif last_close > bb_upper:
        score -= 1
        reasons.append("Bollinger üst bandında (düzeltme riski)")

    if score >= 3:
        decision = "GÜÇLÜ AL"
        trend_strength = "Güçlü"
    elif score >= 1:
        decision = "KADEMELİ AL"
        trend_strength = "Orta"
    elif score <= -3:
        decision = "GÜÇLÜ SAT"
        trend_strength = "Zayıflıyor"
    elif score <= -1:
        decision = "ZAYIF GÖRÜNÜM"
        trend_strength = "Zayıf"
    else:
        decision = "TUT / İZLE"
        trend_strength = "Nötr"

    confidence = min(95.0, max(30.0, 50 + abs(score) * 10))
    risk_level = _risk_from_vol(_safe_float(vol))

    comment = (
        f"Karar skoru {score} olarak hesaplandı. Öne çıkan sinyaller: "
        + ", ".join(reasons[:3])
        + "."
    )

    return {
        "symbol_name": "Varlık Analizi",
        "last_price": last_close,
        "change_pct": change_pct,
        "rsi": rsi,
        "volatility": _safe_float(vol),
        "decision": decision,
        "comment": comment,
        "risk_level": risk_level,
        "trend_strength": trend_strength,
        "confidence": confidence,
    }
