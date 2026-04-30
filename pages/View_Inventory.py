import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Analytics", layout="wide")

st.title("📊 Inventory Analytics")
st.write("---")

conn = sqlite3.connect('inventory.db')
df = pd.read_sql_query("SELECT * FROM products", conn)
conn.close()

if not df.empty:
    st.success(f"### Live Inventory Table (Total Items: {len(df)})")
    st.dataframe(df, use_container_width=True)

    st.write("---")
    st.success("### Visual Stock Analysis")
    st.bar_chart(df.set_index('name')['stock'])
else:
    st.warning("Inventory is empty. Please add items first.")