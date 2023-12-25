import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

# menggunakan path relatif ke file CSV yang berada dalam satu folder dengan stproyekakhirdata.py
file_csv_path = 'all_data_2.csv'


# Membaca DataFrame dari file CSV
all_data_2 = pd.read_csv(file_csv_path)


# df_sum_order_items
def create_sum_order_items(all_data_2):
    df_sum_order_items = all_data_2.groupby("product_category_name").product_id.sum().sort_values(ascending=False).reset_index()
    return df_sum_order_items


# df_payment_methods
def create_payment_methods(all_data_2):
    df_payment_methods = all_data_2.groupby(by="payment_type").product_id.nunique().reset_index()
    df_payment_methods.rename(columns={
        "product_id": "product_count"
    }, inplace=True)

    return df_payment_methods


# df_market_location
def create_market_location(all_data_2):
    df_market_location = all_data_2.groupby(by="customer_city").customer_id.nunique().reset_index()
    df_market_location.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)

    return df_market_location


# df_rfm
def create_df_rfm(df):
    rfm_df = df.groupby(by="customer_id", as_index=False).agg({
        "order_purchase_timestamp": "max",  # mengambil tanggal order terakhir
        "order_id": "nunique",  # menghitung jumlah order
        "price": "sum"  # menghitung jumlah revenue yang dihasilkan
    })

    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]

    # menghitung kapan terakhir pelanggan melakukan transaksi (hari)
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = rfm_df["max_order_timestamp"].max()

    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)

    return rfm_df



# pembuatan filter datetime
columns_datetime = ["order_purchase_timestamp", "order_estimated_delivery_date"]
all_data_2.sort_values( by="order_purchase_timestamp", inplace=True)
all_data_2.reset_index(inplace=True)

for column in columns_datetime:
    all_data_2[column] = pd.to_datetime(all_data_2[column])



# membuat komponen filter
min_date = all_data_2["order_purchase_timestamp"].min()
max_date = all_data_2["order_purchase_timestamp"].max()

with st.sidebar:

    # mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
    
    main_df = all_data_2[(all_data_2["order_purchase_timestamp"] >= str(start_date)) &
                     (all_data_2["order_purchase_timestamp"] <= str(end_date))]


df_sum_order_items = create_sum_order_items(main_df)
df_payment_methods = create_payment_methods(main_df)
df_market_location = create_market_location(main_df)
rfm_df = create_df_rfm(main_df)


# melengkapi dashboard dengan berbagai visuaisasi data

# header
st.header('Brazilian E-Commerce Public Collection Dashboard :sparkles:')

# Penggunaan metode pembayaran
st.subheader("Best Payment Methods")
fig_payment, ax_payment = plt.subplots(figsize=(8, 4), dpi=80) 
sns.barplot(x="payment_type", y="product_count", data=df_payment_methods, palette="viridis", ax=ax_payment)
ax_payment.set_ylabel("Number of Products", fontsize=12)
ax_payment.set_xlabel("Payment Method", fontsize=12)
ax_payment.set_title("Best Payment Methods", fontsize=15)
ax_payment.tick_params(axis='y', labelsize=8)
ax_payment.tick_params(axis='x', labelsize=8)
st.pyplot(fig_payment)


# Lokasi pasar penjualan
st.subheader("Best Market Locations")
fig_market, ax_market = plt.subplots(figsize=(8, 4), dpi=80)  
sns.barplot(x="customer_count", y="customer_city", data=df_market_location.head(3), palette="mako", ax=ax_market) 
ax_market.set_ylabel(None)
ax_market.set_xlabel("Number of Customers", fontsize=12)
ax_market.set_title("Top 20 Market Locations", fontsize=15)
ax_market.tick_params(axis='y', labelsize=8)
ax_market.tick_params(axis='x', labelsize=8)
st.pyplot(fig_market)

# RFM analysis
st.subheader("Best Customer Based on RFM Parameters")

# Metric display
col1, col2, col3 = st.columns(3)
with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)
with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)
with col3:
    avg_monetary = format_currency(rfm_df.monetary.mean(), "AUD", locale='en_US') 
    st.metric("Average Monetary", value=avg_monetary)

# Visualisasi grafik
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(12, 4), dpi=80)  

# Grafik recency
sns.barplot(y="recency", x="customer_id", data=rfm_df.sort_values(by="recency", ascending=True).head(3), palette="muted", ax=ax[0])  
ax[0].set_ylabel("Recency (days)", fontsize=12)
ax[0].set_xlabel("Customer ID", fontsize=12)
ax[0].set_title("By Recency (days)", loc="center", fontsize=15)
ax[0].tick_params(axis='y', labelsize=8)
ax[0].tick_params(axis='x', labelsize=5, rotation=45)

# Grafik frequency
sns.barplot(y="frequency", x="customer_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(3), palette="muted", ax=ax[1])  
ax[1].set_ylabel("Frequency", fontsize=12)
ax[1].set_xlabel("Customer ID", fontsize=12)
ax[1].set_title("By Frequency", loc="center", fontsize=15)
ax[1].tick_params(axis='y', labelsize=8)
ax[1].tick_params(axis='x', labelsize=5, rotation=45)

# Grafik monetary
sns.barplot(y="monetary", x="customer_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(3), palette="muted", ax=ax[2])  # Menggunakan sns.barplot
ax[2].set_ylabel("Monetary", fontsize=12)
ax[2].set_xlabel("Customer ID", fontsize=12)
ax[2].set_title("By Monetary", loc="center", fontsize=15)
ax[2].tick_params(axis='y', labelsize=8)
ax[2].tick_params(axis='x', labelsize=5, rotation=45)


# Menambahkan label pada grafik
for axis in ax:
    axis.set_xlabel("Customer ID", fontsize=12)
    axis.set_ylabel(axis.get_ylabel(), fontsize=12)

st.pyplot(fig)


st.pyplot(fig)

st.caption('Copyright 2023')

