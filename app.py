import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

# 1. Sayfa Ayarları
st.set_page_config(page_title="Finance Agent | Light Terminal", layout="wide", page_icon="🤖")

# 2. Midas White CSS - Temiz ve Aydınlık Arayüz
st.markdown("""
    <style>
    /* Ana Arka Plan ve Yazı Rengi */
    .stApp { background-color: #ffffff; color: #1e293b; }
    
    /* Sidebar Düzenlemesi */
    [data-testid="stSidebar"] { 
        background-color: #f8fafc; 
        border-right: 1px solid #e2e8f0; 
    }
    
    /* Midas Stili Kartlar */
    .agent-card {
        background: #ffffff; 
        border-radius: 16px; 
        padding: 25px;
        border: 1px solid #e2e8f0; 
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
    }
    
    /* Başlıklar ve Etiketler */
    .recommendation-label { font-size: 13px; color: #64748b; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
    .rec-buy { color: #00d3ad; font-size: 34px; font-weight: 800; }
    .rec-sell { color: #ff4b50; font-size: 34px; font-weight: 800; }
    .rec-hold { color: #f59e0b; font-size: 34px; font-weight: 800; }
    
    /* Risk Kutuları (Aydınlık Tema) */
    .risk-alert { 
        padding: 15px; border-radius: 12px; background: #fff1f2; 
        border-left: 5px solid #ff4b50; color: #991b1b; margin-top: 10px;
    }
    .risk-safe { 
        padding: 15px; border-radius: 12px; background: #f0fdf4; 
        border-left: 5px solid #00d3ad; color: #166534; margin-top: 10px;
    }
    
    /* Plotly Grafik Alanını Temizleme */
    .js-plotly-plot { border-radius: 16px; overflow: hidden; border: 1px solid #e2e8f0; }
    </style>
    """, unsafe_allow_html=True)

# 3. Analiz Motoru
def get_analysis(df):
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs)).iloc[-1]
    vol = df['Close'].pct_change().std() * np.sqrt(252) * 100
    current_price = df['Close'].iloc[-1]
    sma_50 = df['Close'].rolling(window=50).mean().iloc[-1]
    
    if rsi < 30:
        return "GÜÇLÜ AL", "Fiyat aşırı satım bölgesinde. Teknik dip oluşumu tamamlanmak üzere.", "Düşük/Orta", vol
    elif rsi > 70:
        return "GÜÇLÜ SAT", "Fiyat doyum noktasında. Kar realizasyonu için uygun seviyeler.", "Yüksek", vol
    elif current_price > sma_50:
        return "TUT / EKLE", "Yükseliş trendi sağlıklı şekilde devam ediyor.", "Orta", vol
    else:
        return "İZLE / BEKLE", "Piyasa kararsız. Net bir kırılım beklemek daha güvenli.", "Orta/Yüksek", vol

# 4. Sol Menü
with st.sidebar:
    st.markdown("<h2 style='color:#00d3ad; margin-bottom:0;'>🤖 Finance Agent</h2>", unsafe_allow_html=True)
    st.caption("Veri Odaklı Karar Destek Sistemi")
    st.write("---")
    
    hisse_list = ["THYAO.IS", "ASELS.IS", "EREGL.IS", "BIMAS.IS", "SISE.IS", "KCHOL.IS", "BTC-USD"]
    secim = st.selectbox("İzleme Listeniz", hisse_list)
    
    st.write("---")
    periyot = st.select_slider("Analiz Derinliği", options=["1mo", "3mo", "6mo", "1y", "2y"], value="6mo")
    st.markdown("---")

# 5. Sağ Panel
df = yf.download(secim, period=periyot, interval="1d", auto_adjust=True)

if not df.empty:
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    
    karar, yorum, risk_lvl, vol_val = get_analysis(df)
    fiyat = df['Close'].iloc[-1]
    degisim = ((fiyat / df['Close'].iloc[-2]) - 1) * 100

    # Header
    c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown(f"### {secim} Teknik Terminal")
        st.caption(f"Son Güncelleme: {datetime.now().strftime('%H:%M:%S')}")
    with c2:
        color = "#00d3ad" if degisim >= 0 else "#ff4b50"
        st.markdown(f"<div style='text-align:right'><span style='font-size:32px; font-weight:bold; color:#1e293b;'>{fiyat:,.2f}</span><br><span style='color:{color}; font-weight:600;'>%{degisim:.2f}</span></div>", unsafe_allow_html=True)

    # GRAFİK (Aydınlık Tema Uyumlu)
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
        increasing_line_color='#00d3ad', decreasing_line_color='#ff4b50',
        name="Fiyat"
    ))
    fig.update_layout(
        template="plotly_white", # Beyaz tema şablonu
        height=500, 
        margin=dict(l=0,r=0,t=10,b=0),
        xaxis_rangeslider_visible=False,
        paper_bgcolor='white',
        plot_bgcolor='#fcfcfc'
    )
    st.plotly_chart(fig, use_container_width=True)

    # FINANCE AGENT ANALİZ ALANI
    st.markdown("---")
    st.markdown("#### 🕵️ Agent Strateji Raporu")
    
    col_l, col_r = st.columns(2)
    
    with col_l:
        st.markdown(f'''
            <div class="agent-card">
                <p class="recommendation-label">Önerilen Strateji</p>
                <p class="{"rec-buy" if "AL" in karar else "rec-sell" if "SAT" in karar else "rec-hold"}">{karar}</p>
                <p style="color:#475569; line-height:1.6;">{yorum}</p>
            </div>
        ''', unsafe_allow_html=True)

    with col_r:
        st.markdown(f'''
            <div class="agent-card">
                <p class="recommendation-label">Risk ve Oynaklık</p>
                <p style="font-size:18px; font-weight:600; margin-top:10px;">Volatilite: %{vol_val:.2f}</p>
                <p style="font-size:16px; color:#475569;">Risk Puanı: <b>{risk_lvl}</b></p>
                <div class="{"risk-alert" if vol_val > 35 else "risk-safe"}">
                    {"<b>DİKKAT:</b> Sert hareket beklentisi. Portföy dağılımına dikkat edilmeli." if vol_val > 35 else "<b>STABİL:</b> Yatay/Düşük oynaklık. Güvenli bölge."}
                </div>
            </div>
        ''', unsafe_allow_html=True)

else:
    st.error("Veri alınamadı, lütfen tekrar deneyin.")
