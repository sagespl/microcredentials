import sys
from pathlib import Path

import pandas as pd

p = Path(sys.argv[1]) if len(sys.argv)>1 else Path('data/incoming/unknown/_2026-08-07_akcje.xls')
print('Reading', p)
try:
    df = pd.read_excel(p, sheet_name=0, engine='xlrd')
    cols = list(df.columns)
    for i,c in enumerate(cols, start=1):
        print(f'{i}: {c}')
except Exception as e:
    print('ERROR:', e)
    raise
