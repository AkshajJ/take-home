import pandas as pd
import numpy as np
import streamlit as st
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.tree import DecisionTreeRegressor
from sklearn.svm import SVR
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import xgboost as xgb
import catboost as catb
import joblib
import os

class ModelTrainer:
    def __init__(self, product_df, purchase_lines_df, purchase_header_df):
        self.product_df = product_df
        self.purchase_lines_df = purchase_lines_df
        self.purchase_header_df = purchase_header_df.assign(
            PURCHASE_DATE_TIME=pd.to_datetime(purchase_header_df['PURCHASE_DATE_TIME']),
            PURCHASE_DATE=lambda df: df['PURCHASE_DATE_TIME'].dt.date
        )
        self.data = self.prepare_data()

        # List of models used and loading them in
        self.models = {
            'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'Linear Regression': LinearRegression(),
            'Decision Tree': DecisionTreeRegressor(random_state=42),
            'Ridge Regression': Ridge(),
            'Lasso Regression': Lasso(),
            'Support Vector Regression': SVR(),
            'XGBoost': xgb.XGBRegressor(random_state=42),
            'CatBoost': catb.CatBoostRegressor(random_state=42, verbose=0)
        }
        self.results = {}

        # Ensure the models directory exists
        if not os.path.exists('models'):
            os.makedirs('models')

    # Combingn data and preparing to train model on 
    def prepare_data(self):
        return self.purchase_lines_df.merge(self.purchase_header_df, on='PURCHASE_ID') \
            .merge(self.product_df, on='PRODUCT_ID') \
            .groupby(['PURCHASE_DATE', 'PRODUCT_ID']).size().reset_index(name='PURCHASE_COUNT')


    def create_features(self, df):
        df['PURCHASE_DATE'] = pd.to_datetime(df['PURCHASE_DATE'])
        df = df.assign(
            day_of_week=df['PURCHASE_DATE'].dt.dayofweek,
            month=df['PURCHASE_DATE'].dt.month,
            year=df['PURCHASE_DATE'].dt.year,
        ).sort_values(by=['PRODUCT_ID', 'PURCHASE_DATE'])
        df['lag_1'] = df.groupby('PRODUCT_ID')['PURCHASE_COUNT'].shift(1)
        df['lag_2'] = df.groupby('PRODUCT_ID')['PURCHASE_COUNT'].shift(2)
        df['rolling_mean_7'] = df.groupby('PRODUCT_ID')['PURCHASE_COUNT'].shift(1).rolling(window=7).mean()
        return df.dropna()

    # Saves trained models
    def save_model(self, model_name, model):
        joblib.dump(model, f'models/{model_name}.pkl')

    def load_model(self, model_name):
        return joblib.load(f'models/{model_name}.pkl')

    def evaluate_model(self, model, X_train, y_train, X_test, y_test):
        metrics = {}
        for split, X, y in [('train', X_train, y_train), ('test', X_test, y_test)]:
            y_pred = model.predict(X)
            metrics[f'{split}_mae'] = mean_absolute_error(y, y_pred)
            metrics[f'{split}_mse'] = mean_squared_error(y, y_pred)
            metrics[f'{split}_r2'] = r2_score(y, y_pred)
            metrics[f'{split}_accuracy'] = model.score(X, y) * 100
        return metrics

    def train_and_evaluate(self):
        purchase_data = self.create_features(self.data)
        X = purchase_data[['day_of_week', 'month', 'year', 'lag_1', 'lag_2', 'rolling_mean_7']]
        y = purchase_data['PURCHASE_COUNT']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        for model_name, model in self.models.items():
            if os.path.exists(f'models/{model_name}.pkl'):
                model = self.load_model(model_name)
            else:
                model.fit(X_train, y_train)
                self.save_model(model_name, model)
            self.results[model_name] = {'model': model, **self.evaluate_model(model, X_train, y_train, X_test, y_test)}

    def display_results(self, selected_model):
        metrics = self.results[selected_model]
        st.write(f"### {selected_model}")
        for key, value in metrics.items():
            if key != 'model':  # Skip displaying the model object
                st.write(f"{key.replace('_', ' ').title()}: {value}")


    def get_purchase_forecast(self, model, df, product_id, start_date, end_date):
        df_product = df[df['PRODUCT_ID'] == product_id].copy()
        future_dates = pd.date_range(start=start_date, end=end_date, freq='MS')
        
        forecast_data = []

        for future_date in future_dates:
            if len(df_product) >= 2:
                lag_1 = df_product['PURCHASE_COUNT'].iloc[-1]
                lag_2 = df_product['PURCHASE_COUNT'].iloc[-2]
                rolling_mean_7 = df_product['PURCHASE_COUNT'].iloc[-7:].mean() if len(df_product) >= 7 else df_product['PURCHASE_COUNT'].mean()
            else:
                lag_1, lag_2, rolling_mean_7 = 0, 0, 0

            future_df = pd.DataFrame({'PURCHASE_DATE': [future_date]})
            future_df = future_df.assign(
                day_of_week=future_df['PURCHASE_DATE'].dt.dayofweek,
                month=future_df['PURCHASE_DATE'].dt.month,
                year=future_df['PURCHASE_DATE'].dt.year,
                lag_1=lag_1,
                lag_2=lag_2,
                rolling_mean_7=rolling_mean_7
            )
            predicted_count = model.predict(future_df[['day_of_week', 'month', 'year', 'lag_1', 'lag_2', 'rolling_mean_7']])
            forecast_data.append({'PURCHASE_DATE': future_date, 'PREDICTED_PURCHASE_COUNT': predicted_count[0]})

            # Append the prediction to the df_product to update lag features for next prediction
            new_row = pd.DataFrame({
                'PURCHASE_DATE': [future_date],
                'PURCHASE_COUNT': [predicted_count[0]]
            })
            df_product = pd.concat([df_product, new_row], ignore_index=True)

        forecast_df = pd.DataFrame(forecast_data)
        department = self.product_df[self.product_df['PRODUCT_ID'] == product_id]['DEPARTMENT_NAME'].values[0]
        return forecast_df, department
    


    def forecast_and_plot(self):
        st.sidebar.header('Forecasting Options')
        product_id = st.sidebar.selectbox('Select Product ID', self.product_df['PRODUCT_ID'].unique())
        model_type = st.sidebar.selectbox('Select Model', list(self.models.keys()))
        start_date = st.sidebar.date_input('Start Date')
        end_date = st.sidebar.date_input('End Date', start_date + pd.DateOffset(months=18))
        
        if st.sidebar.button('Generate Forecast'):
            model = self.load_model(model_type)
            forecast_df, department = self.get_purchase_forecast(model, self.data, product_id, start_date, end_date)
            
            st.write(f"### Forecasted Purchase Counts for Product {product_id} in Department {department}")
            st.line_chart(forecast_df.set_index('PURCHASE_DATE'))




    def predict_co_purchases(self, purchase_lines_df, product_id):
        co_purchase_counts = purchase_lines_df[purchase_lines_df['PRODUCT_ID'] != product_id]
        co_purchase_counts = co_purchase_counts.groupby('PRODUCT_ID')['PURCHASE_ID'].count().reset_index(name='CO_PURCHASE_COUNT')
        st.write("### Top 10 Co-Purchased Products")
        st.write(co_purchase_counts.sort_values(by='CO_PURCHASE_COUNT', ascending=False).head(10))


