import streamlit as st
import pandas as pd

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
    st.header("Upload and Inspect Data")

    uploaded_file = st.file_uploader(
        "Upload your dataset", type=["csv", "json"], help="Supported formats: CSV, JSON"
    )

    df = None
    if uploaded_file is not None:
        try:
            if uploaded_file.name.lower().endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.lower().endswith(".json"):
                df = pd.read_json(uploaded_file)
            else:
                st.error("Unsupported file type. Please upload CSV or JSON.")
                st.stop()

            if df is None or len(df) == 0:
                st.warning("Uploaded file is empty.")
                st.stop()

            st.session_state["uploaded_df"] = df
            st.success(
                f"Loaded: {uploaded_file.name} ({len(df):,} rows, {len(df.columns):,} columns)"
            )
        except Exception:
            st.error("Could not read this file. Check the format and try again.")
            st.stop()

    elif "uploaded_df" in st.session_state:
        df = st.session_state["uploaded_df"]

    else:
        st.info("Upload a CSV or JSON file to begin.")

    if df is not None:
        st.sidebar.header("Filters")

        if {"date", "segment", "revenue"}.issubset(df.columns):
            df = df.copy()
            if not pd.api.types.is_datetime64_any_dtype(df["date"]):
                df["date"] = pd.to_datetime(df["date"], errors="coerce")

            df = df.dropna(subset=["date"])
            min_date = df["date"].min().date()
            max_date = df["date"].max().date()
            all_segments = sorted(df["segment"].dropna().unique().tolist())
            revenue_min = int(df["revenue"].min())
            revenue_max = int(df["revenue"].max())

            date_range = st.sidebar.date_input(
                "Date Range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
            )

            selected_segments = st.sidebar.multiselect(
                "Segments",
                options=all_segments,
                default=all_segments,
            )

            min_rev, max_rev = st.sidebar.slider(
                "Revenue Range",
                min_value=revenue_min,
                max_value=revenue_max,
                value=(revenue_min, revenue_max),
            )

            if st.sidebar.button("Reset Filters"):
                st.experimental_rerun()

            if isinstance(date_range, tuple) and len(date_range) == 2:
                start_date, end_date = date_range
            else:
                start_date = end_date = date_range

            filtered_df = df[
                (df["date"] >= pd.Timestamp(start_date))
                & (df["date"] <= pd.Timestamp(end_date))
                & (df["segment"].isin(selected_segments))
                & (df["revenue"] >= min_rev)
                & (df["revenue"] <= max_rev)
            ]

            if len(filtered_df) == 0:
                st.warning(
                    "No data matches the current filters. Try broadening your selection."
                )
                st.stop()

            st.divider()
            st.header("Filtered Dataset Preview")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Filtered Rows", f"{len(filtered_df):,}")
            with col2:
                st.metric("Original Rows", f"{len(df):,}")
            with col3:
                st.metric(
                    "Selected Segments",
                    str(len(selected_segments)) if selected_segments else "0",
                )

            st.write(f"Showing {len(filtered_df):,} of {len(df):,} records")
            st.dataframe(filtered_df.head(20), use_container_width=True)

            st.divider()
            st.header("Filtered Metrics")
            numeric_df = filtered_df.select_dtypes(include="number")
            if not numeric_df.empty:
                st.dataframe(numeric_df.describe(), use_container_width=True)
            else:
                st.info("No numeric columns found in the filtered dataset.")

            st.divider()
            st.header("Filtered Chart")
            if "revenue" in filtered_df.columns and "date" in filtered_df.columns:
                revenue_by_date = (
                    filtered_df.groupby(filtered_df["date"].dt.to_period("D"))["revenue"].sum().reset_index()
                )
                revenue_by_date["date"] = revenue_by_date["date"].dt.to_timestamp()
                st.line_chart(revenue_by_date.rename(columns={"date": "index"}).set_index("index"))
            else:
                st.info("Upload a dataset with date and revenue for charts.")

            st.divider()
            st.subheader("Column Summary")
            summary = pd.DataFrame({
                "Column": filtered_df.columns,
                "Type": filtered_df.dtypes.astype(str).values,
                "Non-Null": filtered_df.notnull().sum().values,
                "Null Count": filtered_df.isnull().sum().values,
                "Null %": (filtered_df.isnull().sum() / len(filtered_df) * 100).round(1).values,
            })
            st.dataframe(summary, use_container_width=True)

        else:
            st.info(
                "Upload a dataset with at least 'date', 'segment', and 'revenue' columns to enable filters."
            )
            st.divider()
            st.header("Dataset Preview")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Rows", f"{len(df):,}")
            with col2:
                st.metric("Columns", str(len(df.columns)))
            with col3:
                null_pct = (df.isnull().sum().sum() / (df.shape[0] * df.shape[1]) * 100) if df.size else 0.0
                st.metric("Null %", f"{null_pct:.1f}%")

            st.subheader("First 10 Rows")
            st.dataframe(df.head(10), use_container_width=True)

    st.divider()
    with st.expander("Additional details"):
        st.write(
            "This section allows team members to inspect uploaded data, review quality metrics, and start downstream analysis without manual preprocessing."
        )
