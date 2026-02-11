import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Sayfa Konfigürasyonu (Gelişmiş Görünüm İçin)
st.set_page_config(
    page_title="Turkish Finance AI Agent",
    page_icon="🚀",
    layout="wide", # Ekranı tam kullanır
    initial_sidebar_state="expanded"
)

# --- SIDEBAR (Yan Menü) ---
with st.sidebar:
    st.image("https://www.freeiconspng.com/uploads/finance-icon-png-5.png", width=100)
    st.title("AI Agent Kontrol")
    st.markdown("---")
    
    # Kullanıcı Girdileri
    symbol = st.text_input("Hisse Sembolü (BIST)", value="THYAO.IS").upper()
    period = st.selectbox("Zaman Aralığı", ["1mo", "3mo", "6mo", "1y", "2y", "5y"])
    
    st.info("💡 Not: BIST hisseleri için sonuna '.IS' eklemeyi unutmayın.")
    
    analyze_button = st.button("Analizi Başlat 🔍", use_container_width=True)

# --- ANA EKRAN ---
st.title("📈 Turkish Finance AI Agent")
st.caption(f"Veri Kaynağı: Yahoo Finance | Son Güncelleme: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

if analyze_button:
    try:
        # Veri Çekme
        with st.spinner('Piyasa verileri analiz ediliyor...'):
            data = yf.download(symbol, period=period)
            
        if data.empty:
            st.error("Veri bulunamadı. Lütfen sembolü kontrol edin.")
        else:
            # Üst Metrik Kartları
            last_price = data['Close'].iloc[-1].item()
            prev_price = data['Close'].iloc[-2].item()
            change = ((last_price - prev_price) / prev_price) * 100
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Son Fiyat", f"{last_price:.2f} ₺", f"{change:.2f}%")
            col2.metric("En Yüksek (Periyot)", f"{data['High'].max().item():.2f} ₺")
            col3.metric("En Düşük (Periyot)", f"{data['Low'].min().item():.2f} ₺")
            col4.metric("İşlem Hacmi", f"{data['Volume'].iloc[-1].item():,.0f}")

            st.markdown("---")

            # Grafik Alanı (Plotly ile İnteraktif)
            fig = go.Figure(data=[go.Candlestick(
                x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name="Fiyat Hareketleri"
            )])
            
            fig.update_layout(
                title=f"{symbol} Teknik Grafik",
                yaxis_title="Fiyat (₺)",
                template="plotly_dark",
                xaxis_rangeslider_visible=False,
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)

            # AI Rapor Alanı (Placeholder)
            st.subheader("🤖 AI Strateji Raporu")
            
            # Burada senin main.py'deki mantığı bir kutu içinde gösterelim
            report_col1, report_col2 = st.columns([2, 1])
            
            with report_col1:
                with st.expander("Detaylı Analiz Raporunu Gör", expanded=True):
                    st.markdown(f"""
                    ### {symbol} Trend Analizi
                    - **Genel Görünüm:** {'Pozitif' if change > 0 else 'Negatif'}
                    - **Destek/Direnç:** Veriler analiz ediliyor...
                    - **AI Yorumu:** Mevcut fiyat hareketleri kısa vadeli bir {'toparlanma' if change > 0 else 'düzeltme'} sinyali veriyor.
                    """)
            
            with report_col2:
                st.warning("⚠️ Risk Analizi: Volatilite yüksek, kademeli alım önerilir.")

    except Exception as e:
        st.error(f"Bir hata oluştu: {e}")

else:
    # İlk Açılış Ekranı
    st.info("Sol taraftaki menüden bir hisse kodu girerek 'Analizi Başlat' butonuna basın.")
    st.image("https://images.unsplash.com/photo-1611974717483-9b32524e6ca8?auto=format&fit=crop&q=80&w=2070", caption="Borsa İstanbul AI Dashboard")
