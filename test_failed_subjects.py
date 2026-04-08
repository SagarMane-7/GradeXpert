import pandas as pd
import os

LATEST_DATA_PATH = os.path.join('generated', 'latest_report.xlsx')

df = pd.read_excel(LATEST_DATA_PATH, sheet_name='All Students')
failed = df[df['status'] == 'Fail'].copy()

try:
    sub_df = pd.read_excel(LATEST_DATA_PATH, sheet_name='Subjectwise')
    failed_subs = sub_df[sub_df['status'].astype(str).str.strip().str.title() == 'Fail']
    
    # Aggregate subjects
    agg_subs = failed_subs.groupby('seat_no')['subject_name'].apply(lambda x: ', '.join(x.astype(str))).reset_index()
    agg_subs.rename(columns={'subject_name': 'failed_subjects'}, inplace=True)
    
    failed = failed.merge(agg_subs, on='seat_no', how='left')
    failed['failed_subjects'] = failed['failed_subjects'].fillna('N/A')
    
    print(failed[['seat_no', 'name', 'failed_subjects']].head())
except Exception as e:
    print(e)
