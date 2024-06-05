import os
import pandas as pd
import tushare as ts
import pickle
import re

def load_and_concatenate_csvs(data_dir):
    files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    return pd.concat([pd.read_csv(os.path.join(data_dir, file)) for file in files])

def generate_factor_table(data):
    return data.pivot(index='date', columns='asset', values='RVar')

def rearrange_column_name(col_name):
    match = re.match(r'([A-Za-z]+)(\d+)', col_name)
    return match.group(2) + '.' + match.group(1) if match else col_name

def generate_price_and_return_tables(tushare_token, factor_table):
    ts.set_token(tushare_token)
    factor_table.columns = [rearrange_column_name(col) for col in factor_table.columns]
    dates = factor_table.index.tolist()
    fund_codes = factor_table.columns.tolist()

    # Initialize the dataframes before data fetching
    table_close = pd.DataFrame(index=pd.to_datetime(dates), columns=fund_codes)
    table_returns = pd.DataFrame(index=pd.to_datetime(dates), columns=fund_codes)

    for fund_code in fund_codes:
        df = ts.pro_bar(ts_code=fund_code, start_date='20230101', end_date='20230907')
        if not df.empty:
            for _, row in df.iterrows():
                date = pd.to_datetime(row['trade_date'], format='%Y%m%d').strftime("%Y-%m-%d")
                close_price_today = row['close']
                pre_close = row['pre_close']
                returns = (close_price_today - pre_close) / pre_close
                if date in table_close.index:
                    table_close.at[date, fund_code] = close_price_today
                    table_returns.at[date, fund_code] = returns
    return table_close, table_returns

