import pandas as pd
import json

try:
    df = pd.read_excel('generated_data.xlsx', sheet_name='Subjectwise')
    # Let's inspect rows where name contains 'Signals' and outof is 50 or similar
    # or just print a few rows randomly to see if tw_pr exists
    if 'tw_pr' in df.columns:
        print('tw_pr exists!')
        print(df[['subject_name', 'marks', 'tw_pr']].dropna(subset=['tw_pr']).head(5))
    else:
        print('tw_pr does NOT exist in columns:', df.columns.tolist())
except Exception as e:
    print('Failed:', e)
