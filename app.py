import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import joblib
import plotly.express as px
from datetime import datetime
from data_processor import DataProcessor
from home_page import HomePage
from data_analysis_page import DataPlots
from query_tool import QueryTool
from model_page import ModelTrainer
from conclusion_page import ConclusionPage

# Globally load data
data_processor = DataProcessor()
product_df = data_processor.get_df('product')
purchase_header_df = data_processor.get_df('purchase_header')
purchase_lines_df = data_processor.get_df('purchase_lines')

# Load trained models
def load_model(model_name):
    model_path = os.path.join('models', f'{model_name}.pkl')
    selected_model = joblib.load(model_path)
    return selected_model

def home():
    HomePage.load_project_intro()

def data_anlysis():
    data_plots = DataPlots(data_processor, product_df, purchase_lines_df, purchase_header_df)
    data_plots.plots()

def query_tool():
    query_tool = QueryTool(product_df, purchase_lines_df, purchase_header_df)
    query_tool.purchase_info()
    query_tool.product_info()
    query_tool.purchases_by_date()

def models():
    st.title("Future Purchase Prediction")
    st.header("DISCLAIMER: Page is slow, please be patient")

    # Initialize ModelTrainer
    model_trainer = ModelTrainer(product_df, purchase_lines_df, purchase_header_df)
    model_trainer.train_and_evaluate()

    # Select Product ID and Model
    product_id = st.selectbox("Select Product ID", model_trainer.data['PRODUCT_ID'].unique())
    model_name = st.selectbox("Select Model", list(model_trainer.models.keys()))

    # User input for future date
    future_date = st.date_input("Select a future date for prediction")
    
    start_date = st.date_input("Select the start date for forecast plot")
    end_date = st.date_input("Select the end date for forecast plot", start_date + pd.DateOffset(months=18))

    # Load selected model
    selected_model = load_model(model_name)

    # Forecast Prediction
    future_df, department = model_trainer.get_purchase_forecast(selected_model, model_trainer.data, product_id, start_date, end_date)

    # Display results
    st.write(f"## Predictions for Product {product_id}")
    st.write(f"### Predicted Purchase Count on {future_date}: {future_df['PREDICTED_PURCHASE_COUNT'].iloc[0]}")
    st.write(f"### Department: {department}")

    # Forecast Plot
    st.write(f"## Forecasting for Product {product_id}")
    fig = px.line(future_df, x='PURCHASE_DATE', y='PREDICTED_PURCHASE_COUNT', title='Forecasted Purchase Count')
    fig.update_xaxes(title_text='Date', dtick='M1', tickformat='%b\n%Y')
    fig.update_yaxes(title_text='Purchase Count')
    st.plotly_chart(fig)

    # Display Model Performance Metrics
    model_trainer.display_results(model_name)

    # Predict Co-Purchased Products
    st.write("## Co-Purchase Prediction")
    model_trainer.predict_co_purchases(purchase_lines_df, product_id)

def conclusion():
    ConclusionPage.load_project_conclusiom()

def navbar():
    selected = st.sidebar.radio("Menu", ["Home 🏡", "Data Analysis 📊", "Query Tool 🔍", "ML Modeling 🤖", "Conclusions + Next Steps 🚀"])
    
    if selected == "Home 🏡":
        home()

    elif selected == "Data Analysis 📊":
        data_anlysis()

    elif selected == "Query Tool 🔍":
        query_tool()

    elif selected == "ML Modeling 🤖":
        models()

    elif selected == "Conclusions + Next Steps 🚀":
        conclusion()

# Main Function
def main():
    navbar()

# Entry Point
if __name__ == "__main__":
    main()
