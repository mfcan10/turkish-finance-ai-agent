from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from asset_catalog import get_all_assets, get_category_names, get_symbols_by_category
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


all_assets = get_all_assets()
asset_lookup = {f"{item.symbol} — {item.label}": item.symbol for item in all_assets}

with st.sidebar:
    st.markdown("## 🤖 Finance Agent")
    st.caption("YFinance kategorili tarama + teknik analiz")

    category_names = get_category_names()
    selected_category = st.selectbox("Varlık Kategorisi", category_names)
    category_assets = get_symbols_by_category(selected_category)
    default_display = f"{category_assets[0].symbol} — {category_assets[0].label}" if category_assets else list(asset_lookup.keys())[0]

    symbol_display = st.selectbox("Kategori İçinden Varlık", [f"{a.symbol} — {a.label}" for a in category_assets], index=0 if category_assets else None)

    custom_symbol = st.text_input("Özel sembol ekle (YFinance)", placeholder="Örn: AAPL, MSFT, TSLA, ^IXIC")
    active_symbol = custom_symbol.strip().upper() if custom_symbol.strip() else asset_lookup.get(symbol_display, symbol_display.split(" — ")[0])

    period = st.select_slider("Analiz Periyodu", ["1mo", "3mo", "6mo", "1y", "2y"], value="1y")
    use_demo_fallback = st.toggle("Bağlantı sorunu olursa demo veriye geç", value=True)

    st.markdown("---")
    bulk_limit = st.slider("Toplu analizde sembol limiti", min_value=3, max_value=20, value=8)
    run_bulk = st.button("📡 Kategoriyi Toplu Analiz Et", use_container_width=True)

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


df, volatility, is_demo = load_market_data(active_symbol, period, use_demo_fallback)

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
            <h2 style='margin:0'>{active_symbol} Teknik Panel</h2>
            <div style='color:#64748b;margin-top:6px'>Kategori: {selected_category}</div>
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

tab_overview, tab_strategy, tab_report, tab_bulk = st.tabs(["📊 Piyasa", "🧠 Strateji", "📝 Rapor", "🗂️ Kategori Tarama"])

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
    report_md = generate_report(active_symbol, analysis)
    st.markdown(report_md)

    d1, d2 = st.columns(2)
    with d1:
        st.download_button(
            "📥 Markdown Raporu İndir",
            data=report_md,
            file_name=f"{active_symbol}_strateji_raporu.md",
            mime="text/markdown",
            width="stretch",
        )
    with d2:
        csv_bytes = df.tail(120).to_csv(index=True).encode("utf-8")
        st.download_button(
            "📥 Son 120 Gün Verisini İndir (CSV)",
            data=csv_bytes,
            file_name=f"{active_symbol}_son120.csv",
            mime="text/csv",
            width="stretch",
        )

with tab_bulk:
    st.caption("Seçili kategorideki varlıkların tamamına yakınını toplu teknik analiz eder.")

    if run_bulk:
        records = []
        subset = category_assets[:bulk_limit]
        progress = st.progress(0)
        status = st.empty()

        for i, asset in enumerate(subset, start=1):
            status.info(f"Analiz ediliyor: {asset.symbol}")
            bdf, bvol, bdemo = load_market_data(asset.symbol, period, use_demo_fallback)
            if bdf is not None and not bdf.empty:
                out = advanced_analysis(bdf, bvol)
                records.append(
                    {
                        "Sembol": asset.symbol,
                        "Ad": asset.label,
                        "Karar": out["decision"],
                        "Risk": out["risk_level"],
                        "Güven": round(float(out["confidence"]), 1),
                        "Volatilite": round(float(out["volatility"]), 2),
                        "Demo": "Evet" if bdemo else "Hayır",
                    }
                )
            progress.progress(i / len(subset))

        status.success("Kategori taraması tamamlandı.")

        if records:
            result_df = pd.DataFrame(records).sort_values(by=["Güven", "Volatilite"], ascending=[False, True])
            st.dataframe(result_df, width="stretch", hide_index=True)
            st.download_button(
                "📥 Kategori Analiz Sonucu (CSV)",
                data=result_df.to_csv(index=False).encode("utf-8"),
                file_name=f"kategori_tarama_{selected_category}.csv",
                mime="text/csv",
                width="stretch",
            )
        else:
            st.warning("Hiçbir sembol için veri alınamadı.")
    else:
        st.info("Toplu analiz için soldaki 'Kategoriyi Toplu Analiz Et' butonuna tıkla.")
