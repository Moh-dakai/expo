import streamlit as st
import pandas as pd
import os
from datetime import datetime
import pymysql
import matplotlib.pyplot as plt
from dotenv import load_dotenv

# Load environment variables
load_dotenv("cre.env")

# Connect to MySQL
connection = pymysql.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)
cursor = connection.cursor()

# Session state for login
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
    st.session_state.username = None

# Helper Functions
def register_user():
    st.subheader("Register")
    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    if st.button("Register"):
        if password != confirm_password:
            st.error("Passwords do not match.")
            return
        cursor.execute("SELECT * FROM users WHERE username=%s OR user_email=%s", (username, email))
        if cursor.fetchone():
            st.error("Username or email already exists.")
        else:
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                "INSERT INTO users (username, user_email, password, created_at, last_login) VALUES (%s, %s, %s, %s, %s)",
                (username, email, password, created_at, None))
            connection.commit()
            st.success("Registration successful! Please login.")

def login_user():
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        cursor.execute("SELECT user_id FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        if user:
            st.session_state.user_id = user[0]
            st.session_state.username = username
            last_login = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("UPDATE users SET last_login=%s WHERE user_id=%s", (last_login, st.session_state.user_id))
            connection.commit()
            st.success(f"Welcome, {username}!")
        else:
            st.error("Invalid credentials.")

def add_expense():
    st.subheader("Add Expense")
    amount = st.number_input("Amount", min_value=0.01, step=0.01)
    category = st.text_input("Category")
    date = st.date_input("Date")
    note = st.text_area("Note (optional)")
    payment_method = st.text_input("Payment Method (optional)")
    if st.button("Add Expense"):
        cursor.execute("""
            INSERT INTO expense (user_id, amount, category, date, note, payment_method)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (st.session_state.user_id, amount, category, date, note, payment_method))
        connection.commit()
        st.success("Expense added successfully.")

def add_income():
    st.subheader("Add Income")
    amount = st.number_input("Amount", min_value=0.01, step=0.01, key="income_amount")
    source = st.text_input("Source")
    date = st.date_input("Date", key="income_date")
    note = st.text_area("Note (optional)", key="income_note")
    if st.button("Add Income"):
        cursor.execute("""
            INSERT INTO income (user_id, amount, source, date, note)
            VALUES (%s, %s, %s, %s, %s)
        """, (st.session_state.user_id, amount, source, date, note))
        connection.commit()
        st.success("Income added successfully.")

def view_expense_chart():
    st.subheader("Expense Chart")
    cursor.execute("""
        SELECT category, SUM(amount) FROM expense
        WHERE user_id=%s GROUP BY category
    """, (st.session_state.user_id,))
    results = cursor.fetchall()
    if results:
        df = pd.DataFrame(results, columns=["Category", "Amount"])
        fig, ax = plt.subplots()
        ax.bar(df["Category"], df["Amount"], color='skyblue')
        ax.set_title("Expenses by Category")
        ax.set_ylabel("Amount")
        ax.set_xlabel("Category")
        st.pyplot(fig)
    else:
        st.info("No expense data found.")

def view_budget_status():
    st.subheader("Budget Status")
    cursor.execute("""
        SELECT
            (SELECT IFNULL(SUM(amount), 0) FROM income WHERE user_id = %s),
            (SELECT IFNULL(SUM(amount), 0) FROM expense WHERE user_id = %s)
    """, (st.session_state.user_id, st.session_state.user_id))
    income_total, expense_total = cursor.fetchone()
    st.write(f"Total Income: ${income_total:.2f}")
    st.write(f"Total Expense: ${expense_total:.2f}")
    if expense_total > income_total:
        st.warning("Alert: Your expenses exceed your income!")

# Main Navigation
st.title("NairaGhibli: Financial Tracker")

if st.session_state.user_id:
    st.sidebar.write(f"Logged in as: {st.session_state.username}")
    page = st.sidebar.radio("Navigation", ["Add Income", "Add Expense", "Expense Chart", "Budget Status", "Logout"])
    if page == "Add Income":
        add_income()
    elif page == "Add Expense":
        add_expense()
    elif page == "Expense Chart":
        view_expense_chart()
    elif page == "Budget Status":
        view_budget_status()
    elif page == "Logout":
        st.session_state.user_id = None
        st.session_state.username = None
        st.experimental_rerun()
else:
    choice = st.selectbox("Choose Action", ["Login", "Register"])
    if choice == "Login":
        login_user()
    elif choice == "Register":
        register_user()
