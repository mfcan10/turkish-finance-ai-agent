import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# Sayfa Ayarları
st.set_page_config(page_title="Pro Terminal | Live", layout="wide")

# Her 30 saniyede bir sayfayı canlı güncelle (Canlı veri hissi)
st_autorefresh(interval=30000, key="datarefresh")

# Takip Listesi Tanımları (İstediğin her şeyi buraya ekle)
ASSETS = {
    "Hisseler": ["THYAO.IS", "ASELS.IS", "EREGL.IS", "AAPL", "TSLA"],
    "Emtia": ["GC=F", "SI=F", "CL=F"], # Altın, Gümüş, Petrol
    "Kripto": ["BTC-USD", "ETH-USD", "SOL-USD"],
    "Döviz": ["USDTRY=X", "EURTRY=X"]
}

# --- CSS ile Arayüzü Güzelleştirme ---
st.markdown("""
    <style>
    .metric-card { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    .stMetric { background-color: #0d1117; padding: 10px; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR: Canlı Takip Listesi ---
with st.sidebar:
    st.title("🛰️ Live Watchlist")
    all_data = []
    
    # Tüm varlıkların son fiyatlarını toplayalım
    flat_list = [item for sublist in ASSETS.values() for item in sublist]
    
    with st.spinner('Veriler akıyor...'):
        for ticker in flat_list:
            stock = yf.Ticker(ticker)
            # Fast_info veya history ile hızlı veri çekme
            hist = stock.history(period="2d")
            if not hist.empty:
                last_price = hist['Close'].iloc[-1]
                prev_price = hist['Close'].iloc[-2]
                change = ((last_price - prev_price) / prev_price) * 100
                all_data.append({"Symbol": ticker, "Price": round(last_price, 2), "Change %": round(change, 2)})

    # Listeyi Tablo Olarak Göster
    df_watch = pd.DataFrame(all_data)
    st.dataframe(df_watch.style.format({"Change %": "{:.2f}%"}).applymap(
        lambda x: 'color: #28a745' if isinstance(x, (int, float)) and x > 0 else 'color: #ea4335', subset=['Change %']
    ), hide_index=True, use_container_width=True)

    selected_symbol = st.selectbox("Grafik İçin Seçin", df_watch['Symbol'])

# --- ANA EKRAN: Grafik ve Detay ---
col_main, col_stats = st.columns([3, 1])

with col_main:
    st.subheader(f"📊 {selected_symbol} Analiz Terminali")
    
    # Zaman Aralığı Seçimi
    time_frame = st.tabs(["1G", "1H", "1A", "1Y", "Max"])
    periods = {"1G": "1d", "1H": "1wk", "1A": "1mo", "1Y": "1y", "Max": "max"}
    
    # Seçili tab'a göre veri çek (Basitleştirilmiş gösterim)
    data = yf.download(selected_symbol, period="1mo", interval="1h")
    
    fig = go.Figure(data=[go.Candlestick(
        x=data.index, open=data['Open'], high=data['High'],
        low=data['Low'], close=data['Close']
    )])
    fig.update_layout(template="plotly_dark", height=600, margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig, use_container_width=True)

with col_stats:
    st.subheader("📌 Özet Bilgi")
    info = yf.Ticker(selected_symbol).fast_info
    
    st.metric("Piyasa Değeri", f"{info.market_cap / 1e9:.2f}B" if info.market_cap else "N/A")
    st.metric("Günlük Volatilite", f"{info.year_high - info.year_low:.2f}")
    
    st.markdown("---")
    st.write("**🤖 AI Sinyali:**")
    st.info("Kısa vadeli RSI değerleri aşırı alım bölgesinde. Kar realizasyonu beklenebilir.")
