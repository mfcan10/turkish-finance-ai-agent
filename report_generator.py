import os
from datetime import datetime

def generate_report(symbol, analysis):
    """
    finance_agent.py'dan gelen gelişmiş analiz verilerini 
    profesyonel bir Markdown raporuna dönüştürür.
    """
    now = datetime.now().strftime('%d/%m/%Y %H:%M')
    
    # Görsel belirteçler
    status_emoji = "🟢" if "AL" in analysis['decision'] else "🔴" if "SAT" in analysis['decision'] else "🟡"
    risk_emoji = "⚠️" if analysis['risk_level'] == "Yüksek" else "✅"

    report = f"""# 🤖 FINANCE AGENT | Strateji Raporu
**Varlık:** {symbol}  
**Analiz Tarihi:** {now}

---

## 🎯 AGENT KARARI: {status_emoji} **{analysis['decision']}**

### 🧠 Stratejik Değerlendirme
> {analysis['comment']}

---

## 📊 Teknik Göstergeler
| Gösterge | Değer | Durum |
| :--- | :--- | :--- |
| **Son Fiyat** | {analysis['last_price']:,.2f} TL | - |
| **Dönem Değişimi** | %{analysis['change_pct']:.2f} | {"Artış" if analysis['change_pct'] > 0 else "Azalış"} |
| **RSI (14)** | {analysis['rsi']:.2f} | {"Aşırı Alım" if analysis['rsi'] > 70 else "Aşırı Satım" if analysis['rsi'] < 30 else "Nötr"} |
| **Volatilite** | %{analysis['volatility']:.2f} | {analysis['risk_level']} Risk |
| **Trend Gücü** | {analysis.get('trend_strength', 'Nötr')} | Momentum |
| **Güven Skoru** | %{analysis.get('confidence', 0):.0f} | Model Tutarlılığı |

---

## ⚠️ Risk ve Oynaklık Analizi
{risk_emoji} **Risk Seviyesi:** {analysis['risk_level']}

**Agent Notu:** {symbol} varlığı için yıllıklandırılmış oynaklık %{analysis['volatility']:.2f} olarak hesaplanmıştır. 
{ "Bu seviye, sermaye üzerinde yüksek oynaklık riski taşımaktadır. Stop-loss seviyeleri dar tutulmalıdır." if analysis['volatility'] > 35 else "Varlık şu an stabil bir bantta hareket ediyor. Teknik formasyonların çalışma olasılığı daha yüksek." }

---
*Yasal Uyarı: Bu rapor Finance Agent algoritması tarafından otomatik üretilmiştir. Yatırım tavsiyesi içermez.*
"""
    return report

def save_report(report, symbol):
    """Raporu indirilebilir bir dosya olarak kaydeder."""
    filename = f"{symbol}_Analiz_{datetime.now().strftime('%Y%m%d')}.md"
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report)
        return filename
    except Exception as e:
        print(f"Rapor kaydedilirken hata oluştu: {e}")
        return None
