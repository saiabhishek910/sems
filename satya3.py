import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
from sklearn.linear_model import LinearRegression
import numpy as np

# Excel file paths
EXCEL_BILLS = "monthly_bills.xlsx"
EXCEL_APPLIANCE_DATA = "appliance_data.xlsx"

# Function to send an email
def send_email(subject, body, receiver_email):
    sender_email = "v647414@gmail.com"  # Replace with your email
    sender_password = "kmmz ktrc tgnt ovvf"  # Replace with your App Password

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
            st.success(f"Email alert sent successfully to {receiver_email}!")
    except Exception as e:
        st.error(f"Error sending email: {e}")

# Function to initialize Excel files
def initialize_excel(file, columns):
    try:
        return pd.read_excel(file)
    except FileNotFoundError:
        df = pd.DataFrame(columns=columns)
        df.to_excel(file, index=False)
        return df

# Initialize files
bills_df = initialize_excel(EXCEL_BILLS, ["Month", "Category", "Amount", "Description", "Type"])  # Add 'Type'
appliance_data_df = initialize_excel(EXCEL_APPLIANCE_DATA, ["Item", "Kilovolts (kV)", "Start Time", "Max Limit (kV)", "Total Volts", "Email"])

# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Data Entry for Bills", "Graphical Reports", "Appliance Voltage Monitoring", "Electricity Bill Prediction"])

# ---- DATA ENTRY SECTION ----
if page == "Data Entry for Bills":
    st.title("Monthly Bills - Data Entry")
    with st.form("bills_form"):
        col1, col2 = st.columns(2)
        month = col1.selectbox("Select Month", range(1, 13), format_func=lambda x: date(1900, x, 1).strftime('%B'))
        category = col2.selectbox("Category", ["Electricity", "Water", "Internet", "Gas", "Other"])
        bill_type = st.selectbox("Type", ["Household", "Business"])  # New field for Type
        amount = st.number_input("Amount (₹)", min_value=0.0, step=0.1, format="%.2f")
        description = st.text_area("Description", placeholder="Enter any additional notes")

        submitted = st.form_submit_button("Add Bill")
        if submitted:
            if amount > 0:
                new_data = {"Month": month, "Category": category, "Amount": amount, "Description": description, "Type": bill_type}  # Include 'Type'
                bills_df = pd.concat([bills_df, pd.DataFrame([new_data])], ignore_index=True)
                bills_df.to_excel(EXCEL_BILLS, index=False)
                st.success("Bill data added successfully!")
                st.write(new_data)
            else:
                st.error("Amount must be greater than zero!")

# ---- GRAPHICAL REPORTS SECTION ----
# ---- GRAPHICAL REPORTS SECTION ----
# ---- GRAPHICAL REPORTS SECTION ----
# ---- GRAPHICAL REPORTS SECTION ----
elif page == "Graphical Reports":
    st.title("Graphical Reports - Monthly Bills")
    try:
        bills_df = pd.read_excel(EXCEL_BILLS)
        if bills_df.empty:
            st.warning("No data available. Please enter bill data first.")
        else:
            # Display the data
            st.subheader("All Bills Data")

            # Sort the data by 'Month' to ensure chronological order
            bills_df = bills_df.sort_values(by="Month", ascending=True)

            st.write(bills_df)

            # Grouping data by Month and Type
            bills_df["Month_Name"] = bills_df["Month"].apply(lambda x: date(1900, x, 1).strftime('%B'))
            household_data = bills_df[bills_df["Type"] == "Household"]
            business_data = bills_df[bills_df["Type"] == "Business"]

            # Group by month for Household
            monthly_household_totals = household_data.groupby("Month_Name")["Amount"].sum().reset_index()

            # Group by month for Business
            monthly_business_totals = business_data.groupby("Month_Name")["Amount"].sum().reset_index()

            # Sort the grouped data by month to ensure chronological order
            monthly_household_totals["Month_Name"] = pd.to_datetime(monthly_household_totals["Month_Name"], format='%B').dt.month
            monthly_business_totals["Month_Name"] = pd.to_datetime(monthly_business_totals["Month_Name"], format='%B').dt.month

            # Sort the data by the month number
            monthly_household_totals = monthly_household_totals.sort_values(by="Month_Name")
            monthly_business_totals = monthly_business_totals.sort_values(by="Month_Name")

            # Convert month numbers back to month names
            monthly_household_totals["Month_Name"] = monthly_household_totals["Month_Name"].apply(lambda x: date(1900, x, 1).strftime('%B'))
            monthly_business_totals["Month_Name"] = monthly_business_totals["Month_Name"].apply(lambda x: date(1900, x, 1).strftime('%B'))

            # Display Summary Table for Household (sorted)
            st.subheader("Monthly Total Bills - Household")
            st.table(monthly_household_totals)

            # Display Summary Table for Business (sorted)
            st.subheader("Monthly Total Bills - Business")
            st.table(monthly_business_totals)

            # Bar Chart for Household (sorted)
            st.subheader("Monthly Bills Overview - Household")
            st.bar_chart(monthly_household_totals.set_index("Month_Name")["Amount"])

            # Bar Chart for Business (sorted)
            st.subheader("Monthly Bills Overview - Business")
            st.bar_chart(monthly_business_totals.set_index("Month_Name")["Amount"])

    except Exception as e:
        st.error(f"Error loading reports: {e}")


