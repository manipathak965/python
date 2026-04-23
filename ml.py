import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestRegressor

# --- 1. Page Configuration & Theme ---
st.set_page_config(page_title="Parcl Real Estate Intelligence", layout="wide")

# Custom CSS for Premium Design
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        border-left: 5px solid #1E3A8A;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        background: linear-gradient(to right, #1E3A8A, #3B82F6);
        color: white;
        height: 3em;
        font-weight: bold;
    }
    h1 { color: #1E3A8A; font-weight: 800; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. Backend Functions (ML & Logic) ---

def apply_ml_and_clustering(data):
    """Cleans data and identifies buyer segments using K-Means."""
    df = data.copy()
    
    # Numeric Cleaning (Fixing the String error)
    num_cols = ['sale_price', 'floor_area_sqft', 'satisfaction_score']
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(r'[$,]', '', regex=True), errors='coerce')
    
    # Age Calculation
    if 'date_of_birth' in df.columns:
        df['date_of_birth'] = pd.to_datetime(df['date_of_birth'], errors='coerce')
        df['age'] = 2024 - df['date_of_birth'].dt.year
        df['age'] = df['age'].fillna(df['age'].median())

    # Clustering logic
    cluster_features = ['age', 'sale_price', 'satisfaction_score']
    df[cluster_features] = df[cluster_features].fillna(df[cluster_features].mean())
    
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(df[cluster_features])
    
    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    df['Cluster'] = kmeans.fit_predict(scaled_data)
    
    # Define Segment Labels
    labels = {0: "💎 Premium Investors", 1: "🏠 Family Homebuyers", 
              2: "📈 Growth Seekers", 3: "🏢 Corporate Clients"}
    df['Buyer Segment'] = df['Cluster'].map(labels)
    
    return df

def price_predictor_tool(data):
    """Random Forest Model to predict property prices."""
    st.markdown("### 🤖 AI Property Price Predictor")
    
    # Train-ready Features
    X = data[['age', 'floor_area_sqft', 'satisfaction_score']].fillna(0)
    y = data['sale_price'].fillna(data['sale_price'].mean())
    
    rf = RandomForestRegressor(n_estimators=100, random_state=42)
    rf.fit(X, y)

    # Input UI
    c1, c2, c3 = st.columns(3)
    with c1: area = st.number_input("Area (sqft)", value=1200)
    with c2: age = st.slider("Property Age", 0, 50, 10)
    with c3: qual = st.slider("Quality/Score", 1, 10, 7)

    if st.button("Predict Market Value"):
        prediction = rf.predict([[age, area, qual]])
        st.success(f"#### 💰 Estimated Value: ${prediction:,.2f}")

# --- 3. Main Dashboard UI ---

st.sidebar.image("https://flaticon.com", width=70)
st.sidebar.title("Parcl Analytics")
st.sidebar.markdown("---")

client_file = st.sidebar.file_uploader("1. Client CSV", type=["csv"])
property_file = st.sidebar.file_uploader("2. Properties CSV", type=["csv"])

if client_file and property_file:
    c_df = pd.read_csv(client_file)
    p_df = pd.read_csv(property_file)
    
    # Clean Column Names
    c_df.columns = c_df.columns.str.strip().str.lower()
    p_df.columns = p_df.columns.str.strip().str.lower()

    if 'client_id' in c_df.columns and 'client_ref' in p_df.columns:
        # Merge Logic
        merged = pd.merge(c_df, p_df, left_on='client_id', right_on='client_ref', how='inner')
        final_df = apply_ml_and_clustering(merged)

        # Dashboard Header
        st.title("🏙️ Real Estate Market Intelligence")
        st.info("AI-powered buyer segmentation and investment profiling for Parcl Co. Limited")

        # Top Level Metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Buyers", len(final_df))
        m2.metric("Avg Sale Price", f"${final_df['sale_price'].mean():,.0f}")
        m3.metric("Avg Area", f"{final_df['floor_area_sqft'].mean():,.0f} sqft")
        m4.metric("Avg Satisfaction", f"{final_df['satisfaction_score'].mean():.1f}/10")

        st.markdown("---")

        # Tabs for Visuals
        tab1, tab2, tab3 = st.tabs(["📊 Segments", "🌐 Map", "🔮 Price Predictor"])

        with tab1:
            col_l, col_r = st.columns(2)
            with col_l:
                st.plotly_chart(px.pie(final_df, names='Buyer Segment', hole=0.5, title="Buyer Segments"), use_container_width=True)
            with col_r:
                st.plotly_chart(px.box(final_df, x='Buyer Segment', y='sale_price', color='Buyer Segment', title="Price Range per Segment"), use_container_width=True)

        with tab2:
            st.plotly_chart(px.scatter_geo(final_df, locations="country", locationmode='country names', color="Buyer Segment", size="sale_price", projection="natural earth"), use_container_width=True)

        with tab3:
            price_predictor_tool(final_df)

        st.markdown("---")
        with st.expander("📂 View Full Merged Data"):
            st.dataframe(final_df)
    else:
        st.error("Missing linking columns! Ensure Client CSV has 'client_id' and Properties CSV has 'client_ref'.")
else:
    st.title("👋 Welcome to Parcl Intelligence Dashboard")
    st.image("https://unsplash.com", use_column_width=True)
    st.info("Please upload both CSV files in the sidebar to start the AI analysis.")
