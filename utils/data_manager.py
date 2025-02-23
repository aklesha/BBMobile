import pandas as pd
import os
from datetime import datetime
import numpy as np
from functools import lru_cache
from typing import Optional

class DataManager:
    def __init__(self):
        self.data_dir = "data"
        self.ensure_data_files()
        self._cache_timestamp = datetime.now()

    def ensure_data_files(self):
        """Create data files if they don't exist"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

        files = {
            'products.csv': ['id', 'name', 'category', 'price', 'created_at', 'notes'],
            'sales.csv': ['id', 'product_id', 'quantity', 'price', 'date'],
            'expenses.csv': ['id', 'description', 'amount', 'date']
        }

        for file, columns in files.items():
            path = os.path.join(self.data_dir, file)
            if not os.path.exists(path):
                pd.DataFrame(columns=columns).to_csv(path, index=False)

    def _invalidate_cache(self):
        """Invalidate all cached data"""
        self._cache_timestamp = datetime.now()
        self.get_products.cache_clear()
        self.get_sales_data.cache_clear()
        self.get_expenses.cache_clear()

    def add_product(self, name: str, category: str, price: float, notes: str = "") -> int:
        """Add a new product with improved ID handling"""
        df = pd.read_csv(f"{self.data_dir}/products.csv")
        new_id = 1 if df.empty else df['id'].max() + 1

        new_product = pd.DataFrame({
            'id': [new_id],
            'name': [name],
            'category': [category],
            'price': [price],
            'created_at': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            'notes': [notes]
        })

        df = pd.concat([df, new_product], ignore_index=True)
        df.to_csv(f"{self.data_dir}/products.csv", index=False)
        self._invalidate_cache()
        return new_id

    def remove_product(self, product_id: int) -> bool:
        """Remove a product if it has no associated sales"""
        sales_df = pd.read_csv(f"{self.data_dir}/sales.csv")

        if not sales_df.empty and product_id in sales_df['product_id'].values:
            return False

        products_df = pd.read_csv(f"{self.data_dir}/products.csv")
        products_df = products_df[products_df['id'] != product_id]
        products_df.to_csv(f"{self.data_dir}/products.csv", index=False)
        self._invalidate_cache()
        return True

    @lru_cache(maxsize=1)
    def get_products(self) -> pd.DataFrame:
        """Get products with proper data types and caching"""
        df = pd.read_csv(f"{self.data_dir}/products.csv")
        if not df.empty:
            df['id'] = df['id'].astype(int)
            df['price'] = df['price'].astype(float)
            df['created_at'] = pd.to_datetime(df['created_at'])
        return df

    def add_sale(self, product_id: int, quantity: int, price: float) -> int:
        """Add a new sale record"""
        df = pd.read_csv(f"{self.data_dir}/sales.csv")
        new_id = len(df) + 1 if df.empty else df['id'].max() + 1
        new_sale = pd.DataFrame({
            'id': [new_id],
            'product_id': [product_id],
            'quantity': [quantity],
            'price': [price],
            'date': [datetime.now().strftime('%Y-%m-%d')]
        })
        df = pd.concat([df, new_sale], ignore_index=True)
        df.to_csv(f"{self.data_dir}/sales.csv", index=False)
        self._invalidate_cache()
        return new_id

    def remove_sale(self, sale_id: int) -> None:
        """Remove a sale record by its ID"""
        df = pd.read_csv(f"{self.data_dir}/sales.csv")
        df = df[df['id'] != sale_id]
        df.to_csv(f"{self.data_dir}/sales.csv", index=False)
        self._invalidate_cache()

    def add_expense(self, description: str, amount: float) -> None:
        """Add a new expense record"""
        df = pd.read_csv(f"{self.data_dir}/expenses.csv")
        new_id = len(df) + 1 if df.empty else df['id'].max() + 1
        new_expense = pd.DataFrame({
            'id': [new_id],
            'description': [description],
            'amount': [amount],
            'date': [datetime.now().strftime('%Y-%m-%d')]
        })
        df = pd.concat([df, new_expense], ignore_index=True)
        df.to_csv(f"{self.data_dir}/expenses.csv", index=False)
        self._invalidate_cache()

    @lru_cache(maxsize=1)
    def get_sales_data(self) -> pd.DataFrame:
        """Get sales data with product details and caching"""
        sales = pd.read_csv(f"{self.data_dir}/sales.csv")
        products = pd.read_csv(f"{self.data_dir}/products.csv")

        # Rename columns to avoid confusion after merge
        sales = sales.rename(columns={'price': 'sale_price', 'id': 'sale_id'})
        products = products.rename(columns={'price': 'product_price', 'id': 'product_id'})

        # Merge sales and products data
        merged_data = pd.merge(sales, products, on='product_id')
        return merged_data

    @lru_cache(maxsize=1)
    def get_expenses(self) -> pd.DataFrame:
        """Get expenses data with caching"""
        return pd.read_csv(f"{self.data_dir}/expenses.csv")