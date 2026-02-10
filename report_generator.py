# generates markdown report
# english is not perfect, but ok for demo

from datetime import datetime

def generate_report(symbol, analysis):
    today = datetime.now().strftime("%Y-%m-%d")
    
    report = f"""
# Daily Finance AI Report - {today}

Stock: {symbol}

Start Price: {analysis['start_price']}
End Price: {analysis['end_price']}
Price Change: {analysis['change']}
Percent Change: {analysis['pct_change']} %

## AI Comment (prototype)
Market shows some volatility.  
If positive trend continues, short term momentum can be bullish.  
But macro risks still exist, need more confirmation.

(This is just experimental agent output)
"""
    return report

def save_report(text):
    with open("sample_report.md", "w", encoding="utf-8") as f:
        f.write(text)
