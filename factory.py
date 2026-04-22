import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Nassau Candy Logistics", layout="wide")
st.title("🚛 Factory-to-Customer Shipping Efficiency Dashboard")

factory_coords = {
    'Factory': ["Lot's O' Nuts", "Wicked Choccy's", "Sugar Shack", "Secret Factory", "The Other Factory"],
    'F_Lat': [32.881893, 32.076176, 48.11914, 41.446333, 35.1175],
    'F_Lon': [-111.768036, -81.088371, -96.18115, -90.565487, -89.971107]
}
df_factories = pd.DataFrame(factory_coords)

product_to_factory = {
    'Wonka Bar - Nutty Crunch Surprise': "Lot's O' Nuts",
    'Wonka Bar - Fudge Mallows': "Lot's O' Nuts",
    'Wonka Bar -Scrumdiddlyumptious': "Lot's O' Nuts",
    'Wonka Bar - Milk Chocolate': "Wicked Choccy's",
    'Wonka Bar - Triple Dazzle Caramel': "Wicked Choccy's",
    'Laffy Taffy': "Sugar Shack",
    'SweeTARTS': "Sugar Shack",
    'Nerds': "Sugar Shack",
    'Fun Dip': "Sugar Shack",
    'Fizzy Lifting Drinks': "Sugar Shack",
    'Everlasting Gobstopper': "Secret Factory",
    'Hair Toffee': "The Other Factory",
    'Lickable Wallpaper': "Secret Factory",
    'Wonka Gum': "Secret Factory",
    'Kazookles': "The Other Factory"
}

st.sidebar.header("Step 1: Upload Data")
uploaded_file = st.sidebar.file_uploader("Upload your Nassau Candy CSV", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    # Required columns from your dataset
    required_cols = ['Row ID', 'Order ID', 'Order Date', 'Ship Date', 'Ship Mode', 'Customer ID', 'Country/Region', 'City', 'State/Province', 'Postal Code', 'Division', 'Region', 'Product ID', 'Product Name', 'Sales', 'Units', 'Gross Profit', 'Cost']
    
    if all(col in df.columns for col in required_cols):
        st.success("✅ Columns Matched! Loading Analysis...")

        # Factory Mapping
        df['Factory_Name'] = df['Product Name'].map(product_to_factory)
        df = df.merge(df_factories, left_on='Factory_Name', right_on='Factory', how='left')
        
        # Fixing Dates (Corrected dayfirst spelling)
        df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True, errors='coerce')
        df['Ship Date'] = pd.to_datetime(df['Ship Date'], dayfirst=True, errors='coerce')
        
        # Lead Time Calculation
        df['Lead_Time'] = (df['Ship Date'] - df['Order Date']).dt.days
        df = df[df['Lead_Time'] >= 0].dropna(subset=['Lead_Time'])
        
        # Route Definition (Using 'State/Province' as per your required_cols)
        df['Route'] = df['Factory_Name'] + " ➔ " + df['State/Province']

        st.sidebar.divider()
        st.sidebar.header("Step 2: Filters")
        selected_states = st.sidebar.multiselect("Select States", options=df['State/Province'].unique(), default=df['State/Province'].unique())
        filtered_df = df[df['State/Province'].isin(selected_states)]
        
        # KPIs
        m1, m2, m3 = st.columns(3)
        m1.metric("Avg Lead Time", f"{filtered_df['Lead_Time'].mean():.2f} Days")
        m2.metric("Total Shipments", len(filtered_df))
        m3.metric("Busiest Route", filtered_df['Route'].mode()[0] if not filtered_df.empty else "N/A")

        st.divider()
        col_a, col_b = st.columns(2)

        with col_a:
            st.subheader("Route Efficiency (Avg Days)")
            route_avg = filtered_df.groupby('Route')['Lead_Time'].mean().sort_values().reset_index()
            fig_bar = px.bar(route_avg, x='Lead_Time', y='Route', orientation='h', color='Lead_Time', color_continuous_scale='Reds')
            st.plotly_chart(fig_bar, use_container_width=True)

        with col_b:
            st.subheader("State-wise Delivery Heatmap")
            state_avg = filtered_df.groupby('State/Province')['Lead_Time'].mean().reset_index()
            fig_map = px.choropleth(state_avg, locations='State/Province', locationmode="USA-states", color='Lead_Time', scope="usa", color_continuous_scale="Reds")
            st.plotly_chart(fig_map, use_container_width=True)

    else:
        st.error(f"❌ Error: Aapki file mein zaroori columns nahi mile!")
        st.stop()

else:
    st.info("👋 Welcome! Side-bar se 'Nassau_Candy_Data.csv' file upload karke analysis shuru karein.")
