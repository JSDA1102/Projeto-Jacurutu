from functions.pipeline import get_dashboard_data

RAW_PATH = 'raw_data/'
OUTPUT_PATH = 'functions/front/dashboard_data.parquet'

df_final = get_dashboard_data(RAW_PATH)
df_final.to_parquet(OUTPUT_PATH, index=False)