# ---- APPLIANCE VOLTAGE MONITORING SECTION ----
elif page == "Appliance Voltage Monitoring":
    st.title("Appliance Voltage Monitoring with Email Alerts")
    
    # Form for Appliance Entry
    with st.form("appliance_form"):
        st.subheader("Enter Appliance Details")
        item = st.text_input("Appliance Name (e.g., Fan, AC, TV):", placeholder="Enter appliance name")
        kilovolts = st.number_input("Kilovolts (kV):", min_value=0.0, step=0.1)
        start_time = st.time_input("Start Time")
        max_limit = st.number_input("Daily Voltage Limit (kV):", min_value=0.0, step=0.1)
        email = st.text_input("Email for Alerts", placeholder="Enter email for voltage alerts")

        submitted = st.form_submit_button("Save Appliance Data")
        if submitted and item and email:
            new_data = {
                "Item": item,
                "Kilovolts (kV)": kilovolts,
                "Start Time": start_time.strftime("%H:%M"),
                "Max Limit (kV)": max_limit,
                "Total Volts": 0,
                "Email": email
            }
            appliance_data_df = pd.concat([appliance_data_df, pd.DataFrame([new_data])], ignore_index=True)
            appliance_data_df.to_excel(EXCEL_APPLIANCE_DATA, index=False)
            st.success(f"Appliance data for '{item}' saved successfully!")

    # Automatic Monitoring Loop
    st.subheader("Monitoring Appliances...")
    progress_bar = st.progress(0)

    for i in range(5):  # Number of auto-refresh cycles
        for index, row in appliance_data_df.iterrows():
            item = row["Item"]
            kilovolts = row["Kilovolts (kV)"]
            start_time_str = row["Start Time"]
            max_limit = row["Max Limit (kV)"]
            email = row["Email"]

            # Calculate total hours since the start time
            today = datetime.today()
            start_time = datetime.strptime(start_time_str, "%H:%M")
            start_datetime = datetime.combine(today, start_time.time())
            current_time = datetime.now()
            total_hours = max((current_time - start_datetime).total_seconds() / 3600, 0)  # Ensure non-negative
            total_volts = round(kilovolts * total_hours, 2)

            # Send email if the limit is exceeded
            if total_volts > max_limit:
                subject = f"⚠️Voltage Limit Exceeded for {item}⚠️"
                body = f"Warning! {item} exceeded its daily voltage limit.\nTotal Volts: {total_volts} kV\nLimit: {max_limit} kV\nPlease Turn Off Your {item}"
                send_email(subject, body, email)
                st.warning(f"Alert: {item} exceeded its limit! Email sent to {email}.")

            # Update Total Volts
            appliance_data_df.at[index, "Total Volts"] = total_volts
            appliance_data_df.to_excel(EXCEL_APPLIANCE_DATA, index=False)

        progress_bar.progress((i + 1) / 5)
        time.sleep(1800)  # Pause 10 seconds before the next refresh cycle
        st.rerun()  # Auto-refresh Streamlit app

# ---- ELECTRICITY BILL PREDICTION SECTION ----
elif page == "Electricity Bill Prediction":
    st.title("Electricity Bill Prediction")

    try:
        # Load data
        bills_df = pd.read_excel(EXCEL_BILLS)
        electricity_data = bills_df[bills_df['Category'] == 'Electricity']

        if electricity_data.empty:
            st.warning("No electricity bill data available. Please enter data first.")
        else:
            # Prepare the features (X) and target (y)
            X = electricity_data[['Month']].values  # Month as the independent variable
            y = electricity_data['Amount'].values  # Amount as the dependent variable

            # Train a linear regression model
            model = LinearRegression()
            model.fit(X, y)

            # Predict the amount for the next month
            next_month = np.array([[electricity_data['Month'].max() + 1]])
            predicted_amount = model.predict(next_month)

            # Separate predictions for Household and Business
            household_data = electricity_data[electricity_data["Type"] == "Household"]
            business_data = electricity_data[electricity_data["Type"] == "Business"]

            # Predicted Amount for Household
            X_household = household_data[['Month']].values
            y_household = household_data['Amount'].values
            model_household = LinearRegression()
            model_household.fit(X_household, y_household)
            predicted_household = model_household.predict(np.array([[household_data['Month'].max() + 1]]))

            # Predicted Amount for Business
            X_business = business_data[['Month']].values
            y_business = business_data['Amount'].values
            model_business = LinearRegression()
            model_business.fit(X_business, y_business)
            predicted_business = model_business.predict(np.array([[business_data['Month'].max() + 1]]))

            # Calculate the units consumed
            units_household = predicted_household[0] / 1.5  # ₹1.5 per unit
            units_business = predicted_business[0] / 2  # ₹2 per unit

            st.subheader("Prediction Result")
            st.write(f"Predicted Electricity Bill for Household for Month {next_month[0][0]} is expected to be: ₹{abs(int(predicted_household[0]))}")
            st.write(f"Units Consumed by Household for Month {next_month[0][0]} is expected to be: {abs(round(units_household, 2))} units")

            st.write(f"Predicted Electricity Bill for Business for Month {next_month[0][0]} is expected to be: ₹{abs(int(predicted_business[0]))}")
            st.write(f"Units Consumed by Business for Month {next_month[0][0]} is expected to be: {abs(round(units_business, 2))} units")

    except Exception as e:
        st.error(f"Error in prediction: {e}")
