# app.py içine eklenecek 'Ajan' entegrasyonu
import finance_agent as fa # Senin harici dosyaların
import report_generator as rg

# Sidebar veya ana ekrana bir buton
if st.button("🤖 Yapay Zeka Raporu Oluştur"):
    with st.spinner("Analiz motoru çalışıyor..."):
        # 1. Veriyi çek (main.py'daki mantık)
        prices = fa.get_stock_data(asset) 
        
        # 2. Analizi yap
        analysis_results = fa.basic_analysis(prices)
        
        # 3. Raporu oluştur (Dosyaya yazmak yerine metin olarak al)
        report_text = rg.generate_report(asset, analysis_results)
        
        # 4. Ekranda göster
        st.markdown("---")
        st.subheader("📊 AI Strateji Raporu")
        st.info(report_text)
