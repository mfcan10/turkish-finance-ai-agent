import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

# 1. Finance Agent Marka ve Sayfa Ayarları
st.set_page_config(page_title="Finance Agent | AI Terminal", layout="wide", page_icon="🤖")

# Custom CSS: Midas & Bloomberg Modern Dark UI
st.markdown("""
    <style>
    .stApp { background-color: #0c0e12; color: #e2e8f0; }
    [data-testid="stSidebar"] { background-color: #111418; border-right: 1px solid #232933; }
    
    /* Finance Agent Özel Kartları */
    .agent-card {
        background: #161a22; border-radius: 12px; padding: 25px;
        border: 1px solid #232933; margin-bottom: 20px;
    }
    .recommendation-label { font-size: 14px; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; }
    .rec-buy { color: #00d3ad; font-size: 32px; font-weight: 800; }
    .rec-sell { color: #ff4b50; font-size: 32px; font-weight: 800; }
    .rec-hold { color: #ffab00; font-size: 32px; font-weight: 800; }
    
    /* Risk Kutusu */
    .risk-alert { 
        padding: 15px; border-radius: 10px; background: rgba(255, 75, 80, 0.1); 
        border-left: 5px solid #ff4b50; margin-top: 10px;
    }
    .risk-safe { 
        padding: 15px; border-radius: 10px; background: rgba(0, 211, 173, 0.1); 
        border-left: 5px solid #00d3ad; margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Zeka Motoru (Analiz Fonksiyonları)
def get_analysis(df):
    # RSI Hesaplama
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs)).iloc[-1]
    
    # Volatilite (Yıllıklandırılmış)
    vol = df['Close'].pct_change().std() * np.sqrt(252) * 100
    
    # Karar Algoritması
    current_price = df['Close'].iloc[-1]
    sma_50 = df['Close'].rolling(window=50).mean().iloc[-1]
    
    if rsi < 30:
        return "GÜÇLÜ AL", "Fiyat aşırı satım bölgesinde. Teknik tepki ve dip dönüşü beklentisi hakim.", "Düşük/Orta", vol
    elif rsi > 70:
        return "GÜÇLÜ SAT", "Fiyat aşırı alım bölgesinde yoruluyor. Kar realizasyonu riski çok yüksek.", "Yüksek", vol
    elif current_price > sma_50:
        return "TUT / EKLE", "Pozitif trend korunuyor. 50 günlük ortalamanın üzerinde güç topluyor.", "Orta", vol
    else:
        return "İZLE / BEKLE", "Trend zayıf. Yeni bir giriş sinyali için hacimli bir kırılım beklenmeli.", "Orta/Yüksek", vol

# 3. SOL MENÜ (Finance Agent Seçim Paneli)
with st.sidebar:
    st.markdown("<h2 style='color:#00d3ad;'>🤖 Finance Agent</h2>", unsafe_allow_html=True)
    st.caption("Veri Odaklı Karar Destek Sistemi")
    st.write("---")
    
    category = st.tabs(["Hisseler", "Kripto", "Emtia"])
    
    with category[0]:
        hisse_list = ["THYAO.IS", "ASELS.IS", "EREGL.IS", "BIMAS.IS", "SISE.IS", "KCHOL.IS", "SASA.IS"]
        secim = st.selectbox("BIST İzleme Listesi", hisse_list)
    with category[1]:
        st.caption("Yakında Aktif")
    with category[2]:
        st.caption("Yakında Aktif")
        
    st.write("---")
    periyot = st.select_slider("Analiz Derinliği", options=["1mo", "3mo", "6mo", "1y", "2y"], value="6mo")
    st.info("Agent Notu: Uzun periyotlar daha güvenilir trend analizi sunar.")

# 4. SAĞ PANEL (Canlı Terminal)
df = yf.download(secim, period=periyot, interval="1d", auto_adjust=True)

if not df.empty:
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    
    karar, yorum, risk_lvl, vol_val = get_analysis(df)
    fiyat = df['Close'].iloc[-1]
    degisim = ((fiyat / df['Close'].iloc[-2]) - 1) * 100

    # Header
    c1, c2 = st.columns([3, 1])
    with c1:
        st.title(f"{secim} Analiz Raporu")
        st.caption(f"Veri çekilme zamanı: {datetime.now().strftime('%H:%M:%S')}")
    with c2:
        color = "#00d3ad" if degisim >= 0 else "#ff4b50"
        st.markdown(f"<div style='text-align:right'><span style='font-size:32px; font-weight:bold;'>{fiyat:,.2f}</span><br><span style='color:{color}'>%{degisim:.2f}</span></div>", unsafe_allow_html=True)

    # GRAFİK (Profesyonel Candlestick)
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Mum Grafiği"))
    fig.update_layout(template="plotly_dark", height=500, margin=dict(l=0,r=0,t=10,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

    # FINANCE AGENT PROFESYONEL YORUM ALANI
    st.markdown("---")
    st.subheader("🕵️ Finance Agent Strateji Notları")
    
    col_l, col_r = st.columns(2)
    
    with col_l:
        st.markdown(f'<div class="agent-card">', unsafe_allow_html=True)
        st.markdown('<p class="recommendation-label">ÖNERİLEN STRATEJİ</p>', unsafe_allow_html=True)
        rec_style = "rec-buy" if "AL" in karar else "rec-sell" if "SAT" in karar else "rec-hold"
        st.markdown(f'<p class="{rec_style}">{karar}</p>', unsafe_allow_html=True)
        st.write(f"**Agent Analizi:** {yorum}")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        st.markdown(f'<div class="agent-card">', unsafe_allow_html=True)
        st.markdown('<p class="recommendation-label">RİSK PROFİLİ & VOLATİLİTE</p>', unsafe_allow_html=True)
        st.write(f"Varlık Oynaklığı: **%{vol_val:.2f}**")
        st.write(f"Sistem Risk Puanı: **{risk_lvl}**")
        
        if vol_val > 35:
            st.markdown(f'<div class="risk-alert"><b>DİKKAT:</b> {secim} şu an yüksek volatilite bölgesinde. Sert fiyat dalgalanmaları sermaye kaybı riski taşır. Kademeli alım önerilir.</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="risk-safe"><b>STABİL:</b> Varlık düşük volatilite ile hareket ediyor. Teknik formasyonların çalışma olasılığı yüksek.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

else:
    st.error("Finance Agent veriye ulaşamadı. Sembol geçerliliğini kontrol edin.")


