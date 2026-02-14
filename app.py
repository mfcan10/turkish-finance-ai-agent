from datetime import datetime

import plotly.graph_objects as go
import streamlit as st

from finance_agent import advanced_analysis, get_stock_data
from report_generator import generate_report

st.set_page_config(page_title="Finance Agent | Midas Tarzı", layout="wide", page_icon="📈")

st.markdown(
    """
    <style>
    .stApp { background: #f8fafc; color: #0f172a; }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
        border-right: 1px solid rgba(148, 163, 184, 0.25);
    }
    [data-testid="stSidebar"] * { color: #e2e8f0 !important; }
    .card {
        background: #fff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 18px;
        box-shadow: 0 10px 24px rgba(15, 23, 42, 0.06);
    }
    .metric-title { font-size: 12px; color: #64748b; margin-bottom: 6px; }
    .metric-value { font-size: 26px; font-weight: 800; color: #0f172a; }
    .buy { color:#10b981; font-weight:800; }
    .sell { color:#ef4444; font-weight:800; }
    .hold { color:#f59e0b; font-weight:800; }
    </style>
    """,
    unsafe_allow_html=True,
)


def _signal_class(signal: str) -> str:
    if "AL" in signal:
        return "buy"
    if "SAT" in signal or "ZAYIF" in signal:
        return "sell"
    return "hold"


@st.cache_data(ttl=300)
def load_market_data(symbol: str, period: str, demo_fallback: bool):
    return get_stock_data(symbol=symbol, period=period, allow_demo_fallback=demo_fallback)


with st.sidebar:
    st.markdown("## 🤖 Finance Agent")
    st.caption("Sade + güçlü Midas tarzı terminal")

    symbols = ["THYAO.IS", "ASELS.IS", "EREGL.IS", "BIMAS.IS", "SISE.IS", "KCHOL.IS", "BTC-USD"]
    symbol = st.selectbox("Varlık", symbols)
    period = st.select_slider("Analiz Periyodu", ["1mo", "3mo", "6mo", "1y", "2y"], value="1y")
    use_demo_fallback = st.toggle("Bağlantı sorunu olursa demo veriye geç", value=True)

    col_a, col_b = st.columns(2)
    with col_a:
        refresh_clicked = st.button("🔄 Yenile", use_container_width=True)
    with col_b:
        clear_clicked = st.button("🧹 Cache Temizle", use_container_width=True)

    if clear_clicked:
        st.cache_data.clear()
        st.success("Cache temizlendi")

if refresh_clicked:
    load_market_data.clear()


df, volatility, is_demo = load_market_data(symbol, period, use_demo_fallback)

if df is None or df.empty:
    st.error("Veri alınamadı. Demo fallback kapalıysa açıp tekrar deneyin.")
    st.stop()

analysis = advanced_analysis(df, volatility)
last_price = float(df["Close"].iloc[-1])
prev_price = float(df["Close"].iloc[-2]) if len(df) > 1 else last_price
change_daily = ((last_price - prev_price) / prev_price * 100) if prev_price else 0.0

h1, h2 = st.columns([3, 1])
with h1:
    st.markdown(
        f"""
        <div class='card'>
            <h2 style='margin:0'>{symbol} Teknik Panel</h2>
            <div style='color:#64748b;margin-top:6px'>Güncelleme: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}</div>
            <div style='margin-top:6px;color:{'#f59e0b' if is_demo else '#64748b'}'>
            {'⚠️ Demo veri modu aktif (internet/proxy engeli nedeniyle).' if is_demo else 'Canlı veri kullanılıyor.'}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with h2:
    color = "#10b981" if change_daily >= 0 else "#ef4444"
    st.markdown(
        f"""
        <div class='card' style='text-align:right'>
            <div style='font-size:34px;font-weight:800'>{last_price:,.2f}</div>
            <div style='font-size:16px;font-weight:700;color:{color}'>%{change_daily:.2f}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

tab_overview, tab_strategy, tab_report = st.tabs(["📊 Piyasa", "🧠 Strateji", "📝 Rapor"])

with tab_overview:
    fig = go.Figure()
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            increasing_line_color="#10b981",
            decreasing_line_color="#ef4444",
            name="Fiyat",
        )
    )
    fig.add_trace(go.Scatter(x=df.index, y=df["SMA20"], mode="lines", line=dict(color="#3b82f6", width=1.5), name="SMA20"))
    fig.add_trace(go.Scatter(x=df.index, y=df["SMA50"], mode="lines", line=dict(color="#8b5cf6", width=1.5), name="SMA50"))
    fig.add_trace(go.Scatter(x=df.index, y=df["BB_UPPER"], mode="lines", line=dict(color="#94a3b8", width=1, dash="dot"), name="BB Üst"))
    fig.add_trace(go.Scatter(x=df.index, y=df["BB_LOWER"], mode="lines", line=dict(color="#94a3b8", width=1, dash="dot"), name="BB Alt"))
    fig.update_layout(template="plotly_white", height=520, xaxis_rangeslider_visible=False, margin=dict(l=0, r=0, t=8, b=0))
    st.plotly_chart(fig, width="stretch")

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f"<div class='card'><div class='metric-title'>RSI</div><div class='metric-value'>{analysis['rsi']:.2f}</div></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='card'><div class='metric-title'>Yıllık Volatilite</div><div class='metric-value'>%{analysis['volatility']:.2f}</div></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='card'><div class='metric-title'>Trend Gücü</div><div class='metric-value' style='font-size:22px'>{analysis['trend_strength']}</div></div>", unsafe_allow_html=True)
    c4.markdown(f"<div class='card'><div class='metric-title'>Güven Skoru</div><div class='metric-value'>%{analysis['confidence']:.0f}</div></div>", unsafe_allow_html=True)

with tab_strategy:
    st.markdown(
        f"""
        <div class='card'>
            <div class='metric-title'>Model Kararı</div>
            <div class='{_signal_class(analysis['decision'])}' style='font-size:30px'>{analysis['decision']}</div>
            <p style='color:#334155; margin-top:8px'>{analysis['comment']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    rc1, rc2 = st.columns(2)
    with rc1:
        st.info(f"Risk Seviyesi: **{analysis['risk_level']}**")
    with rc2:
        st.info(f"Dönemsel Değişim: **%{analysis['change_pct']:.2f}**")

with tab_report:
    report_md = generate_report(symbol, analysis)
    st.markdown(report_md)

    d1, d2 = st.columns(2)
    with d1:
        st.download_button(
            "📥 Markdown Raporu İndir",
            data=report_md,
            file_name=f"{symbol}_strateji_raporu.md",
            mime="text/markdown",
            width="stretch",
        )
    with d2:
        csv_bytes = df.tail(120).to_csv(index=True).encode("utf-8")
        st.download_button(
            "📥 Son 120 Gün Verisini İndir (CSV)",
            data=csv_bytes,
            file_name=f"{symbol}_son120.csv",
            mime="text/csv",
            width="stretch",
        )
