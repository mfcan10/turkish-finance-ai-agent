import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# 1. Sayfa Ayarları
st.set_page_config(page_title="Alpha Terminal V3.5", layout="wide", page_icon="🚀")

# Modern Arayüz CSS
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 28px; font-weight: bold; color: #00ffcc; }
    .stAlert { border-radius: 8px; border: 1px solid #444; }
    .main { background-color: #0e1117; }
    </style>
    """, unsafe_allow_html=True)

# 2. Otomatik Yenileme
st_autorefresh(interval=15000, key="fiyat_guncelleme")

# 3. Sidebar ve Parametreler
with st.sidebar:
    st.title("🛰️ Alpha Monitor")
    st.info(f"Son Güncelleme: {datetime.now().strftime('%H:%M:%S')}")
    
    asset = st.selectbox(
        "İzlenecek Varlık", 
        ["BTC-USD", "ETH-USD", "GC=F", "SI=F", "USDTRY=X", "THYAO.IS", "ASELS.IS", "EREGL.IS"],
        index=0
    )
    
    ma_period = st.slider("SMA Periyodu (Trend)", 5, 100, 20)
    rsi_period = st.slider("RSI Periyodu (Momentum)", 7, 30, 14)
    
    st.divider()
    if st.button("🔴 Önbelleği Temizle"):
        st.cache_data.clear()

# 4. Veri Mühendisliği ve Analiz
@st.cache_data(ttl=10)
def veri_hazirla(ticker, ma_p, rsi_p):
    try:
        # 1 dakikalık veri için genellikle '1d' periyodu yeterlidir
        df = yf.download(ticker, period="1d", interval="1m", auto_adjust=True, progress=False)
        
        if df.empty or len(df) < 5:
            return None
        
        # yfinance Multi-Index Düzeltmesi
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        # Sütun isimlerini garantiye alalım
        df = df.copy()

        # SMA Analizi
        df['SMA'] = df['Close'].rolling(window=ma_p).mean()
        
        # RSI Analizi (Geliştirilmiş Doğruluk)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=rsi_p).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_p).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        return df
    except Exception as e:
        print(f"Veri çekme hatası: {e}")
        return None

# 5. Ana Ekran Mantığı
try:
    data = veri_hazirla(asset, ma_period, rsi_period)
    
    if data is not None:
        # Son verilerin güvenli çekilmesi
        current_row = data.iloc[-1]
        prev_row = data.iloc[-2] if len(data) > 1 else current_row
        
        son_fiyat = float(current_row['Close'])
        acilis_fiyat = float(data['Open'].iloc[0])
        degisim = ((son_fiyat - acilis_fiyat) / acilis_fiyat) * 100
        current_rsi = current_row['RSI']

        # --- ÜST METRİKLER ---
        c1, c2, c3, c4 = st.columns(4)
        c1.metric(f"{asset}", f"{son_fiyat:,.2f}", f"{degisim:.2f}%")
        
        rsi_val = f"{current_rsi:.2f}" if not pd.isna(current_rsi) else "Veri Bekleniyor..."
        c2.metric(f"RSI ({rsi_period})", rsi_val)
        
        # Risk ve Karar Motoru
        if not pd.isna(current_rsi):
            if current_rsi > 70:
                c3.error("⚠️ AŞIRI ALIM (Satış Baskısı Olabilir)")
            elif current_rsi < 30:
                c3.success("📉 AŞIRI SATIM (Tepki Alımı Gelebilir)")
            else:
                c3.info("⚖️ NÖTR BÖLGE")
        else:
            c3.info("⏳ Sinyal Hesaplanıyor...")
            
        c4.metric("İşlem Hacmi", f"{int(current_row['Volume']):,}")

        # --- GELİŞMİŞ GRAFİK ---
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                           vertical_spacing=0.05, row_heights=[0.7, 0.3])

        # Candlestick
        fig.add_trace(go.Candlestick(
            x=data.index, open=data['Open'], high=data['High'],
            low=data['Low'], close=data['Close'], name="Fiyat"
        ), row=1, col=1)

        # SMA
        fig.add_trace(go.Scatter(
            x=data.index, y=data['SMA'], 
            line=dict(color='#ff9800', width=1.5), 
            name=f"SMA {ma_period}"
        ), row=1, col=1)

        # Hacim Barları
        colors = ['#26a69a' if data['Close'].iloc[i] >= data['Open'].iloc[i] else '#ef5350' for i in range(len(data))]
        fig.add_trace(go.Bar(
            x=data.index, y=data['Volume'], 
            marker_color=colors, name="Hacim", opacity=0.8
        ), row=2, col=1)

        fig.update_layout(
            height=600,
            template="plotly_dark",
            xaxis_rangeslider_visible=False,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="#0e1117",
            plot_bgcolor="#161a22",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)

        # --- İLERİ ANALİZ NOTLARI (RİSK ANALİZİ) ---
        with st.expander("🔍 Akıllı Trend ve Risk Analizi"):
            col_a, col_b = st.columns(2)
            with col_a:
                if son_fiyat > current_row['SMA']:
                    st.write("📈 **Trend:** Pozitif. Fiyat ortalamanın üzerinde tutunuyor.")
                else:
                    st.write("📉 **Trend:** Negatif. Ortalamanın altındaki seyir baskıyı artırabilir.")
            
            with col_b:
                volatilite = (data['High'].iloc[-10:].max() - data['Low'].iloc[-10:].min()) / son_fiyat * 100
                st.write(f"⚡ **Volatilite (Son 10 dk):** %{volatilite:.2f}")
                if volatilite > 0.5:
                    st.write("❗ **Dikkat:** Sert hareketler beklenen bir bölgedesiniz.")

    else:
        st.warning(f"⚠️ {asset} için şu an veri alınamıyor. Piyasa kapalı olabilir veya sembol hatalıdır.")

except Exception as e:
    st.error(f"Sistem Hatası: {e}")
