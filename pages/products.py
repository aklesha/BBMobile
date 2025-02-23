import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Products - B&B Mobile", page_icon="📱")

st.title("Product Management")

# Product List
st.subheader("Current Products")

products = st.session_state.data_manager.get_products()

# Search and filter
col1, col2 = st.columns([2, 1])
with col1:
    search = st.text_input("Search Products")
with col2:
    category_filter = st.multiselect(
        "Filter by Category",
        products['category'].unique() if not products.empty else []
    )

filtered_products = products
if search:
    filtered_products = filtered_products[filtered_products['name'].str.contains(search, case=False)]
if category_filter:
    filtered_products = filtered_products[filtered_products['category'].isin(category_filter)]

# Display products in a table with sorting
if not filtered_products.empty:
    st.dataframe(
        filtered_products[['id', 'name', 'category', 'price', 'created_at']],
        use_container_width=True,
        hide_index=True,
        column_config={
            "id": "Product ID",
            "name": "Product Name",
            "category": "Category",
            "price": st.column_config.NumberColumn(
                "Price",
                format="$%.2f"
            ),
            "created_at": "Added Date"
        }
    )
else:
    st.info("No products found.")

# Add new product
st.subheader("Add New Product")
with st.form("add_product_form"):
    name = st.text_input("Product Name")
    category = st.selectbox(
        "Category",
        [
            "Phones - New",
            "Phones - Used",
            "Screen Protectors",
            "Phone Cases",
            "Chargers & Cables",
            "Batteries",
            "Memory Cards",
            "Screen Repair",
            "Battery Replacement",
            "Other Repairs",
            "Accessories",
            "Other"
        ]
    )
    col1, col2 = st.columns(2)
    with col1:
        price = st.number_input("Price", min_value=0.0, step=0.01)
    with col2:
        quantity = st.number_input("Initial Stock", min_value=0, value=1)

    notes = st.text_area("Product Notes", placeholder="Enter any additional details about the product...")

    submitted = st.form_submit_button("Add Product")
    if submitted:
        if name and price >= 0:
            st.session_state.data_manager.add_product(name, category, price, notes)
            st.success("Product added successfully!")
            st.rerun()
        else:
            st.error("Please fill in all required fields correctly.")

# Remove product
st.subheader("Remove Product")
if not products.empty:
    col1, col2 = st.columns([3, 1])
    with col1:
        product_to_remove = st.selectbox(
            "Select product to remove",
            products['id'].tolist(),
            format_func=lambda x: f"{products[products['id'] == x]['name'].iloc[0]} (ID: {x}) - ${products[products['id'] == x]['price'].iloc[0]:.2f}"
        )
    with col2:
        if st.button("Remove Selected Product", type="secondary"):
            if st.session_state.data_manager.remove_product(product_to_remove):
                st.success("Product removed successfully!")
                st.rerun()
            else:
                st.error("Cannot remove product - it has associated sales.")
else:
    st.info("No products available to remove.")

# Product Statistics
if not products.empty:
    st.subheader("Product Statistics")
    col1, col2, col3 = st.columns(3)

    with col1:
        total_products = len(products)
        st.metric("Total Products", total_products)

    with col2:
        categories_count = len(products['category'].unique())
        st.metric("Categories", categories_count)

    with col3:
        total_value = products['price'].sum()
        st.metric("Total Value", f"${total_value:,.2f}")