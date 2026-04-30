import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Settings", layout="wide")

st.title("⚙️ System Settings")
st.write("---")

st.warning("### Database Controls")
st.write("Remove records or reset the entire system from here.")

conn = sqlite3.connect('inventory.db')
df = pd.read_sql_query("SELECT * FROM products", conn)
conn.close()

if not df.empty:
    item_to_del = st.selectbox("Select item to delete:", df['name'].tolist())
    if st.button("🗑️ Delete Selected"):
        conn = sqlite3.connect('inventory.db')
        curr = conn.cursor()
        curr.execute("DELETE FROM products WHERE name=?", (item_to_del,))
        conn.commit()
        conn.close()
        st.error(f"Removed {item_to_del} from records.")
        st.rerun()
else:
    st.info("No data to manage.")