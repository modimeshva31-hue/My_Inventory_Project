import streamlit as st
import sqlite3

st.set_page_config(page_title="Add Stock", layout="wide")

st.title("➕ Stock Management")
st.write("---")

# બ્લુ કલરનું કાર્ડ લુક આપવા માટે
st.info("### Register New Product")
st.write("Fill in the details below to update your inventory.")

with st.form("add_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Product Name")
        price = st.number_input("Unit Price (₹)", min_value=0.0)
    with col2:
        stock = st.number_input("Initial Quantity", min_value=0)
    
    submit = st.form_submit_button("🚀 Save to Database")

    if submit:
        if name:
            conn = sqlite3.connect('inventory.db')
            curr = conn.cursor()
            curr.execute("INSERT INTO products (name, price, stock) VALUES (?,?,?)", (name, price, stock))
            conn.commit()
            conn.close()
            st.success(f"Done! {name} has been added successfully.")
        else:
            st.error("Please enter a product name.")