import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from collections import Counter

class QueryTool:
    def __init__(self, product_df, purchase_lines_df, purchase_header_df):
        self.product_df = product_df
        self.purchase_lines_df = purchase_lines_df
        self.purchase_header_df = purchase_header_df
        # Calculate the volume and add it to the product_df
        self.product_df['VOLUME'] = self.product_df['HEIGHT_INCHES'] * self.product_df['WIDTH_INCHES'] * self.product_df['DEPTH_INCHES']

    def purchase_info(self):
        st.title("Information about your purchase")
        st.subheader("Example Purchase ID: 386880957")
        st.subheader("Example Product ID: 76610")

        purchase_id = st.text_input("Enter Purchase ID")
        if purchase_id:
            purchase_id = str(purchase_id).replace(',', '')  # remove commas
            # Grab relevant info of purchase by querying into other dataframes
            try:
                purchase_date = self.purchase_header_df.query('PURCHASE_ID == @purchase_id')['PURCHASE_DATE_TIME'].values[0]
                product_details = self.purchase_lines_df.query('PURCHASE_ID == @purchase_id').merge(
                    self.product_df, on='PRODUCT_ID').drop(columns=['PURCHASE_ID'])
                
                st.write(f"**Purchase ID**: {purchase_id}")
                st.write(f"**Purchase Date**: {purchase_date}")
                st.write("**Product Details**:")
                st.dataframe(product_details)

            except IndexError:
                st.write("Invalid Purchase ID or data not found.")

    def display_commonly_bought_products(self, product_id):
        try:
            purchase_ids = self.purchase_lines_df[self.purchase_lines_df['PRODUCT_ID'] == product_id]['PURCHASE_ID'].unique()
            other_products = []

            for purchase_id in purchase_ids:
                products_in_purchase = self.purchase_lines_df[self.purchase_lines_df['PURCHASE_ID'] == purchase_id]['PRODUCT_ID'].tolist()
                other_products.extend([p for p in products_in_purchase if p != product_id])
            product_counts = Counter(other_products)
            top_common_products = product_counts.most_common(5)

            st.write(f"Top 5 commonly bought products with Product ID {product_id}:")

            for product, count in top_common_products:
                st.write(f"Product ID: {product}, Count: {count}")
        except IndexError:
            st.write("Invalid Product ID or data not found.")

    def product_info(self):
        st.title("Product Information")
        product_id = st.text_input("Enter Product ID")
        if product_id:
            product_id = str(product_id).replace(',', '')

            try:
                product_purchase_lines = self.purchase_lines_df[self.purchase_lines_df['PRODUCT_ID'] == str(product_id)]
                if not product_purchase_lines.empty:
                    purchase_ids = product_purchase_lines['PURCHASE_ID'].tolist()
                    quantities = product_purchase_lines['QUANTITY'].tolist()
                    purchase_dates = []
                    
                    for purchase_id in purchase_ids:
                        purchase_date = self.purchase_header_df.loc[self.purchase_header_df['PURCHASE_ID'] == purchase_id, 'PURCHASE_DATE_TIME'].iloc[0]
                        purchase_dates.append(purchase_date)
                    
                    st.write("**Product Details**:")

                    product_details = self.product_df.query('PRODUCT_ID == @product_id')
                    
                    st.dataframe(product_details)

                    product_info_df = pd.DataFrame({
                        'Purchase ID': purchase_ids,
                        'Purchase Date': purchase_dates,
                        'Quantity': quantities
                    })

                    self.display_commonly_bought_products(product_id)

                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=purchase_dates, y=quantities, mode='markers+lines', name='Quantity', marker=dict(size=8)))
                    fig.update_layout(title="Purchase Quantity Over Time", xaxis_title="Purchase Date", yaxis_title="Quantity")

                    col1, col2 = st.columns([2, 3]) # spacing

                    with col1:
                        st.write("**Purchase Information of the product**:")
                        st.dataframe(product_info_df)
                    with col2:
                        st.plotly_chart(fig)
                else:
                    st.write("No purchase information available for this product.")
            except IndexError:
                st.write("Invalid Product ID or data not found.")

    def purchases_by_date(self):
        st.title("Purchases by Date")
        st.write("Make sure to select a date from 3/25/2020 to 4/12/2020 since that's the time frame of the data")

        selected_date = st.date_input("Select a Date")

        if selected_date:
            self.purchase_header_df['PURCHASE_DATE_TIME'] = pd.to_datetime(self.purchase_header_df['PURCHASE_DATE_TIME'])
            self.purchase_header_df['PURCHASE_DATE'] = self.purchase_header_df['PURCHASE_DATE_TIME'].dt.strftime('%m/%d/%Y')
            filtered_purchases = self.purchase_header_df[self.purchase_header_df['PURCHASE_DATE'] == selected_date.strftime('%m/%d/%Y')]
            
            if not filtered_purchases.empty:
                purchase_ids = filtered_purchases['PURCHASE_ID'].tolist()
                st.write(f"**Purchases on {selected_date.strftime('%m/%d/%Y')}**:")
                purchase_details = self.purchase_lines_df[self.purchase_lines_df['PURCHASE_ID'].isin(purchase_ids)].merge(self.product_df, on='PRODUCT_ID')
                st.dataframe(purchase_details)
            else:
                st.write("No purchases found for the selected date.")
