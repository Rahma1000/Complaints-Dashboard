import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("📊 Customer Complaints Dashboard")

df = pd.read_csv("rows.csv", low_memory=False)
df['Date received'] = pd.to_datetime(df['Date received'])

st.sidebar.header("🔍 Filters")


start_date = st.sidebar.date_input("Start Date", df['Date received'].min())
end_date = st.sidebar.date_input("End Date", df['Date received'].max())


product_list = ['All'] + sorted(df['Product'].dropna().unique().tolist())
selected_product = st.sidebar.selectbox("🛍️ Filter by Product", product_list)

company_list = ['All'] + sorted(df['Company'].dropna().unique().tolist())
selected_company = st.sidebar.selectbox("🏢 Filter by Company", company_list)

filtered_df = df[
    (df['Date received'] >= pd.to_datetime(start_date)) &
    (df['Date received'] <= pd.to_datetime(end_date))
]

if selected_product != 'All':
    filtered_df = filtered_df[filtered_df['Product'] == selected_product]

if selected_company != 'All':
    filtered_df = filtered_df[filtered_df['Company'] == selected_company]

tab1, tab2, tab3 = st.tabs(["📊 Main Analysis", "🗺️ States Analysis", "📘 Company Response Analysis"])

with tab1:
    filtered_df["Month"] = filtered_df["Date received"].dt.strftime('%Y-%m')
    monthly_counts = filtered_df.groupby("Month").size().reset_index(name="Count")

    st.subheader("📈 Monthly Complaint Volume")
    fig1 = px.line(monthly_counts, x="Month", y="Count", title="Monthly Complaints Over Time")
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("🔝 Top 10 Complained Products")
    top_products = filtered_df['Product'].value_counts().head(10).reset_index()
    top_products.columns = ['Product', 'Count']
    fig2 = px.bar(top_products, x='Count', y='Product', orientation='h', title="Top 10 Products")
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("🏢 Top 10 Companies by Complaints")
    top_companies = filtered_df['Company'].value_counts().head(10).reset_index()
    top_companies.columns = ['Company', 'Count']
    fig3 = px.bar(top_companies, x='Count', y='Company', orientation='h', title="Top 10 Companies")
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("📄 Sample Complaint Records")
    st.dataframe(filtered_df[['Date received', 'Product', 'Company', 'Issue']].head(20))

    st.subheader("⬇️ Download Filtered Data")
    @st.cache_data
    def convert_df_to_csv(data):
        return data.to_csv(index=False).encode('utf-8')

    csv = convert_df_to_csv(filtered_df)
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name='filtered_complaints.csv',
        mime='text/csv',
    )


with tab2:
    st.subheader("🗺️ Top 10 States by Complaint Volume")
    top_states = filtered_df['State'].value_counts().head(10).reset_index()
    top_states.columns = ['State', 'Count']
    fig4 = px.bar(top_states, x='Count', y='State', orientation='h', title="Top 10 States")
    st.plotly_chart(fig4, use_container_width=True)


with tab3:
    st.subheader("📘 Company Response Types")

    
    def classify_response(x):
        if x in ['Closed with explanation', 'Closed with monetary relief', 'Closed with non-monetary relief']:
            return 'Positive'
        else:
            return 'Negative'

    filtered_df['Response Category'] = filtered_df['Company response to consumer'].apply(classify_response)
    response_counts = filtered_df['Response Category'].value_counts().reset_index()
    response_counts.columns = ['Response', 'Count']

    fig5 = px.pie(response_counts, names='Response', values='Count', title="Company Response (Positive vs Negative)")
    st.plotly_chart(fig5, use_container_width=True)
