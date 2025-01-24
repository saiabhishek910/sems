import streamlit as st
import pandas as pd
from openpyxl import load_workbook
from datetime import date

# Define the Excel file path
EXCEL_FILE = "daily_data.xlsx"

# Ensure the Excel file exists with required columns
try:
    df = pd.read_excel(EXCEL_FILE)
except FileNotFoundError:
    df = pd.DataFrame(columns=["Month", "Category", "Amount", "Season"])
    df.to_excel(EXCEL_FILE, index=False)

# Sidebar for Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Data Entry", "Graphical Reports"])

# Data Entry Page
if page == "Data Entry":
    st.title("Data Entry")
    
    # Input Fields
    with st.form("entry_form"):
        col1, col2 = st.columns(2)
        month = col1.selectbox("Select Month", range(1, 13), format_func=lambda x: date(1900, x, 1).strftime('%B'))
        category = col2.selectbox("Category", ["Electricity"])
        amount = st.number_input("Amount", min_value=0.0, step=0.1, format="%.2f")
        description = st.text_input("Description", "")
        
        # Submit Button
        submitted = st.form_submit_button("Submit")
        
        if submitted:
            # Add data to Excel
            new_data = {"Month": month, "Category": category, "Amount": amount, "Description": description}
            df = pd.read_excel(EXCEL_FILE)
            df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
            df.to_excel(EXCEL_FILE, index=False)
            st.success("Data added successfully!")
            st.write(new_data)

# Daily Reports Page
elif page == "Graphical Reports":
    st.title("Monthly Reports")
    
    # Load Data
    try:
        df = pd.read_excel(EXCEL_FILE)
    except Exception as e:
        st.error("Error reading the Excel file. Please ensure the file is properly formatted.")
        st.stop()
    
    if df.empty:
        st.warning("No data available in the file.")
        st.stop()
    
    # Ensure Month column is numeric
    df["Month"] = pd.to_numeric(df["Month"], errors="coerce")
    
    # Filter Data by Month
    col1, col2 = st.columns(2)
    start_month = col1.selectbox("Start Month", range(1, 13), format_func=lambda x: date(1900, x, 1).strftime('%B'))
    end_month = col2.selectbox("End Month", range(1, 13), format_func=lambda x: date(1900, x, 1).strftime('%B'))
    
    # Filtered Data
    mask = (df["Month"] >= start_month) & (df["Month"] <= end_month)
    filtered_data = df[mask]
    
    if filtered_data.empty:
        st.warning("No data found for the selected month range.")
    else:
        # Display Data
        st.subheader("Filtered Data")
        st.write(filtered_data)
        
        # Summary Table
        st.subheader("Summary by Category")
        summary = filtered_data.groupby("Category")["Amount"].sum().reset_index()
        st.table(summary)
        
        # Plotting
        st.subheader("Monthly Totals")
        monthly_totals = filtered_data.groupby("Month")["Amount"].sum().reset_index()
        monthly_totals["Month_Name"] = monthly_totals["Month"].apply(lambda x: date(1900, x, 1).strftime('%B'))
        st.bar_chart(monthly_totals.set_index("Month_Name")["Amount"])


