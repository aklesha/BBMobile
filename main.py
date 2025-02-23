import streamlit as st
from utils.data_manager import DataManager
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="B&B Mobile - Revenue Tracker",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced UI
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #0E1117 0%, #262730 100%);
    }
    .stMetric {
        background: rgba(255, 255, 255, 0.05);
        padding: 15px;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: all 0.3s ease;
    }
    .stMetric:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    .stButton button {
        background: linear-gradient(45deg, #FF4B4B 0%, #FF7676 100%);
        border: none;
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    .status-card {
        padding: 1rem;
        border-radius: 10px;
        background: rgba(255, 255, 255, 0.05);
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize DataManager
if 'data_manager' not in st.session_state:
    st.session_state.data_manager = DataManager()

# Main page header with animation
st.markdown("""
    <h1 style='text-align: center; color: #FF4B4B; margin-bottom: 2rem;'>
        📱 B&B Mobile Revenue Tracker
    </h1>
""", unsafe_allow_html=True)

# Dashboard Overview with enhanced metrics
col1, col2, col3, col4 = st.columns(4)

# Calculate key metrics
sales_data = st.session_state.data_manager.get_sales_data()
expenses_data = st.session_state.data_manager.get_expenses()

# Today's metrics
today = datetime.now().strftime('%Y-%m-%d')
today_sales = sales_data[sales_data['date'] == today]['sale_price'].sum() if not sales_data.empty else 0
total_revenue = sales_data['sale_price'].sum() if not sales_data.empty else 0
total_expenses = expenses_data['amount'].sum() if not expenses_data.empty else 0
net_profit = total_revenue - total_expenses

with col1:
    st.metric("Today's Sales", f"${today_sales:,.2f}", delta=None)

with col2:
    st.metric("Total Revenue", f"${total_revenue:,.2f}", delta=None)

with col3:
    st.metric("Total Expenses", f"${total_expenses:,.2f}", delta=None)

with col4:
    profit_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0
    st.metric("Net Profit", f"${net_profit:,.2f}", f"{profit_margin:.1f}%")

# Quick Actions Section
st.markdown("### 🚀 Quick Actions")

# Create three columns for quick actions
quick_col1, quick_col2, quick_col3 = st.columns(3)

with quick_col1:
    with st.container():
        st.markdown('<div class="status-card">', unsafe_allow_html=True)
        if st.button("➕ New Sale", use_container_width=True):
            st.session_state.action = "Add New Sale"
        st.markdown('</div>', unsafe_allow_html=True)

with quick_col2:
    with st.container():
        st.markdown('<div class="status-card">', unsafe_allow_html=True)
        if st.button("📦 Add Product", use_container_width=True):
            st.session_state.action = "Add New Product"
        st.markdown('</div>', unsafe_allow_html=True)

with quick_col3:
    with st.container():
        st.markdown('<div class="status-card">', unsafe_allow_html=True)
        if st.button("💰 Record Expense", use_container_width=True):
            st.session_state.action = "Record Expense"
        st.markdown('</div>', unsafe_allow_html=True)

# Quick Action Forms
if 'action' in st.session_state:
    st.markdown(f"### {st.session_state.action}")

    if st.session_state.action == "Add New Sale":
        with st.form("quick_sale_form"):
            products = st.session_state.data_manager.get_products()
            product_id = st.selectbox(
                "Select Product",
                products['id'].tolist(),
                format_func=lambda x: f"{products[products['id'] == x]['name'].iloc[0]} - ${products[products['id'] == x]['price'].iloc[0]:.2f}"
            )
            quantity = st.number_input("Quantity", min_value=1, value=1)
            price = st.number_input(
                "Price",
                min_value=0.0,
                value=float(products[products['id'] == product_id]['price'].iloc[0])
            )

            if st.form_submit_button("Record Sale"):
                sale_id = st.session_state.data_manager.add_sale(product_id, quantity, price)
                st.success(f"Sale #{sale_id} recorded successfully!")
                st.session_state.pop('action')
                st.rerun()

    elif st.session_state.action == "Add New Product":
        with st.form("quick_product_form"):
            name = st.text_input("Product Name")
            category = st.selectbox(
                "Category",
                ["Phones - New", "Phones - Used", "Screen Protectors", "Phone Cases",
                 "Chargers & Cables", "Batteries", "Memory Cards", "Screen Repair",
                 "Battery Replacement", "Other Repairs", "Accessories", "Other"]
            )
            price = st.number_input("Price", min_value=0.0, step=0.01)

            if st.form_submit_button("Add Product"):
                if name and price >= 0:
                    product_id = st.session_state.data_manager.add_product(name, category, price)
                    st.success(f"Product added successfully! (ID: {product_id})")
                    st.session_state.pop('action')
                    st.rerun()
                else:
                    st.error("Please fill in all required fields correctly.")

    elif st.session_state.action == "Record Expense":
        with st.form("quick_expense_form"):
            description = st.text_input("Expense Description")
            amount = st.number_input("Amount", min_value=0.0, step=0.01)

            if st.form_submit_button("Record Expense"):
                if description and amount > 0:
                    st.session_state.data_manager.add_expense(description, amount)
                    st.success("Expense recorded successfully!")
                    st.session_state.pop('action')
                    st.rerun()
                else:
                    st.error("Please fill in all required fields correctly.")

# Recent Activity Chart
if not sales_data.empty:
    st.markdown("### 📊 Recent Activity")

    # Last 7 days of sales
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)

    sales_data['date'] = pd.to_datetime(sales_data['date'])
    mask = (sales_data['date'] >= start_date) & (sales_data['date'] <= end_date)
    recent_sales = sales_data.loc[mask]

    if not recent_sales.empty:
        daily_sales = recent_sales.groupby('date')['sale_price'].sum().reset_index()
        fig = px.line(
            daily_sales,
            x='date',
            y='sale_price',
            title='Last 7 Days Sales',
            labels={'sale_price': 'Sales ($)', 'date': 'Date'}
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#FAFAFA'
        )
        st.plotly_chart(fig, use_container_width=True)