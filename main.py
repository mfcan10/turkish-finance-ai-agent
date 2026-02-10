# main runner file
# future: integrate LLM and news sentiment

from finance_agent import get_stock_data, basic_analysis
from report_generator import generate_report, save_report

def run():
    symbol = "GARAN.IS"  # Garanti Bankası
    
    print("Fetching data...")
    prices = get_stock_data(symbol)
    
    print("Running basic analysis...")
    analysis = basic_analysis(prices)
    
    print("Generating report...")
    report = generate_report(symbol, analysis)
    save_report(report)
    
    print("Report generated -> sample_report.md")

if __name__ == "__main__":
    run()
