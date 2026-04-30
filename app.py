import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from auth import hash_password, check_password

# --- 1. INITIALIZE SESSION STATE ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user' not in st.session_state:
    st.session_state['user'] = ""

st.set_page_config(page_title="Inventory & Sales Pro", layout="wide")

# --- 2. GLOBAL THEME CSS ---
st.markdown("""
    <style>
        .stApp { background-color: #F6F4E8; color: #4A4A4A; }
        [data-testid="stSidebar"] { background-color: #C0E1D2 !important; }
        .stForm, div[data-testid="stExpander"], .stTabs {
            background: #FFFFFF !important;
            border: 2px solid #DC9B9B !important;
            border-radius: 15px !important;
            padding: 20px;
        }
        div.stButton > button {
            background-color: #DC9B9B !important;
            color: white !important;
            border-radius: 10px;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# --- 3. DATABASE SETUP ---
def init_db():
    conn_inv = sqlite3.connect('inventory.db')
    curr = conn_inv.cursor()
    curr.execute('CREATE TABLE IF NOT EXISTS products (name TEXT, price REAL, stock INTEGER)')
    curr.execute('CREATE TABLE IF NOT EXISTS sales (product_name TEXT, quantity INTEGER, total_price REAL, date TEXT)')
    conn_inv.commit()
    conn_inv.close()

    conn_user = sqlite3.connect('users.db')
    curr_u = conn_user.cursor()
    curr_u.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT, password TEXT)')
    conn_user.commit()
    conn_user.close()

init_db()

# --- 4. AUTHENTICATION UI ---
if not st.session_state['logged_in']:
    st.markdown("<h1 style='text-align: center; margin-top: 50px;'>🌐 Digital Business Portal</h1>", unsafe_allow_html=True)
    st.markdown("<style>section[data-testid='stSidebar'] {display: none;}</style>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["🔒 Login", "📝 Create Account"])
        
        with tab1:
            email = st.text_input("Email", placeholder="Enter your email")
            password = st.text_input("Password", type='password')
            if st.button("Log In"):
                conn = sqlite3.connect('users.db')
                curr = conn.cursor()
                curr.execute('SELECT password FROM userstable WHERE username =?', (email,))
                user_data = curr.fetchone()
                conn.close()
                
                if user_data and check_password(password, user_data[0]):
                    st.session_state['logged_in'] = True
                    st.session_state['user'] = email
                    st.success("Login Successful!")
                    st.rerun()
                else:
                    st.error("Invalid Email or Password")
                    
        with tab2:
            new_email = st.text_input("New Email")
            new_pass = st.text_input("New Password", type='password')
            confirm_pass = st.text_input("Confirm Password", type='password')
            if st.button("Register Now"):
                if new_pass == confirm_pass and new_email != "":
                    conn = sqlite3.connect('users.db')
                    curr = conn.cursor()
                    hashed_pass = hash_password(new_pass)
                    curr.execute('INSERT INTO userstable VALUES (?,?)', (new_email, hashed_pass))
                    conn.commit()
                    conn.close()
                    st.success("Account Created! Please log in.")
                else:
                    st.error("Passwords do not match or fields are empty")

# --- 5. MAIN APPLICATION (LOGGED IN) ---
else:
    st.sidebar.markdown(f"### 👤 {st.session_state['user'].split('@')[0].capitalize()}")
    main_menu = st.sidebar.selectbox("Go To:", ["🏠 Dashboard", "📦 Inventory", "🛒 Sales", "⚙️ Settings"])
    
    if st.sidebar.button("🚪 Logout"):
        st.session_state['logged_in'] = False
        st.rerun()

    if main_menu == "🏠 Dashboard":
        st.title("🚀 Business Overview")
        conn = sqlite3.connect('inventory.db')
        col1, col2, col3 = st.columns(3)
        
        total_p = pd.read_sql_query("SELECT COUNT(*) as count FROM products", conn).iloc[0]['count']
        sales_df = pd.read_sql_query("SELECT SUM(total_price) as total FROM sales", conn)
        total_revenue = sales_df.iloc[0]['total'] if sales_df.iloc[0]['total'] else 0
        low_stock_df = pd.read_sql_query("SELECT * FROM products WHERE stock < 5", conn)

        col1.metric("Total Products", total_p)
        col2.metric("Total Revenue", f"₹{total_revenue:,.2f}")
        col3.metric("Low Stock Alerts", len(low_stock_df))

        col3.metric("Low Stock Alerts", len(low_stock_df))

        # --- ૧.  New graph ---
        st.markdown("### 📈 Inventory Stock Levels")
        chart_data = pd.read_sql_query("SELECT name, stock FROM products", conn)
        if not chart_data.empty:
            st.bar_chart(chart_data.set_index('name')) 

        # --- ૨.  old graph ---
        st.markdown("### 📊 Recent Inventory Status")
        st.dataframe(pd.read_sql_query("SELECT * FROM products", conn), use_container_width=True)
        
        conn.close()

    elif main_menu == "📦 Inventory":
        st.title("Inventory Control")
        sub_opt = st.radio("Select Action:", ["View All", "Add New", "Remove Product"], horizontal=True)
        conn = sqlite3.connect('inventory.db')
        curr = conn.cursor()

        if sub_opt == "View All":
            st.dataframe(pd.read_sql_query("SELECT * FROM products", conn), use_container_width=True)
        elif sub_opt == "Add New":
            with st.form("add_form"):
                n = st.text_input("Name")
                p = st.number_input("Price", min_value=0.0)
                q = st.number_input("Stock", min_value=0)
                if st.form_submit_button("Save"):
                    curr.execute("INSERT INTO products VALUES (?,?,?)", (n, p, q))
                    conn.commit()
                    st.success("Added!")
                    st.rerun()
        conn.close()

    elif main_menu == "🛒 Sales":
        st.title("Sales Operations")
        conn = sqlite3.connect('inventory.db')
        curr = conn.cursor()
        products_df = pd.read_sql_query("SELECT name, price, stock FROM products", conn)
        
        with st.form("sale_form"):
            p_name = st.selectbox("Select Product", products_df['name'].tolist())
            s_qty = st.number_input("Quantity", min_value=1)
            if st.form_submit_button("Complete Sale"):
                p_info = products_df[products_df['name'] == p_name].iloc[0]
                if s_qty <= p_info['stock']:
                    total = s_qty * p_info['price']
                    dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    curr.execute("INSERT INTO sales VALUES (?,?,?,?)", (p_name, s_qty, total, dt))
                    curr.execute("UPDATE products SET stock = stock - ? WHERE name = ?", (s_qty, p_name))
                    conn.commit()
                    st.success(f"Sold! Total: ₹{total}")
                    st.rerun()
        conn.close()

    elif main_menu == "⚙️ Settings":
        st.title("Settings")
        with st.form("settings_form"):
            st.write(f"User: {st.session_state['user']}")
            new_p = st.text_input("New Password", type="password")
            if st.form_submit_button("Update Password"):
                hashed_p = hash_password(new_p)
                conn = sqlite3.connect('users.db')
                curr = conn.cursor()
                curr.execute('UPDATE userstable SET password = ? WHERE username = ?', (hashed_p, st.session_state['user']))
                conn.commit()
                conn.close()
                st.success("Password Updated!")