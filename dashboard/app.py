import streamlit as st

st.set_page_config(page_title="Analytics Dashboard", layout="wide")

st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Overview", "Trends", "Data Explorer"]
)

if page == "Overview":
    st.title("Business Overview")
    st.header("Executive KPI Summary")

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Revenue", "$5.2M", "+12.5%")
    with col2:
        st.metric("Active Customers", "2,500", "+5.2%")
    with col3:
        st.metric("Avg Order Value", "$145", "+3.1%")
    with col4:
        st.metric("Churn Rate", "4.8%", "-1.2%", delta_color="inverse")
    with col5:
        st.metric("Customer Satisfaction", "72", "+4")

    st.divider()
    st.header("Overview Details")
    st.subheader("Why this matters")
    st.write("A clear summary of the business health will be shown here, with top-level metrics that stakeholders need first.")

    with st.expander("About These Metrics"):
        st.write(
            "Revenue is shown for the current reporting window. "
            "Customer count and retention metrics are prioritized for executive review."
        )

elif page == "Trends":
    st.title("Trend Analysis")
    st.header("Revenue Trends")
    st.subheader("Monthly Revenue (Last 12 Months)")
    cols = st.columns(2)
    with cols[0]:
        st.write("Chart placeholder for revenue trend.")
    with cols[1]:
        st.write("Comparison placeholder for forecast and actual performance.")

    st.divider()
    st.header("Customer Metrics")
    st.subheader("Active Customers Over Time")
    with st.expander("Why these trends matter"):
        st.write(
            "Trend charts will show momentum, seasonality, and early warning signals for changes in customer engagement."
        )
    st.write("Chart placeholder for customer trend and churn comparison.")

elif page == "Data Explorer":
    st.title("Data Explorer")
    st.header("Filter and Inspect")
    st.subheader("Customer and Order Data")

    left, right = st.columns([2, 1])
    with left:
        st.write("Filters will appear here so users can narrow the dataset by segment, date, or status.")
    with right:
        st.write("Download and export controls will appear here.")

    st.divider()
    with st.expander("Additional details"):
        st.write(
            "This section will allow team members to explore raw data, export CSV files, and validate assumptions."
        )
    st.write("Data table placeholder for exploratory analysis.")
