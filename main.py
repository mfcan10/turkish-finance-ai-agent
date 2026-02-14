# Finance Agent 
import logging
from finance_agent import get_stock_data, advanced_analysis
from report_generator import generate_report, save_report

# Loglama ayarlarını yapalım (Terminalde ne olup bittiğini görmek için)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("FinanceAgentMain")

def run_agent_workflow(symbol: str):
    """
    Belirli bir hisse için tüm analiz ve raporlama sürecini yönetir.
    """
    try:
        logger.info(f"🚀 {symbol} için Finance Agent süreci başlatılıyor...")
        
        # 1. Veri Çekme (Beyin - Adım 1)
        # finance_agent.py içindeki yeni fonksiyonu kullanıyoruz
        df, vol, is_demo = get_stock_data(symbol, period="1y", allow_demo_fallback=True) 
        
        if df is None:
            logger.error(f"❌ {symbol} verisi alınamadığı için süreç durduruldu.")
            return

        # 2. Gelişmiş Analiz (Beyin - Adım 2)
        # Sadece fiyat değil, RSI ve Trend analizi yapılır
        analysis = advanced_analysis(df, vol)
        if is_demo:
            logger.warning("⚠️ %s için demo veri ile analiz üretildi.", symbol)
        logger.info(f"📊 Analiz tamamlandı. Karar: {analysis['decision']}")

        # 3. Rapor Oluşturma (Fabrika - Adım 3)
        # report_generator.py içindeki Midas tarzı raporu hazırlar
        report_md = generate_report(symbol, analysis)
        
        # 4. Raporu Kaydetme (Çıktı - Adım 4)
        saved_file = save_report(report_md, symbol)
        
        if saved_file:
            logger.info(f"✅ İşlem başarılı! Rapor oluşturuldu: {saved_file}")
            print("-" * 30)
            print(f"Finance Agent Özeti ({symbol}):")
            print(f"Fiyat: {analysis['last_price']:.2f}")
            print(f"Sinyal: {analysis['decision']}")
            print(f"Risk: {analysis['risk_level']}")
            print("-" * 30)

    except Exception as e:
        logger.error(f"⚠️ Kritik sistem hatası: {e}")

if __name__ == "__main__":
  
    test_list = ["THYAO.IS", "BTC-USD"]
    
    print("🤖 FINANCE AGENT - OTONOM ANALİZ SİSTEMİ")
    for asset in test_list:
        run_agent_workflow(asset)
