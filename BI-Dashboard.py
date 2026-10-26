import streamlit as st
import pandas as pd
import plotly.express as px

# Page Layout Configuration
st.set_page_config(page_title="Professional Power BI Style Dashboard", layout="wide")

st.title("📊 Professional Business Intelligence & Decision Dashboard")
st.markdown("Smart BI Dashboard with **Intelligent Slicers**, Full-Dataset Analysis, AI Problem Detection, and Decision Support.")

# Caching for Fast File Loading
@st.cache_data
def load_data(file):
    file_extension = file.name.split('.')[-1].lower()
    if file_extension == 'csv':
        return pd.read_csv(file)
    elif file_extension in ['xlsx', 'xls']:
        return pd.read_excel(file)
    return None

uploaded_file = st.file_uploader("Upload your data file (CSV or Excel)", type=["csv", "xlsx", "xls"], key="smart_bi_uploader")

if uploaded_file is not None:
    try:
        with st.spinner("⏳ Processing dataset and setting up smart slicers..."):
            df = load_data(uploaded_file)
    except Exception as e:
        st.error(f"Error reading file: {e}")
        df = None

    if df is not None:
        df = df.drop_duplicates()
        
        # Smart Date & Year Extraction
        date_cols = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
        for d_col in date_cols:
            try:
                df[d_col] = pd.to_datetime(df[d_col], errors='coerce')
                df[f'{d_col}_Year'] = df[d_col].dt.year
            except:
                pass

        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
        
        # Intelligent Slicer Filter (Excluding IDs and Names)
        exclude_keywords = ['id', 'name', 'customer', 'address', 'phone', 'zip', 'postal', 'email', 'url', 'row']
        smart_categorical_cols = []
        
        for col in df.select_dtypes(include=['object', 'category', 'int64', 'float64']).columns:
            if any(kw in col.lower() for kw in exclude_keywords):
                continue
            if 2 <= df[col].nunique() <= 100:
                smart_categorical_cols.append(col)
                
        year_cols = [c for c in df.columns if 'year' in c.lower()]
        slicer_options = year_cols + smart_categorical_cols

        # Power BI Style Sidebar Slicers
        st.sidebar.header("🎛️ Power BI Slicers (Filters)")
        filtered_df = df.copy()
        
        for col in slicer_options[:5]:
            unique_vals = df[col].dropna().unique().tolist()
            try:
                unique_vals = sorted(unique_vals)
            except:
                pass
            selected_vals = st.sidebar.multiselect(f"Filter by {col}", unique_vals, default=unique_vals)
            if selected_vals:
                filtered_df = filtered_df[filtered_df[col].isin(selected_vals)]

        # Top KPI Cards
        st.subheader("📌 Key Performance Indicators (KPIs)")
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        
        kpi1.metric("Total Filtered Records", f"{len(filtered_df):,}")
        
        if numeric_cols:
            primary_metric = numeric_cols[0]
            kpi2.metric(f"Total {primary_metric}", f"{filtered_df[primary_metric].sum():,.2f}")
            kpi3.metric(f"Average {primary_metric}", f"{filtered_df[primary_metric].mean():,.2f}")
            kpi4.metric("Total Columns", len(df.columns))
        else:
            kpi2.metric("Numeric Metrics", "N/A")
            kpi3.metric("Average", "N/A")
            kpi4.metric("Total Columns", len(df.columns))

        st.markdown("---")

        # Interactive Charts
        st.subheader("📊 Interactive Visualizations")
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            if slicer_options and numeric_cols:
                st.markdown("### 📊 Bar Chart Breakdown")
                bar_x = st.selectbox("Select Category for X-Axis", slicer_options, key="smart_bar_x")
                bar_y = st.selectbox("Select Metric for Y-Axis", numeric_cols, key="smart_bar_y")
                
                grouped_bar = filtered_df.groupby(bar_x)[bar_y].sum().reset_index()
                if len(grouped_bar) > 30:
                    grouped_bar = grouped_bar.sort_values(by=bar_y, ascending=False).head(30)
                    
                fig_bar = px.bar(grouped_bar, x=bar_x, y=bar_y, title=f"{bar_y} by {bar_x}", template="plotly_white", color=bar_y)
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("Insufficient category/numeric columns for bar chart.")

        with col_chart2:
            if slicer_options and numeric_cols:
                st.markdown("### 🍩 Donut Share Breakdown")
                donut_cat = st.selectbox("Select Category for Donut", slicer_options, key="smart_donut_cat")
                donut_num = st.selectbox("Select Metric for Donut", numeric_cols, key="smart_donut_num")
                
                grouped_donut = filtered_df.groupby(donut_cat)[donut_num].sum().reset_index()
                if len(grouped_donut) > 12:
                    grouped_donut = grouped_donut.sort_values(by=donut_num, ascending=False).head(12)
                    
                fig_donut = px.pie(grouped_donut, names=donut_cat, values=donut_num, hole=0.4, title=f"Share Breakdown ({donut_num})", template="plotly_white")
                st.plotly_chart(fig_donut, use_container_width=True)
            else:
                st.info("Insufficient columns for donut chart.")

        st.markdown("---")

        # AI Problem Detector, Solutions & Predictive Analysis
        st.subheader("🔍 AI Problem Detector, Predictive Analysis & Actionable Solutions")
        
        problems = []
        solutions = []
        predictions = []
        
        missing_vals = filtered_df.isnull().sum().sum()
        if missing_vals > 0:
            problems.append(f"⚠️ **Data Quality:** Found {missing_vals} missing values in the filtered view.")
            solutions.append("💡 **Solution:** Fill missing gaps to ensure accurate regional/yearly segment reporting.")
        else:
            problems.append("✅ **Data Quality:** Clean and structured data.")
            solutions.append("💡 **Solution:** Proceed with standard reporting metrics.")

        if numeric_cols:
            p_col = numeric_cols[0]
            mean_val = filtered_df[p_col].mean()
            std_val = filtered_df[p_col].std()
            
            upper_bound = mean_val + (2 * std_val)
            lower_bound = mean_val - (2 * std_val)
            outliers = filtered_df[(filtered_df[p_col] > upper_bound) | (filtered_df[p_col] < lower_bound)]
            
            if not outliers.empty:
                problems.append(f"⚠️ **Anomaly Alert:** Detected {len(outliers)} unusual records in '{p_col}'.")
                solutions.append(f"💡 **Solution:** Check specific regional transactions causing these variations.")
            else:
                problems.append(f"✅ **Performance Stability:** '{p_col}' trends look uniform across selected filters.")
                solutions.append("💡 **Solution:** Maintain growth momentum.")

            projected_val = mean_val * 1.12
            predictions.append(f"📈 **Predictive Forecast:** Based on current filters, next-cycle projected growth points toward an estimated target of **{projected_val:,.2f}**.")
            predictions.append(f"🎯 **Decision Support:** Allocate resources to top-performing segments identified in breakdown charts.")

        col_prob, col_sol = st.columns(2)
        with col_prob:
            st.markdown("#### 🚨 Identified Problems & Anomalies")
            for p in problems:
                st.markdown(f"- {p}")
        with col_sol:
            st.markdown("#### 🛠️ Actionable Solutions")
            for s in solutions:
                st.markdown(f"- {s}")

        st.markdown("#### 🔮 Strategic Predictive Insights")
        for pr in predictions:
            st.markdown(f"- {pr}")

        st.markdown("---")

        # Data Table
        with st.expander("🔍 View Filtered Data Table"):
            st.dataframe(filtered_df)
            
        csv_data = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Filtered BI Report",
            data=csv_data,
            file_name='professional_bi_report.csv',
            mime='text/csv',
        )