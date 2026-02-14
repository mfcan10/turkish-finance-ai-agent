from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class AssetItem:
    symbol: str
    label: str


def _items(raw: list[tuple[str, str]]) -> list[AssetItem]:
    return [AssetItem(symbol=s, label=l) for s, l in raw]


ASSET_CATEGORIES: Dict[str, List[AssetItem]] = {
    "🇹🇷 BIST Hisseleri": _items(
        [
            ("THYAO.IS", "Türk Hava Yolları"),
            ("ASELS.IS", "Aselsan"),
            ("EREGL.IS", "Ereğli Demir Çelik"),
            ("BIMAS.IS", "Bim Mağazalar"),
            ("SISE.IS", "Şişecam"),
            ("KCHOL.IS", "Koç Holding"),
            ("TUPRS.IS", "Tüpraş"),
            ("AKBNK.IS", "Akbank"),
            ("GARAN.IS", "Garanti BBVA"),
            ("ISCTR.IS", "İş Bankası C"),
        ]
    ),
    "🌍 Global Endeksler": _items(
        [
            ("^GSPC", "S&P 500"),
            ("^NDX", "NASDAQ 100"),
            ("^DJI", "Dow Jones"),
            ("^RUT", "Russell 2000"),
            ("^FTSE", "FTSE 100"),
            ("^GDAXI", "DAX"),
            ("^N225", "Nikkei 225"),
            ("XU100.IS", "BIST 100"),
        ]
    ),
    "📊 ETF'ler": _items(
        [
            ("SPY", "SPDR S&P 500 ETF"),
            ("QQQ", "Invesco QQQ"),
            ("IWM", "iShares Russell 2000"),
            ("DIA", "SPDR Dow Jones"),
            ("VTI", "Vanguard Total Stock Market"),
            ("EEM", "iShares Emerging Markets"),
            ("GLD", "SPDR Gold Shares"),
            ("SLV", "iShares Silver Trust"),
        ]
    ),
    "🪙 Kripto Paralar": _items(
        [
            ("BTC-USD", "Bitcoin"),
            ("ETH-USD", "Ethereum"),
            ("BNB-USD", "BNB"),
            ("SOL-USD", "Solana"),
            ("XRP-USD", "XRP"),
            ("ADA-USD", "Cardano"),
            ("DOGE-USD", "Dogecoin"),
            ("AVAX-USD", "Avalanche"),
        ]
    ),
    "💱 Döviz Pariteleri": _items(
        [
            ("EURUSD=X", "EUR/USD"),
            ("GBPUSD=X", "GBP/USD"),
            ("USDJPY=X", "USD/JPY"),
            ("USDTRY=X", "USD/TRY"),
            ("EURTRY=X", "EUR/TRY"),
            ("XAUUSD=X", "Altın/USD"),
            ("TRY=X", "USD/TRY (legacy)"),
        ]
    ),
    "⛏️ Emtialar & Vadeli": _items(
        [
            ("GC=F", "Gold Futures"),
            ("SI=F", "Silver Futures"),
            ("CL=F", "Crude Oil WTI"),
            ("BZ=F", "Brent Crude"),
            ("NG=F", "Natural Gas"),
            ("HG=F", "Copper"),
            ("ZC=F", "Corn"),
            ("ZS=F", "Soybeans"),
        ]
    ),
    "🏦 Fonlar / Mutual Funds": _items(
        [
            ("VTSAX", "Vanguard Total Stock Market Index Fund"),
            ("VFIAX", "Vanguard 500 Index Fund"),
            ("SWPPX", "Schwab S&P 500 Index Fund"),
            ("FXAIX", "Fidelity 500 Index Fund"),
            ("VWELX", "Vanguard Wellington Fund"),
        ]
    ),
}


def get_category_names() -> list[str]:
    return list(ASSET_CATEGORIES.keys())


def get_symbols_by_category(category: str) -> list[AssetItem]:
    return ASSET_CATEGORIES.get(category, [])


def get_all_assets() -> list[AssetItem]:
    merged: list[AssetItem] = []
    for items in ASSET_CATEGORIES.values():
        merged.extend(items)
    return merged
