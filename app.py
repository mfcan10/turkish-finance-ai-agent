import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# ====== PAGE CONFIG ======
st.set_page_config(page_title="Hisse Rapor Paneli", layout="centered")

# ====== TITLE ======
st.title("📊 Hisse Analiz Raporu")
st.caption("Basit Finansal Rapor Paneli")

# ====== SIDEBAR ======
with st.sidebar:
    st.header("⚙️ Ayarlar")

    hisse = st.selectbox(
        "Hisse / Varlık Seç",
        ["THYAO.IS", "ASELS.IS", "EREGL.IS", "BTC-USD", "ETH-USD", "USDTRY=X"]
    )

    periyot = st.selectbox("Zaman Aralığı", ["1mo", "3mo", "6mo", "1y", "5y"])

    if st.button("📥 Rapor Oluştur"):
        st.session_state["run"] = True

# ====== DATA LOAD ======
@st.cache_data
def load_data(symbol, period):
    return yf.download(symbol, period=period)

# ====== MAIN ======
if "run" in st.session_state:

    df = load_data(hisse, periyot)

    if df.empty:
        st.error("Veri alınamadı")
        st.stop()

    # ====== BASIC METRICS ======
    son_fiyat = df["Close"].iloc[-1]
    ilk_fiyat = df["Close"].iloc[0]
    degisim = ((son_fiyat - ilk_fiyat) / ilk_fiyat) * 100

    col1, col2, col3 = st.columns(3)
    col1.metric("Son Fiyat", f"{son_fiyat:,.2f}")
    col2.metric("Dönem Getirisi", f"{degisim:.2f}%")
    col3.metric("Veri Sayısı", len(df))

    # ====== PRICE CHART ======
    st.subheader("📈 Fiyat Grafiği")
    st.line_chart(df["Close"])

    # ====== SIMPLE REPORT ======
    st.subheader("🧾 Otomatik Analiz Raporu")

    trend = "Yükseliş" if degisim > 0 else "Düşüş"
    max_price = df["High"].max()
    min_price = df["Low"].min()

    report = f"""
    **Hisse:** {hisse}  
    **Rapor Tarihi:** {datetime.now().strftime('%d %B %Y %H:%M')}  

    • Genel Trend: **{trend}**  
    • Dönem Getirisi: **{degisim:.2f}%**  
    • En Yüksek Fiyat: **{max_price:.2f}**  
    • En Düşük Fiyat: **{min_price:.2f}**  
    """

    st.markdown(report)

    # ====== DOWNLOAD REPORT ======
    rapor_txt = report.replace("**", "")
    st.download_button("📄 Raporu TXT indir", rapor_txt, file_name="hisse_raporu.txt")


