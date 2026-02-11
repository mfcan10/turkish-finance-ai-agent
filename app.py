import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Finance Ai Agent",
    layout="wide",
    page_icon="⚡"
)

# ================= PREMIUM UI CSS =================
st.markdown("""
<style>

.main {
    background: radial-gradient(circle at top, #0b1020, #05080f);
    color: #eaeaea;
}

section[data-testid="stSidebar"] {
    background: rgba(15, 23, 42, 0.95);
    backdrop-filter: blur(12px);
}

/* Terminal Title */
.terminal-title {
    font-size: 48px;
    font-weight: 800;
    text-align: center;
    background: linear-gradient(90deg,#00ffc6,#0077ff);
    -webkit-background-clip: text;
    color: transparent;
}

/* Metric Cards */
[data-testid="stMetric"] {
    background: rgba(20, 30, 60, 0.6);
    padding: 20px;
    border-radius: 18px;
    border: 1px solid rgba(0,255,204,0.15);
    box-shadow: 0 0 20px rgba(0,255,204,0.1);
}

[data-testid="stMetricValue"] {
    font-size: 34px;
    font-weight: 700;
    color: #00ffc6;
}

/* Buttons */
.stButton>button {
    background: linear-gradient(135deg, #00ffc6, #0077ff);
    border-radius: 12px;
    border: none;
    color: black;
    font-weight: bold;
    padding: 8px 20px;
}

/* Expander */
details {
    background: rgba(20,30,60,0.5);
    border-radius: 12px;
    padding: 10px;
    border: 1px solid rgba(255,255,255,0.05);
}

</style>
""", unsafe_allow_html=True)

# ================= TITLE =================
st.markdown("<div class='terminal-title'>ALPHA TERMINAL PRO ⚡</div>", unsafe_allow_html=True)
st.caption("Quant Trading Dashboard | Real-Time Market Intelligence")

# ================= AUTO REFRESH =================
st_autorefresh(interval=15000, key="market_refresh")

# ================= SIDEBAR =================
with st.sidebar:
    st.markdown("## 🛰️ Alpha Control Panel")
    st.caption(f"Last Update: {datetime.now().strftime('%H:%M:%S')}")

    asset = st.selectbox(
        "Asset",
        ["BTC-USD", "ETH-USD", "GC=F", "SI=F", "USDTRY=X", "THYAO.IS", "ASELS.IS", "EREGL.IS"]
    )

    ma_period = st.slider("SMA Trend Period", 5, 100, 20)
    rsi_period = st.slider("RSI Momentum Period", 7, 30, 14)

    if st.button("🧹 Clear Cache"):
        st.cache_data.clear()

# ================= DATA ENGINE =================
@st.cache_data(ttl=10)
def load_data(ticker, ma_p, rsi_p):
    df = yf.download(ticker, period="1d", interval="1m", auto_adjust=True, progress=False)

    if df.empty or len(df) < 5:
        return None

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df["SMA"] = df["Close"].rolling(ma_p).mean()

    delta = df["Close"].diff()
    gain = delta.where(delta > 0, 0).rolling(rsi_p).mean()
    loss = -delta.where(delta < 0, 0).rolling(rsi_p).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))

    return df

# ================= MAIN =================
try:
    data = load_data(asset, ma_period, rsi_period)

    if data is None:
        st.error("No market data. Market closed or ticker invalid.")
        st.stop()

    current = data.iloc[-1]
    open_price = data["Open"].iloc[0]
    price = float(current["Close"])
    change = ((price - open_price) / open_price) * 100
    rsi = current["RSI"]

    # ===== TOP METRICS =====
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(asset, f"{price:,.2f}", f"{change:.2f}%")

    rsi_text = f"{rsi:.2f}" if not pd.isna(rsi) else "Loading..."
    c2.metric("RSI", rsi_text)

    if not pd.isna(rsi):
        if rsi > 70:
            c3.error("⚠ OVERBOUGHT")
        elif rsi < 30:
            c3.success("🔥 OVERSOLD")
        else:
            c3.info("⚖ NEUTRAL")
    else:
        c3.info("Calculating...")

    c4.metric("Volume", f"{int(current['Volume']):,}")

    # ================= CHART =================
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                       vertical_spacing=0.03, row_heights=[0.7, 0.3])

    # Candles
    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data["Open"],
        high=data["High"],
        low=data["Low"],
        close=data["Close"],
        name="Price",
        increasing_line_color="#00ffc6",
        decreasing_line_color="#ff3b3b"
    ), row=1, col=1)

    # SMA
    fig.add_trace(go.Scatter(
        x=data.index, y=data["SMA"],
        line=dict(color="#ffaa00", width=1.5),
        name=f"SMA {ma_period}"
    ), row=1, col=1)

    # Volume
    colors = ["#00ffc6" if data["Close"].iloc[i] >= data["Open"].iloc[i] else "#ff3b3b" for i in range(len(data))]
    fig.add_trace(go.Bar(
        x=data.index,
        y=data["Volume"],
        marker_color=colors,
        name="Volume"
    ), row=2, col=1)

    fig.update_layout(
        height=700,
        paper_bgcolor="#05080f",
        plot_bgcolor="#05080f",
        template="plotly_dark",
        font=dict(color="#e0e0e0"),
        xaxis_rangeslider_visible=False,
        xaxis=dict(showgrid=False),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        margin=dict(l=10, r=10, t=20, b=10)
    )

    st.plotly_chart(fig, use_container_width=True)

    # ================= SMART ANALYSIS =================
    with st.expander("🧠 AI Trend & Risk Intelligence"):
        col1, col2 = st.columns(2)

        with col1:
            if price > current["SMA"]:
                st.write("📈 Trend: Bullish (Above SMA)")
            else:
                st.write("📉 Trend: Bearish (Below SMA)")

        with col2:
            vol = (data["High"].iloc[-10:].max() - data["Low"].iloc[-10:].min()) / price * 100
            st.write(f"⚡ Volatility (10m): {vol:.2f}%")
            if vol > 0.6:
                st.warning("High volatility zone!")

except Exception as e:
    st.error(f"System Error: {e}")

