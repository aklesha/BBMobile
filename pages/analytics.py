import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Analytics - B&B Mobile", page_icon="📱", layout="wide")

st.title("Analytics Dashboard")

# Date range selector
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input(
        "Start Date",
        datetime.now() - timedelta(days=30)
    )
with col2:
    end_date = st.date_input(
        "End Date",
        datetime.now()
    )

# Get data
sales_data = st.session_state.data_manager.get_sales_data()
expenses_data = st.session_state.data_manager.get_expenses()

# Convert dates
sales_data['date'] = pd.to_datetime(sales_data['date'])
expenses_data['date'] = pd.to_datetime(expenses_data['date'])

# Filter by date range
sales_mask = (sales_data['date'].dt.date >= start_date) & (sales_data['date'].dt.date <= end_date)
expenses_mask = (expenses_data['date'].dt.date >= start_date) & (expenses_data['date'].dt.date <= end_date)

filtered_sales = sales_data.loc[sales_mask]
filtered_expenses = expenses_data.loc[expenses_mask]

# Revenue Trends
st.subheader("Revenue Trends")
daily_revenue = filtered_sales.groupby('date')['sale_price'].sum().reset_index()
fig_revenue = px.line(
    daily_revenue,
    x='date',
    y='sale_price',
    title='Daily Revenue',
    labels={'sale_price': 'Revenue ($)', 'date': 'Date'}
)
st.plotly_chart(fig_revenue, use_container_width=True)

# Category Performance
st.subheader("Category Performance")
category_sales = filtered_sales.groupby('category').agg({
    'sale_price': 'sum',
    'sale_id': 'count'
}).reset_index()

col1, col2 = st.columns(2)

with col1:
    fig_category_revenue = px.pie(
        category_sales,
        values='sale_price',
        names='category',
        title='Revenue by Category'
    )
    st.plotly_chart(fig_category_revenue)

with col2:
    fig_category_count = px.pie(
        category_sales,
        values='sale_id',
        names='category',
        title='Number of Sales by Category'
    )
    st.plotly_chart(fig_category_count)

# Profit Analysis
st.subheader("Profit Analysis")

daily_profit = pd.DataFrame()
daily_profit['date'] = pd.date_range(start=start_date, end=end_date)
daily_profit['revenue'] = filtered_sales.groupby('date')['sale_price'].sum()
daily_profit['expenses'] = filtered_expenses.groupby('date')['amount'].sum()
daily_profit = daily_profit.fillna(0)
daily_profit['profit'] = daily_profit['revenue'] - daily_profit['expenses']

fig_profit = go.Figure()
fig_profit.add_trace(go.Bar(
    x=daily_profit['date'],
    y=daily_profit['revenue'],
    name='Revenue',
    marker_color='green'
))
fig_profit.add_trace(go.Bar(
    x=daily_profit['date'],
    y=daily_profit['expenses'],
    name='Expenses',
    marker_color='red'
))
fig_profit.add_trace(go.Scatter(
    x=daily_profit['date'],
    y=daily_profit['profit'],
    name='Net Profit',
    line=dict(color='blue', width=2)
))

fig_profit.update_layout(
    title='Daily Profit Analysis',
    xaxis_title='Date',
    yaxis_title='Amount ($)',
    barmode='group'
)

st.plotly_chart(fig_profit, use_container_width=True)

# Key Metrics
st.subheader("Key Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_revenue = filtered_sales['sale_price'].sum()
    st.metric("Total Revenue", f"${total_revenue:,.2f}")

with col2:
    total_expenses = filtered_expenses['amount'].sum()
    st.metric("Total Expenses", f"${total_expenses:,.2f}")

with col3:
    net_profit = total_revenue - total_expenses
    st.metric("Net Profit", f"${net_profit:,.2f}")

with col4:
    profit_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0
    st.metric("Profit Margin", f"{profit_margin:.1f}%")

# Top Products
st.subheader("Top Products")
top_products = filtered_sales.groupby('name').agg({
    'sale_price': 'sum',
    'quantity': 'sum'
}).reset_index().sort_values('sale_price', ascending=False).head(10)

fig_top_products = px.bar(
    top_products,
    x='name',
    y='sale_price',
    title='Top 10 Products by Revenue',
    labels={'sale_price': 'Revenue ($)', 'name': 'Product'}
)
st.plotly_chart(fig_top_products, use_container_width=True)