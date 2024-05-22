import os
import pandas as pd
import streamlit as st

class DataProcessor:
    def __init__(self):
        self.dataframes = self.load_data()

    def load_data(self):
        base_path = "data"
        files = ['product', 'purchase_header', 'purchase_lines']
        dfs = {}
        for file in files:
            csv_path = os.path.join(base_path, f"{file}.csv")
            parquet_path = os.path.join(base_path, f"{file}.parquet")

            if os.path.exists(parquet_path):
                df = pd.read_parquet(parquet_path)
                #st.text(f"Loaded {file} from Parquet file.")  # Loaded parquet file
            else:
                df = pd.read_csv(csv_path)
                for col in ['PRODUCT_ID', 'PURCHASE_ID']:
                    if col in df.columns:
                        df[col] = df[col].astype(str).str.replace(',', '')
                df.to_parquet(parquet_path, index=False)
                #st.text(f"Converted {file} from CSV to Parquet and saved.")
            dfs[file] = df
        return dfs

    def get_df(self, name):
        return self.dataframes[name]
    


