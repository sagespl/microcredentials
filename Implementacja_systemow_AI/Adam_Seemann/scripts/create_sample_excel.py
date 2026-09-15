from pathlib import Path

import pandas as pd

p = Path('data/incoming')
p.mkdir(parents=True, exist_ok=True)

df = pd.DataFrame({
    'Ticker': ['AAA', 'BBB'],
    'ISIN': ['PLAAA0000001', 'PLBBB0000002'],
    'Date': ['2026-08-10', '2026-08-11'],
    'Open': [100.0, 105.0],
    'High': [110.0, 108.0],
    'Low': [99.0, 103.0],
    'Close': [108.0, 107.0],
})

out = p / 'real_akcje.xlsx'
df.to_excel(out, index=False)
print('Created', out)
