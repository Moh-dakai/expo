import streamlit as st
from data import (
    register_user, login_user,
    add_income, add_expense,
    get_expense_by_category, get_totals,
    get_income_data, get_expense_data, add_budget_goal
)

# Session state for login
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
    st.session_state.username = None

# Authentication Functions
def register_user_ui():
    st.subheader("Register")
    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    if st.button("Register"):
        success, message = register_user(username, email, password)
        if success:
            st.success(message)
        else:
            st.error(message)

def login_user_ui():
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        success, user_id = login_user(username, password)
        if success:
            st.session_state.user_id = user_id
            st.session_state.username = username
            st.success(f"Welcome, {username}!")
        else:
            st.error("Invalid credentials.")

# Core App Functions
def add_expense_ui():
    st.subheader("Add Expense")
    amount = st.number_input("Amount", min_value=0.01, step=0.01)
    category = st.text_input("Category")
    date = st.date_input("Date")
    note = st.text_area("Note (optional)")
    payment_method = st.text_input("Payment Method (optional)")
    if st.button("Add Expense"):
        add_expense(st.session_state.user_id, amount, category, date, note, payment_method)
        st.success("Expense added successfully.")

def add_income_ui():
    st.subheader("Add Income")
    amount = st.number_input("Amount", min_value=0.01, step=0.01)
    source = st.text_input("Source")
    date = st.date_input("Date")
    note = st.text_area("Note (optional)")
    if st.button("Add Income"):
        add_income(st.session_state.user_id, amount, source, date, note)
        st.success("Income added successfully.")

def view_expense_chart():
    st.subheader("Expense Chart")
    results = get_expense_by_category(st.session_state.user_id)
    if results:
        df = pd.DataFrame(results, columns=["Category", "Amount"])
        fig, ax = plt.subplots()
        ax.bar(df["Category"], df["Amount"], color='skyblue')
        ax.set_title("Expenses by Category")
        st.pyplot(fig)
    else:
        st.info("No expense data found.")

def view_budget_status():
    st.subheader("Budget Status")
    income_total, expense_total = get_totals(st.session_state.user_id)
    st.write(f"Total Income: ₦{income_total:.2f}")
    st.write(f"Total Expense: ₦{expense_total:.2f}")
    if expense_total > income_total:
        st.warning("Alert: Your expenses exceed your income!")

def add_budget_goal_ui():
    st.subheader("Set Budget Goal")
    category = st.text_input("Category")
    goal_amount = st.number_input("Goal Amount", min_value=0.01, step=0.01)
    if st.button("Save Goal"):
        add_budget_goal(st.session_state.user_id, category, goal_amount)
        st.success("Budget goal saved.")

def export_data():
    st.subheader("Export Data")
    expenses_df = get_expense_data(st.session_state.user_id)
    income_df = get_income_data(st.session_state.user_id)

    if st.button("Download CSV"):
        st.download_button("Download Expenses CSV", expenses_df.to_csv(index=False), "expenses.csv")
        st.download_button("Download Income CSV", income_df.to_csv(index=False), "income.csv")

# Main Navigation
st.title("NairaGhibli: Financial Tracker")

if st.session_state.user_id:
    st.sidebar.write(f"Logged in as: {st.session_state.username}")
    page = st.sidebar.radio("Navigation", [
        "Add Income", "Add Expense", "Expense Chart", "Budget Status",
        "Set Budget Goal", "Export Data", "Logout"])

    if page == "Add Income":
        add_income_ui()
    elif page == "Add Expense":
        add_expense_ui()
    elif page == "Expense Chart":
        view_expense_chart()
    elif page == "Budget Status":
        view_budget_status()
    elif page == "Set Budget Goal":
        add_budget_goal_ui()
    elif page == "Export Data":
        export_data()
    elif page == "Logout":
        st.session_state.user_id = None
        st.session_state.username = None
        st.experimental_rerun()
else:
    choice = st.selectbox("Choose Action", ["Login", "Register"])
    if choice == "Login":
        login_user_ui()
    elif choice == "Register":
        register_user_ui()
