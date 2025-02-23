import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Sales - B&B Mobile", page_icon="📱")

# Custom CSS for mobile responsiveness
st.markdown("""
    <style>
    @media (max-width: 768px) {
        .stButton button {
            width: 100%;
            margin-bottom: 10px;
        }
        .row-widget {
            flex-direction: column;
        }
        [data-testid="stHorizontalBlock"] {
            flex-direction: column;
        }
        [data-testid="stHorizontalBlock"] > div {
            width: 100% !important;
            margin-bottom: 1rem;
        }
    }
    </style>
""", unsafe_allow_html=True)

st.title("Sales Management")

# Sales Entry
st.subheader("Record New Sale")
products = st.session_state.data_manager.get_products()

if products.empty:
    st.warning("No products available. Please add products first.")
else:
    with st.form("sales_entry_form"):
        product_id = st.selectbox(
            "Select Product",
            products['id'].tolist(),
            format_func=lambda x: f"{products[products['id'] == x]['name'].iloc[0]} - ${products[products['id'] == x]['price'].iloc[0]:.2f}"
        )

        # Get default price safely
        selected_product = products[products['id'] == product_id]
        default_price = float(selected_product['price'].iloc[0]) if not selected_product.empty else 0.0

        quantity = st.number_input("Quantity", min_value=1, value=1)
        price = st.number_input("Price", min_value=0.0, value=default_price)

        submitted = st.form_submit_button("Record Sale")
        if submitted:
            new_sale_id = st.session_state.data_manager.add_sale(product_id, quantity, price)
            st.success(f"Sale #{new_sale_id} recorded successfully!")
            st.rerun()

# Sales History
st.subheader("Sales History")

# Date filter
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

sales_data = st.session_state.data_manager.get_sales_data()

if sales_data.empty:
    st.info("No sales records found.")
else:
    # Filter by date
    sales_data['date'] = pd.to_datetime(sales_data['date'])
    mask = (sales_data['date'].dt.date >= start_date) & (sales_data['date'].dt.date <= end_date)
    filtered_sales = sales_data.loc[mask]

    if not filtered_sales.empty:
        # Display sales summary
        total_sales = filtered_sales['sale_price'].sum()
        total_items = filtered_sales['quantity'].sum()

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Sales", f"${total_sales:,.2f}")
        with col2:
            st.metric("Items Sold", int(total_items))

        # Display detailed sales table
        st.dataframe(
            filtered_sales[['sale_id', 'date', 'name', 'category', 'quantity', 'sale_price']],
            use_container_width=True,
            hide_index=True,
            column_config={
                "sale_id": "Sale ID",
                "date": "Date",
                "name": "Product",
                "category": "Category",
                "quantity": "Quantity",
                "sale_price": st.column_config.NumberColumn(
                    "Price",
                    format="$%.2f"
                )
            }
        )

        # Remove sale section
        with st.expander("Remove Sale"):
            sale_to_remove = st.selectbox(
                "Select sale to remove",
                filtered_sales['sale_id'].tolist(),
                format_func=lambda x: f"Sale #{x} - {filtered_sales[filtered_sales['sale_id'] == x]['name'].iloc[0]} - ${filtered_sales[filtered_sales['sale_id'] == x]['sale_price'].iloc[0]:.2f}"
            )

            if st.button("Remove Selected Sale", type="secondary"):
                st.session_state.data_manager.remove_sale(sale_to_remove)
                st.success(f"Sale #{sale_to_remove} removed successfully!")
                st.rerun()

        # Export option
        if st.button("Export to CSV"):
            filtered_sales.to_csv("sales_export.csv", index=False)
            st.success("Sales data exported to sales_export.csv")
    else:
        st.info("No sales data for the selected period.")