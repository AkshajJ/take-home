import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime

class DataPlots:
    
    def __init__(self, data_processor, product_df, purchase_lines_df, purchase_header_df):
        self.data_processor = data_processor
        self.product_df = product_df
        self.purchase_lines_df = purchase_lines_df
        self.purchase_header_df = purchase_header_df
        self.product_df['VOLUME'] = self.product_df['HEIGHT_INCHES'] * self.product_df['WIDTH_INCHES'] * self.product_df['DEPTH_INCHES']

    # Count missing values
    def count_missing_values(self):
        
        missing_values = {
            'Product DataFrame': self.product_df.isnull().sum(),
            'Purchase Lines DataFrame': self.purchase_lines_df.isnull().sum(),
            'Purchase Header DataFrame': self.purchase_header_df.isnull().sum()
        }

        st.write("### Missing Values Summary")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(f"**{list(missing_values.keys())[0]}:**")
            st.write(missing_values['Product DataFrame'].to_frame(name='Count'))

        with col2:
            st.write(f"**{list(missing_values.keys())[1]}:**")
            st.write(missing_values['Purchase Lines DataFrame'].to_frame(name='Count'))

        with col3:
            st.write(f"**{list(missing_values.keys())[2]}:**")
            st.write(missing_values['Purchase Header DataFrame'].to_frame(name='Count'))


    def plot_basic_stats(self):
        st.write("## Basic Statistics of Numerical Data")
        st.write(self.product_df.describe())

    def plot_categorical_summary(self):
        st.write("## Categorical Column Summaries (in inches)")
        stats = ['mean', 'min', 'max', 'std']
        columns = ['HEIGHT_INCHES', 'WIDTH_INCHES', 'DEPTH_INCHES', 'WEIGHT_GRAMS', 'VOLUME']

        agg_dict = {col: stats for col in columns}
        agg_dict['PRODUCT_ID'] = 'count'
        department_summary = self.product_df.groupby('DEPARTMENT_NAME').agg(agg_dict).reset_index()
        department_summary.columns = ['_'.join(col).strip() if col[1] else col[0] for col in department_summary.columns.values]
        rename_dict = {f'{col}_{stat}': f'{stat.capitalize()} {col.split("_")[0].capitalize()}' for col in columns for stat in stats}
        rename_dict['PRODUCT_ID_count'] = 'Count'
        department_summary.rename(columns=rename_dict, inplace=True)
        
        cols = ['DEPARTMENT_NAME', 'Count'] + [col for col in department_summary.columns if col not in ['DEPARTMENT_NAME', 'Count']]
        department_summary = department_summary[cols]

        st.dataframe(department_summary)

    def plot_correlation_heatmap(self):
        st.write("## Correlation Heatmap for Product Dataset")
        fig, ax = plt.subplots()
        sns.heatmap(self.product_df.select_dtypes(include=['float64', 'int64']).corr(), annot=True, cmap='coolwarm', ax=ax)
        ax.set_title('Correlation Heatmap')
        st.pyplot(fig)

    def plot_interactive_bar(self, department_summary):
        st.write("## Interactive Bar Plot for Product Statistics")
        col1, col2 = st.columns([1, 3])
        with col1:
            measurement = st.selectbox("Select Measurement", options=['Height', 'Width', 'Depth', 'Weight', 'Volume', 'Count'])
            stat_type = st.selectbox("Select Statistic", options=['Mean', 'Min', 'Max', 'Std']) if measurement != 'Count' else 'Count'
            column_name = f'{stat_type} {measurement}' if measurement != 'Count' else 'Count'
        with col2:
            fig = px.bar(department_summary, x='DEPARTMENT_NAME', y=column_name, 
                title=f'{stat_type} of {measurement} by Department' if measurement != 'Count' else 'Count by Department',
                labels={'DEPARTMENT_NAME': 'Department', column_name: f'{stat_type} {measurement}' if measurement != 'Count' else 'Count'})
            st.plotly_chart(fig)

    def plot_top_products(self):
        merged_df = self.purchase_lines_df.merge(self.product_df, on='PRODUCT_ID')

        # Count the number of purchases for each product
        product_popularity = merged_df['PRODUCT_ID'].value_counts()

        # Calculate the total quantity purchased for each product
        product_quantities = merged_df.groupby('PRODUCT_ID')['QUANTITY'].sum()

        # Extract the top 10 most purchased products
        top_product_ids = product_popularity.head(10).index

        # Extract details of top products
        top_products = self.product_df[self.product_df['PRODUCT_ID'].isin(top_product_ids)].set_index('PRODUCT_ID')
        top_products['PURCHASE_COUNT'] = product_popularity[top_product_ids]
        top_products['TOTAL_QUANTITY'] = product_quantities[top_product_ids]

        # Combine Product ID, Department Name, and Total Quantity for the plot
        top_products['Product_Info'] = top_products.index.astype(str) + " (" + top_products['DEPARTMENT_NAME'] + "), Total Qty: " + top_products['TOTAL_QUANTITY'].astype(str)

        # Create a Plotly bar plot
        fig = px.bar(top_products, 
            x='PURCHASE_COUNT', 
            y='Product_Info', 
            orientation='h', 
            title='Top 10 Most Purchased Products',
            labels={'PURCHASE_COUNT': 'Number of Purchases', 'Product_Info': 'Product (Department, Total Quantity)'})

        fig.update_layout(
            xaxis_title="Number of Purchases",
            yaxis_title="Product ID",
            yaxis=dict(categoryorder='total ascending'),
            template='plotly_dark',
            width=800,
            height=600
        )
        st.plotly_chart(fig)

    def plot_quantity_analysis(self):
        st.write("## Time vs Quantity Purchased Plots")

        # Merge purchase lines with product data
        merged_df = self.purchase_lines_df.merge(self.product_df, on='PRODUCT_ID')

        # Merge with purchase header to get purchase date
        merged_df = merged_df.merge(self.purchase_header_df[['PURCHASE_ID', 'PURCHASE_DATE_TIME']], on='PURCHASE_ID')

        # Convert 'PURCHASE_DATE_TIME' to datetime
        merged_df['PURCHASE_DATE_TIME'] = pd.to_datetime(merged_df['PURCHASE_DATE_TIME'])

        # Calculate total purchase quantity per day
        merged_df['PURCHASE_DATE'] = merged_df['PURCHASE_DATE_TIME'].dt.date
        daily_purchase_quantity = merged_df.groupby('PURCHASE_DATE')['QUANTITY'].sum()

        # Plot total purchase quantity over time
        fig = go.Figure(data=go.Scatter(x=daily_purchase_quantity.index, y=daily_purchase_quantity.values, mode='lines'))
        fig.update_layout(title='Total Purchase Quantity Over Time', xaxis_title='Date', yaxis_title='Total Purchase Quantity')
        st.plotly_chart(fig)

        # Analyze purchase patterns by department
        department_purchase = merged_df.groupby(['DEPARTMENT_NAME', 'PURCHASE_DATE'])['QUANTITY'].sum().reset_index()

        # Plot purchase trends by department
        fig = px.line(department_purchase, x='PURCHASE_DATE', y='QUANTITY', color='DEPARTMENT_NAME', title='Purchase Trends by Department')
        st.plotly_chart(fig)

        # Analyze average purchase quantity by department
        avg_purchase_by_department = merged_df.groupby('DEPARTMENT_NAME')['QUANTITY'].mean().sort_values(ascending=False)

        # Visualize average purchase quantity by department
        fig = go.Figure(data=go.Bar(x=avg_purchase_by_department.values, y=avg_purchase_by_department.index, orientation='h'))
        fig.update_layout(title='Average Purchase Quantity by Department', xaxis_title='Average Purchase Quantity', yaxis_title='Department')
        st.plotly_chart(fig)

    

    def plot_hourly_products(self):
        
        self.purchase_header_df['PURCHASE_DATE_TIME'] = pd.to_datetime(self.purchase_header_df['PURCHASE_DATE_TIME'])

        # Extracting purchase hour
        self.purchase_header_df['PURCHASE_HOUR'] = self.purchase_header_df['PURCHASE_DATE_TIME'].dt.hour
        merged_df = self.purchase_lines_df.merge(self.product_df, on='PRODUCT_ID')
        merged_df = merged_df.merge(self.purchase_header_df[['PURCHASE_ID', 'PURCHASE_HOUR']], on='PURCHASE_ID')

        # Group by purchase hour and product ID
        hourly_products_count = merged_df.groupby(['PURCHASE_HOUR', 'PRODUCT_ID']).size().reset_index(name='COUNT')

        # Find the most popular and least bought product for each hour
        idx_max = hourly_products_count.groupby('PURCHASE_HOUR')['COUNT'].transform(max) == hourly_products_count['COUNT']
        hourly_most_popular_products = hourly_products_count[idx_max]
        

        idx_min = hourly_products_count.groupby('PURCHASE_HOUR')['COUNT'].transform(min) == hourly_products_count['COUNT']
        hourly_least_bought_products = hourly_products_count[idx_min]

        # Merge with product_df to get department name
        hourly_most_popular_products = hourly_most_popular_products.merge(self.product_df, on='PRODUCT_ID', how='left')
        hourly_least_bought_products = hourly_least_bought_products.merge(self.product_df, on='PRODUCT_ID', how='left')
        
        st.write("## Most Popular Product bought each Hour")
        st.write(hourly_most_popular_products)

        st.write("## Least Bought Product bought each Hour")
        st.write(hourly_least_bought_products)

        # Counting purchases by hour
        purchase_by_hour = self.purchase_header_df['PURCHASE_HOUR'].value_counts().sort_index()

        # Plotting the distribution of purchases by hour
        fig = px.bar(x=purchase_by_hour.index, y=purchase_by_hour.values, labels={'x': 'Hour of the Day', 'y': 'Number of Purchases'})
        fig.update_layout(title='Distribution of Purchases by Hour of the Day', xaxis_title='Hour', yaxis_title='Number of Purchases')
        st.plotly_chart(fig)

        # Finding the most popular hour
        most_popular_hour = purchase_by_hour.idxmax()
        st.write(f"The most popular time of day for purchases is around {most_popular_hour}:00")


    def plot_purchase_over_time(self):
        st.write("## Number of Purchases Over Time")
        # Convert 'PURCHASE_DATE_TIME' to datetime
        self.purchase_header_df['PURCHASE_DATE_TIME'] = pd.to_datetime(self.purchase_header_df['PURCHASE_DATE_TIME'])
        
        # Extracting purchase date
        self.purchase_header_df['PURCHASE_DATE'] = self.purchase_header_df['PURCHASE_DATE_TIME'].dt.date
        
        # Counting total purchases per day
        total_purchases_over_time = self.purchase_header_df['PURCHASE_DATE'].value_counts().sort_index()

        # Plotting the number of total purchases over time
        fig_total = px.line(x=total_purchases_over_time.index, y=total_purchases_over_time.values, labels={'x': 'Date', 'y': 'Total Number of Purchases'})
        fig_total.update_layout(title='Total Number of Purchases Over Time', xaxis_title='Date', yaxis_title='Total Number of Purchases')
        st.plotly_chart(fig_total)
        
        st.write("## Filtered Purchases Over Time by Department")
        # Get unique department names
        department_names = self.product_df['DEPARTMENT_NAME'].unique()
        
        selected_departments = st.multiselect("Select Departments", department_names)

        if not selected_departments:
            st.warning("Please select at least one department.")
            return

        # Merge 'DEPARTMENT_NAME' from product_df into purchase_lines_df
        merged_purchase_lines = self.purchase_lines_df.merge(self.product_df[['PRODUCT_ID', 'DEPARTMENT_NAME']], on='PRODUCT_ID')

        # Filter merged purchase lines by selected departments
        filtered_purchase_lines = merged_purchase_lines[merged_purchase_lines['DEPARTMENT_NAME'].isin(selected_departments)]

        # Merge filtered purchase lines with product data and purchase header
        merged_df = filtered_purchase_lines.merge(self.purchase_header_df[['PURCHASE_ID', 'PURCHASE_DATE_TIME']], on='PURCHASE_ID')

        # Convert 'PURCHASE_DATE_TIME' to datetime
        merged_df['PURCHASE_DATE_TIME'] = pd.to_datetime(merged_df['PURCHASE_DATE_TIME'])

        # Extracting department name and purchase date
        merged_df['DEPARTMENT_NAME'] = merged_df['DEPARTMENT_NAME'].str.capitalize()
        merged_df['PURCHASE_DATE'] = merged_df['PURCHASE_DATE_TIME'].dt.date

        # Counting purchases by department over time
        purchases_by_department = merged_df.groupby(['DEPARTMENT_NAME', 'PURCHASE_DATE'])['PURCHASE_ID'].count().reset_index()

        # Plotting the number of purchases by department over time
        fig_department = px.line(purchases_by_department, x='PURCHASE_DATE', y='PURCHASE_ID', color='DEPARTMENT_NAME',
            title='Number of Purchases by Department Over Time',
            labels={'PURCHASE_DATE': 'Date', 'PURCHASE_ID': 'Number of Purchases'})
        st.plotly_chart(fig_department)


    def plot_purchases_by_department(self):
        st.write("## Number of Purchases by Department")
        # Merge purchase lines with product data
        merged_df = self.purchase_lines_df.merge(self.product_df, on='PRODUCT_ID')
        
        # Merge with purchase header to get purchase date
        merged_df = merged_df.merge(self.purchase_header_df[['PURCHASE_ID', 'PURCHASE_DATE_TIME']], on='PURCHASE_ID')
        
        # Extracting department name
        merged_df['DEPARTMENT_NAME'] = merged_df['DEPARTMENT_NAME'].str.capitalize()
        
        # Counting purchases by department
        purchases_by_department = merged_df.groupby('DEPARTMENT_NAME')['PURCHASE_ID'].count().sort_values(ascending=False)

        # Plotting the number of purchases by department
        fig = px.bar(x=purchases_by_department.index, y=purchases_by_department.values, labels={'x': 'Department', 'y': 'Number of Purchases'})
        fig.update_layout(title='Number of Purchases by Department', xaxis_title='Department', yaxis_title='Number of Purchases')
        st.plotly_chart(fig)


    def plots(self):
        st.title("Exploring the Data!")

        self.count_missing_values()
      
        # Common stats used
        stats = ['mean', 'min', 'max', 'std']
        columns = ['HEIGHT_INCHES', 'WIDTH_INCHES', 'DEPTH_INCHES', 'WEIGHT_GRAMS', 'VOLUME']

        agg_dict = {col: stats for col in columns}
        agg_dict['PRODUCT_ID'] = 'count'
        department_summary = self.product_df.groupby('DEPARTMENT_NAME').agg(agg_dict).reset_index()
        department_summary.columns = ['_'.join(col).strip() if col[1] else col[0] for col in department_summary.columns.values]
        rename_dict = {f'{col}_{stat}': f'{stat.capitalize()} {col.split("_")[0].capitalize()}' for col in columns for stat in stats}
        rename_dict['PRODUCT_ID_count'] = 'Count'
        department_summary.rename(columns=rename_dict, inplace=True)
        
        cols = ['DEPARTMENT_NAME', 'Count'] + [col for col in department_summary.columns if col not in ['DEPARTMENT_NAME', 'Count']]
        department_summary = department_summary[cols]


        st.header("Select from the drop down to see different visualizations, or you can see all of them as you scroll down")
        # Dropdown menu to select plots
        plot_functions = {
            "Product Dimension Correlation Heatmap": self.plot_correlation_heatmap,
            "Product Dimensions stats ": lambda: self.plot_interactive_bar(department_summary),
            "Top Products": self.plot_top_products,
            "Time vs Quantity Purchased": self.plot_quantity_analysis,
            "Hourly Products": self.plot_hourly_products,
            "Purchases Over Time": self.plot_purchase_over_time,
            "Purchases by Department": self.plot_purchases_by_department
        }

        # Dropdown menu for selecting plot
        plot_selection = st.selectbox("Select Plot", list(plot_functions.keys()))
        plot_functions[plot_selection]()

        st.markdown("""----""")

        self.plot_basic_stats()
        self.plot_categorical_summary()
        self.plot_correlation_heatmap()
        self.plot_interactive_bar(department_summary)
        self.plot_top_products()
        self.plot_quantity_analysis()
        self.plot_hourly_products()
        self.plot_purchase_over_time()
        self.plot_purchases_by_department()
